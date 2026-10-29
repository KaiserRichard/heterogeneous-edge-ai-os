#ifndef HEA_CAMERA_RING_H
#define HEA_CAMERA_RING_H
#include <cstddef>
#include <cstdint>
#include <string>

namespace hea {
// ABI v1: native little endian, 64-byte header; slots aligned to 64 bytes.
struct Header {
    uint32_t magic, version, width, height, slots, pixels, stride, ready;
    uint8_t reserved[32];
};
struct Slot { uint64_t seq; uint32_t frame_id; uint32_t reserved; };
static_assert(sizeof(Header) == 64 && sizeof(Slot) == 16, "ring ABI");
class Ring {
public:
    Ring(const std::string &name, uint32_t width = 0, uint32_t height = 0, uint32_t slots = 0);
    ~Ring();
    Ring(const Ring &) = delete;
    Ring &operator=(const Ring &) = delete;
    const Header &header() const { return *header_; }
    uint64_t write(uint32_t id, const uint8_t *rgb);
    // 0 success, 1 overwritten/unpublished, 2 torn/busy; one bounded attempt.
    int read(uint32_t id, uint8_t *rgb, size_t size) const;
    Slot *slot(uint32_t id) const;
    // Keep completed frames available to consumers draining the socket after exit.
    void retain_name() { unlink_on_close_ = false; }
private:
    int fd_ = -1;
    size_t size_ = 0;
    Header *header_ = nullptr;
    std::string name_;
    bool owner_ = false;
    bool unlink_on_close_ = true;
};
}
extern "C" {
void *hea_camera_open(const char *name, uint32_t *width, uint32_t *height);
int hea_camera_read(void *reader, uint32_t id, uint8_t *rgb, size_t size);
void hea_camera_close(void *reader);
const char *hea_camera_error();
}
#endif
