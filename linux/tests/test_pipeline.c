#include "hea_ipc.h"
#include "hea_proto.h"
#include "hea_runtime.h"
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
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
static pid_t children[8];
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
        "--csv", bridge_csv, "--baud", "115200", "--heartbeat-ms", "5", "--policy", "fifo", NULL};
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
    run_case(0); run_case(1);
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
