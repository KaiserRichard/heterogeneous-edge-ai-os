#!/usr/bin/env python3
"""Pi-only GPIO markers and bounded E4 scheduling faults; standard library only."""
import csv
import os
import signal
import subprocess
import sys
import time


def raw():
    return time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)


def log(writer, stream, *row):
    writer.writerow(row)
    stream.flush()


def main():
    if sys.platform != 'linux':
        raise SystemExit('requires Linux Pi target')
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    mode = sys.argv[1]
    if mode == 'gpio':
        line, filename = sys.argv[2:]
        chip = os.environ.get('HEA_GPIO_CHIP', 'gpiochip0')
        help_text = subprocess.check_output(['gpioset', '--help'], text=True)
        with open(filename, 'x', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['t_edge_command_pi_ns', 'value', 'completed_pi_ns'])
            value = 0
            deadline = time.monotonic()
            while True:
                value ^= 1
                if '--hold-period' in help_text:
                    # Keep exclusive ownership until the next edge; no daemon leaks.
                    command = ['gpioset', '-c', chip, f'{line}={value}']
                else:
                    command = ['gpioset', '-m', 'signal', chip, f'{line}={value}']
                onset = raw()
                process = subprocess.Popen(command)
                try:
                    time.sleep(0.05)
                    if process.poll() is not None:
                        raise SystemExit('gpioset failed; check chip/line permissions and GPIO ownership')
                    log(writer, stream, onset, value, raw())
                    deadline += 1
                    time.sleep(max(0, deadline - time.monotonic()))
                finally:
                    process.terminate()
                    process.wait()
        return
    kind, pid_text, ms_text, core_text, filename = sys.argv[2:]
    pid, ms, core = int(pid_text), int(ms_text), int(core_text)
    if pid <= 1 or ms <= 0 or core < 0 or ms > 60000:
        raise SystemExit('PID > 1, duration 1..60000 ms and CPU >= 0 required')
    os.kill(pid, 0)
    if kind == 'hog' and os.geteuid() != 0:
        raise SystemExit('SCHED_FIFO hog requires sudo')
    with open(filename, 'a', newline='') as stream:
        writer = csv.writer(stream)
        if stream.tell() == 0:
            writer.writerow(['fault', 'bridge_pid', 'duration_ms', 'core', 't_onset_pi_ns'])
        if kind == 'kill':
            log(writer, stream, kind, pid, ms, core, raw())
            os.kill(pid, signal.SIGKILL)
        elif kind == 'stop':
            log(writer, stream, kind, pid, ms, core, raw())
            os.kill(pid, signal.SIGSTOP)
            try:
                time.sleep(ms / 1000)
            finally:
                os.kill(pid, signal.SIGCONT)
        elif kind == 'hog':
            if core not in os.sched_getaffinity(pid):
                raise SystemExit('selected core is outside bridge affinity')
            child = os.fork()
            if child == 0:
                try:
                    os.sched_setaffinity(0, {core})
                    os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(99))
                    log(writer, stream, kind, pid, ms, core, raw())
                    deadline = time.monotonic_ns() + ms * 1000000
                    while time.monotonic_ns() < deadline:
                        pass
                    os._exit(0)
                except Exception as error:
                    print(f'SCHED_FIFO hog failed: {error}', file=sys.stderr, flush=True)
                    os._exit(1)
            _, status = os.waitpid(child, 0)
            if status:
                raise SystemExit('SCHED_FIFO hog failed; check sudo/CAP_SYS_NICE and CPU')
        else:
            raise SystemExit('fault must be kill, stop or hog')


if __name__ == '__main__':
    main()
