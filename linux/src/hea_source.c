#include "hea_ipc.h"
#include "hea_runtime.h"
#include <errno.h>
#include <inttypes.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    struct hea_options o;
    int rc = hea_options_parse(argc, argv, &o);
    if (rc) return rc > 0 ? 0 : 2;
    if (!o.output_path && o.output_fd < 0) { fprintf(stderr, "hea_source requires --output PATH\n"); return 2; }
    hea_signals();
    int fd = hea_socket_output(&o);
    FILE *csv = hea_csv_open(o.csv_path, "frame_id,t_input_ns,status");
    if (hea_schedule(&o)) return 1;
    uint64_t period = o.period_ms * UINT64_C(1000000);
    uint64_t deadline = hea_now(CLOCK_MONOTONIC), generated = 0, sent = 0, missed = 0;
    while (!hea_stop && (!o.count || generated < o.count)) {
        rc = hea_sleep_until(deadline);
        if (rc && !(rc == EINTR && hea_stop)) { errno = rc; hea_fatal("absolute sleep"); }
        if (hea_stop) break;
        if (generated > UINT32_MAX) { fprintf(stderr, "frame_id exhausted; start a new run\n"); break; }
        struct hea_input in = { (uint32_t)generated, hea_raw_now() };
        uint8_t bytes[HEA_INPUT_SIZE]; hea_input_pack(&in, bytes);
        int ok = hea_send_record(fd, o.output_path, bytes, sizeof(bytes));
        sent += (uint64_t)ok;
        if (fprintf(csv, "%" PRIu32 ",%" PRIu64 ",%s\n", in.frame_id, in.t_input_ns,
                    ok ? "sent" : "dropped") < 0) hea_fatal("source CSV");
        ++generated; deadline += period;
        uint64_t now = hea_now(CLOCK_MONOTONIC);
        if (now > deadline) {
            uint64_t skip = (now - deadline) / period + 1u;
            deadline += skip * period; missed += skip;
        }
    }
    fprintf(stderr, "{\"generated\":%" PRIu64 ",\"sent\":%" PRIu64
            ",\"dropped\":%" PRIu64 ",\"missed_releases\":%" PRIu64 "}\n",
            generated, sent, generated - sent, missed);
    close(fd);
    if (fclose(csv)) hea_fatal("close source CSV");
    return 0;
}
