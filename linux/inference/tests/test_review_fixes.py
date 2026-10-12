"""Deterministic C race/stall tests using syscall boundaries, no hardware needed."""
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMMON = ['linux/src/hea_runtime.c', 'linux/src/hea_ipc.c',
          'protocol/src/hea_proto.c', 'protocol/src/hea_clock_sync.c']
PRELUDE = r'''
#include "hea_runtime.h"
#include "hea_ipc.h"
#include "hea_proto.h"
#include <assert.h>
#include <errno.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdio.h>
'''


class CReviewRegressions(unittest.TestCase):
    def compile(self, directory, code, defines=(), common=True):
        source = Path(directory) / 'test.c'
        binary = Path(directory) / 'test'
        source.write_text(code)
        command = shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c11', '-D_GNU_SOURCE', '-D_DARWIN_C_SOURCE', '-D_POSIX_C_SOURCE=200809L',
            '-Wall', '-Wextra', '-Werror', '-I' + str(ROOT),
            '-I' + str(ROOT / 'linux/include'), '-I' + str(ROOT / 'protocol/include'),
            *defines, str(source)]
        if common:
            command += [str(ROOT / path) for path in COMMON]
        return subprocess.run(command + ['-lm', '-o', str(binary)], capture_output=True,
                              text=True), binary

    def run_c(self, code, *args):
        with tempfile.TemporaryDirectory(dir=ROOT / 'linux/build') as directory:
            compiled, binary = self.compile(directory, PRELUDE + code)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = subprocess.run([str(binary), *args], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result

    def test_transit_static_assert_rejects_small_allowance_at_low_baud(self):
        main = (ROOT / 'stm32/firmware/main.c').read_text()
        assertions = main[main.index('/* Override only'):main.index('_Static_assert(configTICK')]
        code = '#include "stm32/firmware/uart_budget.h"\n' + assertions + '\nint main(void) {return 0;}\n'
        with tempfile.TemporaryDirectory(dir=ROOT / 'linux/build') as directory:
            for baud in (9600, 115200, 921600):
                result, _ = self.compile(directory, code, [f'-DUART_BAUD={baud}'], common=False)
                self.assertEqual(result.returncode, 0, result.stderr)
            result, _ = self.compile(directory, code,
                                     ['-DUART_BAUD=9600', '-DUART_TRANSIT_US=5000'], common=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('smaller than UART serialization time', result.stderr)

    def test_partial_write_expires_and_first_attempt_restamps_age(self):
        self.run_c(r'''
static uint64_t tick = 1000000000;
static unsigned calls;
static int mode;
static uint64_t test_now(void) { return tick; }
static ssize_t test_write(int fd, const void *bytes, size_t size) {
    (void)fd; (void)bytes; ++calls;
    if (mode == 0) { errno = EAGAIN; return -1; }
    if (mode == 1) return 1;
    if (mode == 3) tick += 40000000;
    return (ssize_t)size;
}
#define hea_raw_now test_now
#define write test_write
#define main bridge_main
#include "linux/src/hea_bridge.c"
#undef main
#undef write
#undef hea_raw_now
int main(void) {
    struct pending p = {0};
    p.result = (struct hea_result){7, tick - 100000000, tick - 1000000, 1, 90};
    assert(transmit(&p, 0, 1, 42) == 0 && p.offset == 0);
    uint64_t first = p.t_send;
    tick += 1000000; mode = 1;
    assert(transmit(&p, 0, 1, 42) == 0 && p.offset == 1 && p.t_send > first);
    struct hea_parser parser; hea_parser_init(&parser);
    for (size_t i = 0; i < p.size; ++i) hea_parser_feed(&parser, p.bytes[i]);
    struct hea_inference inf; assert(!hea_unpack_inference(&parser.frame, &inf));
    assert(inf.age_at_send_us == 101000);
    tick += 40000000; unsigned before = calls;
    assert(transmit(&p, 0, 1, 42) == -2 && calls == before);
    p.offset = 0; mode = 2;
    assert(transmit(&p, 0, 2, 42) == 1 && p.t_send == tick);
    p.offset = 0; mode = 3;
    assert(transmit(&p, 0, 3, 42) == -2); /* Suspension within final write. */
    return 0;
}
''')

    def test_shutdown_signal_pending_at_wait_exits_both_programs(self):
        for program in ('hea_rx', 'hea_infer_stub'):
            code = r'''
static unsigned waits;
static int test_wait(int n, fd_set *r, fd_set *w, fd_set *e,
                     const struct timespec *t, const sigset_t *mask) {
    sigset_t current; assert(!sigprocmask(SIG_SETMASK, NULL, &current));
    assert(sigismember(&current, SIGTERM) == 1);
    assert(!sigismember(mask, SIGTERM));
    ++waits; assert(!raise(SIGTERM)); /* Exactly after flag check, before wait. */
    return pselect(n, r, w, e, t, mask);
}
#define pselect test_wait
#define main program_main
#include "linux/src/PROGRAM.c"
#undef main
#undef pselect
int main(void) {
    int pair[2]; assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, pair));
    char input[32], output[32];
    snprintf(input, sizeof input, "%d", pair[0]);
    snprintf(output, sizeof output, "%d", pair[1]);
    char *args[] = {"infer", "--socket-fd", input, "--output-fd", output,
                    "--csv", "/dev/null", NULL};
    ARGS_SETUP
    assert(!program_main(ARGC, args));
    assert(waits == 1 && hea_stop);
    close(pair[0]); close(pair[1]); return 0;
}
'''.replace('PROGRAM', program)
            if program == 'hea_rx':
                code = code.replace('#define pselect', '#include <fcntl.h>\n#define pselect')
                code = code.replace('ARGS_SETUP', r'''
    int master = posix_openpt(O_RDWR | O_NOCTTY); assert(master >= 0);
    assert(!grantpt(master) && !unlockpt(master));
    args[1] = "--serial"; args[2] = ptsname(master);
    args[3] = "--csv"; args[4] = "/dev/null"; args[5] = NULL;
    (void)output;
''').replace('ARGC', '5')
                code = '#include <stdlib.h>\n' + code
            else:
                code = code.replace('ARGS_SETUP', '').replace('ARGC', '7')
            with self.subTest(program=program):
                result = self.run_c(code)
                self.assertIn('"malformed":0', result.stderr)

    def test_c_latest_infinite_queue_has_count_and_time_bounds(self):
        code = r'''
static unsigned received;
static uint64_t ticks, step;
static uint64_t test_now(clockid_t clock) {
    (void)clock; uint64_t value = ticks; ticks += step; return value;
}
static ssize_t test_recv(int fd, void *bytes, size_t size, int flags) {
    (void)fd; (void)size; (void)flags;
    struct hea_input in = {++received, 0}; hea_input_pack(&in, bytes);
    return HEA_INPUT_SIZE; /* Permanently nonempty queue. */
}
static int test_wait(int n, fd_set *r, fd_set *w, fd_set *e,
                     const struct timespec *t, const sigset_t *mask) {
    (void)n; (void)r; (void)w; (void)e; (void)t; (void)mask; return 1;
}
#define recv test_recv
#define hea_now test_now
#define pselect test_wait
#define main program_main
#include "linux/src/hea_infer_stub.c"
#undef main
#undef pselect
#undef hea_now
#undef recv
int main(int argc, char **argv) {
    (void)argc; step = argv[1][0] == 'c' ? 0 : 1000000;
    int pair[2]; assert(!socketpair(AF_UNIX, SOCK_DGRAM, 0, pair));
    char input[32], output[32];
    snprintf(input, sizeof input, "%d", pair[0]);
    snprintf(output, sizeof output, "%d", pair[1]);
    char *args[] = {"infer", "--socket-fd", input, "--output-fd", output,
        "--csv", "/dev/null", "--input-policy", "latest", "--count", "1", "--work-us", "0", NULL};
    assert(!program_main(13, args));
    assert(received == (step ? 2u : 65u));
    close(pair[0]); close(pair[1]); return 0;
}
'''
        for bound in ('count', 'time'):
            with self.subTest(bound=bound):
                result = self.run_c(code, bound)
                self.assertIn('"processed":1', result.stderr)


if __name__ == '__main__':
    unittest.main()
