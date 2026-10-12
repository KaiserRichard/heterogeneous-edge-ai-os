#!/usr/bin/env python3
"""Bounded E4 orchestration for the real Linux Pi/UART/STM32 rig."""
import argparse
import csv
import importlib.util
import json
import math
import os
from pathlib import Path
import select
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("e4_summary", REPO / "analysis/e4_summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


def raw():
    return time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def hog(core):
    """Called with sudo, on the bridge core; log after the timed interval."""
    os.sched_setaffinity(0, {core})
    os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(99))
    onset = raw()
    deadline = onset + 1_000_000_000
    while raw() < deadline:
        pass
    finish = raw()
    # Drop FIFO before stdout/file I/O.
    os.sched_setscheduler(0, os.SCHED_OTHER, os.sched_param(0))
    print(json.dumps(dict(onset_pi_ns=onset, fault_end_pi_ns=finish)), flush=True)


def signal_fault(pid, fault, meta):
    # No file I/O or subprocess launch between this clock read and signal.
    onset = raw()
    os.kill(pid, signal.SIGKILL if fault == "F1" else signal.SIGSTOP)
    meta["onset_pi_ns"] = onset
    if fault != "F1":
        try:
            time.sleep(1)
        finally:
            finish = raw()
            os.kill(pid, signal.SIGCONT)
            meta["fault_end_pi_ns"] = finish


