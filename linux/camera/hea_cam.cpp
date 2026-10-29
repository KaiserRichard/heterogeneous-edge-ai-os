#include "camera.h"
#include "ring.h"
extern "C" {
#include "hea_ipc.h"
#include "hea_runtime.h"
}
#include <cerrno>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#include <unistd.h>

namespace {
uint64_t number(const std::string &s, uint64_t max) {
    size_t used = 0;
    if (s.empty() || s.find_first_not_of("0123456789") != std::string::npos)
        throw std::runtime_error("invalid integer: " + s);
    uint64_t value = std::stoull(s, &used);
    if (used != s.size() || value > max) throw std::runtime_error("out-of-range integer: " + s);
    return value;
}
}
int main(int argc, char **argv) {
    try {
        std::string backend = "fake", name = "hea_camera";
        uint32_t width = 640, height = 480, slots = 4;
        double fps = 30;
        uint64_t offset = 1000000, drop_every = 0;
        bool fps_set = false, period_set = false;
        std::vector<char *> common{argv[0]};
        for (int i = 1; i < argc; ++i) {
            std::string key(argv[i]), value;
            auto equal = key.find('=');
            if (equal != std::string::npos) { value = key.substr(equal + 1); key.resize(equal); }
            bool own = key == "--backend" || key == "--width" || key == "--height" ||
                key == "--fps" || key == "--shm" || key == "--slots" ||
                key == "--fake-offset-ns" || key == "--fake-drop-every";
            if (!own) {
                if (key == "--period-ms") period_set = true;
                if (key == "--help") std::cout << "hea_cam: --backend fake|libcamera --width 640 --height 480 --fps 30\n"
                    "--shm hea_camera --slots 4 --fake-offset-ns 1000000 --fake-drop-every 0\n";
                common.push_back(argv[i]); continue;
            }
            if (equal == std::string::npos) {
                if (++i == argc) throw std::runtime_error("missing value for " + key);
                value = argv[i];
            }
            if (key == "--backend") backend = value;
            else if (key == "--shm") name = value;
            else if (key == "--width") width = static_cast<uint32_t>(number(value, 4096));
            else if (key == "--height") height = static_cast<uint32_t>(number(value, 4096));
            else if (key == "--slots") slots = static_cast<uint32_t>(number(value, 64));
            else if (key == "--fake-offset-ns") offset = number(value, UINT64_MAX);
            else if (key == "--fake-drop-every") drop_every = number(value, UINT32_MAX);
            else {
                size_t used;
                fps = std::stod(value, &used); fps_set = true;
                if (used != value.size() || !std::isfinite(fps) || fps < 0.1 || fps > 1000)
                    throw std::runtime_error("fps must be in 0.1..1000");
            }
        }
        int common_argc = static_cast<int>(common.size()); common.push_back(nullptr);
        hea_options options{};
        int parsed = hea_options_parse(common_argc, common.data(), &options);
        if (parsed) return parsed > 0 ? 0 : 2;
        if (period_set && fps_set) throw std::runtime_error("choose --fps or --period-ms");
        if (period_set) fps = 1000.0 / static_cast<double>(options.period_ms);
        if (!options.output_path && options.output_fd < 0) throw std::runtime_error("--output PATH required");
        if (backend != "fake" && backend != "libcamera") throw std::runtime_error("unknown backend");
#ifndef HEA_HAVE_LIBCAMERA
        if (backend == "libcamera") throw std::runtime_error("libcamera backend not built (pkg-config libcamera unavailable)");
#endif
        if (backend == "libcamera" && (offset != 1000000 || drop_every))
            throw std::runtime_error("fake timestamp/drop options require fake backend");
        hea_signals();
        if (hea_schedule(&options)) return 1;
        hea::Ring ring(name, width, height, slots);
        std::vector<uint8_t> pixels(ring.header().pixels);
        int fd = hea_socket_output(&options);
        FILE *csv = hea_csv_open(options.csv_path, "frame_id,seq,t_sensor_ns,t_recv_mono_ns,t_input_ns,status");
        uint64_t boot = 0;
#ifdef CLOCK_BOOTTIME
        boot = hea_now(CLOCK_BOOTTIME);
#endif
        uint64_t mono = hea_now(CLOCK_MONOTONIC);
        std::string metadata = "{\"backend\":\"" + backend + "\",\"shm\":\"" + name +
            "\",\"width\":" + std::to_string(width) + ",\"height\":" + std::to_string(height) +
            ",\"slots\":" + std::to_string(slots) + ",\"fps\":" + std::to_string(fps) +
            ",\"clock_boottime_ns\":" + (boot ? std::to_string(boot) : "null") +
            ",\"clock_monotonic_ns\":" + std::to_string(mono) +
            ",\"t_input_clock\":\"" + (backend == "fake" ? "CLOCK_MONOTONIC" : "SensorTimestamp (CLOCK_BOOTTIME; requires no suspend)") + "\"}";
        std::cerr << metadata << '\n';
        if (options.csv_path) {
            std::string path = std::string(options.csv_path) + ".meta.json";
            FILE *meta = std::fopen(path.c_str(), "w");
            if (!meta) hea_fatal("open camera metadata");
            if (std::fprintf(meta, "%s\n", metadata.c_str()) < 0 || std::fclose(meta)) hea_fatal("write camera metadata");
        }
        uint64_t generated = 0, sent = 0, missed = 0;
        Frame frame = [&](uint32_t sequence, uint64_t sensor, uint64_t recv, const uint8_t *rgb, const char *status) {
            if (hea_stop || (options.count && generated >= options.count)) return false;
            if (rgb) {
                ring.write(sequence, rgb);
                hea_input record{sequence, sensor};
                uint8_t bytes[HEA_INPUT_SIZE]; hea_input_pack(&record, bytes);
                int ok = hea_send_record(fd, options.output_path, bytes, sizeof(bytes));
                status = ok ? "sent" : "dropped"; sent += static_cast<uint64_t>(ok);
            }
            if (std::fprintf(csv, "%u,%u,%llu,%llu,%llu,%s\n", sequence, sequence,
                    static_cast<unsigned long long>(sensor), static_cast<unsigned long long>(recv),
                    static_cast<unsigned long long>(sensor), status) < 0) hea_fatal("camera CSV");
            ++generated;
            return !hea_stop && (!options.count || generated < options.count);
        };
        if (backend == "fake") {
            uint64_t period = static_cast<uint64_t>(1e9 / fps), deadline = mono, sequence = 0;
            while (!hea_stop && sequence <= UINT32_MAX) {
                int rc = hea_sleep_until(deadline);
                if (rc && !(rc == EINTR && hea_stop)) { errno = rc; hea_fatal("camera sleep"); }
                if (hea_stop) break;
                uint64_t recv = hea_now(CLOCK_MONOTONIC);
                if (recv < offset) throw std::runtime_error("fake offset exceeds monotonic timestamp");
                for (uint32_t y = 0; y < height; ++y) for (uint32_t x = 0; x < width; ++x) {
                    size_t p = (size_t(y) * width + x) * 3;
                    pixels[p] = static_cast<uint8_t>(x + sequence);
                    pixels[p + 1] = static_cast<uint8_t>(y + sequence);
                    pixels[p + 2] = static_cast<uint8_t>(sequence);
                }
                bool drop = drop_every && (sequence + 1) % drop_every == 0;
                if (!frame(static_cast<uint32_t>(sequence), recv - offset, recv,
                           drop ? nullptr : pixels.data(), "injected_drop")) break;
                ++sequence; deadline += period;
                uint64_t now = hea_now(CLOCK_MONOTONIC);
                if (now > deadline) {
                    uint64_t skip = (now - deadline) / period + 1;
                    deadline += skip * period; sequence += skip; missed += skip;
                }
            }
        }
#ifdef HEA_HAVE_LIBCAMERA
        else capture_libcamera(width, height, fps, frame);
#endif
        std::cerr << "{\"generated\":" << generated << ",\"sent\":" << sent
                  << ",\"dropped\":" << generated - sent << ",\"missed_releases\":" << missed << "}\n";
        close(fd);
        if (std::fclose(csv)) hea_fatal("close camera CSV");
        ring.retain_name();
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "hea_cam: " << error.what() << '\n'; return 2;
    }
}
