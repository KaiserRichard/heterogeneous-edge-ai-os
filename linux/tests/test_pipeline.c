#include "hea_ipc.h"
#include "hea_proto.h"
#include "hea_runtime.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>
#ifdef __APPLE__
#include <util.h>
#else
#include <pty.h>
#endif

#define N 32u
static pid_t children[16];
static size_t child_count;
static int connected_ipc;
static char directory[] = "build/pipeline-test-XXXXXX";
static void cleanup(void)
{
    for (size_t i = 0; i < child_count; ++i) {
        if (children[i] > 0) { kill(children[i], SIGKILL); waitpid(children[i], NULL, 0); }
    }
}
static void path(char *out, size_t cap, const char *name)
{
    int n = snprintf(out, cap, "%s/%s", directory, name);
    assert(n > 0 && (size_t)n < cap);
}
static void pause_ms(uint64_t ms)
{
    assert(!hea_sleep_until(hea_now(CLOCK_MONOTONIC) + ms * UINT64_C(1000000)));
}
static pid_t launch(char *const args[], int master, int slave, int keep_master)
{
    pid_t pid = fork(); assert(pid >= 0);
    if (!pid) {
        if (!keep_master) close(master);
        close(slave);
        for (size_t i = 1; args[i]; ++i)
            if (!strcmp(args[i], "--serial-fd") || !strcmp(args[i], "--socket-fd") || !strcmp(args[i], "--output-fd")) {
                ++i; assert(args[i]);
                if (fcntl(atoi(args[i]), F_SETFD, 0)) _exit(126);
            }
        char logfile[256];
        const char *base = strrchr(args[0], '/'); assert(base);
        path(logfile, sizeof(logfile), base + 1);
        int logfd = open(logfile, O_WRONLY | O_CREAT | O_APPEND, 0600);
        if (logfd < 0 || dup2(logfd, STDERR_FILENO) < 0) _exit(126);
        close(logfd); execv(args[0], args); _exit(127);
    }
    assert(child_count < sizeof(children) / sizeof(children[0]));
    children[child_count++] = pid; return pid;
}
static void finish(pid_t pid, int terminate)
{
    if (terminate) assert(!kill(pid, SIGTERM));
    int status = 0;
    for (unsigned i = 0; i < 1000u; ++i) {
        pid_t rc = waitpid(pid, &status, WNOHANG);
        assert(rc >= 0);
        if (rc == pid) {
            for (size_t j = 0; j < child_count; ++j) if (children[j] == pid) children[j] = 0;
            if (!WIFEXITED(status) || WEXITSTATUS(status)) {
                fprintf(stderr, "child %ld failed; logs in %s\n", (long)pid, directory); exit(1);
            }
            return;
        }
        pause_ms(10);
    }
    fprintf(stderr, "child timed out; logs in %s\n", directory); exit(1);
}
static void ready(const char *filename)
{
    for (unsigned i = 0; i < 500u; ++i) {
        struct stat st;
        if (!stat(filename, &st) && (S_ISSOCK(st.st_mode) || st.st_size > 0)) return;
        pause_ms(10);
    }
    fprintf(stderr, "startup timed out for %s; logs in %s\n", filename, directory); exit(1);
}
static void check_csv(const char *bridge_path, const char *rx_path, unsigned expected, unsigned expected_crc_errors)
{
    uint16_t sequences[N];
    uint64_t inputs[N], dones[N], sends[N];
    FILE *f = fopen(bridge_path, "r"); assert(f);
    char line[512]; assert(fgets(line, sizeof(line), f));
    unsigned i = 0;
    while (fgets(line, sizeof(line), f)) {
        uint32_t id;
        assert(i < expected);
        assert(sscanf(line, "%" SCNu16 ",%" SCNu32 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64,
                      &sequences[i], &id, &inputs[i], &dones[i], &sends[i]) == 5);
        assert(id == i && inputs[i] <= dones[i] && dones[i] <= sends[i]);
        ++i;
    }
    fclose(f); assert(i == expected);
    f = fopen(rx_path, "r"); assert(f); assert(fgets(line, sizeof(line), f));
    i = 0; uint16_t next = 0; unsigned heartbeat_count = 0, crc_errors = 0;
    while (fgets(line, sizeof(line), f)) {
        if (!strncmp(line, "CRC_ERROR,", 10)) { ++crc_errors; continue; }
        char type[32]; uint16_t seq;
        assert(sscanf(line, "%31[^,],%" SCNu16, type, &seq) == 2);
        assert(seq == next); next = (uint16_t)(next + 1u);
        if (!strcmp(type, "HEARTBEAT")) { ++heartbeat_count; continue; }
        assert(!strcmp(type, "INFERENCE") && i < expected && heartbeat_count > 0);
        uint32_t id, age; uint64_t input, reconstructed, rx; unsigned crc;
        assert(sscanf(line, "%31[^,],%" SCNu16 ",%" SCNu32 ",%" SCNu64 ",%" SCNu64
                      ",%" SCNu64 ",%" SCNu32 ",%u", type, &seq, &id, &input,
                      &reconstructed, &rx, &age, &crc) == 8);
        uint32_t want;
        assert(!hea_age_at_send_us(inputs[i], sends[i], &want));
        assert(seq == sequences[i] && id == i && input == inputs[i] && age == want && crc == 1);
        assert(reconstructed >= sends[i] && reconstructed - sends[i] < 1000u);
        assert(rx >= sends[i]); ++i;
    }
    fclose(f); assert(i == expected && heartbeat_count > 0 && crc_errors == expected_crc_errors);
}
static void run_case(int full_pipeline)
{
    int master, slave; char tty[128];
    assert(!openpty(&master, &slave, tty, NULL, NULL));
    assert(!fcntl(master, F_SETFD, FD_CLOEXEC));
    assert(!hea_serial_configure(slave, 115200));
    char fd_text[32], socket_path[256], source_socket[256], bridge_csv[256], rx_csv[256];
    assert(snprintf(fd_text, sizeof(fd_text), "%d", master) > 0);
    path(socket_path, sizeof(socket_path), full_pipeline ? "full.sock" : "direct.sock");
    path(source_socket, sizeof(source_socket), "input.sock");
    path(bridge_csv, sizeof(bridge_csv), full_pipeline ? "full-bridge.csv" : "direct-bridge.csv");
    path(rx_csv, sizeof(rx_csv), full_pipeline ? "full-rx.csv" : "direct-rx.csv");
    int result_pair[2] = {-1, -1}, input_pair[2] = {-1, -1};
    char result_read[32], result_write[32], input_read[32], input_write[32];
    if (connected_ipc) {
        assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, result_pair));
        assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, input_pair));
        for (unsigned i = 0; i < 2u; ++i) {
            assert(!fcntl(result_pair[i], F_SETFD, FD_CLOEXEC));
            assert(!fcntl(input_pair[i], F_SETFD, FD_CLOEXEC));
        }
        snprintf(result_read, sizeof(result_read), "%d", result_pair[1]);
        snprintf(result_write, sizeof(result_write), "%d", result_pair[0]);
        snprintf(input_read, sizeof(input_read), "%d", input_pair[1]);
        snprintf(input_write, sizeof(input_write), "%d", input_pair[0]);
    }
    char *rx_args[] = {"build/san/hea_rx", "--serial-fd", fd_text, "--csv", rx_csv,
        "--baud", "115200", "--count", full_pipeline ? "8" : "32", NULL};
    pid_t rx = launch(rx_args, master, slave, 1); ready(rx_csv);
    if (!full_pipeline) {
        uint8_t payload[HEA_MAX_PAYLOAD], wire[HEA_MAX_FRAME];
        struct hea_heartbeat h = {hea_raw_now(), 123};
        uint8_t len = hea_pack_heartbeat(&h, payload);
        size_t n = hea_encode(HEA_MSG_HEARTBEAT, UINT16_MAX, payload, len, wire, sizeof(wire));
        wire[n - 1u] ^= 1u;
        assert(write(slave, wire, n) == (ssize_t)n);
    }
    char *bridge_args[] = {"build/san/hea_bridge", "--serial", tty,
        connected_ipc ? "--socket-fd" : "--socket", connected_ipc ? result_read : socket_path,
        "--csv", bridge_csv, "--baud", "115200", "--heartbeat-ms", "5", "--policy", "fifo", "--echo-ms", "0", "--status-csv", "/dev/null", "--echo-csv", "/dev/null", "--inf-rx-csv", "/dev/null", "--state-events-csv", "/dev/null", "--control-csv", "/dev/null", NULL};
    pid_t bridge = launch(bridge_args, master, slave, 0); ready(connected_ipc ? bridge_csv : socket_path);
    if (!full_pipeline) {
        int sender = connected_ipc ? result_pair[0] : hea_socket_sender();
        const char *destination = connected_ipc ? NULL : socket_path;
        uint8_t bytes[HEA_RESULT_SIZE + 1u];
        memset(bytes, 0, sizeof(bytes));
        assert(hea_send_record(sender, destination, bytes, sizeof(bytes)));
        struct hea_result future = { UINT32_MAX, 1, hea_raw_now() + UINT64_C(60000000000), 0, 100 };
        hea_result_pack(&future, bytes);
        assert(hea_send_record(sender, destination, bytes, HEA_RESULT_SIZE));
        pause_ms(10);
        for (uint32_t i = 0; i < N; ++i) {
            uint64_t now = hea_raw_now();
            struct hea_result r = { i, now - 1000001u, now, 7, 99 };
            hea_result_pack(&r, bytes);
            assert(hea_send_record(sender, destination, bytes, HEA_RESULT_SIZE));
            pause_ms(5);
        }
        if (!connected_ipc) close(sender);
    } else {
        char duration_path[256], infer_csv[256], source_csv[256];
        path(duration_path, sizeof(duration_path), "durations.txt");
        FILE *d = fopen(duration_path, "w"); assert(d); fputs("0\n1000\n", d); fclose(d);
        path(infer_csv, sizeof(infer_csv), "infer.csv"); path(source_csv, sizeof(source_csv), "source.csv");
        char *infer_args[] = {"build/san/hea_infer_stub", connected_ipc ? "--socket-fd" : "--socket",
            connected_ipc ? input_read : source_socket, connected_ipc ? "--output-fd" : "--output",
            connected_ipc ? result_write : socket_path,
            "--durations", duration_path, "--csv", infer_csv, "--count", "8", NULL};
        pid_t infer = launch(infer_args, master, slave, 0); ready(connected_ipc ? infer_csv : source_socket);
        char *source_args[] = {"build/san/hea_source", connected_ipc ? "--output-fd" : "--output",
            connected_ipc ? input_write : source_socket,
            "--period-ms", "10", "--count", "8", "--csv", source_csv, NULL};
        pid_t source = launch(source_args, master, slave, 0);
        finish(source, 0); finish(infer, 0);
    }
    finish(rx, 0); finish(bridge, 1);
    check_csv(bridge_csv, rx_csv, full_pipeline ? 8u : N, full_pipeline ? 0u : 1u);
    close(master); close(slave);
    if (connected_ipc) for (unsigned i = 0; i < 2u; ++i) { close(result_pair[i]); close(input_pair[i]); }
}
static void fake_mcu(void)
{
    int master, slave, pair[2]; char tty[128], fd[32];
    assert(!openpty(&master, &slave, tty, NULL, NULL));
    assert(!hea_serial_configure(slave, 115200));
    assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, pair));
    snprintf(fd, sizeof(fd), "%d", pair[1]);
    char status[256], echo[256], tx[256], events[256], reports[256];
    path(reports, sizeof(reports), "inf_rx.csv");
    path(status, sizeof(status), "status.csv"); path(echo, sizeof(echo), "echo.csv");
    path(tx, sizeof(tx), "fake-tx.csv"); path(events, sizeof(events), "events.csv");
    char *args[] = {"build/san/hea_bridge", "--serial", tty, "--socket-fd", fd,
        "--inf-rx-csv", reports, "--csv", tx, "--status-csv", status, "--echo-csv", echo, "--state-events-csv", events,
        "--echo-ms", "20", "--baud", "115200", "--control-csv", "/dev/null", NULL};
    pid_t bridge = launch(args, master, slave, 0); ready(status);
    uint8_t payload[64], wire[HEA_MAX_FRAME];
    struct hea_mcu_status_extended x = {{123, 3, 4, 5}, 6, 7, 8, 9, 10, 11, 1, 12, 13, 14, 15, 16, 2100, -18000, 10000};
    uint8_t len = hea_pack_mcu_status(&x.base, payload);
    size_t n = hea_encode(HEA_MSG_MCU_STATUS, 40, payload, len, wire, sizeof(wire));
    wire[n-1] ^= 1; assert(write(master, wire, n) == (ssize_t)n);
    wire[n-1] ^= 1; assert(write(master, wire, 3) == 3);
    assert(write(master, wire+3, n-3) == (ssize_t)(n-3));
    len = hea_pack_mcu_status_extended(&x, payload);
    n = hea_encode(HEA_MSG_MCU_STATUS, 41, payload, len, wire, sizeof(wire));
    assert(write(master, wire, n) == (ssize_t)n);
    n = hea_encode(HEA_MSG_MCU_STATUS, 45, payload, 33, wire, sizeof(wire));
    assert(write(master, wire, n) == (ssize_t)n); /* Previous firmware diagnostics. */
    n = hea_encode(HEA_MSG_MCU_STATUS, 46, payload, 38, wire, sizeof(wire));
    assert(write(master, wire, n) == (ssize_t)n); /* Clock/event-era firmware. */
    n = hea_encode(HEA_MSG_MCU_STATUS, 47, payload, 58, wire, sizeof(wire));
    assert(write(master, wire, n) == (ssize_t)n); /* IRQ timing-era firmware. */
    struct hea_parser parser; hea_parser_init(&parser);
    struct hea_state_event ev = {UINT64_C(0x2ffffd8ef), 1, 2, 9, UINT64_MAX, UINT64_C(0x2ffffd800), 7};
    len = hea_pack_state_event(&ev, payload);
    n = hea_encode(HEA_MSG_STATE_EVENT, 42, payload, len, wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n); /* Before estimator: empty mapped time. */
    struct hea_inf_rx report = {65535, 123456, UINT64_C(0x2ffffd8ef), 2, 7};
    len = hea_pack_inf_rx(&report, payload);
    n = hea_encode(HEA_MSG_INF_RX, 50, payload, len, wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n); /* No map/fit yet. */
    uint64_t input_stamp = hea_raw_now() - 20000000u;
    struct hea_result result = {1234, input_stamp, input_stamp + 10000000u, 7, 99};
    uint8_t ipc[HEA_RESULT_SIZE]; hea_result_pack(&result, ipc);
    assert(send(pair[0], ipc, sizeof ipc, 0) == (ssize_t)sizeof ipc);
    unsigned replies = 0;
    int have_inference = 0;
    uint16_t inference_seq = 0;
    uint64_t start = hea_now(CLOCK_MONOTONIC);
    uint64_t raw_start = hea_raw_now();
    while ((replies < 3 || !have_inference) && hea_now(CLOCK_MONOTONIC)-start < UINT64_C(2000000000)) {
        uint8_t bytes[256]; ssize_t nr = read(master, bytes, sizeof(bytes));
        if (nr < 0) { assert(errno == EAGAIN || errno == EINTR); pause_ms(1); continue; }
        for (ssize_t i = 0; i < nr; ++i) {
            if (!hea_parser_feed(&parser, bytes[i])) continue;
            if (parser.frame.type == HEA_MSG_INFERENCE) {
                inference_seq = parser.frame.seq; have_inference = 1;
            }
            if (parser.frame.type != HEA_MSG_ECHO_REQ || replies >= 3) continue;
            struct hea_echo_req req; assert(!hea_unpack_echo_req(&parser.frame, &req));
            uint32_t t2 = (uint32_t)((uint64_t)UINT32_MAX - 10000u + (hea_raw_now()-raw_start)/1000u);
            struct hea_echo_resp resp = {req.linux_t1_ns, t2, t2};
            len = hea_pack_echo_resp(&resp, payload);
            n = hea_encode(HEA_MSG_ECHO_RESP, parser.frame.seq, payload, len, wire, sizeof(wire));
            assert(write(master, wire, n) == (ssize_t)n); ++replies;
        }
    }
    assert(replies == 3 && have_inference); pause_ms(10);
    ev.mcu_us = UINT64_C(0x2ffffd8ef) + (hea_raw_now() - raw_start) / 1000u;
    len = hea_pack_state_event(&ev, payload);
    n = hea_encode(HEA_MSG_STATE_EVENT, 43, payload, len, wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n);
    report.wire_seq = inference_seq; report.mcu_rx_us = ev.mcu_us;
    len = hea_pack_inf_rx(&report, payload);
    n = hea_encode(HEA_MSG_INF_RX, 51, payload, len, wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n);
    n = hea_encode(HEA_MSG_INF_RX, 52, payload, 22, wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n);
    len = hea_pack_state_event(&ev, payload);
    /* A malformed event must not produce a CSV row. */
    n = hea_encode(HEA_MSG_STATE_EVENT, 44, payload, (uint8_t)(len - 1u), wire, sizeof wire);
    assert(write(master, wire, n) == (ssize_t)n);
    pause_ms(10); finish(bridge, 1);
    FILE *f = fopen(status, "r"); assert(f); char line[1024];
    assert(fgets(line, sizeof(line), f)); assert(fgets(line, sizeof(line), f));
    assert(strstr(line, ",123,3,4,5,0,,,,,,"));
    assert(fgets(line, sizeof(line), f)); assert(strstr(line, ",123,3,4,5,1,6,7,8,9,10,11,1,12,13,14,15,16,2100,-18000,10000\n"));
    assert(fgets(line, sizeof(line), f)); assert(strstr(line, ",123,3,4,5,1,6,7,8,9,10,11,,,,,,,,,\n"));
    assert(fgets(line, sizeof(line), f)); assert(strstr(line, ",123,3,4,5,1,6,7,8,9,10,11,1,12,,,,,,,\n"));
    assert(fgets(line, sizeof(line), f));
    assert(strstr(line, ",123,3,4,5,1,6,7,8,9,10,11,1,12,13,14,15,16,2100,,\n"));
    assert(!fgets(line, sizeof(line), f)); fclose(f);
    f = fopen(echo, "r"); assert(f); assert(fgets(line, sizeof(line), f));
    unsigned count = 0;
    while (fgets(line, sizeof(line), f)) {
        unsigned commas = 0; for (char *c = line; *c; ++c) if (*c == ',') ++commas;
        unsigned seq_read, accepted;
        uint64_t t1, t4, t2ext, t3ext, reference, delay;
        uint32_t t2raw, t3raw; double offset;
        assert(sscanf(line, "%u,%" SCNu64 ",%" SCNu32 ",%" SCNu32 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%u,%" SCNu64 ",%lf,%" SCNu64,
            &seq_read, &t1, &t2raw, &t3raw, &t4, &t2ext, &t3ext, &accepted, &reference, &offset, &delay) == 11);
        assert(commas == 19 && accepted == 1 && t4 >= t1 && t3ext >= t2ext);
        assert(delay <= (t4/1000u-t1/1000u)-(t3ext-t2ext));
        ++count;
    }
    assert(count == 3); fclose(f);
    f = fopen(events, "r"); assert(f); assert(fgets(line, sizeof(line), f));
    assert(strstr(line, "lost_count,t_mcu_pi_est_ns"));
    assert(fgets(line, sizeof(line), f));
    assert(strstr(line, ",1,2,9,18446744073709551615,12884891648,7,\n"));
    assert(fgets(line, sizeof(line), f));
    unsigned seq_event, old, state, reason, lost;
    uint64_t rx, mcu, hb, inf; long double mapped;
    assert(sscanf(line, "%u,%" SCNu64 ",%" SCNu64 ",%u,%u,%u,%" SCNu64 ",%" SCNu64 ",%u,%Lf",
        &seq_event, &rx, &mcu, &old, &state, &reason, &hb, &inf, &lost, &mapped) == 10);
    assert(seq_event == 43 && mcu == ev.mcu_us && hb == UINT64_MAX && lost == 7);
    assert(mapped > (long double)rx - 20000000.0L && mapped < (long double)rx + 20000000.0L);
    assert(!fgets(line, sizeof(line), f)); fclose(f);
    f = fopen(reports, "r"); assert(f); assert(fgets(line, sizeof line, f));
    assert(strstr(line, "seq,frame_id,t_input_ns,mcu_rx_us,t_mcu_pi_est_ns,age_mcu_us,state,lost_count"));
    assert(fgets(line, sizeof line, f)); assert(strstr(line, "65535,,,12884891887,,123456,2,7,,"));
    assert(fgets(line, sizeof line, f));
    unsigned wire_seq, frame_id, report_state, report_lost;
    uint64_t ti, receipt, age_us, report_rx; long double pi_stamp, aoi;
    assert(sscanf(line, "%u,%u,%" SCNu64 ",%" SCNu64 ",%Lf,%" SCNu64 ",%u,%u,%Lf,%" SCNu64,
        &wire_seq, &frame_id, &ti, &receipt, &pi_stamp, &age_us, &report_state, &report_lost, &aoi, &report_rx) == 10);
    assert(wire_seq == inference_seq && frame_id == 1234 && ti == input_stamp && receipt == report.mcu_rx_us);
    assert(age_us == 123456 && report_state == 2 && report_lost == 7);
    assert(fabsl((pi_stamp - (long double)ti) / 1000.0L - aoi) < 0.001L);
    assert(!fgets(line, sizeof line, f)); fclose(f);
    puts("PASS: INF_RX absent correlation/fit, extended MCU time, mapped receipt AoI, local age, losses and malformed rejection");
    puts("PASS: state event CSV, absent estimator, full MCU epoch alignment and mapped Pi time");
    puts("PASS: fake MCU base/v3 diagnostics, CRC recovery, echo estimator and timer wrap over openpty"); close(master); close(slave); close(pair[0]); close(pair[1]);
}
/* Exercise the real SIGUSR1 handler and UART loop over a PTY, without hardware. */
static uint64_t control_ack(const char *filename, unsigned expected_rows, int expected_state)
{
    for (unsigned attempt = 0; attempt < 400u; ++attempt) {
        FILE *f = fopen(filename, "r"); assert(f);
        char line[256]; assert(fgets(line, sizeof line, f));
        unsigned rows = 0; uint64_t stamp = 0; int state = -1; size_t pending = 0;
        while (fgets(line, sizeof line, f)) {
            assert(sscanf(line, "%" SCNu64 ",%d,%zu", &stamp, &state, &pending) == 3);
            ++rows;
        }
        fclose(f);
        if (rows == expected_rows) { assert(state == expected_state && stamp > 0); return stamp; }
        pause_ms(5);
    }
    assert(0 && "SIGUSR1 ack timeout"); return 0;
}
static void control_frames(int master, struct hea_parser *parser, int result_fd,
                           uint32_t id, unsigned *hb, unsigned *inf, uint32_t *last_id)
{
    uint64_t now = hea_raw_now();
    struct hea_result r = {id, now - 20000000u, now, 7, 99};
    uint8_t bytes[HEA_RESULT_SIZE]; hea_result_pack(&r, bytes);
    assert(send(result_fd, bytes, sizeof bytes, 0) == (ssize_t)sizeof bytes);
    uint64_t end = hea_now(CLOCK_MONOTONIC) + 10000000u;
    while (hea_now(CLOCK_MONOTONIC) < end) {
        uint8_t wire[256]; ssize_t n = read(master, wire, sizeof wire);
        if (n < 0) { assert(errno == EAGAIN || errno == EINTR); pause_ms(1); continue; }
        for (ssize_t i = 0; i < n; ++i) {
            if (!hea_parser_feed(parser, wire[i])) continue;
            if (parser->frame.type == HEA_MSG_HEARTBEAT) ++*hb;
            else if (parser->frame.type == HEA_MSG_INFERENCE) {
                struct hea_inference m; assert(!hea_unpack_inference(&parser->frame, &m));
                ++*inf; *last_id = m.input_seq;
            } else assert(0 && "unexpected frame while echoes disabled");
        }
    }
}
static void inference_control(void)
{
    int master, slave, pair[2]; char tty[128], fd[32], control[256], tx[256];
    assert(!openpty(&master, &slave, tty, NULL, NULL));
    assert(!hea_serial_configure(slave, 115200));
    assert(!fcntl(master, F_SETFL, O_NONBLOCK));
    assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, pair));
    snprintf(fd, sizeof fd, "%d", pair[1]);
    path(control, sizeof control, "control.csv"); path(tx, sizeof tx, "control-tx.csv");
    char *args[] = {"build/san/hea_bridge", "--serial", tty, "--socket-fd", fd,
        "--csv", tx, "--status-csv", "/dev/null", "--echo-csv", "/dev/null",
        "--inf-rx-csv", "/dev/null", "--state-events-csv", "/dev/null", "--control-csv", control,
        "--echo-ms", "0", "--heartbeat-ms", "5", "--baud", "115200", NULL};
    pid_t bridge = launch(args, master, slave, 0); ready(control);
    struct hea_parser parser; hea_parser_init(&parser);
    unsigned hb = 0, inf = 0; uint32_t last_id = 0;
    control_frames(master, &parser, pair[0], 1, &hb, &inf, &last_id);
    assert(inf == 1 && last_id == 1);
    uint64_t before = hea_raw_now();
    assert(!kill(bridge, SIGUSR1));
    uint64_t onset = control_ack(control, 1, 1);
    assert(onset >= before && onset <= hea_raw_now());
    /* Drain any already-started frame, then verify 200 ms of live heartbeats. */
    control_frames(master, &parser, pair[0], 2, &hb, &inf, &last_id);
    unsigned initial_inf = inf, initial_hb = hb;
    for (uint32_t i = 3; i < 23; ++i)
        control_frames(master, &parser, pair[0], i, &hb, &inf, &last_id);
    assert(inf == initial_inf && hb > initial_hb + 10u);
    assert(!kill(bridge, SIGUSR1));
    uint64_t finish_stamp = control_ack(control, 2, 0);
    assert(finish_stamp > onset);
    /* A result delayed in IPC from the suppressed interval must also be dropped. */
    struct hea_result delayed = {23, onset - 20000000u, onset, 7, 99};
    uint8_t stale_bytes[HEA_RESULT_SIZE]; hea_result_pack(&delayed, stale_bytes);
    assert(send(pair[0], stale_bytes, sizeof stale_bytes, 0) == (ssize_t)sizeof stale_bytes);
    control_frames(master, &parser, pair[0], 100, &hb, &inf, &last_id);
    assert(inf == initial_inf + 1u && last_id == 100);
    assert(parser.stats.crc_errors == 0);
    finish(bridge, 1);
    close(master); close(slave); close(pair[0]); close(pair[1]);
    puts("PASS: SIGUSR1 suppression/resume, RAW timestamp acknowledgements, live heartbeats and no stale replay");
}
static void inference_input_policy(void)
{
    for (unsigned mode = 0; mode < 3u; ++mode) {
        int input[2], output[2];
        assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, input));
        assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, output));
        char in_fd[32], out_fd[32], csv_path[256];
        snprintf(in_fd, sizeof(in_fd), "%d", input[1]);
        snprintf(out_fd, sizeof(out_fd), "%d", output[0]);
        path(csv_path, sizeof(csv_path), mode == 2u ? "latest.csv" : mode == 1u ? "fifo.csv" : "default.csv");
        uint8_t bytes[HEA_INPUT_SIZE + 1u];
        uint64_t timestamp = hea_raw_now();
        /* Queue a burst before launch: deterministic drain, including ID wrap. */
        struct hea_input records[] = {{UINT32_MAX - 1u, timestamp}, {UINT32_MAX, timestamp}, {0, timestamp}};
        for (unsigned i = 0; i < 3u; ++i) {
            hea_input_pack(&records[i], bytes);
            assert(send(input[0], bytes, HEA_INPUT_SIZE, 0) == HEA_INPUT_SIZE);
            if (i == 0u) assert(send(input[0], bytes, 1, 0) == 1);
        }
        assert(send(input[0], bytes, sizeof(bytes), 0) == (ssize_t)sizeof(bytes));
        struct hea_input future = {1, timestamp + UINT64_C(60000000000)};
        hea_input_pack(&future, bytes);
        assert(send(input[0], bytes, HEA_INPUT_SIZE, 0) == HEA_INPUT_SIZE);
        char *args[] = {"build/san/hea_infer_stub", "--socket-fd", in_fd, "--output-fd", out_fd,
            "--csv", csv_path, "--work-us", "0", "--count", "1",
            mode ? "--input-policy" : NULL, mode == 2u ? "latest" : "fifo", NULL};
        pid_t infer = launch(args, -1, -1, 0);
        finish(infer, 0);
        uint8_t result_bytes[HEA_RESULT_SIZE];
        assert(recv(output[1], result_bytes, sizeof(result_bytes), MSG_DONTWAIT) == HEA_RESULT_SIZE);
        struct hea_result result;
        assert(!hea_result_unpack(&result, result_bytes, sizeof(result_bytes)));
        assert(result.frame_id == records[mode == 2u ? 2u : 0u].frame_id);
        assert(result.t_input_ns == timestamp && result.t_done_ns >= timestamp);
        FILE *f = fopen(csv_path, "r"); assert(f);
        char line[256]; assert(fgets(line, sizeof(line), f));
        unsigned skipped = 0, completed = 0;
        while (fgets(line, sizeof(line), f)) {
            if (strstr(line, "skipped_stale")) {
                uint32_t id; uint64_t ti;
                assert(sscanf(line, "%" SCNu32 ",%" SCNu64, &id, &ti) == 2);
                assert(skipped < 2u && id == records[skipped].frame_id && ti == timestamp);
                assert(strstr(line, ",,0,skipped_stale"));
                ++skipped;
            } else { assert(strstr(line, ",sent")); ++completed; }
        }
        fclose(f);
        assert(completed == 1u && skipped == (mode == 2u ? 2u : 0u));
        for (unsigned i = 0; i < 2u; ++i) { close(input[i]); close(output[i]); }
    }
    puts("PASS: inference default/FIFO/latest socketpair bursts, skipped IDs, malformed/future rejection and ID wrap");
}
int main(void)
{
    assert(mkdtemp(directory)); assert(!atexit(cleanup));
    int probe = socket(AF_UNIX, SOCK_DGRAM, 0); assert(probe >= 0);
    struct sockaddr_un a; memset(&a, 0, sizeof(a)); a.sun_family = AF_UNIX;
    path(a.sun_path, sizeof(a.sun_path), "probe.sock");
    if (bind(probe, (struct sockaddr *)&a, sizeof(a))) {
        assert(errno == EPERM || errno == EACCES);
        connected_ipc = 1;
        puts("SKIP: named Unix socket bind denied by sandbox; exercising the same datagram ABI via socketpair");
    } else unlink(a.sun_path);
    close(probe);
    run_case(0); run_case(1); fake_mcu(); inference_control(); inference_input_policy();
#ifdef __linux__
    assert(!hea_sleep_until(hea_now(CLOCK_MONOTONIC) + 1000000u));
    puts("PASS: Linux absolute CLOCK_MONOTONIC sleep and RAW timestamps exercised");
#else
    puts("SKIP: Linux clock_nanosleep/RAW/sched_setaffinity checks (macOS host)");
#endif
    puts("PASS: sanitized executables over openpty; shared sequence/session heartbeat first; exact age rounding; CRC recovery;");
    puts("      32 socket results + 8 source/stub results with cycling CPU durations");
    printf("Test artifacts: %s\n", directory);
    return 0;
}
