#include "hea_runtime.h"
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <limits.h>
#include <poll.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <termios.h>
#include <unistd.h>
#ifdef __linux__
#include <sched.h>
#include <sys/mman.h>
#elif defined(__APPLE__)
#include <sys/ioctl.h>
#include <IOKit/serial/ioss.h>
#endif

volatile sig_atomic_t hea_stop = 0;
void hea_fatal(const char *what) { perror(what); exit(EXIT_FAILURE); }
static void stop_handler(int sig) { (void)sig; hea_stop = 1; }
void hea_signals(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa)); sa.sa_handler = stop_handler;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGINT, &sa, NULL) || sigaction(SIGTERM, &sa, NULL)) hea_fatal("sigaction");
    signal(SIGPIPE, SIG_IGN);
}
uint64_t hea_now(clockid_t clock)
{
    struct timespec t;
    if (clock_gettime(clock, &t)) hea_fatal("clock_gettime");
    return (uint64_t)t.tv_sec * UINT64_C(1000000000) + (uint64_t)t.tv_nsec;
}
uint64_t hea_raw_now(void)
{
#ifdef __linux__
    return hea_now(CLOCK_MONOTONIC_RAW);
#else
    return hea_now(CLOCK_MONOTONIC); /* Host software checks only. */
#endif
}
int hea_sleep_until(uint64_t deadline_ns)
{
    int rc;
#ifdef __linux__
    struct timespec t = { (time_t)(deadline_ns / UINT64_C(1000000000)),
                         (long)(deadline_ns % UINT64_C(1000000000)) };
    do { rc = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t, NULL); }
    while (rc == EINTR && !hea_stop);
#else
    rc = 0;
    while (!hea_stop) {
        uint64_t now = hea_now(CLOCK_MONOTONIC);
        if (now >= deadline_ns) break;
        uint64_t delta = deadline_ns - now;
        struct timespec t = { (time_t)(delta / UINT64_C(1000000000)),
                             (long)(delta % UINT64_C(1000000000)) };
        if (nanosleep(&t, NULL) && errno != EINTR) { rc = errno; break; }
    }