class Monitor:
    def __init__(self, directory):
        self.directory = directory
        self.stop = threading.Event()
        self.ready = threading.Event()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.thread.start()
        if not self.ready.wait(3):
            raise RuntimeError("power monitor failed to start")

    def close(self):
        self.stop.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=3)

    def run(self):
        with (self.directory / "power.csv").open("x", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["t_pi_ns", "throttled", "temp_millic"] + [f"cpu{i}_khz" for i in range(4)])
            deadline = time.monotonic()
            while True:
                timestamp = raw()
                try:
                    text = subprocess.check_output(["vcgencmd", "get_throttled"], text=True, timeout=.2)
                    throttled = text.strip().split("=")[1]
                    int(throttled, 0)
                except (OSError, subprocess.SubprocessError, ValueError, IndexError):
                    throttled = ""
                def read(path):
                    try:
                        return Path(path).read_text().strip()
                    except OSError:
                        return ""
                temp = read("/sys/class/thermal/thermal_zone0/temp")
                freqs = [read(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq") for i in range(4)]
                writer.writerow([timestamp, throttled, temp] + freqs)
                stream.flush()
                self.ready.set()
                if self.stop.is_set():
                    return
                deadline += .5
                # Final sample covers the recovery window after close().
                self.stop.wait(max(0, deadline - time.monotonic()))


class Pipeline:
    def __init__(self, directory, args, ipc, serial_fd):
        self.directory, self.args, self.ipc = directory, args, Path(ipc)
        self.fd = serial_fd
        self.processes = {}
        self.streams = []

    def launch(self, name, arguments, inherited=()):
        command = [str(REPO / "linux/build" / name)] + list(map(str, arguments))
        with (self.directory / "process_commands.txt").open("a") as stream:
            stream.write(shlex.join(command) + "\n")
        output = (self.directory / f"{name}.stdout.log").open("w")
        error = (self.directory / f"{name}.stderr.log").open("w")
        self.streams += [output, error]
        process = subprocess.Popen(command, stdout=output, stderr=error, pass_fds=inherited, cwd=self.directory)
        self.processes[name] = process
        (self.directory / f"{name}.pid").write_text(str(process.pid) + "\n")
        return process

    def ready(self, path, process):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"{path}: process exited; inspect {self.directory}")
            if Path(path).exists() and (not Path(path).is_file() or Path(path).stat().st_size > 0):
                return
            time.sleep(.02)
        raise RuntimeError(f"startup timed out: {path}")

    def start(self):
        self.directory.mkdir()
        for path in (self.ipc / "bridge.sock", self.ipc / "source.sock"):
            path.unlink(missing_ok=True)
        event_options = [self.args.state_events_option, self.directory / "state_events.csv"] if self.args.state_events_option else []
        bridge = self.launch("hea_bridge", ["--serial-fd", self.fd, "--baud", self.args.baud,
            "--socket", self.ipc / "bridge.sock", "--csv", self.directory / "bridge.csv",
            "--status-csv", self.directory / "mcu_status.csv", "--echo-csv", self.directory / "echo.csv",
            *event_options, "--echo-ms", 500,
            "--heartbeat-ms", 20, "--policy", "latest", "--cpu", self.args.bridge_core], (self.fd,))
        self.ready(self.ipc / "bridge.sock", bridge)
        self.ready(self.directory / "state_events.csv", bridge)
        # Validate the parallel branch's schema before any fault is attempted.
        summary.read_csv(self.directory / "state_events.csv", summary.EVENT_COLUMNS)
        infer = self.launch("hea_infer_stub", ["--socket", self.ipc / "source.sock", "--output", self.ipc / "bridge.sock",
            "--csv", self.directory / "infer.csv", "--work-us", 20000, "--cpu", self.args.controller_core])
        self.ready(self.ipc / "source.sock", infer)
        self.launch("hea_source", ["--output", self.ipc / "source.sock", "--period-ms", 100,
            "--csv", self.directory / "source.csv", "--cpu", self.args.controller_core])

    def check(self):
        if any(p.poll() is not None for p in self.processes.values()):
            raise RuntimeError(f"pipeline exited unexpectedly: {self.directory}")

    def records(self):
        # Ignore a partially written final line while the line-buffered bridge runs.
        path = self.directory / "state_events.csv"
        lines = path.read_text().splitlines(keepends=True)
        if lines and not lines[-1].endswith("\n"):
            lines.pop()
        return list(csv.DictReader(lines))

    def wait_fresh(self, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.check()
            records = self.records()
            fits = summary.clock_fits(self.directory)
            if records and summary.state(records[-1]["new"]) == "FRESH" and fits:
                return raw()
            time.sleep(.05)
        raise RuntimeError("no FRESH STATE_EVENT plus clock fit before startup/recovery deadline")

    def wait(self, until, require_fresh=False):
        initial_count = len(self.records()) if require_fresh else 0
        while raw() < until:
            self.check()
            if require_fresh:
                records = self.records()
                if not records or summary.state(records[-1]["new"]) != "FRESH" or any(
                        summary.state(r["old"]) != summary.state(r["new"]) for r in records[initial_count:]):
                    raise RuntimeError("transition during the required 20 s steady FRESH phase")
            time.sleep(min(.05, max(0, (until - raw()) / 1e9)))

    def close(self):
        # Resume stopped children before termination; reap every owned PID.
        for name in ("hea_source", "hea_infer_stub", "hea_bridge"):
            process = self.processes.get(name)
            if process is None or process.poll() is not None:
                continue
            process.send_signal(signal.SIGCONT)
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for stream in self.streams:
            stream.close()


def capture_dead_bridge(fd, directory, until):
    """Only reader after the killed bridge is reaped; never transmits to MCU."""
    directory.mkdir()
    with (directory / "uart.bin").open("xb") as binary, (directory / "chunks.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["t_rx_pi_ns", "offset", "bytes"])
        offset = 0
        while raw() < until:
            ready, _, _ = select.select([fd], [], [], min(.05, max(0, (until - raw()) / 1e9)))
            if ready:
                data = os.read(fd, 4096)
                if not data:
                    raise RuntimeError("UART EOF during F1 passive capture")
                timestamp = raw()
                binary.write(data)
                writer.writerow([timestamp, offset, len(data)])
                offset += len(data)


def decode_capture(directory, args, ipc):
    """Use the hw-fixes decoder via a socketpair; generated TX is discarded."""
    parent, child = socket.socketpair()
    parent.setblocking(False)
    pipeline = Pipeline(directory, args, ipc, child.fileno())
    # Directory already contains raw evidence. No firmware framing replicated here.
    event_options = [args.state_events_option, directory / "state_events.csv"] if args.state_events_option else []
    decoder = pipeline.launch("hea_bridge", ["--serial-fd", child.fileno(), "--baud", args.baud,
        "--socket", Path(ipc) / "decode.sock", "--csv", directory / "bridge.csv",
        "--status-csv", directory / "mcu_status.csv", "--echo-csv", directory / "echo.csv",
        *event_options, "--echo-ms", 0], (child.fileno(),))
    try:
        pipeline.ready(directory / "state_events.csv", decoder)
        data = (directory / "uart.bin").read_bytes()
        position = 0
        deadline = time.monotonic() + 5
        while position < len(data):
            if time.monotonic() > deadline or decoder.poll() is not None:
                raise RuntimeError("F1 captured UART replay failed")
            readable, writable, _ = select.select([parent], [parent], [], .05)
            if readable:
                parent.recv(65536)  # Never forward replay-generated heartbeat to UART.
            if writable:
                position += parent.send(data[position:position + 4096])
        # FIONREAD on our duplicate of the peer observes unread kernel bytes.
        # Keep that duplicate open until decoding completes; it never reads.
        import array
        import fcntl
        import termios
        while time.monotonic() < deadline:
            pending = array.array("i", [0])
            fcntl.ioctl(child.fileno(), termios.FIONREAD, pending, True)
            if pending[0] == 0:
                # Allow the final read's parser/CSV writes to complete.
                time.sleep(.1)
                break
            readable, _, _ = select.select([parent], [], [], .05)
            if readable:
                parent.recv(65536)
        else:
            raise RuntimeError("F1 decoder did not drain replay")
    finally:
        pipeline.close()
        parent.close()
        child.close()
    save(directory / "replay.json", dict(t_rx_pi_ns="decoder replay time; use chunks.csv for original byte capture",
                                          mapping="pre-fault pipeline echo estimator, not replay t_mcu_pi_est_ns"))


def rearm(args, directory):
    command = shlex.split(args.rearm_command)
    with (directory / "rearm.log").open("a") as stream:
        stream.write(shlex.join(command) + "\n")
        stream.flush()
        subprocess.run(command, check=True, stdout=stream, stderr=stream, timeout=15, cwd=REPO)


def metadata(directory, phase):
    with (directory / f"meta_{phase}.json").open("w") as output, (directory / f"meta_{phase}.stderr.log").open("w") as error:
        subprocess.run(["bash", str(REPO / "scripts/pi/collect_metadata.sh")], cwd=REPO,
                       stdout=output, stderr=error, timeout=10, check=True)


def one_run(directory, fault, rep, args):
    directory.mkdir()
    meta = dict(fault=fault, rep=rep, status="FAILED", evidence=summary.EVIDENCE)
    if fault == "F5":
        meta.update(status="NOT_DONE", reason="bridge has no documented runtime inference-only suppression control; HEARTBEAT must remain active")
        save(directory / "run.json", meta)
        return
    save(directory / "run.json", meta)
    monitor = Monitor(directory)
    pipeline = recovery = None
    fd = None
    try:
        metadata(directory, "before")
        monitor.start()
        rearm(args, directory)
        # Keep tty open across F1's kill so the kernel does not discard RX on close.
        fd = os.open(args.serial, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        with tempfile.TemporaryDirectory(prefix="hea-e4-") as ipc:
            pipeline = Pipeline(directory / "pipeline", args, ipc, fd)
            pipeline.start()
            meta["steady_start_pi_ns"] = pipeline.wait_fresh(args.ready_timeout)
            pipeline.wait(meta["steady_start_pi_ns"] + 20_000_000_000, require_fresh=True)
            bridge = pipeline.processes["hea_bridge"]
            target = pipeline.processes["hea_infer_stub"] if fault == "F3" else bridge
            if fault == "F4":
                completed = subprocess.run(["sudo", "-n", sys.executable, str(Path(__file__).resolve()), "--hog", str(args.bridge_core)],
                                           text=True, capture_output=True, check=True, timeout=5)
                meta.update(json.loads(completed.stdout))
            else:
                signal_fault(target.pid, fault, meta)
            until = meta["onset_pi_ns"] + 10_000_000_000
            if fault == "F1":
                bridge.wait(timeout=2)
                capture_dead_bridge(fd, directory / "capture", until)
            else:
                pipeline.wait(until)
            meta["observation_end_pi_ns"] = raw()
            # Fresh pipeline for every recovery and every repetition.
            pipeline.close()
            if fault == "F1":
                decode_capture(directory / "capture", args, ipc)
            meta["recovery_start_pi_ns"] = raw()
            if fault == "F1":
                # Persistent crash ends when restore/rearm begins, not at SIGKILL.
                meta["fault_end_pi_ns"] = meta["recovery_start_pi_ns"]
            rearm(args, directory)
            # Clear pre-reset bytes before the new epoch. Never clear F1 capture.
            import termios
            termios.tcflush(fd, termios.TCIFLUSH)
            recovery = Pipeline(directory / "recovery", args, ipc, fd)
            recovery.start()
            recovery.wait_fresh(args.ready_timeout)
            # At least two more echo rounds make recovery fit/residual available.
            recovery.wait(raw() + 2_000_000_000)
            meta["recovery_observation_end_pi_ns"] = raw()
            meta["status"] = "COMPLETE"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        meta["reason"] = str(error)
        print(f"{directory.name}: FAILED: {error}", file=sys.stderr, flush=True)
    except KeyboardInterrupt:
        meta["reason"] = "campaign interrupted"
        raise
    finally:
        if recovery:
            recovery.close()
        if pipeline:
            pipeline.close()
        if fd is not None:
            os.close(fd)
        monitor.close()
        save(directory / "run.json", meta)
        try:
            metadata(directory, "after")
        except (OSError, subprocess.SubprocessError) as error:
            (directory / "metadata_error.txt").write_text(str(error) + "\n")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--hog":
        hog(int(sys.argv[2]))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outdir", type=Path, help="new campaign directory; refuses overwrite")
    parser.add_argument("reps", type=int, nargs="?", default=5)
    parser.add_argument("--serial", default="/dev/ttyAMA0")
    parser.add_argument("--baud", type=int, default=921600)
    parser.add_argument("--bridge-core", type=int, default=2)
    parser.add_argument("--controller-core", type=int, default=0)
    parser.add_argument("--ready-timeout", type=float, default=15)
    parser.add_argument("--rms-bound-us", type=float, default=200)
    parser.add_argument("--thresholds", type=Path)
    parser.add_argument("--state-events-option", default="",
                        help="optional hea_bridge CSV option from hw-fixes; default reads state_events.csv in bridge cwd; use --state-events-option=--NAME")
    parser.add_argument("--rearm-command", default=os.environ.get("HEA_E4_REARM", f"bash {shlex.quote(str(REPO / 'scripts/stm32/reset.sh'))}"),
                        help="local rearm/reset command, argv parsed with shlex; timeout 15 s")
    parser.add_argument("--estimate-only", action="store_true", help="print command and planned wall time, without hardware or sudo")
    args = parser.parse_args()
    if args.reps < 1 or args.reps > 100 or not math.isfinite(args.ready_timeout) or args.ready_timeout <= 0 or args.baud <= 0 or not math.isfinite(args.rms_bound_us) or args.rms_bound_us <= 0:
        parser.error("reps 1..100, positive timeout/baud/RMS bound required")
    # Four executed faults; F5 is explicitly NOT_DONE on this bridge API.
    minimum = 4 * args.reps * 32
    budget = 4 * args.reps * (32 + 2 * args.ready_timeout + 30 + 10)
    command = [str(REPO / "tools/experiments/e4_campaign.sh")] + [s for s in sys.argv[1:] if s != "--estimate-only"]
    print("Run command: " + shlex.join(command), flush=True)
    print(f"Wall-time estimate: >= {minimum / 60:.1f} min measured windows; allow about {budget / 60:.1f} min with startup/rearm/timeouts plus initial build. F5 NOT DONE.", flush=True)
    if args.estimate_only:
        return 0
    args.outdir = args.outdir.resolve()
    if args.thresholds:
        args.thresholds = args.thresholds.resolve()
    if sys.platform != "linux":
        parser.error("requires Linux Pi target; --estimate-only and synthetic analysis tests run on macOS")
    if args.outdir.exists():
        parser.error("outdir already exists; use a new directory")
    if args.bridge_core == args.controller_core or not {args.bridge_core, args.controller_core} <= os.sched_getaffinity(0):
        parser.error("distinct bridge/controller cores within current affinity required")
    if not Path(args.serial).exists():
        parser.error("serial device missing")
    for tool in ("make", "sudo", "vcgencmd", shlex.split(args.rearm_command)[0]):
        if shutil.which(tool) is None:
            parser.error(f"missing tool: {tool}")
    # Validate threshold configuration before spending time on the rig.
    configured, threshold_source = summary.thresholds(args.thresholds, REPO / "stm32/include")
    subprocess.run(["make", "-C", str(REPO / "linux"), "all"], check=True)
    subprocess.run(["sudo", "-n", "true"], check=True)
    os.sched_setaffinity(0, {args.controller_core})
    args.outdir.mkdir(parents=True)
    config = vars(args).copy()
    config.update(configured_thresholds_us=configured, threshold_source=threshold_source)
    save(args.outdir / "campaign.json", {k: str(v) if isinstance(v, Path) else v for k, v in config.items()})
    threshold_snapshot = args.outdir / "supervisor_thresholds.json"
    save(threshold_snapshot, {k: v for k, v in configured.items() if v is not None})
    (args.outdir / "command.txt").write_text(shlex.join(command) + "\n")
    with (args.outdir / "revision.txt").open("w") as stream:
        subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], stdout=stream, check=True)
    failed = False
    try:
        for rep in range(1, args.reps + 1):
            for fault in ("F1", "F2", "F3", "F4", "F5"):
                directory = args.outdir / f"{fault}-r{rep:02d}"
                print(f"Running {directory.name}", flush=True)
                one_run(directory, fault, rep, args)
                meta = json.loads((directory / "run.json").read_text())
                failed |= meta["status"] == "FAILED"
                # Missing hw-fixes/schema/startup is a campaign-level blocker.
                if meta["status"] == "FAILED":
                    raise RuntimeError(f"aborting after {directory.name}; evidence retained")
    except (KeyboardInterrupt, RuntimeError) as error:
        failed = True
        print(str(error), file=sys.stderr)
    finally:
        command = [sys.executable, str(REPO / "analysis/e4_summary.py"), str(args.outdir), "--rms-bound-us", str(args.rms_bound_us)]
        command += ["--thresholds", str(threshold_snapshot)]
        subprocess.run(command, check=True)
    return 1 if failed else 0


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    sys.exit(main())
