#ifndef HEA_CAMERA_H
#define HEA_CAMERA_H
#include <cstdint>
#include <functional>
// RGB bytes are tightly packed, valid only during the callback. seq is the
// capture buffer sequence (not Request::sequence); nullptr denotes capture error.
// seq, raw sensor timestamp, RAW receive timestamp, mapped RAW input timestamp.
using Frame = std::function<bool(uint32_t, uint64_t, uint64_t, uint64_t, const uint8_t *, const char *)>;
void capture_libcamera(uint32_t width, uint32_t height, double fps, const Frame &frame);
#endif
