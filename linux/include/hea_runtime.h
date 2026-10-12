#ifndef HEA_RUNTIME_H
#define HEA_RUNTIME_H
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>

struct hea_options {
    const char *socket_path, *output_path, *serial_path, *csv_path, *durations_path;
    const char *status_csv, *echo_csv;
    uint64_t echo_ms;
    uint64_t period_ms, heartbeat_ms, work_us, count;
    unsigned baud;
    int priority, cpu, latest, input_latest, serial_fd, socket_fd, output_fd, lock_memory;
};
extern volatile sig_atomic_t hea_stop;
int hea_options_parse(int argc, char **argv, struct hea_options *o);
int hea_schedule(const struct hea_options *o);
void hea_signals(void);
void hea_fatal(const char *what);
uint64_t hea_now(clockid_t clock);
uint64_t hea_raw_now(void);
int hea_sleep_until(uint64_t deadline_ns);
int hea_socket_bind(const char *path);
int hea_socket_sender(void);
int hea_socket_input(const struct hea_options *o);
int hea_socket_output(const struct hea_options *o);
void hea_socket_cleanup(const struct hea_options *o);
int hea_send_record(int fd, const char *path, const uint8_t *bytes, size_t n);
int hea_serial_open(const char *path, unsigned baud);
int hea_serial_get(const struct hea_options *o);
int hea_serial_configure(int fd, unsigned baud);
FILE *hea_csv_open(const char *path, const char *header);
#endif
