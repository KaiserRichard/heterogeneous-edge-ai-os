#!/usr/bin/env python3
"""Shuffled E3 campaign on /dev/ttyAMA0; run only on the Pi."""
import argparse
import hashlib
import os
from pathlib import Path
import platform
import random
import shlex
import shutil
import signal
import subprocess
import sys

import e_campaign as campaign
sys.path.insert(0, str(campaign.ROOT / 'analysis'))
import e3_real_summary as summary


def plan(reps):
    runs = [('P1', load, ip, bp, rep) for rep in range(1, reps + 1)
            for load in ('B0_idle', 'B2_memrate_c23')
            for ip, bp in (('fifo', 'fifo'), ('fifo', 'latest'), ('latest', 'latest'))]
    random.Random(42).shuffle(runs)
    return runs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    parser.add_argument('reps', type=campaign.positive, nargs='?', default=3)
    parser.add_argument('seconds', type=campaign.positive, nargs='?', default=60)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--rearm-command', default=f"bash {shlex.quote(str(Path.home() / 'osbuild/rearm_via_mac.sh'))}",
                        help='synchronous MCU reset argv; after model initialization, before UART launch, timeout 15 s')
    parser.add_argument('--fresh-timeout', type=campaign.positive, default=30)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.model = args.model.resolve()
    args.python = shutil.which(os.environ.get('PYTHON', 'python3'))
    args.stage = 'onnx'
    args.summary_func = summary.summarize_run
    print('Run command: ' + shlex.join(['env', f'PYTHON={os.environ.get("PYTHON", "python3")}',
          'bash', str(campaign.ROOT / 'tools/experiments/e3_real.sh')] + sys.argv[1:]), flush=True)
    n = 6 * args.reps
    print(f'Wall-time estimate: {n * args.seconds / 60:.1f} min measured; '
          f'allow {n * (args.seconds + 30) / 60:.1f} min plus initial build/model startup.', flush=True)
    try:
        if platform.system() != 'Linux':
            raise ValueError('Run on the Linux Pi target, not macOS')
        if args.out.exists():
            raise ValueError(f'Refusing existing campaign: {args.out}')
        if not args.model.is_file() or not args.python:
            raise ValueError('existing --model and PYTHON interpreter required')
        command = shlex.split(args.rearm_command)
        if not command:
            raise ValueError('empty rearm command')
        for tool in ('make', 'python3', 'taskset', 'stress-ng', 'vcgencmd', 'git', 'lscpu', 'sudo', command[0]):
            if shutil.which(tool) is None:
                raise ValueError(f'Missing dependency: {tool}')
        subprocess.run(['sudo', '-n', 'true'], check=True)
        subprocess.run([args.python, '-c', 'import numpy, onnxruntime'], check=True)
        subprocess.run(['make', '-C', str(campaign.ROOT / 'linux'), 'all'], check=True)
        args.out.mkdir(parents=True)
        order = plan(args.reps)
        campaign.json_write(args.out / 'campaign.json', dict(experiment='E3_REAL', reps=args.reps,
            seconds=args.seconds, seed=42, stage='onnx', model=str(args.model), python=args.python,
            model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),
            rearm_command=args.rearm_command, serial='/dev/ttyAMA0', baud=921600,
            rms_bound_us=200, monitor_period_seconds=.5, evidence=summary.EVIDENCE,
            source_cpu=1, source_priority=60, bridge_cpu=1, bridge_priority=70,
            inference_cpu=0, inference_policy='SCHED_OTHER', threads=1))
        campaign.json_write(args.out / 'order.json', order)
        (args.out / 'platform.txt').write_text(campaign.capture(['stress-ng', '--version']) + '\n' +
                                             campaign.capture(['lscpu']) + '\n')
        for condition in order:
            print(f'Running {condition}', flush=True)
            campaign.execute_run(args, 'E3_REAL', condition)
        runs, _ = summary.write_summary(args.out)
        (args.out / 'DONE').touch()
        print(f"Complete: {sum(r['valid'] for r in runs)}/{len(runs)} valid; {args.out / 'summary'}")
        return 0 if all(r['valid'] for r in runs) else 1
    except (ValueError, OSError, subprocess.SubprocessError, InterruptedError) as exc:
        if args.out.is_dir() and list(args.out.glob('E3_REAL*/condition.json')):
            summary.write_summary(args.out)
        print(f'e3_real: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    def interrupted(signum, frame):
        raise InterruptedError(f'interrupted by signal {signum}')
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    sys.exit(main())
