#include "ring.h"
#include <algorithm>
#include <atomic>
#include <cassert>
#include <functional>
#include <iostream>
#include <thread>
#include <vector>
#include <unistd.h>

std::function<void()> copy_hook;
void hea_camera_copy_hook() { if (copy_hook) copy_hook(); }

int main() {
    std::string name = "hea-test-" + std::to_string(getpid());
    {
        hea::Ring writer(name, 64, 32, 2), reader(name);
        std::vector<uint8_t> pixels(writer.header().pixels, 42), copy(pixels.size());
        assert(reader.read(0, copy.data(), copy.size()) == 1); // Never published.
        assert(writer.write(0, pixels.data()) == 2);
        assert(reader.read(0, copy.data(), copy.size()) == 0 && copy == pixels);
        assert(writer.write(2, pixels.data()) == 4);
        assert(reader.read(0, copy.data(), copy.size()) == 1); // Reused slot.
        assert(reader.read(2, copy.data(), copy.size()) == 0);
        __atomic_store_n(&writer.slot(2)->seq, 5u, __ATOMIC_SEQ_CST);
        assert(reader.read(2, copy.data(), copy.size()) == 2); // Paused mid-write.
        __atomic_store_n(&writer.slot(2)->seq, 6u, __ATOMIC_RELEASE);
        // Deterministically reuse the slot between the copy and final seq load.
        copy_hook = [&] { writer.write(4, pixels.data()); };
        assert(reader.read(2, copy.data(), copy.size()) == 2);
        copy_hook = {};
        bool refused = false;
        try { hea::Ring duplicate(name, 1, 1, 1); } catch (...) { refused = true; }
        assert(refused);
    }
    // Reopening after normal Ring destruction proves cleanup; one slot maximizes contention.
    {
        hea::Ring writer(name, 128, 128, 1), reader(name);
        std::atomic<bool> go{false}, done{false};
        std::atomic<uint32_t> latest{0};
        std::atomic<uint32_t> checked{0};
        std::vector<uint8_t> pixels(writer.header().pixels, 0), copy(pixels.size());
        writer.write(0, pixels.data());
        std::thread producer([&] {
            while (!go.load()) std::this_thread::yield();
            for (uint32_t id = 1; id <= 250; ++id) {
                std::fill(pixels.begin(), pixels.end(), static_cast<uint8_t>(id));
                writer.write(id, pixels.data()); latest.store(id);
                // Periodically hold a published frame until the concurrent reader
                // accepts it; this checks successful copies as well as collisions.
                if (id % 25 == 0) while (checked.load() < id) std::this_thread::yield();
            }
            done.store(true);
        });
        unsigned valid = 0, torn = 0, overwritten = 0;
        go.store(true);
        do {
            uint32_t id = latest.load();
            int result = reader.read(id, copy.data(), copy.size());
            if (!result) {
                ++valid;
                assert(std::all_of(copy.begin(), copy.end(), [id](uint8_t value) {
                    return value == static_cast<uint8_t>(id);
                }));
                checked.store(id);
            } else if (result == 2) ++torn;
            else ++overwritten;
        } while (!done.load());
        producer.join();
        assert(valid >= 10);
        assert(reader.read(250, copy.data(), copy.size()) == 0);
        assert(std::all_of(copy.begin(), copy.end(), [](uint8_t value) { return value == 250; }));
        std::cout << "PASS: concurrent atomic copies (valid=" << valid << ", torn=" << torn
                  << ", overwritten=" << overwritten << "); no torn payload accepted\n";
    }
    std::cout << "PASS: unpublished slot, odd sequence and changed-after-copy rejected, slot reuse, exclusive owner, cleanup\n";
}
