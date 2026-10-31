#!/usr/bin/env python3
"""Shuffled E campaigns using the existing PTY pipeline; no new dependencies."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis'))
import e_summary

STRESSORS = ['B0_idle', 'CPU_c23', 'B1_stream_c2', 'C1_cache2M_c2', 'B2_memrate_c23']


def stress_commands(condition):
    options = {
        'CPU_c23': ([2, 3], ['--cpu', '1']),
        'B1_stream_c2': ([2], ['--stream', '1', '--stream-l3-size', '2M', '--stream-index', '0']),
        'C1_cache2M_c2': ([2], ['--cache', '1', '--cache-level', '3', '--cache-size', '2M', '--cache-no-affinity']),
        'B2_memrate_c23': ([2, 3], ['--memrate', '1', '--memrate-bytes', '64M']),
    }
    if condition == 'B0_idle':
        return []
    cores, args = options[condition]
    return [['taskset', '-c', str(core), 'stress-ng'] + args + ['--metrics-brief'] for core in cores]


def plan(experiment, reps, worst=None):
    if experiment == 'E1':
        conditions = [('P0', stressor, 'latest') for stressor in STRESSORS]
    elif experiment == 'E2':
        conditions = [(p, s, 'latest') for p in ('P0', 'P1') for s in ['B0_idle'] + worst[:2]]
    elif experiment == 'E3B':
        # In this experiment q is the input policy; bridge is fixed to latest.
        conditions = [('P1', s, q) for s in ('B0_idle', 'B2_memrate_c23') for q in ('fifo', 'latest')]
    else:
        conditions = [('P1', s, q) for s in ['B0_idle', worst[0]] for q in ('fifo', 'latest')]
    result = [(p, s, q, rep) for rep in range(1, reps + 1) for p, s, q in conditions]
    random.Random(42).shuffle(result)
    return result


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def capture(args):
    result = subprocess.run(args, text=True, capture_output=True, timeout=10)
    return result.stdout.strip() if result.returncode == 0 else ''


def snapshot(path):
    with path.open('w') as stream, path.with_suffix('.stderr.log').open('w') as errors:
        subprocess.run(['bash', str(ROOT / 'scripts/pi/collect_metadata.sh')], cwd=ROOT,
                       stdout=stream, stderr=errors, check=True)


def read_sys(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ''


def voltage_value(output):
    # Firmware can include an ADC channel annotation, e.g. "volt(24)".
    match = re.search(r'\bEXT5V_V\b[^=\n]*=\s*([0-9]+(?:\.[0-9]+)?)V\b', output)
    return match[1] if match else ''


def process_evidence(pipeline):
    result = {}
    ticks = rss = 0
    for name in ('source', 'infer', 'bridge'):
        try:
            pid = int((pipeline / f'{name}.pid').read_text())
            status = Path(f'/proc/{pid}/status').read_text()
            stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
            ticks += int(stat[11]) + int(stat[12])  # proc stat fields 14,15
            rss += int(re.search(r'^VmRSS:\s+(\d+)', status, re.M)[1]) / 1024
            locked = int(re.search(r'^VmLck:\s+(\d+)', status, re.M)[1])
            result[name] = dict(pid=pid, policy=os.sched_getscheduler(pid),
                                priority=os.sched_getparam(pid).sched_priority,
                                affinity=sorted(os.sched_getaffinity(pid)), locked_kib=locked,
                                allowed_list=re.search(r'^Cpus_allowed_list:\s+(.*)', status, re.M)[1])
        except (OSError, ValueError, TypeError):
            pass
    return result, ticks, rss


def settings_match(evidence, profile, stage='stub'):
    if set(evidence) != {'source', 'infer', 'bridge'}:
        return False
    for name, cpu, priority in [('source', 1, 60), ('bridge', 1, 70), ('infer', 0, 0)]:
        expected = priority if profile == 'P1' else 0
        r = evidence[name]
        if r['policy'] != (os.SCHED_FIFO if expected else os.SCHED_OTHER) or r['priority'] != expected or r['affinity'] != [cpu]:
            return False
        if profile == 'P1' and (name in ('source', 'bridge') or stage == 'stub') and r['locked_kib'] <= 0:
            return False
    return True


def monitor(run, stop, profile, evidence_records, errors):
    try:
        monitor_samples(run, stop, evidence_records)
    except Exception as exc:
        errors.append(str(exc))


def monitor_samples(run, stop, evidence_records):
    with (run / 'thermal.csv').open('w', newline='') as thermal, (run / 'resources.csv').open('w', newline='') as resources:
        tw, rw = csv.writer(thermal), csv.writer(resources)
        tw.writerow(['t_pi_ns', 'timestamp', 'temp_millic', 'cpu0_khz', 'throttled', 'ext5v_v'])
        rw.writerow(['timestamp', 'cpu_percent', 'rss_mib'])
        previous = None
        while not stop.is_set():
            t0 = time.monotonic()
            flags = capture(['vcgencmd', 'get_throttled']).partition('=')[2]
            voltage = capture(['vcgencmd', 'pmic_read_adc', 'EXT5V_V'])
            tw.writerow([time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW), time.time(), read_sys('/sys/class/thermal/thermal_zone0/temp'),
                         read_sys('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'),
                         flags, voltage_value(voltage)])
            evidence, ticks, rss = process_evidence(run / 'pipeline')
            counter_time = time.monotonic()
            if set(evidence) == {'source', 'infer', 'bridge'}:
                evidence_records.append(evidence)
                cpu = ''
                if previous is not None:
                    old_time, old_ticks, old_pids = previous
                    if [r['pid'] for r in evidence.values()] == old_pids and ticks >= old_ticks:
                        cpu = (ticks - old_ticks) / os.sysconf('SC_CLK_TCK') / (counter_time - old_time) * 100
                previous = (counter_time, ticks, [r['pid'] for r in evidence.values()])
                rw.writerow([time.time(), cpu, rss])
            thermal.flush()
            resources.flush()
            stop.wait(max(0, 0.5 - (time.monotonic() - t0)))


def stop_process(process, elevated=False, group=False):
    if process.poll() is not None:
        return
    if elevated:
        subprocess.run(['sudo', '-n', 'kill', '-TERM', '--', str(process.pid)], check=False)
    elif group:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    else:
        process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        if elevated:
            subprocess.run(['sudo', '-n', 'kill', '-KILL', '--', f'-{process.pid}'], check=False)
        elif group:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.wait(timeout=5)


def execute_run(args, experiment, condition):
    if experiment == 'E3_REAL':
        profile, stressor, input_policy, bridge_policy, repetition = condition
        policy = f'input_{input_policy}_bridge_{bridge_policy}'
    else:
        profile, stressor, policy, repetition = condition
    if experiment != 'E3_REAL':
        input_policy = policy if experiment == 'E3B' else 'fifo'
        bridge_policy = 'latest' if experiment == 'E3B' else policy
    run = args.out / f'{experiment}_{profile}_{stressor}_{policy}_r{repetition}'
    run.mkdir()
    stress = stress_commands(stressor)
    json_write(run / 'condition.json', dict(experiment=experiment, profile=profile, stressor=stressor,
               policy=bridge_policy, input_policy=input_policy, repetition=repetition,
               exact_load=' ; '.join(shlex.join(c) for c in stress) or 'idle'))
    snapshot(run / 'meta_before.json')
    stop = threading.Event()
    evidence = []
    monitor_errors = []
    thread = threading.Thread(target=monitor, args=(run, stop, profile, evidence, monitor_errors), daemon=True)
    processes = []
    handles = []
    pipeline = None
    stressor_ok = True
    rc = 1
    command = ['bash', str(ROOT / 'scripts/pi/run_pipeline.sh'), '--duration', str(args.seconds),
               '--period-ms', '100', '--policy', bridge_policy, '--input-policy', input_policy,
               '--stage', args.stage, '--threads', '1',
               '--source-cpu', '1', '--infer-cpu', '0', '--bridge-cpu', '1',
               '--run-dir', str(run / 'pipeline')]
    if experiment == 'E3_REAL':
        command += ['--serial', '/dev/ttyAMA0', '--baud', '921600', '--echo-ms', '100', '--fresh-timeout', str(getattr(args, 'fresh_timeout', 30)),
                    '--reset-command', args.rearm_command]
    if args.model:
        command += ['--model', str(args.model)]
    elevated = profile == 'P1'
    if elevated:
        command += ['--source-priority', '60', '--bridge-priority', '70', '--mlock']
        # Elevate the existing pipeline as a unit so datagram socket ownership
        # remains consistent. Inference/receiver retain SCHED_OTHER.
        command = ['sudo', '-n', 'env', f'PYTHON={args.python}',
                   f'HEA_COOLER={os.environ.get("HEA_COOLER", "unknown")}'] + command
    (run / 'command.txt').write_text(shlex.join(command) + '\n')
    thread.start()
    try:
        for i, cmd in enumerate(stress):
            handle = (run / f'stress_{i}.log').open('w')
            handles.append(handle)
            processes.append(subprocess.Popen(cmd, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True))
        if processes:
            time.sleep(5)
        handle = (run / 'pipeline.log').open('w')
        handles.append(handle)
        pipeline = subprocess.Popen(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
        while pipeline.poll() is None:
            if any(p.poll() is not None for p in processes):
                stressor_ok = False
                stop_process(pipeline, elevated)
                break
            time.sleep(0.2)
        rc = pipeline.wait()
    finally:
        if pipeline is not None:
            stop_process(pipeline, elevated)
        for p in processes:
            if p.poll() is not None:
                stressor_ok = False
            stop_process(p, group=True)
            # stress-ng should handle SIGTERM and report metrics normally.
            if p.returncode != 0:
                stressor_ok = False
        stop.set()
        thread.join(timeout=25)
        for handle in handles:
            handle.close()
        if elevated and (run / 'pipeline').exists():
            subprocess.run(['sudo', '-n', 'chown', '-R', f'{os.getuid()}:{os.getgid()}', str(run / 'pipeline')], check=True)
        snapshot(run / 'meta_after.json')
        (run / 'exit_code').write_text(str(rc) + '\n')
        json_write(run / 'settings.json', evidence)
        json_write(run / 'execution.json', dict(stressor_ok=stressor_ok,
                   stress_exit_codes=[p.returncode for p in processes],
                   monitor_ok=not monitor_errors and not thread.is_alive(), monitor_errors=monitor_errors,
                   settings_ok=bool(evidence) and all(settings_match(e, profile, args.stage) for e in evidence)))
    report = getattr(args, 'summary_func', e_summary.summarize_run)(run)
    (run / 'validity').write_text(report['validity'] + '\n')
    print(f"{run.name}: {report['validity']}", flush=True)
    time.sleep(5)


def positive(value):
    if not re.fullmatch('[1-9][0-9]{0,4}', value) or int(value) > 86400:
        raise argparse.ArgumentTypeError('expected integer 1..86400')
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', choices=['E1', 'E2', 'E3', 'E3B', 'ALL'])
    parser.add_argument('out', type=Path)
    parser.add_argument('reps', type=positive, nargs='?', default=3)
    parser.add_argument('seconds', type=positive, nargs='?', default=60)
    parser.add_argument('--stage', choices=['onnx', 'stub'], default='stub')
    parser.add_argument('--model', type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.python = shutil.which(os.environ.get('PYTHON', 'python3'))
    try:
        if platform.system() != 'Linux':
            raise ValueError('Run on the Linux Pi target, not macOS.')
        if args.out.exists():
            raise ValueError(f'Refusing existing campaign: {args.out}')
        for tool in ('make', 'python3', 'socat', 'taskset', 'stress-ng', 'vcgencmd', 'git', 'lscpu'):
            if shutil.which(tool) is None:
                raise ValueError(f'Missing dependency: {tool}')
        if not args.python:
            raise ValueError('PYTHON interpreter unavailable')
        if args.stage == 'onnx':
            if args.model is None or not args.model.is_file():
                raise ValueError('--stage onnx requires --model PATH to an existing file')
            args.model = args.model.resolve()
            subprocess.run([args.python, '-c', 'import numpy, onnxruntime'], check=True)
        if args.experiment != 'E1':
            if shutil.which('sudo') is None or subprocess.run(['sudo', '-n', 'true']).returncode:
                raise ValueError('P1 requires passwordless sudo: sudo -n true failed.')
        subprocess.run(['make', '-C', str(ROOT / 'linux'), 'all'], check=True)
        args.out.mkdir(parents=True)
        json_write(args.out / 'campaign.json', dict(experiment=args.experiment, reps=args.reps, seconds=args.seconds,
                   stage=args.stage, model=str(args.model) if args.model else None,
                   model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest() if args.model else None,
                   seed=42, warmup_seconds=5, cooldown_seconds=5, source_cpu=1, inference_cpu=0, bridge_cpu=1,
                   source_period_ms=100, python=args.python, p2='not done: systemd quota/delegation not validated',
                   evidence=e_summary.EVIDENCE, ranking='E1 median per-run delivery P99; ties: max then stressor name'))
        (args.out / 'platform.txt').write_text(capture(['stress-ng', '--version']) + '\n' + capture(['lscpu']) + '\n')
        experiments = (['E1', 'E2', 'E3', 'E3B'] if args.experiment == 'ALL' else
                       [args.experiment] if args.experiment in ('E1', 'E3B') else ['E1', args.experiment])
        worst = None
        for experiment in experiments:
            if experiment in ('E2', 'E3'):
                worst = e_summary.worst_stressors(args.out)
                json_write(args.out / 'worst_stressors.json', worst)
            order = plan(experiment, args.reps, worst)
            json_write(args.out / f'{experiment}_order.json', order)
            for condition in order:
                print(f'Running {experiment} {condition}', flush=True)
                execute_run(args, experiment, condition)
            e_summary.write_summary(args.out)
        (args.out / 'DONE').touch()
        runs, _ = e_summary.write_summary(args.out)
        print(f"Campaign complete: {sum(r['valid'] for r in runs)}/{len(runs)} valid; {args.out / 'summary'}")
        return 0 if all(r['valid'] for r in runs) else 1
    except (ValueError, OSError, subprocess.SubprocessError, InterruptedError) as exc:
        if args.out.is_dir() and list(args.out.glob('E*/condition.json')):
            e_summary.write_summary(args.out)
        print(f'e_campaign: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise InterruptedError(f'interrupted by signal {signum}')
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    sys.exit(main())
