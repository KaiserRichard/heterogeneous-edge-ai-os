#include "hea_clock_sync.h"
#include "hea_ipc.h"
#include "hea_proto.h"
#include "hea_runtime.h"
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <poll.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

/* Echo fields are raw u32. A full event timestamp supplies their boot epoch.
 * UART observations must remain within half a TIM2 wrap of the echo sample. */
static void align_mcu_epoch(struct hea_clock_wrap *wrap, struct hea_clock_filter *filter,
                            uint64_t anchor)
{
    if (!wrap->initialized) return;
    int64_t delta = (int64_t)(uint32_t)anchor - (int64_t)wrap->last_raw;
    if (delta > INT32_MAX) delta -= INT64_C(4294967296);
    if (delta < INT32_MIN) delta += INT64_C(4294967296);
    uint64_t aligned;
    if (delta >= 0) {
        if (anchor < (uint64_t)delta) return;
        aligned = anchor - (uint64_t)delta;
    } else {
        if (anchor > UINT64_MAX - (uint64_t)(-delta)) return;
        aligned = anchor + (uint64_t)(-delta);
    }
    double shift = aligned >= wrap->last_extended ? (double)(aligned - wrap->last_extended)
        : -(double)(wrap->last_extended - aligned);
    for (size_t i = 0; i < filter->count; ++i) filter->samples[i].offset_us += shift;
    wrap->last_extended = aligned;
}

