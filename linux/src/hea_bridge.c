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

struct pending {
    struct hea_result result;
    uint8_t bytes[HEA_MAX_FRAME];
    size_t size, offset;
    uint64_t t_send;
    int active, heartbeat;
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
    if (p->heartbeat) {
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
    p->size = hea_encode(p->heartbeat ? HEA_MSG_HEARTBEAT : HEA_MSG_INFERENCE,
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
    if (hea_schedule(&o)) { close(input); hea_socket_cleanup(&o); return 1; }
    struct hea_queue q; hea_queue_init(&q, o.latest);
    struct pending p; memset(&p, 0, sizeof(p));
    uint16_t seq = 0;
    uint64_t sent = 0, heartbeats = 0, malformed = 0, received = 0;
    uint64_t interval = o.heartbeat_ms * UINT64_C(1000000);
    uint64_t next_hb = hea_now(CLOCK_MONOTONIC);
    while (!hea_stop) {
        uint64_t now = hea_now(CLOCK_MONOTONIC);
        uint64_t wait_ms = now >= next_hb ? 0 : (next_hb - now + 999999u) / 1000000u;
        /* Once a heartbeat is pending, wait for output instead of spinning on its deadline. */
        int timeout = (p.active && p.heartbeat) || now >= next_hb ? -1 :
            (wait_ms > INT_MAX ? INT_MAX : (int)wait_ms);
        struct pollfd fds[2] = { { input, POLLIN, 0 },
            { serial, (short)((p.active || q.count || now >= next_hb) ? POLLOUT : 0), 0 } };
        if (poll(fds, 2, timeout) < 0) { if (errno == EINTR) continue; hea_fatal("bridge poll"); }
        if (fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) {
            fprintf(stderr, "serial disconnected\n"); close(input); hea_socket_cleanup(&o); return 1;
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
                if (o.latest && p.active && !p.heartbeat && !p.offset) {
                    p.result = r; ++q.overwritten;
                } else (void)hea_queue_push(&q, &r);
            }
        }
        if (!(fds[1].revents & POLLOUT)) continue;
        now = hea_now(CLOCK_MONOTONIC);
        if (!p.active) {
            p.heartbeat = now >= next_hb;
            if (!p.heartbeat && !hea_queue_pop(&q, &p.result)) continue;
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
        if (p.heartbeat) {
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
            q.count + (size_t)(p.active && !p.heartbeat));
    close(input); close(serial); hea_socket_cleanup(&o);
    if (fclose(csv)) hea_fatal("close bridge CSV");
    return 0;
}
