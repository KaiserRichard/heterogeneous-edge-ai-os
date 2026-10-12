#include "hea_proto.h"
#include "hea_runtime.h"
#include "../../stm32/firmware/uart_budget.h"
#include <errno.h>
#include <inttypes.h>
#include <sys/select.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    struct hea_options o;
    int rc = hea_options_parse(argc, argv, &o);
    if (rc) return rc > 0 ? 0 : 2;
    if (!o.serial_path && o.serial_fd < 0) { fprintf(stderr, "hea_rx requires --serial PATH\n"); return 2; }
    hea_signals();
    int fd = hea_serial_get(&o);
    if (fd >= FD_SETSIZE) { errno = EINVAL; hea_fatal("receiver fd exceeds pselect range"); }
    FILE *csv = hea_csv_open(o.csv_path, "type,seq,frame_id,t_input_ns,t_send_ns,t_rx_ns,age_at_send_us,crc_ok");
    if (hea_schedule(&o)) return 1;
    struct hea_parser parser; hea_parser_init(&parser);
    uint32_t frame_started = 0;
    uint64_t results = 0, malformed = 0;
    while (!hea_stop && (!o.count || results < o.count)) {
        sigset_t blocked, previous;
        sigemptyset(&blocked); sigaddset(&blocked, SIGINT); sigaddset(&blocked, SIGTERM);
        if (sigprocmask(SIG_BLOCK, &blocked, &previous)) hea_fatal("rx signal mask");
        fd_set readable; FD_ZERO(&readable); FD_SET(fd, &readable);
        int ready = hea_stop ? 0 : pselect(fd + 1, &readable, NULL, NULL, NULL, &previous);
        int wait_error = errno;
        if (sigprocmask(SIG_SETMASK, &previous, NULL)) hea_fatal("rx restore mask");
        if (hea_stop) break;
        if (ready < 0) { if (wait_error == EINTR) continue; errno = wait_error; hea_fatal("rx pselect"); }
        uint8_t bytes[1024];
        ssize_t n = read(fd, bytes, sizeof(bytes));
        if (n < 0) { if (errno == EAGAIN || errno == EINTR) continue; hea_fatal("rx read"); }
        if (!n) { fprintf(stderr, "receiver serial EOF\n"); return 1; }
        for (size_t i = 0; i < (size_t)n; ++i) {
            uint32_t errors = parser.stats.crc_errors;
            int frame_ready = hea_uart_feed(&parser, bytes[i], (uint32_t)(hea_raw_now() / 1000u),
                                &frame_started, (uint32_t)HEA_UART_ASSEMBLY_US(o.baud));
            if (parser.stats.crc_errors != errors)
                if (fprintf(csv, "CRC_ERROR,,,,,%" PRIu64 ",,0\n", hea_raw_now()) < 0) hea_fatal("rx CSV");
            if (!frame_ready) continue;
            uint64_t t_rx = hea_raw_now();
            struct hea_frame *f = &parser.frame;
            if (f->type == HEA_MSG_INFERENCE) {
                struct hea_inference m;
                if (hea_unpack_inference(f, &m)) { ++malformed; continue; }
                if (fprintf(csv, "INFERENCE,%" PRIu16 ",%" PRIu32 ",%" PRIu64 ",",
                            f->seq, m.input_seq, m.linux_input_ns) < 0) hea_fatal("rx CSV");
                if (f->version != HEA_PROTO_VERSION_LEGACY && m.age_at_send_us != UINT32_MAX &&
                    m.linux_input_ns <= UINT64_MAX - (uint64_t)m.age_at_send_us * 1000u)
                    if (fprintf(csv, "%" PRIu64, m.linux_input_ns + (uint64_t)m.age_at_send_us * 1000u) < 0)
                        hea_fatal("rx CSV");
                if (fprintf(csv, ",%" PRIu64 ",", t_rx) < 0) hea_fatal("rx CSV");
                if (f->version != HEA_PROTO_VERSION_LEGACY)
                    if (fprintf(csv, "%" PRIu32, m.age_at_send_us) < 0) hea_fatal("rx CSV");
                if (fprintf(csv, ",1\n") < 0) hea_fatal("rx CSV");
                ++results;
            } else if (f->type == HEA_MSG_HEARTBEAT) {
                struct hea_heartbeat h;
                if (hea_unpack_heartbeat(f, &h)) { ++malformed; continue; }
                if (fprintf(csv, "HEARTBEAT,%" PRIu16 ",,,%" PRIu64 ",%" PRIu64 ",,1\n",
                            f->seq, h.linux_send_ns, t_rx) < 0) hea_fatal("rx CSV");
            } else {
                if (fprintf(csv, "TYPE_%u,%" PRIu16 ",,,,%" PRIu64 ",,1\n", (unsigned)f->type,
                            f->seq, t_rx) < 0) hea_fatal("rx CSV");
            }
            if (o.count && results >= o.count) break;
        }
    }
    fprintf(stderr, "{\"inferences\":%" PRIu64 ",\"frames_ok\":%" PRIu32
            ",\"crc_errors\":%" PRIu32 ",\"len_errors\":%" PRIu32
            ",\"version_errors\":%" PRIu32 ",\"malformed\":%" PRIu64 "}\n",
            results, parser.stats.frames_ok, parser.stats.crc_errors, parser.stats.len_errors,
            parser.stats.version_errors, malformed);
    close(fd);
    if (fclose(csv)) hea_fatal("close rx CSV");
    return 0;
}
