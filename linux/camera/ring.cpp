#include "ring.h"
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <stdexcept>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef HEA_CAMERA_TEST_HOOK
void hea_camera_copy_hook();
#endif

namespace {
constexpr uint32_t magic = 0x43414548; // HEAC
static_assert(__atomic_always_lock_free(8, nullptr), "requires lock-free 64-bit atomics");
static_assert(__atomic_always_lock_free(1, nullptr), "requires lock-free byte atomics");
std::string object_name(std::string name) {
    if (!name.empty() && name[0] == '/') name.erase(0, 1);
    if (name.empty() || name.size() > 100 || name.find_first_not_of(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-") != std::string::npos)
        throw std::runtime_error("shm NAME must contain only letters, digits, underscore or hyphen");
#ifdef __APPLE__
    return "/tmp/hea-cam-" + name; // macOS has no /dev/shm; host-only mmap surrogate.
#else
    return "/" + name;
#endif
}
void remove_object(const std::string &name) {
#ifdef __APPLE__
    unlink(name.c_str());
#else
    shm_unlink(name.c_str());
#endif
}
size_t layout(uint32_t w, uint32_t h, uint32_t n, uint32_t &pixels, uint32_t &stride) {
    if (!w || !h || w > 4096 || h > 4096 || !n || n > 64)
        throw std::runtime_error("ring requires dimensions 1..4096 and slots 1..64");
    pixels = w * h * 3;
    stride = (pixels + sizeof(hea::Slot) + 63u) & ~63u;
    size_t size = sizeof(hea::Header) + size_t(n) * stride;
    if (size > 256u * 1024u * 1024u) throw std::runtime_error("ring exceeds 256 MiB limit");
    return size;
}
}
namespace hea {
Ring::Ring(const std::string &name, uint32_t w, uint32_t h, uint32_t n)
    : name_(object_name(name)), owner_(w != 0) {
    const uint16_t endian = 1;
    if (*reinterpret_cast<const uint8_t *>(&endian) != 1)
        throw std::runtime_error("ring ABI requires little endian");
    int flags = owner_ ? O_RDWR | O_CREAT | O_EXCL : O_RDONLY;
#ifdef __APPLE__
    fd_ = open(name_.c_str(), flags | O_NOFOLLOW, 0600);
#else
    fd_ = shm_open(name_.c_str(), flags, 0600);
#endif
    if (fd_ < 0) throw std::runtime_error("open ring: " + std::string(std::strerror(errno)));
    try {
        uint32_t pixels = 0, stride = 0;
        if (owner_) {
            size_ = layout(w, h, n, pixels, stride);
            if (ftruncate(fd_, static_cast<off_t>(size_))) throw std::runtime_error("size ring failed");
        } else {
            struct stat st{};
            if (fstat(fd_, &st) || st.st_size < static_cast<off_t>(sizeof(Header)) ||
                    st.st_size > 256 * 1024 * 1024) throw std::runtime_error("invalid ring size");
            size_ = static_cast<size_t>(st.st_size);
        }
        void *p = mmap(nullptr, size_, owner_ ? PROT_READ | PROT_WRITE : PROT_READ, MAP_SHARED, fd_, 0);
        if (p == MAP_FAILED) throw std::runtime_error("map ring failed");
        header_ = static_cast<Header *>(p);
        if (owner_) {
            std::memset(header_, 0, size_);
            *header_ = {magic, 1, w, h, n, pixels, stride, 0, {0}};
            __atomic_store_n(&header_->ready, 1u, __ATOMIC_RELEASE);
        } else {
            if (__atomic_load_n(&header_->ready, __ATOMIC_ACQUIRE) != 1 ||
                    header_->magic != magic || header_->version != 1)
                throw std::runtime_error("ring not ready or unsupported ABI");
            size_t expected = layout(header_->width, header_->height, header_->slots, pixels, stride);
            if (expected != size_ || header_->pixels != pixels || header_->stride != stride)
                throw std::runtime_error("invalid ring layout");
        }
    } catch (...) {
        if (header_) munmap(header_, size_);
        close(fd_);
        if (owner_) remove_object(name_);
        throw;
    }
}
Ring::~Ring() {
    if (header_) munmap(header_, size_);
    if (fd_ >= 0) close(fd_);
    if (owner_ && unlink_on_close_) remove_object(name_);
}
Slot *Ring::slot(uint32_t id) const {
    return reinterpret_cast<Slot *>(reinterpret_cast<uint8_t *>(header_) + sizeof(Header) +
                                    size_t(id % header_->slots) * header_->stride);
}
uint64_t Ring::write(uint32_t id, const uint8_t *rgb) {
    if (!owner_) throw std::runtime_error("read-only ring");
    Slot *s = slot(id);
    uint64_t seq = __atomic_load_n(&s->seq, __ATOMIC_RELAXED);
    __atomic_store_n(&s->seq, seq + 1, __ATOMIC_SEQ_CST);
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    __atomic_store_n(&s->frame_id, id, __ATOMIC_RELAXED);
    auto *dst = reinterpret_cast<uint8_t *>(s + 1);
    for (uint32_t i = 0; i < header_->pixels; ++i) __atomic_store_n(dst + i, rgb[i], __ATOMIC_RELAXED);
    __atomic_store_n(&s->seq, seq + 2, __ATOMIC_RELEASE);
    return seq + 2;
}
int Ring::read(uint32_t id, uint8_t *rgb, size_t size) const {
    if (size != header_->pixels) throw std::runtime_error("incorrect pixel buffer size");
    Slot *s = slot(id);
    uint64_t before = __atomic_load_n(&s->seq, __ATOMIC_ACQUIRE);
    if (before & 1u) return 2;
    if (!before) return 1;
    uint32_t stored = __atomic_load_n(&s->frame_id, __ATOMIC_RELAXED);
    auto *src = reinterpret_cast<const uint8_t *>(s + 1);
    for (uint32_t i = 0; i < header_->pixels; ++i) rgb[i] = __atomic_load_n(src + i, __ATOMIC_RELAXED);
#ifdef HEA_CAMERA_TEST_HOOK
    hea_camera_copy_hook();
#endif
    __atomic_thread_fence(__ATOMIC_SEQ_CST);
    if (__atomic_load_n(&s->seq, __ATOMIC_ACQUIRE) != before) return 2;
    return stored == id ? 0 : 1;
}
}
namespace { thread_local std::string last_error; }
extern "C" void *hea_camera_open(const char *name, uint32_t *w, uint32_t *h) {
    try {
        auto *ring = new hea::Ring(name);
        *w = ring->header().width; *h = ring->header().height;
        return ring;
    } catch (const std::exception &e) { last_error = e.what(); return nullptr; }
}
extern "C" int hea_camera_read(void *reader, uint32_t id, uint8_t *rgb, size_t size) {
    try { return static_cast<hea::Ring *>(reader)->read(id, rgb, size); }
    catch (const std::exception &e) { last_error = e.what(); return -1; }
}
extern "C" void hea_camera_close(void *reader) { delete static_cast<hea::Ring *>(reader); }
extern "C" const char *hea_camera_error() { return last_error.c_str(); }