#endif
    return rc;
}
static uint64_t number(const char *s, uint64_t max)
{
    char *end = NULL;
    errno = 0;
    unsigned long long n = strtoull(s, &end, 10);
    if (errno || s[0] == '-' || s[0] == '\0' || *end != '\0' || n > max) {
        fprintf(stderr, "invalid numeric option: %s\n", s); exit(2);
    }
    return (uint64_t)n;
}
int hea_options_parse(int argc, char **argv, struct hea_options *o)
{
    static const struct option opts[] = {
        {"socket", required_argument, NULL, 's'}, {"output", required_argument, NULL, 'o'},
        {"serial", required_argument, NULL, 'd'}, {"csv", required_argument, NULL, 'l'},
        {"echo-ms", required_argument, NULL, 1000},
        {"status-csv", required_argument, NULL, 1001},
        {"echo-csv", required_argument, NULL, 1002},
        {"state-events-csv", required_argument, NULL, 1003},
        {"control-csv", required_argument, NULL, 1004},
        {"inf-rx-csv", required_argument, NULL, 1007},
        {"mlock", no_argument, NULL, 1005},
        {"input-policy", required_argument, NULL, 1006},
        {"serial-fd", required_argument, NULL, 'a'},
        {"socket-fd", required_argument, NULL, 'i'}, {"output-fd", required_argument, NULL, 'u'},
        {"period-ms", required_argument, NULL, 'p'}, {"heartbeat-ms", required_argument, NULL, 'h'},
        {"work-us", required_argument, NULL, 'w'}, {"durations", required_argument, NULL, 'f'},
        {"count", required_argument, NULL, 'n'}, {"baud", required_argument, NULL, 'b'},
        {"fifo-priority", required_argument, NULL, 'r'}, {"cpu", required_argument, NULL, 'c'},
        {"policy", required_argument, NULL, 'q'}, {"help", no_argument, NULL, '?'},
        {NULL, 0, NULL, 0}
    };
    memset(o, 0, sizeof(*o)); o->period_ms = 100; o->heartbeat_ms = 20;
    o->echo_ms = 1000; o->work_us = 20000; o->baud = 921600; o->cpu = -1; o->serial_fd = -1;
    o->socket_fd = -1; o->output_fd = -1;
    int ch;
    while ((ch = getopt_long(argc, argv, "", opts, NULL)) != -1) {
        switch (ch) {
        case 1000: o->echo_ms = number(optarg, 3600000); break;
        case 1001: o->status_csv = optarg; break;
        case 1002: o->echo_csv = optarg; break;
        case 1003: o->state_events_csv = optarg; break;
        case 1004: o->control_csv = optarg; break;
        case 1007: o->inf_rx_csv = optarg; break;
        case 1005: o->lock_memory = 1; break;
        case 1006:
            if (strcmp(optarg, "fifo") && strcmp(optarg, "latest")) {
                fprintf(stderr, "--input-policy must be fifo or latest\n"); return -1;
            }
            o->input_latest = !strcmp(optarg, "latest"); break;
        case 's': o->socket_path = optarg; break;
        case 'o': o->output_path = optarg; break;
        case 'd': o->serial_path = optarg; break;
        case 'a': o->serial_fd = (int)number(optarg, INT_MAX); break;
        case 'i': o->socket_fd = (int)number(optarg, INT_MAX); break;
        case 'u': o->output_fd = (int)number(optarg, INT_MAX); break;
        case 'l': o->csv_path = optarg; break;
        case 'f': o->durations_path = optarg; break;
        case 'p': o->period_ms = number(optarg, 3600000); break;
        case 'h': o->heartbeat_ms = number(optarg, 3600000); break;
        case 'w': o->work_us = number(optarg, 60000000); break;
        case 'n': o->count = number(optarg, UINT32_MAX); break;
        case 'b': o->baud = (unsigned)number(optarg, UINT_MAX); break;
        case 'r': o->priority = (int)number(optarg, 99); break;
        case 'c': o->cpu = (int)number(optarg, INT_MAX); break;
        case 'q':
            if (strcmp(optarg, "fifo") && strcmp(optarg, "latest")) {
                fprintf(stderr, "--policy must be fifo or latest\n"); return -1;
            }
            o->latest = !strcmp(optarg, "latest"); break;
        default:
            if (optind > 0 && !strcmp(argv[optind - 1], "--help")) {
                puts("See linux/README.md. Options: --socket PATH --output PATH --serial PATH\n"
                     "--csv PATH --period-ms N --heartbeat-ms N --work-us N --durations PATH\n"
                     "--count N --baud N --fifo-priority N --cpu N --policy fifo|latest --mlock\n"
                     "--input-policy fifo|latest (default fifo)\n"
                     "--echo-ms N (default 1000, 0 disables) --status-csv PATH --echo-csv PATH --state-events-csv PATH --control-csv PATH --inf-rx-csv PATH (SIGUSR1 inference toggles)");
                return 1;
            }
            return -1;
        }
    }
    if (optind != argc || !o->period_ms || !o->heartbeat_ms || !o->baud ||
        (o->socket_path && o->socket_fd >= 0) || (o->output_path && o->output_fd >= 0) ||
        (o->serial_path && o->serial_fd >= 0)) {
        fprintf(stderr, "unexpected arguments or zero period/baud\n"); return -1;
    }
    return 0;
}
int hea_schedule(const struct hea_options *o)
{
#ifdef __linux__
    if (o->lock_memory && mlockall(MCL_CURRENT | MCL_FUTURE)) {
        perror("mlockall failed (check RLIMIT_MEMLOCK/CAP_IPC_LOCK)"); return -1;
    }
    if (o->cpu >= 0) {
        cpu_set_t set;
        if (o->cpu >= CPU_SETSIZE) { fprintf(stderr, "CPU exceeds CPU_SETSIZE\n"); return -1; }
        CPU_ZERO(&set); CPU_SET((unsigned)o->cpu, &set);
        if (sched_setaffinity(0, sizeof(set), &set)) {
            perror("CPU affinity failed (check allowed CPUs/permissions)"); return -1;
        }
    }
    if (o->priority) {
        struct sched_param p = { .sched_priority = o->priority };
        if (sched_setscheduler(0, SCHED_FIFO, &p)) {
            perror("SCHED_FIFO failed (requires CAP_SYS_NICE/root or suitable RLIMIT_RTPRIO)");
            return -1;
        }
    }
#else
    if (o->cpu >= 0 || o->priority || o->lock_memory) {
        fprintf(stderr, "SCHED_FIFO/CPU affinity options require Linux\n"); return -1;
    }
#endif
    return 0;
}
static void address(struct sockaddr_un *a, const char *path)
{
    memset(a, 0, sizeof(*a)); a->sun_family = AF_UNIX;
    if (!path || strlen(path) >= sizeof(a->sun_path)) {
        fprintf(stderr, "missing or too long Unix socket path\n"); exit(2);
    }
    memcpy(a->sun_path, path, strlen(path) + 1u);
}
int hea_socket_sender(void)
{
    int fd = socket(AF_UNIX, SOCK_DGRAM, 0);
    if (fd < 0 || fcntl(fd, F_SETFL, O_NONBLOCK) < 0) hea_fatal("datagram socket");
    return fd;
}
int hea_socket_bind(const char *path)
{
    struct sockaddr_un a; address(&a, path);
    int fd = hea_socket_sender();
    /* Never unlink another process's socket. Runner supplies a private directory. */
    if (bind(fd, (struct sockaddr *)&a, sizeof(a))) hea_fatal("bind Unix socket (path must be unused)");
    return fd;
}
static int inherited_datagram(int original)
{
    int fd = dup(original), type = 0;
    socklen_t size = sizeof(type);
    if (fd < 0 || getsockopt(fd, SOL_SOCKET, SO_TYPE, &type, &size) || type != SOCK_DGRAM ||
        fcntl(fd, F_SETFL, O_NONBLOCK) < 0) {
        fprintf(stderr, "inherited IPC fd must be a valid datagram socket\n"); exit(2);
    }
    return fd;
}
int hea_socket_input(const struct hea_options *o)
{
    return o->socket_fd >= 0 ? inherited_datagram(o->socket_fd) : hea_socket_bind(o->socket_path);
}
int hea_socket_output(const struct hea_options *o)
{
    return o->output_fd >= 0 ? inherited_datagram(o->output_fd) : hea_socket_sender();
}
void hea_socket_cleanup(const struct hea_options *o)
{
    if (o->socket_fd < 0 && o->socket_path) unlink(o->socket_path);
}
int hea_send_record(int fd, const char *path, const uint8_t *bytes, size_t n)
{
    ssize_t rc;
    if (path) {
        struct sockaddr_un a; address(&a, path);
        rc = sendto(fd, bytes, n, 0, (struct sockaddr *)&a, sizeof(a));
    } else rc = send(fd, bytes, n, 0);
    if (rc == (ssize_t)n) return 1;
    if (rc < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == ENOBUFS || errno == EINTR)) return 0;
    hea_fatal("sendto (start the receiving process first)"); return 0;
}
int hea_serial_configure(int fd, unsigned baud)
{
    if (!isatty(fd)) return 0;
    struct termios t;
    if (tcgetattr(fd, &t)) return -1;
    cfmakeraw(&t); t.c_cflag |= CLOCAL | CREAD;
    t.c_iflag &= (tcflag_t)~(IXON | IXOFF | IXANY);
    t.c_cflag &= (tcflag_t)~CSTOPB;
#ifdef CRTSCTS
    t.c_cflag &= (tcflag_t)~CRTSCTS;
#endif
    t.c_cc[VMIN] = 1; t.c_cc[VTIME] = 0;
    speed_t speed;
    switch (baud) {
    case 9600: speed = B9600; break;
    case 19200: speed = B19200; break;
    case 38400: speed = B38400; break;
    case 57600: speed = B57600; break;
    case 115200: speed = B115200; break;
#ifdef B230400
    case 230400: speed = B230400; break;
#endif
#ifdef B460800
    case 460800: speed = B460800; break;
#endif
#ifdef B921600
    case 921600: speed = B921600; break;
#endif
    default:
#ifdef __APPLE__
        speed = B9600; /* IOSSIOSPEED below applies the requested numeric baud. */
#else
        fprintf(stderr, "unsupported baud: %u\n", baud); errno = EINVAL; return -1;
#endif
    }
    if (cfsetispeed(&t, speed) || cfsetospeed(&t, speed) || tcsetattr(fd, TCSANOW, &t)) return -1;
#ifdef __APPLE__
    speed_t requested = (speed_t)baud;
    if (ioctl(fd, IOSSIOSPEED, &requested) && errno != ENOTTY) return -1;
#endif
    return 0;
}
int hea_serial_open(const char *path, unsigned baud)
{
    int fd = open(path, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) hea_fatal("open serial");
    if (hea_serial_configure(fd, baud)) hea_fatal("configure serial raw 8N1");
    return fd;
}
int hea_serial_get(const struct hea_options *o)
{
    if (o->serial_fd < 0) return hea_serial_open(o->serial_path, o->baud);
    int fd = dup(o->serial_fd);
    if (fd < 0 || fcntl(fd, F_SETFL, O_NONBLOCK) < 0) hea_fatal("inherited serial fd");
    if (hea_serial_configure(fd, o->baud)) hea_fatal("configure inherited serial fd");
    return fd;
}
FILE *hea_csv_open(const char *path, const char *header)
{
    FILE *f = path ? fopen(path, "w") : stdout;
    if (!f) hea_fatal("open CSV");
    if (setvbuf(f, NULL, _IOLBF, 0) || fprintf(f, "%s\n", header) < 0) hea_fatal("CSV header");
    return f;
}
