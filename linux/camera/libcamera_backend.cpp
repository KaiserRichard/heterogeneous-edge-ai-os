#include "camera.h"
extern "C" {
#include "hea_runtime.h"
}
#include <libcamera/libcamera.h>
#include <libcamera/control_ids.h>
#include <libcamera/formats.h>
#include <array>
#include <atomic>
#include <chrono>
#include <cstring>
#include <span>
#include <linux/dma-buf.h>
#include <map>
#include <stdexcept>
#include <string>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <thread>
#include <unistd.h>

namespace {
void check(int rc, const char *what) {
    if (rc < 0) throw std::runtime_error(std::string(what) + ": " + std::to_string(rc));
}
struct Mapping { void *base; size_t size; const uint8_t *pixels; int fd; };
class Capture {
public:
    Capture(uint32_t w, uint32_t h, double fps, const Frame &callback)
        : width(w), height(h), duration(static_cast<int64_t>(1000000.0 / fps)), frame(callback) {}
    ~Capture() {
        if (started) camera->stop(); // Wait for callbacks before releasing mapped buffers.
        if (camera) camera->requestCompleted.disconnect(this);
        requests.clear();
        for (const auto &entry : maps) munmap(entry.second.base, entry.second.size);
        allocator.reset();
        if (acquired) camera->release();
        camera.reset();
        manager.stop();
    }
    void run() {
        check(manager.start(), "start CameraManager");
        if (manager.cameras().empty()) throw std::runtime_error("no libcamera cameras found");
        camera = manager.cameras().front();
        check(camera->acquire(), "acquire camera"); acquired = true;
        auto config = camera->generateConfiguration({libcamera::StreamRole::Viewfinder});
        if (!config || config->empty()) throw std::runtime_error("no viewfinder configuration");
        auto &stream_config = config->at(0);
        // libcamera's BGR888 is RGB byte order on little-endian systems.
        stream_config.pixelFormat = libcamera::formats::BGR888;
        stream_config.size = {width, height};
        stream_config.bufferCount = 4;
        if (config->validate() == libcamera::CameraConfiguration::Invalid ||
                stream_config.pixelFormat != libcamera::formats::BGR888 ||
                stream_config.size.width != width || stream_config.size.height != height)
            throw std::runtime_error("camera cannot provide requested packed RGB dimensions/format");
        check(camera->configure(config.get()), "configure camera");
        stride = stream_config.stride;
        if (stride < width * 3) throw std::runtime_error("invalid RGB stride");
        stream = stream_config.stream();
        allocator = std::make_unique<libcamera::FrameBufferAllocator>(camera);
        check(allocator->allocate(stream), "allocate frame buffers");
        rgb.resize(size_t(width) * height * 3);
        for (const auto &buffer : allocator->buffers(stream)) {
            if (buffer->planes().size() != 1) throw std::runtime_error("packed RGB needs one plane");
            const auto &plane = buffer->planes().front();
            if (plane.length < size_t(stride) * height) throw std::runtime_error("short RGB plane");
            size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
            size_t offset = plane.offset / page * page, delta = plane.offset - offset;
            size_t length = delta + plane.length;
            void *base = mmap(nullptr, length, PROT_READ, MAP_SHARED, plane.fd.get(), static_cast<off_t>(offset));
            if (base == MAP_FAILED) throw std::runtime_error("mmap camera DMA buffer failed");
            maps.emplace(buffer.get(), Mapping{base, length, static_cast<const uint8_t *>(base) + delta, plane.fd.get()});
            auto request = camera->createRequest();
            if (!request) throw std::runtime_error("create camera request failed");
            check(request->addBuffer(stream, buffer.get()), "add request buffer");
            requests.push_back(std::move(request));
        }
        if (requests.empty()) throw std::runtime_error("no capture buffers allocated");
        if (camera->controls().find(&libcamera::controls::FrameDurationLimits) == camera->controls().end())
            throw std::runtime_error("camera lacks FrameDurationLimits control");
        camera->requestCompleted.connect(this, &Capture::completed);
        libcamera::ControlList controls(camera->controls());
        const std::array<int64_t, 2> limits{duration, duration};
        controls.set(libcamera::controls::FrameDurationLimits, std::span<const int64_t, 2>(limits));
        check(camera->start(&controls), "start camera"); started = true;
        for (auto &request : requests) check(camera->queueRequest(request.get()), "queue initial request");
        while (!hea_stop && !finished.load(std::memory_order_acquire))
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        check(camera->stop(), "stop camera"); started = false;
        if (!failure.empty()) throw std::runtime_error(failure);
    }
private:
    void completed(libcamera::Request *request) {
        // Bracket each BOOTTIME sample with RAW and use the narrowest pair.
        uint64_t boot_now = 0, raw_now = 0, best_width = UINT64_MAX;
        for (int i = 0; i < 3; ++i) {
            const uint64_t before = hea_raw_now();
            const uint64_t boot = hea_now(CLOCK_BOOTTIME);
            const uint64_t after = hea_raw_now();
            if (after - before < best_width) {
                best_width = after - before;
                boot_now = boot;
                raw_now = before + best_width / 2;
            }
        }
        const uint64_t recv = raw_now;
        if (request->status() == libcamera::Request::RequestCancelled || hea_stop || finished.load()) return;
        try {
            auto *buffer = request->findBuffer(stream);
            if (!buffer) throw std::runtime_error("completed request missing RGB buffer");
            const auto &meta = buffer->metadata();
            uint32_t sequence = meta.sequence;
            if (have_sequence && sequence <= last_sequence)
                throw std::runtime_error("capture sequence wrapped/regressed; start a new run");
            last_sequence = sequence; have_sequence = true;
            auto timestamp = request->metadata().get(libcamera::controls::SensorTimestamp);
            uint64_t sensor = timestamp && *timestamp > 0 ? static_cast<uint64_t>(*timestamp) : 0;
            const uint64_t input_raw = sensor && boot_now >= sensor
                ? raw_now - (boot_now - sensor) : 0;
            const uint8_t *pixels = nullptr;
            const char *status = "missing_timestamp";
            if (sensor) {
                status = "capture_error";
                // FrameStartup (rpt libcamera): full frame while AGC/AWB settle; timing is valid.
                const bool usable = meta.status == libcamera::FrameMetadata::FrameSuccess ||
                                    meta.status == libcamera::FrameMetadata::FrameStartup;
                if (usable &&
                        meta.planes().size() == 1 && meta.planes()[0].bytesused >= size_t(stride) * height) {
                    const auto &mapping = maps.at(buffer);
                    dma_buf_sync sync{DMA_BUF_SYNC_START | DMA_BUF_SYNC_READ};
                    if (ioctl(mapping.fd, DMA_BUF_IOCTL_SYNC, &sync) < 0)
                        throw std::runtime_error("DMA_BUF_SYNC_START failed");
                    for (uint32_t y = 0; y < height; ++y)
                        std::memcpy(rgb.data() + size_t(y) * width * 3,
                                    mapping.pixels + size_t(y) * stride, size_t(width) * 3);
                    sync.flags = DMA_BUF_SYNC_END | DMA_BUF_SYNC_READ;
                    if (ioctl(mapping.fd, DMA_BUF_IOCTL_SYNC, &sync) < 0)
                        throw std::runtime_error("DMA_BUF_SYNC_END failed");
                    pixels = rgb.data();
                }
            }
            if (!frame(sequence, sensor, recv, input_raw, pixels, status)) { finished.store(true); return; }
            request->reuse(libcamera::Request::ReuseBuffers);
            check(camera->queueRequest(request), "requeue request");
        } catch (const std::exception &e) {
            failure = e.what(); finished.store(true, std::memory_order_release);
        }
    }
    uint32_t width, height, stride = 0, last_sequence = 0;
    int64_t duration;
    Frame frame;
    libcamera::CameraManager manager;
    std::shared_ptr<libcamera::Camera> camera;
    std::unique_ptr<libcamera::FrameBufferAllocator> allocator;
    libcamera::Stream *stream = nullptr;
    std::vector<std::unique_ptr<libcamera::Request>> requests;
    std::map<libcamera::FrameBuffer *, Mapping> maps;
    std::vector<uint8_t> rgb;
    std::atomic<bool> finished{false};
    bool started = false, acquired = false, have_sequence = false;
    std::string failure;
};
}
void capture_libcamera(uint32_t width, uint32_t height, double fps, const Frame &frame) {
    Capture capture(width, height, fps, frame);
    capture.run();
}
