#!/usr/bin/env python3
"""Sequential Unix datagram inference stage with fixed deterministic image input."""
import argparse
import csv
import errno
import os
import signal
import socket
import sys
from pathlib import Path

from bench_common import SOURCE_RECORD, clock, pack_result, parse_cpu, pin_cpu, unpack_source
from model_runtime import Model, add_runtime_args, classify, load_image, preprocess


def serve(model, np, image, source_path, bridge_path, now, max_frames=None, samples=None):
    """Bind without deleting existing endpoints; unlink only our own bound socket."""
    source_path = Path(source_path)
    handled = 0
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as receiver, \
            socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sender:
        receiver.bind(str(source_path))
        try:
            while max_frames is None or handled < max_frames:
                # One extra byte ensures oversized records cannot look valid after truncation.
                data = receiver.recv(SOURCE_RECORD.size + 1)
                try:
                    frame_id, t_input_ns = unpack_source(data)
                except ValueError as exc:
                    print(f'dropping malformed source datagram: {exc}', file=sys.stderr)
                    continue
                output = model.run(preprocess(np, image))
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
    return handled


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_runtime_args(parser)
    parser.add_argument('--socket', '--source-socket', dest='source_socket', required=True)
    parser.add_argument('--output', '--bridge-socket', dest='bridge_socket', required=True)
    parser.add_argument('--fifo-priority', type=int, choices=range(100), default=0)
    parser.add_argument('--csv', help='log every completion, including IPC drops')
    parser.add_argument('--max-frames', type=int, help='exit after N valid frames; default unlimited')
    args = parser.parse_args(argv)
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

    image = load_image(np, args.seed, args.image)
    model = Model(ort, args.model, args.threads)
    now, clock_name = clock()
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
                      args.max_frames, samples)
        else:
            serve(model, np, image, args.source_socket, args.bridge_socket, now, args.max_frames)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
