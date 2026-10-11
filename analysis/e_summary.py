#!/usr/bin/env python3
"""E1/E2/E3 campaign reports, standard library only. No illustrative results."""
import argparse
import csv
import json
import math
import statistics
from pathlib import Path
import sys

import pipeline_summary as pipeline

EVIDENCE = 'MEASURED; software timestamps; pty link; no physical UART, no MCU'
COLUMNS = {
    'E1': ['Condition', 'Service latency', 'Delivery latency', 'CPU', 'RAM', 'Drops', 'Overflows', 'Exact load'],
    'E2': ['Profile', 'Service latency', 'Delivery latency', 'CPU', 'RAM', 'Drops', 'Overflows', 'Exact load'],
    'E3': ['Policy', 'Time-average AoI', 'Peak AoI', 'Age-violation time', 'Deadline misses',
           'Generated count', 'Delivered count', 'Replaced count'],
}


def read_json(path):
    return json.loads(path.read_text())


def throttle(value):
    return int(str(value), 0)


def validity(run):
    """Historical sticky flags are allowed; live or newly sticky flags are not."""
    reasons = []
    try:
        before, after = [throttle(read_json(run / name)['throttled'])
                         for name in ('meta_before.json', 'meta_after.json')]
        records = pipeline.rows(run / 'thermal.csv')
        flags = [throttle(r['throttled']) for r in records]
        if not flags:
            raise ValueError('empty monitor')
        if any(v & 0xF for v in [before, after] + flags):
            reasons.append('live throttling/power bits (0xF)')
        if (after & ~before) & 0xFFFF0000:
            reasons.append('new sticky throttling/power bits')
        if any((v & ~before) & 0xFFFF0000 for v in flags):
            reasons.append('new sticky bits during monitor')
        if any(not r.get('ext5v_v') or not r.get('temp_millic') or not r.get('cpu0_khz') for r in records):
            reasons.append('incomplete power/thermal telemetry')
        else:
            if any(not math.isfinite(float(r[k])) for r in records for k in ('ext5v_v', 'temp_millic', 'cpu0_khz')):
                reasons.append('nonfinite power/thermal telemetry')
            if any(float(r['ext5v_v']) <= 0 or float(r['cpu0_khz']) <= 0 for r in records):
                reasons.append('invalid voltage/frequency telemetry')
        if (run / 'exit_code').read_text().strip() != '0':
            reasons.append('pipeline failed')
        if read_json(run / 'execution.json').get('stressor_ok') is not True:
            reasons.append('stressor failed or ended early')
        if read_json(run / 'execution.json').get('settings_ok') is not True:
            reasons.append('scheduling/affinity/mlock verification failed')
        if read_json(run / 'execution.json').get('monitor_ok') is not True:
            reasons.append('monitor failed or did not stop')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        reasons.append(f'incomplete validity evidence: {exc}')
    return ('INVALID: ' + '; '.join(reasons)) if reasons else 'OK'


def held_age(events, start, end):
    """Integrate piecewise-linear freshest delivered age, including the final tail.

    Before the first informative delivery age is undefined. Report that interval
    explicitly; average denominator is the initialized interval, never zero-fill.
    """
    latest = None
    cursor = start
    area = 0.0
    peak = 0.0
    covered = 0
    violations = {100: 0.0, 150: 0.0}

    def segment(stop):
        nonlocal area, peak, covered, cursor
        if latest is not None and stop > cursor:
            a, b = cursor - latest, stop - latest
            area += (a + b) * (stop - cursor) / 2
            peak = max(peak, b)
            covered += stop - cursor
            for threshold in violations:
                violations[threshold] += max(0, stop - max(cursor, latest + threshold * 1_000_000))
        cursor = stop

    for reception, generated in sorted(events):
        if reception > end:
            break
        if reception < start:
            latest = generated if latest is None else max(latest, generated)
            continue
        segment(reception)
        latest = generated if latest is None else max(latest, generated)
        peak = max(peak, reception - latest)
    segment(end)
    return dict(aoi_time_average_ms=area / covered / 1e6 if covered else None,
                aoi_peak_ms=peak / 1e6 if covered else None,
                initialized_seconds=covered / 1e9,
                uninitialized_seconds=(end - start - covered) / 1e9,
                violation_100_seconds=violations[100] / 1e9,
                violation_150_seconds=violations[150] / 1e9)


