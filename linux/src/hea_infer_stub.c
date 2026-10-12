#include "hea_ipc.h"
#include "hea_runtime.h"
#include <errno.h>
#include <inttypes.h>
#include <poll.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

#define MAX_DURATIONS 4096u
static size_t load_durations(const char *path, uint64_t *values)
{
    if (!path) return 0;
    FILE *f = fopen(path, "r");
    if (!f) hea_fatal("open durations");
    size_t n = 0;
    char line[128];
    while (fgets(line, sizeof(line), f)) {
        char *end;
        errno = 0;
        unsigned long long v = strtoull(line, &end, 10);
        int no_digits = end == line;
        while (*end == ' ' || *end == '\t' || *end == '\r' || *end == '\n') ++end;
        if (errno || no_digits || *end || line[0] == '-' || v > 60000000u || n == MAX_DURATIONS) {
            fprintf(stderr, "durations: require 1..4096 lines of integer CPU microseconds (0..60000000)\n");
            exit(2);
        }
        values[n++] = (uint64_t)v;
    }
    if (ferror(f)) hea_fatal("read durations");
    fclose(f);
    if (!n) { fprintf(stderr, "empty durations file\n"); exit(2); }
    return n;
}
static void busy(uint64_t us)
{
    uint64_t start = hea_now(CLOCK_THREAD_CPUTIME_ID);
    volatile uint32_t v = 1;
    while (!hea_stop && hea_now(CLOCK_THREAD_CPUTIME_ID) - start < us * UINT64_C(1000))
        for (unsigned i = 0; i < 256u; ++i) v = v * 1664525u + 1013904223u;
}
int main(int argc, char **argv)
{
    struct hea_options o;
    int rc = hea_options_parse(argc, argv, &o);
    if (rc) return rc > 0 ? 0 : 2;
    if ((!o.socket_path && o.socket_fd < 0) || (!o.output_path && o.output_fd < 0)) {
        fprintf(stderr, "hea_infer_stub requires --socket PATH --output PATH\n"); return 2;
    }
    uint64_t durations[MAX_DURATIONS];
    size_t nd = load_durations(o.durations_path, durations);
    hea_signals();
    int fd = hea_socket_input(&o), output = hea_socket_output(&o);
    FILE *csv = hea_csv_open(o.csv_path, "frame_id,t_input_ns,t_done_ns,work_us,status");
    if (hea_schedule(&o)) { close(fd); hea_socket_cleanup(&o); return 1; }
    uint64_t processed = 0, sent = 0, malformed = 0, interrupted = 0, skipped = 0;
    while (!hea_stop && (!o.count || processed < o.count)) {
        struct pollfd p = { fd, POLLIN, 0 };
        if (poll(&p, 1, -1) < 0) { if (errno == EINTR) continue; hea_fatal("inference poll"); }
        uint8_t bytes[HEA_INPUT_SIZE + 1u];
        ssize_t n = recv(fd, bytes, sizeof(bytes), 0);
        if (n < 0) { if (errno == EAGAIN || errno == EINTR) continue; hea_fatal("inference recv"); }
        struct hea_input in;
        if (hea_input_unpack(&in, bytes, (size_t)n) || in.t_input_ns > hea_raw_now()) { ++malformed; continue; }
        if (o.input_latest) {
            while (!hea_stop) {
                n = recv(fd, bytes, sizeof(bytes), MSG_DONTWAIT);
                if (n < 0) {
                    if (errno == EINTR) continue;
                    if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                    hea_fatal("inference drain");
                }
                struct hea_input next;
                if (hea_input_unpack(&next, bytes, (size_t)n) || next.t_input_ns > hea_raw_now()) {
                    ++malformed; continue;
                }
                /* Arrival order defines newest, including frame ID wrap. */
                if (fprintf(csv, "%" PRIu32 ",%" PRIu64 ",,0,skipped_stale\n",
                            in.frame_id, in.t_input_ns) < 0) hea_fatal("inference skip CSV");
                ++skipped;
                in = next;
            }
        }
        uint64_t work = nd ? durations[(size_t)(processed % nd)] : o.work_us;
        busy(work);
        if (hea_stop) { ++interrupted; break; }
        struct hea_result result = { in.frame_id, in.t_input_ns, hea_raw_now(), 0, 100 };
        uint8_t out[HEA_RESULT_SIZE]; hea_result_pack(&result, out);
        int ok = hea_send_record(output, o.output_path, out, sizeof(out));
        sent += (uint64_t)ok; ++processed;
        if (fprintf(csv, "%" PRIu32 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%s\n",
                    result.frame_id, result.t_input_ns, result.t_done_ns, work,
                    ok ? "sent" : "dropped") < 0) hea_fatal("inference CSV");
    }
    fprintf(stderr, "{\"processed\":%" PRIu64 ",\"sent\":%" PRIu64
            ",\"dropped\":%" PRIu64 ",\"malformed\":%" PRIu64 ",\"interrupted\":%" PRIu64
            ",\"skipped\":%" PRIu64 "}\n",
            processed, sent, processed - sent, malformed, interrupted, skipped);
    close(fd); close(output); hea_socket_cleanup(&o);
    if (fclose(csv)) hea_fatal("close inference CSV");
    return 0;
}