struct pending {
    struct hea_result result;
    uint8_t bytes[HEA_MAX_FRAME];
    size_t size, offset;
    uint64_t t_send;
    int active, heartbeat, echo;
};
static uint32_t new_session(void)
{
    uint32_t id;
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) hea_fatal("session randomness");
    size_t offset = 0;
    while (offset < sizeof(id)) {
        ssize_t n = read(fd, (uint8_t *)&id + offset, sizeof(id) - offset);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) { fprintf(stderr, "cannot read random session ID\n"); _exit(1); }
        offset += (size_t)n;
    }
    close(fd); return id;
}
static int prepare(struct pending *p, uint16_t seq, uint32_t session)
{
    uint8_t payload[HEA_MAX_PAYLOAD];
    uint8_t len;
    p->t_send = hea_raw_now();
    if (p->echo) {
        struct hea_echo_req e = {p->t_send};
        len = hea_pack_echo_req(&e, payload);
    } else if (p->heartbeat) {
        struct hea_heartbeat h = { p->t_send, session };
        len = hea_pack_heartbeat(&h, payload);
    } else {
        struct hea_result *r = &p->result;
        struct hea_inference m = { r->t_input_ns, r->t_done_ns, r->frame_id,
                                   r->class_id, r->confidence, 0 };
        if (r->t_done_ns > p->t_send || hea_age_at_send_us(r->t_input_ns, p->t_send, &m.age_at_send_us))
            return -1;
        len = hea_pack_inference(&m, payload);
    }
    p->size = hea_encode(p->echo ? HEA_MSG_ECHO_REQ : p->heartbeat ? HEA_MSG_HEARTBEAT : HEA_MSG_INFERENCE,
                         seq, payload, len, p->bytes, sizeof(p->bytes));
    return 0;
}
int main(int argc, char **argv)
{
    struct hea_options o;
    int rc = hea_options_parse(argc, argv, &o);
    if (rc) return rc > 0 ? 0 : 2;
    if ((!o.socket_path && o.socket_fd < 0) || (!o.serial_path && o.serial_fd < 0)) {
        fprintf(stderr, "hea_bridge requires --socket PATH --serial PATH\n"); return 2;
    }
    hea_signals();
    uint32_t session = new_session();
    int serial = hea_serial_get(&o);
    int input = hea_socket_input(&o);
    FILE *csv = hea_csv_open(o.csv_path, "seq,frame_id,t_input_ns,t_done_ns,t_send_ns");
    FILE *status = hea_csv_open(o.status_csv ? o.status_csv : "mcu_status.csv", "seq,version,t_rx_pi_ns,mcu_us,state,missed_heartbeats,rx_crc_errors,diagnostics_present,last_capture_us,capture_count,rx_dropped,uart_errors,queue_dropped,capture_lost,clock_fallback,state_event_lost,uart_ore,uart_fe,uart_ne,uart_pe,max_irq_masked_cycles");
    FILE *echo = hea_csv_open(o.echo_csv ? o.echo_csv : "echo.csv", "seq,t1_pi_ns,t2_mcu_us,t3_mcu_us,t4_pi_ns,t2_mcu_extended_us,t3_mcu_extended_us,accepted,reference_pi_us,offset_us,delay_us,drift_ppm,rms_residual_us,sample_count,mapping_offset_us,mapping_drift,t1_mcu_est_us,t2_pi_est_us,t3_pi_est_us,t4_mcu_est_us");
    FILE *events = hea_csv_open(o.state_events_csv ? o.state_events_csv : "state_events.csv", "seq,t_rx_pi_ns,mcu_us,old,new,reason,last_hb_mcu_us,last_inf_mcu_us,lost_count,t_mcu_pi_est_ns");
    struct hea_parser parser; hea_parser_init(&parser);
    struct hea_clock_wrap wrap = {0};
    struct hea_clock_estimate storage[60];
    struct hea_clock_filter filter;
    (void)hea_clock_filter_init(&filter, storage, 60, UINT64_C(60000000));
    uint64_t outstanding = 0, mcu_anchor_us = 0;
    int have_mcu_anchor = 0;
    if (hea_schedule(&o)) { close(input); hea_socket_cleanup(&o); return 1; }
    struct hea_queue q; hea_queue_init(&q, o.latest);
    struct pending p; memset(&p, 0, sizeof(p));
    uint16_t seq = 0;
    uint64_t sent = 0, heartbeats = 0, malformed = 0, received = 0;
    uint64_t interval = o.heartbeat_ms * UINT64_C(1000000);
    uint64_t next_hb = hea_now(CLOCK_MONOTONIC);
    uint64_t next_echo = next_hb;
    uint64_t echo_interval = o.echo_ms * UINT64_C(1000000);
    while (!hea_stop) {
        uint64_t now = hea_now(CLOCK_MONOTONIC);
        uint64_t deadline = o.echo_ms && next_echo < next_hb ? next_echo : next_hb;
        uint64_t wait_ms = now >= deadline ? 0 : (deadline - now + 999999u) / 1000000u;
        int timeout = p.active ? -1 : (wait_ms > INT_MAX ? INT_MAX : (int)wait_ms);
        struct pollfd fds[2] = { { input, POLLIN, 0 },
            { serial, (short)(POLLIN | ((p.active || q.count || now >= deadline) ? POLLOUT : 0)), 0 } };
        if (poll(fds, 2, timeout) < 0) { if (errno == EINTR) continue; hea_fatal("bridge poll"); }
        if (fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) {
            fprintf(stderr, "serial disconnected\n"); close(input); hea_socket_cleanup(&o); return 1;
        }
        if (fds[1].revents & POLLIN) {
            uint8_t bytes[1024];
            ssize_t nr = read(serial, bytes, sizeof(bytes));
            if (nr < 0 && errno != EAGAIN && errno != EINTR) hea_fatal("serial read");
            for (ssize_t i = 0; i < nr; ++i) {
                if (!hea_parser_feed(&parser, bytes[i])) continue;
                struct hea_frame *f = &parser.frame;
                uint64_t t4 = hea_raw_now();
                if (f->type == HEA_MSG_MCU_STATUS) {
                    struct hea_mcu_status m;
                    struct hea_mcu_status_extended x;
                    if (hea_unpack_mcu_status(f, &m)) { ++malformed; continue; }
                    int ext = !hea_unpack_mcu_status_extended(f, &x);
                    fprintf(status, "%u,%u,%" PRIu64 ",%" PRIu32 ",%u,%u,%u,%d,",
                        f->seq, f->version, t4, m.mcu_us, m.state, m.missed_heartbeats, m.rx_crc_errors, ext);
                    if (ext) fprintf(status, "%" PRIu32 ",%" PRIu32 ",%" PRIu32 ",%" PRIu32 ",%" PRIu32 ",%" PRIu32,
                        x.last_capture_us, x.capture_count, x.rx_dropped, x.uart_errors, x.queue_dropped, x.capture_lost);
                    else fprintf(status, ",,,,,");
                    if (ext && f->len >= 38) fprintf(status, ",%u,%" PRIu32, x.clock_fallback, x.state_event_lost);
                    else fprintf(status, ",,");
                    if (ext && f->len == 58) fprintf(status,
                        ",%" PRIu32 ",%" PRIu32 ",%" PRIu32 ",%" PRIu32 ",%" PRIu32,
                        x.uart_ore, x.uart_fe, x.uart_ne, x.uart_pe, x.max_irq_masked_cycles);
                    else fprintf(status, ",,,,,");
                    fprintf(status, "\n");
                    if (ferror(status)) hea_fatal("status CSV");
                } else if (f->type == HEA_MSG_STATE_EVENT) {
                    struct hea_state_event e;
                    if (hea_unpack_state_event(f, &e)) { ++malformed; continue; }
                    mcu_anchor_us = e.mcu_us; have_mcu_anchor = 1;
                    align_mcu_epoch(&wrap, &filter, mcu_anchor_us);
                    fprintf(events, "%u,%" PRIu64 ",%" PRIu64 ",%u,%u,%u,%" PRIu64 ",%" PRIu64 ",%" PRIu32 ",",
                        f->seq, t4, e.mcu_us, e.old_state, e.new_state, e.reason,
                        e.last_hb_mcu_us, e.last_inf_mcu_us, e.lost_count);
                    struct hea_clock_estimate best;
                    if (!hea_clock_filter_min(&filter, &best)) {
                        struct hea_clock_fit fit;
                        double offset = best.offset_us, drift = 0.0;
                        if (!hea_clock_fit(&filter, best.reference_pi_us, &fit)) {
                            offset = fit.offset_us; drift = fit.drift;
                        }
                        long double slope = 1.0L + (long double)drift;
                        long double ref = (long double)best.reference_pi_us;
                        if (slope > 0.0L) fprintf(events, "%.3Lf",
                            (ref + ((long double)e.mcu_us - ref - (long double)offset) / slope) * 1000.0L);
                    }
                    fprintf(events, "\n");
                    if (ferror(events)) hea_fatal("state event CSV");
                } else if (f->type == HEA_MSG_ECHO_RESP) {
                    struct hea_echo_resp e;
                    if (hea_unpack_echo_resp(f, &e)) { ++malformed; continue; }
                    uint64_t t2 = 0, t3 = 0;
                    int accepted = 0;
                    struct hea_clock_wrap candidate = wrap;
                    if (!candidate.initialized) {
                        hea_clock_wrap_init(&candidate, e.mcu_rx_us);
                        if (have_mcu_anchor) align_mcu_epoch(&candidate, &filter, mcu_anchor_us);
                    }
                    if (outstanding && e.linux_t1_ns == outstanding &&
                        !hea_clock_wrap_extend(&candidate, e.mcu_rx_us, &t2) &&
                        !hea_clock_wrap_extend(&candidate, e.mcu_tx_us, &t3)) {
                        struct hea_clock_sample sample = {e.linux_t1_ns / 1000u, t2, t3, t4 / 1000u};
                        accepted = !hea_clock_filter_add(&filter, &sample);
                        if (accepted) wrap = candidate;
                        outstanding = 0;
                    }
                    fprintf(echo, "%u,%" PRIu64 ",%" PRIu32 ",%" PRIu32 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d,",
                        f->seq, e.linux_t1_ns, e.mcu_rx_us, e.mcu_tx_us, t4, t2, t3, accepted);
                    struct hea_clock_estimate best;
                    if (accepted && !hea_clock_filter_min(&filter, &best)) {
                        struct hea_clock_fit fit;
                        fprintf(echo, "%" PRIu64 ",%.6f,%" PRIu64 ",", best.reference_pi_us, best.offset_us, best.delay_us);
                        double mapping_offset = best.offset_us, mapping_drift = 0.0;
                        if (!hea_clock_fit(&filter, best.reference_pi_us, &fit)) {
                            fprintf(echo, "%.6f,%.6f,%zu", fit.drift_ppm, fit.rms_residual_us, fit.sample_count);
                            mapping_offset = fit.offset_us; mapping_drift = fit.drift;
                        } else fprintf(echo, ",,%zu", filter.count);
                        /* Explicit affine estimator mapping; never raw cross-clock subtraction. */
                        long double ref = (long double)best.reference_pi_us;
                        long double slope = 1.0L + (long double)mapping_drift;
                        if (slope > 0.0L) {
                            long double mref = ref + (long double)mapping_offset;
                            fprintf(echo, ",%.6f,%.12f,%.6Lf,%.6Lf,%.6Lf,%.6Lf",
                                mapping_offset, mapping_drift,
                                mref + slope * ((long double)e.linux_t1_ns / 1000.0L - ref),
                                ref + ((long double)t2 - mref) / slope,
                                ref + ((long double)t3 - mref) / slope,
                                mref + slope * ((long double)t4 / 1000.0L - ref));
                        } else fprintf(echo, ",,,,,,");
                    } else fprintf(echo, ",,,,,,,,,,,");
                    fprintf(echo, "\n");
                    if (ferror(echo)) hea_fatal("echo CSV");
                }
            }
        }
        if (fds[0].revents & POLLIN) {
            /* Bound each batch so a hot IPC producer cannot starve heartbeat dispatch. */
            for (unsigned i = 0; i < HEA_QUEUE_CAPACITY && !hea_stop; ++i) {
                uint8_t bytes[HEA_RESULT_SIZE + 1u];
                ssize_t n = recv(input, bytes, sizeof(bytes), 0);
                if (n < 0) {
                    if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) break;
                    hea_fatal("bridge recv");
                }
                struct hea_result r;
                if (hea_result_unpack(&r, bytes, (size_t)n)) { ++malformed; continue; }
                ++received;
                if (o.latest && p.active && !p.heartbeat && !p.echo && !p.offset) {
                    p.result = r; ++q.overwritten;
                } else (void)hea_queue_push(&q, &r);
            }
        }
        if (!(fds[1].revents & POLLOUT)) continue;
        now = hea_now(CLOCK_MONOTONIC);
        if (!p.active) {
            p.heartbeat = now >= next_hb;
            p.echo = !p.heartbeat && o.echo_ms && now >= next_echo;
            if (!p.heartbeat && !p.echo && !hea_queue_pop(&q, &p.result)) continue;
            p.active = 1; p.offset = 0;
        }
        /* Restamp/repack until a first byte is accepted: EAGAIN is not a send. */
        if (!p.offset && prepare(&p, seq, session)) { ++malformed; p.active = 0; continue; }
        ssize_t n = write(serial, p.bytes + p.offset, p.size - p.offset);
        if (n < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
            hea_fatal("serial write");
        }
        if (!n) { fprintf(stderr, "serial write made no progress\n"); return 1; }
        p.offset += (size_t)n;
        if (p.offset != p.size) continue;
        if (p.echo) {
            outstanding = p.t_send;
            next_echo = hea_now(CLOCK_MONOTONIC) + echo_interval;
        } else if (p.heartbeat) {
            ++heartbeats;
            now = hea_now(CLOCK_MONOTONIC);
            next_hb += ((now - next_hb) / interval + 1u) * interval;
        } else {
            ++sent;
            if (fprintf(csv, "%" PRIu16 ",%" PRIu32 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 "\n",
                        seq, p.result.frame_id, p.result.t_input_ns, p.result.t_done_ns, p.t_send) < 0)
                hea_fatal("bridge CSV");
        }
        seq = (uint16_t)(seq + 1u); p.active = 0;
    }
    fprintf(stderr, "{\"session_id\":%" PRIu32 ",\"received\":%" PRIu64
            ",\"sent\":%" PRIu64 ",\"heartbeats\":%" PRIu64
            ",\"overwritten\":%" PRIu64 ",\"dropped\":%" PRIu64
            ",\"malformed\":%" PRIu64 ",\"discarded_on_stop\":%zu}\n",
            session, received, sent, heartbeats, q.overwritten, q.dropped, malformed,
            q.count + (size_t)(p.active && !p.heartbeat && !p.echo));
    close(input); close(serial); hea_socket_cleanup(&o);
    if (fclose(status) || fclose(echo) || fclose(events)) hea_fatal("close receive CSV");
    if (fclose(csv)) hea_fatal("close bridge CSV");
    return 0;
}
