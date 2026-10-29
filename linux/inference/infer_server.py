#!/usr/bin/env python3
"""Sequential Unix datagram inference stage with fixed or shared-memory images."""
import argparse
import csv
import errno
import json
import os
import signal
import socket
import sys
import time
from pathlib import Path

from bench_common import SOURCE_RECORD, clock, pack_result, parse_cpu, pin_cpu, unpack_source
from model_runtime import Model, ShmImage, add_runtime_args, classify, load_image, preprocess

DRAIN_LIMIT = 64
DRAIN_NS = 2_000_000

def receive_input(receiver, input_policy='fifo', samples=None, now=None):
    """Wait for a valid record; latest collects at most 64 more arrivals / 2 ms.

    Skips have no completion timestamp because no inference was performed.
    Malformed datagrams never replace the current valid candidate.
    """
    if input_policy not in ('fifo', 'latest'):
        raise ValueError('input policy must be fifo or latest')
    if now is None:
        now, _ = clock()
    newest = None
    skipped = 0
    drained = 0
    drain_started = None
    while True:
        if newest is not None:
            if drained >= DRAIN_LIMIT or time.monotonic_ns() - drain_started >= DRAIN_NS:
                return newest, skipped
            drained += 1  # Invalid arrivals also consume the bounded batch.
        flags = socket.MSG_DONTWAIT if newest is not None else 0
        try:
            # One extra byte detects oversized records after truncation.
            data = receiver.recv(SOURCE_RECORD.size + 1, flags)
        except BlockingIOError:
            return newest, skipped
        try:
            record = unpack_source(data)
            # Check each candidate at reception, before inference or skip logs.
            # Completion-time validation alone can conceal a future input.
            if record[1] > now():
                raise ValueError('input timestamp is ahead of reception; check clock domains')
        except ValueError as exc:
            print(f'dropping malformed source datagram: {exc}', file=sys.stderr)
            continue
        if newest is not None:
            skipped += 1
            if samples is not None:
                samples.writerow((*newest, '', 'skipped_stale'))
        newest = record
        if drain_started is None:
            drain_started = time.monotonic_ns()
        if input_policy == 'fifo':
            return newest, skipped


def serve(model, np, image, source_path, bridge_path, now, max_frames=None, samples=None,
          input_policy='fifo', image_source=None):
    """Bind without deleting existing endpoints; unlink only our own bound socket."""
    source_path = Path(source_path)
    handled = 0
    skipped = 0
    image_drops = {'overwritten': 0, 'torn': 0}
    received = 0
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as receiver, \
            socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender:
        receiver.bind(str(source_path))
        try:
            while max_frames is None or received < max_frames:
                (frame_id, t_input_ns), stale = receive_input(receiver, input_policy, samples, now)
                skipped += stale
                received += 1
                frame_image = image
                if image_source is not None:
                    frame_image, image_status = image_source.read(np, frame_id)
                    if image_status is not None:
                        image_drops[image_status] += 1
                        if samples is not None:
                            samples.writerow((frame_id, t_input_ns, '', image_status))
                        continue
                output = model.run(preprocess(np, frame_image))
                class_id, confidence = classify(np, output)
                t_done_ns = now()  # Completion includes preprocessing + postprocessing.
                if t_done_ns < t_input_ns:
                    raise ValueError('input timestamp is ahead of completion; check clock domains')
                status = 'sent'
                try:
                    sender.sendto(pack_result(frame_id, t_input_ns, t_done_ns,
                                              class_id % 256, int(confidence * 100 + 0.5)),
                                  socket.MSG_DONTWAIT, str(bridge_path))
                except OSError as exc:
                    if exc.errno not in (errno.EAGAIN, errno.EWOULDBLOCK, errno.ENOBUFS):
                        raise
                    status = 'dropped'
                if samples is not None:
                    samples.writerow((frame_id, t_input_ns, t_done_ns, status))
                handled += 1
        finally:
            source_path.unlink()
            counts = dict(processed=handled, skipped=skipped)
            if image_source is not None:
                counts.update(image_drops)
            print(json.dumps(counts), file=sys.stderr)
    return handled


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_runtime_args(parser)
    parser.add_argument('--image-source', default='fixed', metavar='fixed|shm:NAME',
                        help='fixed image (default) or camera shared-memory ring')
    parser.add_argument('--socket', '--source-socket', dest='source_socket', required=True)
    parser.add_argument('--output', '--bridge-socket', dest='bridge_socket', required=True)
    parser.add_argument('--fifo-priority', type=int, choices=range(100), default=0)
    parser.add_argument('--input-policy', choices=('fifo', 'latest'), default='fifo')
    parser.add_argument('--csv', help='log completions, IPC drops and skipped_stale inputs')
    parser.add_argument('--max-frames', type=int, help='exit after N valid frames; default unlimited')
    args = parser.parse_args(argv)
    if args.image_source != 'fixed' and not (args.image_source.startswith('shm:') and
                                            args.image_source[4:]):
        parser.error('image-source must be fixed or shm:NAME')
    if args.image_source != 'fixed' and args.image:
        parser.error('--image cannot be combined with a shared-memory image source')
    if args.seed < 0 or (args.max_frames is not None and args.max_frames < 1):
        parser.error('seed must be nonnegative and max-frames positive')
    if args.source_socket == args.bridge_socket:
        parser.error('source and bridge sockets must differ')
    pin_cpu(parse_cpu(args.cpu) if args.cpu else None)
    if args.fifo_priority:
        if not sys.platform.startswith('linux'):
            raise RuntimeError('--fifo-priority requires Linux')
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(args.fifo_priority))
    import numpy as np
    import onnxruntime as ort

    image_source = ShmImage(args.image_source[4:]) if args.image_source != 'fixed' else None
    image = None if image_source else load_image(np, args.seed, args.image)
    model = Model(ort, args.model, args.threads)
    now, clock_name = clock()
    if image_source is not None:
        now = lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC)
        clock_name = 'CLOCK_MONOTONIC (camera; verify BOOTTIME offset)'
    print(f'inference ready: clock={clock_name}; source must use the same clock', file=sys.stderr)

    def stop(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        if args.csv:
            with open(args.csv, 'w', newline='') as stream:
                samples = csv.writer(stream)
                samples.writerow(('frame_id', 't_input_ns', 't_done_ns', 'status'))
                serve(model, np, image, args.source_socket, args.bridge_socket, now,
                      args.max_frames, samples, args.input_policy, image_source)
        else:
            serve(model, np, image, args.source_socket, args.bridge_socket, now, args.max_frames,
                  input_policy=args.input_policy, image_source=image_source)
    except KeyboardInterrupt:
        pass
    finally:
        if image_source is not None:
            image_source.close()


if __name__ == '__main__':
    main()
