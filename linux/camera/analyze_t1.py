#!/usr/bin/env python3
"""OS-T1 timing summary; synthetic runs are software checks, not Pi evidence."""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path

COLUMNS = ['frame_id', 'seq', 't_sensor_ns', 't_recv_mono_ns', 't_input_ns', 'status']
STATUSES = {'sent', 'dropped', 'injected_drop', 'missing_timestamp', 'capture_error'}


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * p / 100
    low, high = math.floor(position), math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def summarize(rows, fps):
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError('fps must be positive and finite')
    if not rows:
        raise ValueError('CSV contains no frames')
    previous = None
    for row in rows:
        for key in COLUMNS[:-1]:
            row[key] = int(row[key])
            if row[key] < 0:
                raise ValueError('negative timestamp or sequence')
        if row['status'] not in STATUSES or row['frame_id'] != row['seq']:
            raise ValueError('invalid status or frame/sequence mismatch')
        if row['t_sensor_ns'] != row['t_input_ns']:
            raise ValueError('input timestamp differs from sensor timestamp')
        if previous is not None and row['seq'] <= previous:
            raise ValueError('sequence regressed/wrapped; analyze separate runs')
        previous = row['seq']
    counts = Counter(row['status'] for row in rows)
    captures = [r for r in rows if r['status'] in ('sent', 'dropped')]
    intervals = [b['t_sensor_ns'] - a['t_sensor_ns'] for a, b in zip(captures, captures[1:])]
    if any(delta <= 0 for delta in intervals) or any(r['t_sensor_ns'] <= 0 for r in captures):
        raise ValueError('capture sensor timestamps must be positive and increasing')
    offsets = [r['t_recv_mono_ns'] - r['t_sensor_ns'] for r in captures]
    missing = sum(b['seq'] - a['seq'] - 1 for a, b in zip(rows, rows[1:]))
    gaps = sum(b['seq'] - a['seq'] - 1 for a, b in zip(captures, captures[1:]))
    explicit_drops = sum(counts[s] for s in ('injected_drop', 'missing_timestamp', 'capture_error'))
    expected = rows[-1]['seq'] - rows[0]['seq'] + 1
    period = 1e9 / fps
    mean = sum(intervals) / len(intervals) if intervals else None
    jitter = percentile([abs(delta - period) for delta in intervals], 99)
    offset_p99 = percentile(offsets, 99)
    return dict(
        fps=fps, nominal_period_ns=period, rows=len(rows), captures=len(captures),
        interval_mean_ns=mean, jitter_p99_ns=jitter, sequence_gaps=gaps,
        missing_sequences=missing, recorded_capture_drops=explicit_drops,
        capture_drops=missing + explicit_drops, capture_drop_fraction=(missing + explicit_drops) / expected,
        ipc_drops=counts['dropped'], statuses=dict(counts),
        recv_sensor_offset_ns=dict(p50=percentile(offsets, 50), p99=offset_p99,
                                   max=max(offsets) if offsets else None,
                                   min=min(offsets) if offsets else None),
        timing_checks=dict(interval_within_one_percent=mean is not None and abs(mean - period) <= .01 * period,
                           jitter_below_2ms=jitter is not None and jitter < 2_000_000,
                           drops_below_point_one_percent=(missing + explicit_drops) / expected < .001,
                           offset_positive_and_bounded=bool(offsets) and min(offsets) > 0 and offset_p99 < period + 10_000_000),
        clock_stability='not established: one startup pair cannot prove constancy',
        hardware_validity='not established: requires Pi metadata and no-suspend clock validation')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--fps', required=True, type=float)
    parser.add_argument('--output', type=Path, default=Path('summary.json'))
    args = parser.parse_args(argv)
    with args.csv.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != COLUMNS:
            parser.error('unexpected camera CSV schema')
        try:
            result = summarize(list(reader), args.fps)
        except (ValueError, TypeError) as exc:
            parser.error(str(exc))
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    main()