def summarize_run(run):
    config = read_json(run / 'condition.json')
    result = dict(config, run=run.name, validity=validity(run))
    result['valid'] = result['validity'] == 'OK'
    if not result['valid']:
        return result
    p = run / 'pipeline'
    try:
        report = pipeline.summarize(p, state='OK')
        if read_json(p / 'config.json').get('serial'):
            raise ValueError('campaign requires pty receiver')
        metrics = report['latency_us']
        for label, key in [('service', 'input_to_done_us'), ('delivery', 'aoi_at_reception_us'),
                           ('dispatch', 'done_to_send_us')]:
            for stat in ('p50', 'p99', 'max'):
                value = metrics[key][stat]
                if value is None:
                    raise ValueError(f'no {label} samples')
                result[f'{label}_{stat}_ms'] = value / 1000
        counts = report['counts']
        for key in ('source_generated', 'source_ipc_dropped', 'infer_completed', 'infer_ipc_dropped',
                    'rx_received', 'bridge_overwritten', 'bridge_queue_dropped', 'bridge_discarded_on_stop',
                    'end_to_end_missing', 'bridge_to_rx_missing', 'rx_crc_errors'):
            if counts[key] is None:
                raise ValueError(f'missing count: {key}')
            result[key] = counts[key]
        result['drops'] = counts['source_ipc_dropped'] + counts['infer_ipc_dropped'] + counts['bridge_queue_dropped']
        result['overflows'] = counts['bridge_queue_dropped']
        rx = pipeline.rows(p / 'rx.csv')
        events = [(int(r['t_rx_ns']), int(r['t_input_ns'])) for r in rx
                  if r['type'] == 'INFERENCE' and r['crc_ok'] == '1']
        result['deadline_denominator'] = len(events)
        for threshold in (100, 150):
            misses = sum(tr - ti > threshold * 1_000_000 for tr, ti in events)
            result[f'misses_{threshold}'] = misses
            result[f'miss_rate_{threshold}'] = misses / len(events) if events else None
        start, end = [int((p / name).read_text()) for name in ('window_start_ns', 'window_end_ns')]
        if end <= start:
            raise ValueError('invalid observation window')
        result.update(held_age(events, start, end))
        resources = pipeline.rows(run / 'resources.csv')
        cpu = [float(r['cpu_percent']) for r in resources if r['cpu_percent']]
        ram = [float(r['rss_mib']) for r in resources if r['rss_mib']]
        if not cpu or not ram:
            raise ValueError('missing CPU/RAM samples')
        result['cpu_percent'] = statistics.median(cpu)
        result['rss_mib'] = max(ram)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.update(valid=False, validity=f'INVALID: analysis: {exc}')
    return result


def aggregate(runs):
    groups = {}
    for r in runs:
        key = tuple(r[k] for k in ('experiment', 'profile', 'stressor', 'policy'))
        groups.setdefault(key, []).append(r)
    output = []
    for key, members in sorted(groups.items()):
        valid = [r for r in members if r['valid']]
        row = dict(zip(('experiment', 'profile', 'stressor', 'policy'), key))
        row.update(valid_reps=len(valid), total_reps=len(members), exact_load=members[0]['exact_load'])
        for field in sorted({k for r in valid for k, v in r.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}):
            if field == 'repetition':
                continue
            values = [r[field] for r in valid if r.get(field) is not None]
            row[field] = max(values) if field.endswith('_max_ms') or field in ('aoi_peak_ms', 'rss_mib') else statistics.median(values)
        output.append(row)
    return output


def csv_write(path, records, columns=None):
    columns = columns or sorted({k for r in records for k in r})
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def fmt(value):
    return 'unavailable' if value is None else f'{value:.4g}' if isinstance(value, float) else str(value)


def table_row(r):
    def latency(prefix):
        return '/'.join(fmt(r.get(f'{prefix}_{s}_ms')) for s in ('p50', 'p99', 'max')) + ' ms'
    if r['experiment'] in ('E1', 'E2'):
        return dict(zip(COLUMNS[r['experiment']], [r['stressor'] if r['experiment'] == 'E1' else r['profile'],
                    latency('service'), latency('delivery'), fmt(r.get('cpu_percent')) + ' %',
                    fmt(r.get('rss_mib')) + ' MiB', fmt(r.get('drops')), fmt(r.get('overflows')), r['exact_load']]))
    return dict(zip(COLUMNS['E3'], [r['policy'], fmt(r.get('aoi_time_average_ms')) + ' ms (initialized)',
                fmt(r.get('aoi_peak_ms')) + ' ms',
                f"{fmt(r.get('violation_100_seconds'))}/{fmt(r.get('violation_150_seconds'))} s",
                f"{fmt(r.get('misses_100'))}/{fmt(r.get('misses_150'))} of {fmt(r.get('deadline_denominator'))}",
                fmt(r.get('source_generated')), fmt(r.get('rx_received')), fmt(r.get('bridge_overwritten'))]))


