#!/usr/bin/env python3
"""E3 real UART receipt-age reports; standard library only."""
import argparse
import math
from pathlib import Path
import sys

import e_summary
import e4_summary
import pipeline_summary as pipeline

EVIDENCE = 'MEASURED (real UART, MCU timestamps)'


def finite(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('nonfinite timestamp/age')
    return value


def receipt_samples(p, fits):
    reports = pipeline.rows(p / 'inf_rx.csv')
    sent = pipeline.indexed(pipeline.rows(p / 'bridge.csv'), 'bridge')
    seen = set()
    samples = []
    for r in reports:
        frame = int(r['frame_id'])  # Missing correlations invalidate, never silently omit.
        if frame in seen:
            raise ValueError('duplicate INF_RX frame_id')
        seen.add(frame)
        source = sent[frame]
        if int(r['seq']) != int(source['seq']) or int(r['t_input_ns']) != int(source['t_input_ns']):
            raise ValueError('INF_RX correlation mismatch')
        if int(r['lost_count']) != 0:
            raise ValueError('INF_RX lost_count > 0')
        if int(r['state']) not in range(4):
            raise ValueError('invalid INF_RX state')
        rx = int(r['t_rx_pi_ns'])
        local = finite(r['age_mcu_us'])
        if local < 0:
            raise ValueError('negative age')
        if fits is None:
            samples.append((None, local))
            continue
        fit = min(fits, key=lambda f: abs(f[0] - rx))
        if abs(fit[0] - rx) > 2_000_000_000:
            raise ValueError('clock fit more than 2 s from report')
        mapped = e4_summary.map_mcu(int(r['mcu_rx_us']), fit)
        age = (mapped - int(r['t_input_ns'])) / 1000
        local = finite(r['age_mcu_us'])
        if age < 0 or local < 0:
            raise ValueError('negative age')
        samples.append((age, local))
    if not samples:
        raise ValueError('no INF_RX reports')
    return samples


def state_times(p, fits, start, end):
    events = pipeline.rows(p / 'state_events.csv')
    ordered = []
    for r in events:
        if int(r['lost_count']) != 0:
            raise ValueError('STATE_EVENT lost_count > 0')
        old, new = int(r['old']), int(r['new'])
        if old not in range(4) or new not in range(4):
            raise ValueError('invalid STATE_EVENT state')
        if fits is None:
            # MCU intervals, anchored to the first event's RAW host receipt.
            anchor = events[0]
            stamp = int(anchor['t_rx_pi_ns']) + (int(r['mcu_us']) - int(anchor['mcu_us'])) * 1000
            ordered.append((stamp, old, new))
            continue
        fit = min(fits, key=lambda f: abs(f[0] - int(r['t_rx_pi_ns'])))
        if abs(fit[0] - int(r['t_rx_pi_ns'])) > 2_000_000_000:
            raise ValueError('clock fit more than 2 s from state event')
        ordered.append((e4_summary.map_mcu(int(r['mcu_us']), fit), old, new))
    # Wire order preserves multiple transitions at the same timestamp.
    fresh = e_summary.read_json(p / 'fresh_start.json') if (p / 'fresh_start.json').exists() else None
    if not ordered and fresh and int(fresh['new']) == 1 and int(fresh['t_rx_pi_ns']) <= start:
        return dict(init_seconds=0., fresh_seconds=(end-start)/1e9, hold_seconds=0., failsafe_seconds=0.)
    if not ordered:
        raise ValueError('STATE_EVENT unavailable; state occupancy unknown')
    if any(b[0] < a[0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError('STATE_EVENT clock ordering regression')
    current = ordered[0][1]
    cursor = start
    durations = [0.0] * 4
    for stamp, old, new in ordered:
        if old != current:
            raise ValueError('STATE_EVENT chain discontinuity')
        if stamp > end:
            break
        if stamp >= start:
            durations[current] += stamp - cursor
            cursor = stamp
        current = new
    durations[current] += end - cursor
    return {f'{name}_seconds': durations[i] / 1e9
            for i, name in enumerate(('init', 'fresh', 'hold', 'failsafe'))}


def summarize_run(run):
    config = e_summary.read_json(run / 'condition.json')
    result = dict(config, run=run.name, evidence=EVIDENCE)
    errors = []
    clock_errors = []
    base = e_summary.validity(run)
    if base != 'OK':
        errors.append(base)
    try:
        p = run / 'pipeline'
        pipeline_config = e_summary.read_json(p / 'config.json')
        if pipeline_config.get('serial') != '/dev/ttyAMA0' or pipeline_config.get('baud') != 921600:
            raise ValueError('requires /dev/ttyAMA0 at 921600')
        if pipeline_config.get('stage') != 'onnx' or config.get('profile') != 'P1':
            raise ValueError('requires ONNX stage and P1')
        start, end = [int((p / name).read_text()) for name in ('window_start_ns', 'window_end_ns')]
        if end <= start:
            raise ValueError('invalid observation window')
        thermal = pipeline.rows(run / 'thermal.csv')
        timestamps = [int(r['t_pi_ns']) for r in thermal]
        if len(timestamps) < 2 or any(b <= a or b - a > 750_000_000 for a, b in zip(timestamps, timestamps[1:])):
            raise ValueError('0.5 s power monitor missing or gap > 0.75 s')
        if timestamps[0] > start or timestamps[-1] < end:
            raise ValueError('power monitor does not cover measurement window')
        fits = None
        try:
            fits = e4_summary.clock_fits(p)
            if not fits:
                raise ValueError('clock-sync fit unavailable')
            result['clock_rms_max_us'] = max(f[-1] for f in fits)
            if result['clock_rms_max_us'] > 200:
                raise ValueError('clock-sync RMS > 200 us')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            clock_errors.append(str(exc))
        statuses = pipeline.rows(p / 'mcu_status.csv')
        if not statuses or any(not r.get('state_event_lost') or int(r['state_event_lost']) > 0 for r in statuses):
            errors.append('MCU status missing or STATE_EVENT losses')
        samples = receipt_samples(p, None)
        result.update(metrics(samples))
        result.update(state_times(p, None, start, end))
        if not clock_errors:
            try:
                result.update(metrics(receipt_samples(p, fits)))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                clock_errors.append(str(exc))
        inf = pipeline.rows(p / 'infer.csv')
        stats = pipeline.stats(p / 'bridge.stderr.log')
        if 'overwritten' not in stats:
            raise ValueError('bridge counters missing')
        result.update(delivered=len(samples), skipped=sum(r['status'] == 'skipped_stale' for r in inf),
                      overwritten=int(stats['overwritten']), bridge_sent=len(pipeline.rows(p / 'bridge.csv')),
                      bridge_dropped=int(stats['dropped']), source_generated=len(pipeline.rows(p / 'source.csv')))
        result['bridge_unreported'] = result['bridge_sent'] - result['delivered']
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    result.update(mcu_valid=not errors, mcu_validity='INVALID: ' + '; '.join(errors) if errors else 'OK',
                  mapped_valid=not (errors or clock_errors),
                  mapped_validity='INVALID: ' + '; '.join(errors + clock_errors) if errors or clock_errors else 'OK')
    result.update(valid=result['mapped_valid'], validity=result['mapped_validity'])
    return result


def metrics(samples):
    output = {}
    for index, label in enumerate(('mapped', 'mcu')):
        values = [s[index] for s in samples]
        if any(v is None for v in values):
            continue
        stats = pipeline.distribution(values)
        for stat in ('p50', 'p99', 'max'):
            output[f'{label}_{stat}_us'] = stats[stat]
        for threshold in (100, 150):
            misses = sum(v > threshold * 1000 for v in values)
            output[f'{label}_misses_{threshold}'] = misses
            output[f'{label}_miss_rate_{threshold}'] = misses / len(values)
    return output


def aggregate(runs, campaign):
    groups = {}
    for r in runs:
        groups.setdefault((r['stressor'], r['input_policy'], r['policy']), []).append(r)
    result = []
    for key, members in sorted(groups.items()):
        valid = [r for r in members if r['valid']]
        row = dict(zip(('stressor', 'input_policy', 'policy'), key), evidence=EVIDENCE,
                   profile='P1', valid_reps=len(valid), total_reps=len(members))
        local_valid = [r for r in members if r.get('mcu_valid', r['valid'])]
        row.update(mapped_valid_reps=len(valid), mcu_valid_reps=len(local_valid))
        for accepted, fits_required in ((local_valid, False), (valid, True)):
            if not accepted:
                continue
            samples = []
            for r in accepted:
                p = campaign / r['run'] / 'pipeline'
                samples.extend(receipt_samples(p, e4_summary.clock_fits(p) if fits_required else None))
            calculated = metrics(samples)
            row.update({k: v for k, v in calculated.items() if not fits_required or k.startswith('mapped_')})
        if local_valid:
            for k in ('delivered', 'skipped', 'overwritten', 'bridge_sent', 'bridge_unreported',
                      'bridge_dropped', 'source_generated', 'init_seconds', 'fresh_seconds', 'hold_seconds', 'failsafe_seconds'):
                row[k] = sum(r[k] for r in local_valid)
        result.append(row)
    return result


def latex(records):
    columns = ('run', 'profile', 'stressor', 'input_policy', 'policy', 'validity', 'mcu_validity', 'mapped_validity', 'valid_reps', 'total_reps',
               'mapped_p50_us', 'mapped_p99_us', 'mapped_max_us', 'mcu_p50_us', 'mcu_p99_us', 'mcu_max_us',
               'mapped_misses_100', 'mapped_misses_150', 'mcu_misses_100', 'mcu_misses_150',
               'delivered', 'skipped', 'overwritten', 'hold_seconds', 'failsafe_seconds')
    columns = [k for k in columns if any(k in r for r in records)]
    escape = e_summary.latex_escape
    lines = ['% ' + EVIDENCE, r'\par ' + escape(EVIDENCE),
             r'\begin{tabular}{' + 'l' * len(columns) + '}',
             ' & '.join(escape(k) for k in columns) + r' \\ \hline']
    for r in records:
        lines.append(' & '.join(escape(e_summary.fmt(r.get(k))) for k in columns) + r' \\')
    return '\n'.join(lines + [r'\end{tabular}']) + '\n'


def write_summary(campaign):
    runs = [summarize_run(p.parent) for p in sorted(campaign.glob('E3_REAL*/condition.json'))]
    if not runs:
        raise ValueError('no E3_REAL runs')
    conditions = aggregate(runs, campaign)
    out = campaign / 'summary'
    out.mkdir(exist_ok=True)
    for name, records in (('per_run', runs), ('per_condition', conditions)):
        e_summary.csv_write(out / f'{name}.csv', records)
        (out / f'{name}.tex').write_text(latex(records))
    (out / 'README.md').write_text(EVIDENCE + '\n\nNearest-rank receipt age quantiles, us. '
        'Condition quantiles pool accepted deliveries from valid runs; counts and state times are summed. '
        'Both strict >100 ms and >150 ms misses use accepted deliveries as denominator. '
        'Counts and receipt ages include shutdown drain; STATE_EVENT occupancy uses the RAW measurement window. '
        'Mapped receipt time uses the nearest echo affine fit (including retrospective startup mapping), '
        'at most 2 s away, with all fit RMS <=200 us. Online mapping remains in inf_rx.csv. '
        'MCU age is the supervisor evaluation estimate: send age + receipt-to-evaluation elapsed + provisional transit allowance. '
        'It includes MCU queue delay and is separate from mapped receipt AoI. '
        'MCU-local validity is independent of clock fits; mapped validity retains the 200 us RMS bound. '
        'State durations use MCU timestamp differences anchored to first RAW event receipt; window edges '
        'therefore include UART reporting delay uncertainty, without cross-clock calibration. '
        'An explicit startup FRESH anchor permits a transition-free 100% FRESH window. '
        'Missing identities, loss reports, missing state evidence, monitor gaps, live/new sticky bits, '
        'or failed process/settings checks exclude a run. Unreported sends remain separate from losses/skips/overwrites.\n')
    return runs, conditions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    args = parser.parse_args()
    runs, _ = write_summary(args.campaign)
    print(f"{EVIDENCE}; {sum(r['valid'] for r in runs)}/{len(runs)} valid; {args.campaign / 'summary'}")
    return 0 if all(r['valid'] for r in runs) else 1


if __name__ == '__main__':
    sys.exit(main())
