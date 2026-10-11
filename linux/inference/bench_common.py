"""Standard-library measurement and IPC helpers; safe to import without ORT/numpy."""
import csv
import hashlib
import math
import os
import struct
import sys
import time
from pathlib import Path

SOURCE_RECORD = struct.Struct('<IQ')
RESULT_RECORD = struct.Struct('<IQQBB')


def percentile(values, percent):
    """Linear interpolation at (n - 1) * percent / 100, including endpoints."""
    if not values:
        raise ValueError('percentile requires samples')
    if not math.isfinite(percent) or not 0 <= percent <= 100:
        raise ValueError('percent must be in [0, 100]')
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def summarize(values):
    return {'count': len(values), 'p50_ns': percentile(values, 50),
            'p95_ns': percentile(values, 95), 'p99_ns': percentile(values, 99),
            'max_ns': max(values), 'mean_ns': sum(values) / len(values)}


def write_csv(path, samples):
    with Path(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(('run_idx', 'pre_ns', 'infer_ns'))
        writer.writerows(samples)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def clock():
    """Select once, so all timestamps in a run have the same clock domain."""
    if sys.platform.startswith('linux') and hasattr(time, 'CLOCK_MONOTONIC_RAW'):
        raw = time.CLOCK_MONOTONIC_RAW
        time.clock_gettime_ns(raw)  # Fail clearly if advertised but unsupported.
        return lambda: time.clock_gettime_ns(raw), 'CLOCK_MONOTONIC_RAW'
    return time.perf_counter_ns, 'perf_counter_ns'


def parse_cpu(value):
    try:
        cpus = {int(item) for item in value.split(',')}
    except ValueError as exc:
        raise ValueError('CPU list must be comma-separated integers') from exc
    if not cpus or min(cpus) < 0:
        raise ValueError('CPU IDs must be nonnegative')
    return cpus


def pin_cpu(cpus):
    if cpus is not None:
        if not sys.platform.startswith('linux') or not hasattr(os, 'sched_setaffinity'):
            raise RuntimeError('--cpu requires Linux sched_setaffinity')
        os.sched_setaffinity(0, cpus)
    return sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None


def unpack_source(data):
    if len(data) != SOURCE_RECORD.size:
        raise ValueError(f'source record must be {SOURCE_RECORD.size} bytes')
    return SOURCE_RECORD.unpack(data)


def pack_result(frame_id, t_input_ns, t_done_ns, class_id, confidence):
    """Pack C ABI fields; confidence is an integer percentage."""
    if not isinstance(confidence, int) or not 0 <= confidence <= 100:
        raise ValueError('confidence must be an integer in [0, 100]')
    if t_done_ns < t_input_ns:
        raise ValueError('completion timestamp precedes input')
    return RESULT_RECORD.pack(frame_id, t_input_ns, t_done_ns, class_id, confidence)


def unpack_result(data):
    if len(data) != RESULT_RECORD.size:
        raise ValueError(f'result record must be {RESULT_RECORD.size} bytes')
    record = RESULT_RECORD.unpack(data)
    if record[4] > 100 or record[2] < record[1]:
        raise ValueError('invalid confidence or completion timestamp')
    return record