def latex_escape(value):
    escapes = {'\\': r'\textbackslash{}', '_': r'\_', '%': r'\%', '&': r'\&', '#': r'\#',
               '$': r'\$', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(escapes.get(c, c) for c in str(value))


def latex_table(records, columns, per_run=False):
    lines = ['% ' + EVIDENCE, r'\par\noindent ' + latex_escape(EVIDENCE) + r'\par',
             r'\begin{tabular}{' + 'l' * len(columns) + '}', r'\toprule',
             ' & '.join(latex_escape(c) for c in columns) + r' \\', r'\midrule']
    for data in records:
        # Excluded per-run measurements remain in the manifest/raw files.
        view = data if not per_run or data['valid'] else {k: data[k] for k in
                ('experiment', 'profile', 'stressor', 'policy', 'exact_load')}
        row = table_row(view)
        label = (f"{data['run']}; {data['validity']}" if per_run else
                 f"{data['profile']} / {data['stressor']}; valid reps {data['valid_reps']}/{data['total_reps']}")
        lines.append(r'\multicolumn{' + str(len(columns)) + r'}{l}{' + latex_escape(label) + r'} \\')
        lines.append(' & '.join(latex_escape(row[c]) for c in columns) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}']
    return '\n'.join(lines) + '\n'


def write_summary(campaign):
    runs = [summarize_run(p.parent) for p in sorted(campaign.glob('E*/condition.json'))]
    if not runs:
        raise ValueError('no campaign runs found')
    conditions = aggregate(runs)
    dest = campaign / 'summary'
    dest.mkdir(exist_ok=True)
    csv_write(dest / 'per_run.csv', runs)
    csv_write(dest / 'per_condition.csv', conditions)
    csv_write(dest / 'excluded.csv', [r for r in runs if not r['valid']],
              ['run', 'experiment', 'profile', 'stressor', 'policy', 'validity'])
    for experiment, columns in COLUMNS.items():
        members = [r for r in conditions if r['experiment'] == experiment]
        # E2/E3 keep identical deck columns; partition matched stressors in LaTeX.
        for kind, records in [('per_run', [r for r in runs if r['experiment'] == experiment]),
                              ('per_condition', members)]:
            csv_write(dest / f'{experiment}_{kind}.csv', records)
            (dest / f'{experiment}_{kind}.tex').write_text(latex_table(records, columns, per_run=kind == 'per_run'))
        table = [table_row(r) for r in members]
        csv_write(dest / f'{experiment}_table.csv', table, columns)
        (dest / f'{experiment}.tex').write_text(latex_table(members, columns))
    (dest / 'README.md').write_text(EVIDENCE + '\n\n'
        'Service = input-to-inference completion (includes input queue/pre/postprocessing). Delivery = input-to-reception. '
        'Latency cells: median of per-run P50 / median of per-run P99 / maximum observed maximum; nearest-rank per run. '
        'Other condition scalars/counts/rates: median per run; peak AoI and RAM: maximum. Counts are not pooled. '
        'CPU = median aggregate source/inference/bridge utilization (100% = one core); RAM = peak summed RSS. '
        'Drops = source/inference IPC drops + bridge queue drops; overflows = bridge queue drops (same events). '
        'Replaced = bridge overwritten; shutdown discards and missing deliveries are separately retained.\n\n'
        'E3 held-value AoI follows the freshest informative delivery, integrates stalls and final tail in the declared RAW-clock window. '
        'Before the first informative delivery AoI is undefined: uninitialized_seconds is retained; the time-average denominator '
        'is initialized_seconds. No zero-filled full-window AoI is claimed. '
        'Age-violation time columns use strict >100/>150 ms. Deadline misses are reception AoI >100/>150 ms, '
        'denominator all CRC-valid inference receptions including drain; missing deliveries are separately reported, not counted as receptions. '
        'Source period is 100 ms; measurement window excludes shutdown drain.\n\n'
        'Validity requires complete monitor and applied-settings evidence, successful pipeline/stressors, no live bits (0xF), '
        'and no new sticky bits. Pre-existing sticky flags alone do not exclude a run. Exclusions remain on disk. '
        'CSV tables retain the exact deck columns; E2/E3 CSV row order and condition identities are in per_condition.csv; '
        'LaTeX adds matched-condition labels and valid repeat counts. Three repeats are the ticket default, '
        'below the deck acceptance gate of five valid repeats. P2 quotas: not done.\n')
    return runs, conditions


def worst_stressors(campaign):
    runs = [summarize_run(p.parent) for p in campaign.glob('E1*/condition.json')]
    rows = [r for r in aggregate(runs) if r['valid_reps'] and r['stressor'] != 'B0_idle']
    rows.sort(key=lambda r: (-r['delivery_p99_ms'], -r['delivery_max_ms'], r['stressor']))
    if len(rows) < 2:
        raise ValueError('E1 requires at least two stressors with valid runs for ranking')
    return [r['stressor'] for r in rows[:2]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    args = parser.parse_args()
    try:
        runs, _ = write_summary(args.campaign)
        print(f"{EVIDENCE}; {sum(r['valid'] for r in runs)}/{len(runs)} valid runs; {args.campaign / 'summary'}")
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f'e_summary: {exc}\n')


if __name__ == '__main__':
    main()
