#!/usr/bin/env python3
"""Read-only replay of RERUN_UPDATE_MAP R1–R6; no acquisition or document edits."""
import argparse
import ast
import binascii
import bisect
import csv
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'analysis'))
import cyclictest_summary as cyclic
import e_summary as pipeline
import e4_summary as e4

DATE = '2026-10-20'
RES = REPO / 'results'
ORIGINAL = {
    'P0': RES / '2026-10-11_cyclictest/20261008T091937Z_cyc_P0',
    'P1': RES / '2026-10-11_cyclictest/20261008T091937Z_cyc_P1',
    'E123': RES / '2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx',
    'E3B': RES / '2026-10-12_e3b_input_latest/20261012T091415Z_e3b',
    'E4': RES / '2026-10-12_e4_faults/20261012T093526Z_e4',
    'LA': RES / '2026-10-12_logic_analyzer',
}
LOADS = ['B0_idle', 'CPU_c23', 'B1_stream_c2', 'C1_cache2M_c2', 'B2_memrate_c23']
NAVY, TEAL, FAULT = '#1F3A5F', '#2A9D8F', '#E76F51'


def read_json(path):
    return json.loads(path.read_text())


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def export_csv(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    pipeline.csv_write(path, records)


def number(value):
    if value is None or value == '':
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('nonfinite metric')
    return result


def cell(value=None, valid=0, total=0, status='ok', **extra):
    return dict(value=value, valid=valid, total=total, status=status, **extra)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def deck_functions():
    # Load only pure function definitions; never execute the fixed-path builder.
    path = REPO / 'submission/defense/build_evidence.py'
    tree = ast.parse(path.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name in ('decode', 'event_values')]
    namespace = dict(bisect=bisect, binascii=binascii, read=rows, ROOT=REPO)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def timer(source, dest):
    dirs = sorted(p for p in source.iterdir() if p.is_dir() and cyclic.RUN_NAME.fullmatch(p.name))
    if not dirs:
        raise ValueError('no condition_rN directories')
    records = []
    for p in dirs:
        try:
            records.append(cyclic.summarize_run(p))
        except Exception as exc:
            records.append(dict(condition=cyclic.RUN_NAME.fullmatch(p.name).group(1),
                                run=p.name, status='INVALID', reason=str(exc)))
    dest.mkdir(parents=True)
    # Keep standard analyzer schema for malformed records too.
    records = [{k: r.get(k) for k in cyclic.RUN_FIELDS} for r in records]
    cyclic.write_outputs(dest, records)
    return records, cyclic.aggregate_runs(records)


def software(source, dest):
    records = []
    for p in sorted(source.glob('E*/condition.json')):
        try:
            records.append(pipeline.summarize_run(p.parent))
        except Exception as exc:
            records.append(dict(run=p.parent.name, experiment=p.parent.name.split('_')[0],
                                profile='unknown', stressor='unknown', policy='unknown',
                                input_policy='unknown', exact_load='unknown', valid=False,
                                validity='INVALID: ' + str(exc)))
    if not records:
        raise ValueError('no E*/condition.json')
    conditions = pipeline.aggregate(records)
    dest.mkdir(parents=True)
    export_csv(dest / 'per_run.csv', records)
    export_csv(dest / 'per_condition.csv', conditions)
    export_csv(dest / 'excluded.csv', [r for r in records if not r['valid']])
    for exp in pipeline.COLUMNS:
        for kind, data in [('per_run', records), ('per_condition', conditions)]:
            members = [r for r in data if r['experiment'] == exp]
            export_csv(dest / f'{exp}_{kind}.csv', members)
            (dest / f'{exp}_{kind}.tex').write_text(pipeline.latex_table(
                members, pipeline.COLUMNS[exp], per_run=kind == 'per_run'))
        members = [r for r in conditions if r['experiment'] == exp]
        export_csv(dest / f'{exp}_table.csv', [pipeline.table_row(r) for r in members])
    return records, conditions


def faults(source, dest):
    manifest = source / 'campaign.json'
    rms = e4.finite(read_json(manifest).get('rms_bound_us', 200)) if manifest.exists() else 200
    if rms <= 0:
        raise ValueError('RMS bound must be positive')
    configured, provenance = e4.thresholds(
        source / 'supervisor_thresholds.json' if (source / 'supervisor_thresholds.json').exists() else None,
        REPO / 'stm32/include')
    records = []
    for p in sorted(source.glob('F*/run.json')):
        try:
            records.append(e4.summarize_run(p.parent, rms, 5))
        except Exception as exc:
            records.append(dict(run=p.parent.name, fault=p.parent.name.split('-')[0],
                                validity='INVALID', reasons=str(exc),
                                **{k: None for k in e4.METRICS}))
    if not records:
        raise ValueError('no F*/run.json')
    table = e4.fault_table(records, configured, provenance)
    export_csv(dest / 'e4_runs.csv', records)
    export_csv(dest / 'e4_faults.csv', table)
    (dest / 'e4_faults.tex').write_text(e4.latex(table))
    dump(dest / 'e4_thresholds.json', dict(values=configured, source=provenance))
    return records, table


def analyzer(batches, dest):
    la = module('rerun_la', REPO / 'tools/la/la_analyze.py')
    decode = deck_functions()['decode']
    records = []
    for batch in batches:
        captures = {p.parent for p in batch.glob('*/capture.vcd')}
        if (batch / 'la_e4.csv').exists():
            captures.update(batch / r['capture'] for r in rows(batch / 'la_e4.csv'))
        for cap in sorted(captures):
            rec = dict(capture=str(cap.resolve()), batch=batch.name)
            try:
                runs = list(cap.glob('pi/F*/run.json'))
                if len(runs) != 1:
                    raise ValueError('expected one pi/F*/run.json')
                trace = la.read_trace(cap / 'capture.vcd')
                rec.update(la.analyze(trace, runs[0].parent))
                frames = decode(trace, rec['t_safe_s']) if rec['t_safe_s'] is not None else []
                frame = frames[-1] if frames else None
                end = rec['t_last_uart_byte_s']
                rec['last_frame_type'] = (frame['type'] if frame and end is not None
                                          and abs(frame['end'] - end) < 1e-9 else None)
                rec['matching'] = rec['last_frame_type'] == 1
                rec['analysis_status'] = ('ok' if rec['delta_safe_us'] is not None
                                          and not rec['comparison'].startswith('INVALID')
                                          else 'failed: ' + rec['comparison'] + '; ' + rec['status'])
            except Exception as exc:
                rec['analysis_status'] = 'failed: ' + str(exc)
            records.append(rec)
    if not records:
        raise ValueError('no captures')
    dump(dest / 'records.json', records)
    dump(dest / 'classified.json', records)
    key = ['# Analyzer capture key', '',
           '| Capture | Last CRC-valid frame | Matching heartbeat | Delta (us) | Status |',
           '|---|---|---|---|---|']
    for r in records:
        key.append('| ' + ' | '.join(str(v).replace('|', '/') for v in
                   (r['capture'], r.get('last_frame_type'), r.get('matching'),
                    r.get('delta_safe_us'), r['analysis_status'])) + ' |')
    (dest / 'LA_capture_key.md').write_text('\n'.join(key) + '\n')
    for name in sorted({r['batch'] for r in records}):
        export_csv(dest / name / 'la_e4.csv', [r for r in records if r['batch'] == name])
    return records


def timer_metrics(conditions):
    result = {}
    for r in conditions:
        for metric in ('p50_us', 'p99_us', 'max_us'):
            n = int(r['runs'])
            result[r['condition'] + ' / ' + metric] = cell(number(r.get(metric)), n,
                n + int(r['invalid_runs']), 'ok' if n else 'failed: no valid runs')
    return result


def software_metrics(conditions, exp):
    result = {}
    keys = ('service_p50_ms', 'service_p99_ms', 'delivery_p50_ms', 'delivery_p99_ms',
            'delivery_max_ms', 'aoi_time_average_ms', 'aoi_peak_ms', 'bridge_overwritten',
            'source_generated', 'rx_received', 'drops', 'overflows', 'cpu_percent', 'rss_mib')
    for r in conditions:
        if r['experiment'] != exp:
            continue
        identity = ' / '.join(r.get(k, 'fifo') for k in ('profile', 'stressor', 'input_policy', 'policy'))
        for key in keys:
            n, total = int(r['valid_reps']), int(r['total_reps'])
            result[identity + ' / ' + key] = cell(number(r.get(key)), n, total,
                'ok' if n else 'failed: no valid runs')
    return result


def fault_metrics(records, historical=False):
    result = {}
    for fault in ('F1', 'F2', 'F3', 'F4', 'F5'):
        members = [r for r in records if r['fault'] == fault]
        valid = [r for r in members if r['validity'] == 'VALID']
        for domain, keys in [('local', ('detection_mcu_us', 'failsafe_mcu_us')),
                             ('mapped', ('detection_us', 'failsafe_us'))]:
            for prefix, key in zip(('first', 'failsafe'), keys):
                values = [(r.get(f'{prefix}_{domain}_ms') if historical else
                           number(r.get(key)) / 1000 if number(r.get(key)) is not None else None)
                          for r in valid]
                values = [v for v in values if v is not None]
                for stat, value in zip(('p50', 'p95', 'max'), e4.distribution(values)):
                    result[f'{fault} / {prefix}_{domain}_{stat}_ms'] = cell(value, len(valid), len(members),
                        'ok' if values else 'failed: no observed valid transitions', samples=len(values))
                for stat, value in [('min', min(values) if values else None), ('range_max', max(values) if values else None)]:
                    result[f'{fault} / {prefix}_{domain}_{stat}_ms'] = cell(value, len(valid), len(members), samples=len(values))
    return result


def la_metrics(records):
    valid = [r for r in records if r.get('analysis_status', 'ok') == 'ok']
    matching = [r for r in valid if r.get('matching')]
    result = {'final HEARTBEAT / captures': cell(len(matching), len(valid), len(records),
              qualification='Frame matching is not collection validity; retained LA is FLAGGED')}
    for key, members in [('matched_delta_us', matching), ('marker_safe_us', valid)]:
        values = [r[key if key != 'matched_delta_us' else 'delta_safe_us'] for r in members
                  if r.get(key if key != 'matched_delta_us' else 'delta_safe_us') is not None]
        for stat, value in [('min', min(values) if values else None), ('max', max(values) if values else None)]:
            result[key + ' / ' + stat] = cell(value, len(valid), len(records), samples=len(values))
    for fault in ('F1', 'F2', 'F4'):
        values = [r['marker_safe_us'] / 1000 for r in valid
                  if Path(r['capture']).name.startswith(fault) and r.get('marker_safe_us') is not None]
        for stat, value in [('min', min(values) if values else None), ('max', max(values) if values else None)]:
            result[f'{fault} / marker_safe_{stat}_ms'] = cell(value, len(valid), len(records), samples=len(values))
    return result


def historical_faults():
    functions = deck_functions()
    result = []
    for r in rows(ORIGINAL['E4'] / 'e4_runs.csv'):
        if r['fault'] == 'F5':
            continue  # original F5 NOT_DONE; separate short windows supplied the deck
        run = ORIGINAL['E4'] / r['run']
        result.append(functions['event_values'](run, read_json(run / 'run.json'), r['validity'],
                                               'original E4', r if r['validity'] == 'VALID' else None))
    for folder, fault in [('2026-10-12_f4_extra', 'F4'), ('2026-10-12_f5_stale', 'F5')]:
        for p in sorted((RES / folder).rglob('run.json')):
            meta = read_json(p)
            if meta.get('fault') != fault:
                continue
            valid = meta['status'] == 'COMPLETE'
            if valid:
                power = rows(p.parent / 'power.csv')
                baseline = int(power[0]['throttled'], 0)
                valid = not any(int(r['throttled'], 0) & 15 or
                    (int(r['throttled'], 0) & 0xf0000) & ~baseline for r in power)
                fits = [float(r['rms_residual_us']) for r in rows(p.parent / 'pipeline/echo.csv')
                        if r['accepted'] == '1' and r['rms_residual_us']]
                valid = valid and bool(fits) and max(fits) <= 200
            result.append(functions['event_values'](p.parent, meta, 'VALID' if valid else 'INVALID',
                                                   'short window; no recovery qualification'))
    return result


def plot_outputs(out, data):
    try:
        import matplotlib
    except ImportError:
        return 'not run: matplotlib is not installed'
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Avenir Next', 'DejaVu Sans'],
        'font.size': 17, 'axes.spines.top': False, 'axes.spines.right': False,
        'axes.labelcolor': '#22262B', 'text.color': '#22262B',
        'figure.facecolor': '#FAFAF7', 'axes.facecolor': '#FAFAF7', 'pdf.fonttype': 42})
    images = out / 'images'
    images.mkdir()
    written = []

    def save(fig, name):
        fig.tight_layout(pad=.6)
        fig.savefig(images / (name + '.pdf'), bbox_inches='tight')
        plt.close(fig)
        written.append('images/' + name + '.pdf')

    if any(k in data for k in ('P0', 'P1')):
        fig, ax = plt.subplots(figsize=(11, 3.2))
        for k, color in enumerate((NAVY, TEAL)):
            by = {r['condition'].split('_', 1)[1]: r for r in data.get(f'P{k}', ([], []))[1]}
            values = [number(by.get(load, {}).get('p99_us')) for load in LOADS]
            ax.bar([i + (k - .5) * .34 for i in range(5)],
                   [v if v is not None else math.nan for v in values], .34, label=f'P{k}', color=color)
        ax.set_xticks(range(5), ['Idle', 'CPU', 'Stream', 'Cache', 'Memrate'])
        ax.set_ylabel('Wake-up P99 (µs)')
        if any(p.get('p99_us') for k in ('P0', 'P1') for p in data.get(k, ([], []))[1]):
            ax.set_yscale('log')
        ax.legend(); ax.grid(axis='y', alpha=.18)
        ax.set_title('Re-run ' + DATE); save(fig, 'cyclic')
    for exp in pipeline.COLUMNS:
        conditions = [r for r in data.get('E123', ([], []))[1] if r['experiment'] == exp]
        if not conditions:
            continue
        metric = 'aoi_time_average_ms' if exp == 'E3' else 'delivery_p99_ms'
        values = [number(r.get(metric)) for r in conditions]
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.bar(range(len(values)), [v if v is not None else math.nan for v in values], color=TEAL)
        ax.set_xticks(range(len(values)), [' / '.join(r[k] for k in
                      ('profile', 'stressor', 'input_policy', 'policy')) for r in conditions],
                      rotation=25, ha='right', fontsize=9)
        if any(v is not None and v > 0 for v in values):
            ax.set_yscale('log')
        else:
            ax.text(.5, .5, 'No valid measurements', transform=ax.transAxes, ha='center')
        ax.set_ylabel('Initialized mean AoI (ms)' if exp == 'E3' else 'Delivery P99 (ms)')
        ax.set_title('Re-run ' + DATE); ax.grid(axis='y', alpha=.18); save(fig, exp)
    if 'E4' in data:
        fig, axes = plt.subplots(1, 2, figsize=(12, 3.5))
        styles = {'3': (FAULT, 's'), '9': (NAVY, '^'), '10': (TEAL, 'o')}
        for ax, prefix in zip(axes, ('detection', 'failsafe')):
            for i, fault in enumerate(('F1', 'F2', 'F3', 'F4', 'F5')):
                members = [r for r in data['E4'][0] if r['fault'] == fault and r['validity'] == 'VALID']
                for j, r in enumerate(members):
                    value = number(r.get(prefix + '_mcu_us'))
                    if value is not None:
                        color, marker = styles.get(str(r.get(prefix + '_reason')), ('gray', 'x'))
                        ax.scatter(i + (j - (len(members) - 1) / 2) * .11, value / 1000,
                                   color=color, marker=marker)
            ax.set_xticks(range(5), ['F1', 'F2', 'F3', 'F4', 'F5'])
            ax.set_ylabel('Receipt to event (ms)'); ax.set_title(prefix); ax.grid(alpha=.18)
        handles = [plt.Line2D([], [], color=c, marker=m, linestyle='None', label=label)
                   for (c, m), label in zip(styles.values(), ('3: heartbeat', '9: HOLD', '10: FAILSAFE'))]
        fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, 1.12), ncol=3)
        save(fig, 'E4')
    if 'LA' in data:
        fig, axes = plt.subplots(1, 2, figsize=(12, 3.1))
        for ax, matched, scale in zip(axes, (True, False), (1, 1000)):
            members = [r for r in data['LA'] if r.get('analysis_status') == 'ok' and r['matching'] == matched]
            ax.scatter(range(1, len(members) + 1), [r['delta_safe_us'] / scale for r in members],
                       color=TEAL if matched else NAVY)
            ax.set_title(f'{len(members)} ' + ('final HEARTBEAT' if matched else 'different / undecoded'))
            ax.set_xlabel('Capture index'); ax.set_ylabel('Δ (µs)' if matched else 'Δ (ms)'); ax.grid(alpha=.18)
        save(fig, 'LA')
        la = module('rerun_waveform', REPO / 'tools/la/la_analyze.py')
        for batch in sorted({r['batch'] for r in data['LA']}):
            first = next((r for r in data['LA'] if r['batch'] == batch and r.get('analysis_status') == 'ok'), None)
            if first:
                trace = la.read_trace(Path(first['capture']) / 'capture.vcd')
                fig, ax = plt.subplots(figsize=(12, 4))
                for i, label in enumerate(('PA5', 'PB5', 'UART', 'marker')):
                    ax.step([(t - first['t_marker_rise_s']) * 1000 for t, _ in trace],
                            [pins[i] * .7 + i for _, pins in trace], where='post', label=label)
                ax.set_xlabel('Analyzer time from marker (ms)'); ax.legend()
                fig.tight_layout(pad=.6)
                fig.savefig(out / 'la' / batch / 'la_timing.png', dpi=160)
                save(fig, 'LA_' + batch + '_timing')
    return dict(status='ok', files=written)


def render(summary, out):
    tex = ['% Requires booktabs; UTF-8 (XeLaTeX). Missing observations are never zero.',
           '% Original v1 acceptance differs from current replay gates. See rerun_summary.json.']
    md = ['# Đối chiếu kết quả đo lại — ' + DATE, '',
          'Giữ nguyên dữ liệu gốc. Lượt chấp nhận theo kiểm tra gốc (v1) và đo lại (v2) có thể khác nhau.', '',
          'E4 gốc gộp các cửa sổ ngắn F4/F5; đo lại dùng chiến dịch đầy đủ, có kiểm tra phục hồi. '
          'LA chỉ đối chiếu mốc thời gian, không xác nhận tính hợp lệ của toàn bộ phép đo.', '']
    for name, exp in summary['experiments'].items():
        old, new = exp['original'], exp['rerun']
        old_date = exp['original_date']
        title = f'{name}: Original ({old_date}) vs Re-run {DATE}'
        tex += ['% ' + title, r'\begin{tabular}{@{}lllll@{}}', r'\toprule',
                'Metric & Original (' + old_date + ') & Re-run ' + DATE + r' & Original n/N & Re-run n/N \\', r'\midrule']
        md += ['## ' + name, '', f'| Phép đo / điều kiện | Gốc ({old_date}) | Đo lại {DATE} | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |',
               '|---|---|---|---|---|']
        for key in sorted(set(old) | set(new)) or ['Collection']:
            a = old.get(key, cell(status=exp.get('original_status', 'not run: unmatched condition')))
            b = new.get(key, cell(status=exp['status'] if exp['status'] != 'ok' else 'not run: unmatched condition'))
            def fmt(c):
                if c['value'] is None:
                    return c['status'] if c['status'] != 'ok' else 'unavailable'
                return f"{c['value']:.6g}" if isinstance(c['value'], (int, float)) else str(c['value'])
            line = [key, fmt(a), fmt(b), f"{a['valid']}/{a['total']}", f"{b['valid']}/{b['total']}"]
            tex.append(' & '.join(pipeline.latex_escape(v) for v in line) + r' \\')
            md.append('| ' + ' | '.join(v.replace('|', '/') for v in line) + ' |')
        tex += [r'\bottomrule', r'\end{tabular}', '']
        md += ['', 'Trạng thái: ' + exp['status'] + '.', '']
    (out / 'rerun_compare.tex').write_text('\n'.join(tex) + '\n')
    (out / 'rerun_compare_vi.md').write_text('\n'.join(md) + '\n')


def build(root, out):
    root, out = root.resolve(), out.resolve()
    sources = [root, RES.resolve()]
    sources += [p.resolve() for p in root.glob('*/*') if p.is_dir()]
    if any(out == p or p in out.parents for p in sources):
        raise ValueError('output must be outside raw root, all linked run directories, and original results')
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError('output directory must be empty (prevents stale results and symlink writes)')
    summary = dict(schema_version=1, rerun_date=DATE, root=str(root),
        notes=['Original v1 summaries are retained; reruns use current v2 acceptance.',
               'R3 physical E3 and R7 standalone inference are not repeated by the supplied layout.',
               'E4 original includes short F4/F5 windows; new full-campaign acceptance is separate.',
               'Counts are independent runs; samples separately counts observed transitions/captures.'],
        original_sources={k: str(v) for k, v in ORIGINAL.items()},
        parts={}, experiments={})
    data = {}

    def part(name, source, callback):
        if not source.is_dir():
            summary['parts'][name] = dict(status='not run', source=str(source), valid=0, total=0)
            return
        try:
            data[name] = callback()
            summary['parts'][name] = dict(status='ok', source=str(source))
        except Exception as exc:
            summary['parts'][name] = dict(status='failed: ' + str(exc), source=str(source), valid=0, total=1 if name == 'PS1' else 0)

    for k in ('P0', 'P1'):
        source = root / 'P1' / ('cyclictest_' + k.lower())
        part(k, source, lambda s=source, k=k: timer(s, out / ('cyclic-' + k)))
    source = root / 'E123/e-onnx'
    part('E123', source, lambda: software(source, out / 'pipeline'))
    source = root / 'E4/e4-real'
    part('E4', source, lambda: faults(source, out / 'e4'))
    source = root / 'LA'
    part('LA', source, lambda: analyzer([source / f for f in ('F1', 'F2', 'F4')], out / 'la'))
    source = root / 'PS1/link60_fixed'
    def smoke():
        report = read_json(source / 'summary.json')
        dump(out / 'ps1/summary.json', report)
        if (source / 'exit_code').exists() and (source / 'exit_code').read_text().strip() != '0':
            raise ValueError('pipeline exit_code is not zero')
        if report.get('validity') != 'OK' or report.get('excluded'):
            raise ValueError(report.get('validity', 'missing validity'))
        config = read_json(source / 'config.json')
        if not config.get('serial'):
            raise ValueError('PS1 requires real UART config')
        return report
    part('PS1', source, smoke)

    def experiment(name, date, original_callback, new_metrics, part_name):
        exp = dict(original_date=date, status=summary['parts'].get(part_name, {}).get('status', 'not run'),
                   original={}, rerun=new_metrics)
        try:
            exp['original'] = original_callback()
        except Exception as exc:
            exp['original_status'] = 'failed: ' + str(exc)
        summary['experiments'][name] = exp

    for k in ('P0', 'P1'):
        experiment('cyclic-' + k, '2026-10-11',
                   lambda k=k: timer_metrics(rows(ORIGINAL[k] / 'summary_by_condition.csv')),
                   timer_metrics(data[k][1]) if k in data else {}, k)
    for exp in pipeline.COLUMNS:
        original_path = ORIGINAL['E3B' if exp == 'E3B' else 'E123'] / 'summary' / (exp + '_per_condition.csv')
        experiment(exp, '2026-10-12' if exp == 'E3B' else '2026-10-11',
                   lambda p=original_path, exp=exp: software_metrics(rows(p), exp),
                   software_metrics(data['E123'][1], exp) if 'E123' in data else {}, 'E123')
    experiment('E4', '2026-10-12', lambda: fault_metrics(historical_faults(), historical=True),
               fault_metrics(data['E4'][0]) if 'E4' in data else {}, 'E4')
    # Recompute original raw VCDs into output too; include check_F2 as the map requires.
    experiment('LA', '2026-10-12', lambda: la_metrics(analyzer(
        sorted(p for p in ORIGINAL['LA'].iterdir() if (p / 'la_e4.csv').exists()), out / 'original-la')),
        la_metrics(data['LA']) if 'LA' in data else {}, 'LA')
    smoke_metrics = {}
    if 'PS1' in data:
        report = data['PS1']
        smoke_metrics.update({k: cell(v, 1, 1) for k, v in report.get('counts', {}).items()})
        for metric, distribution in report.get('latency_us', {}).items():
            for stat in ('p50', 'p99', 'max'):
                smoke_metrics[metric + ' / ' + stat] = cell(distribution.get(stat), 1, 1,
                                                          samples=distribution.get('n'))
    experiment('PS1', 'not acquired', lambda: {}, smoke_metrics, 'PS1')
    for name in ('Standalone inference', 'Physical E3'):
        summary['experiments'][name] = dict(original_date='2026-10-11' if name.startswith('Standalone') else '2026-10-12',
            status='not run: not repeated by this layout', original={}, rerun={})
    # Include historical standalone P50/P99/max and accepted counts without inventing a rerun.
    inf = summary['experiments']['Standalone inference']['original']
    try:
        for line in (RES / '2026-10-11_inference_baseline/SUMMARY.md').read_text().splitlines():
            if line.startswith('| idle |') or line.startswith('| cpu stress'):
                values = [v.strip() for v in line.strip('|').split('|')]
                for key, value in zip(('p50_ms', 'p99_ms', 'max_ms'), values[3:6]):
                    inf[' / '.join(values[:2]) + ' / ' + key] = cell(float(value), int(values[2]), 3)
    except Exception as exc:
        summary['experiments']['Standalone inference']['original_status'] = 'failed: ' + str(exc)
    try:
        original_u = RES / '2026-10-12_e3_real_uart/20261012T105039Z_e3real/summary/per_run.csv'
        original_rows = rows(original_u)
        n = sum(r['valid'] == 'True' for r in original_rows)
        summary['experiments']['Physical E3']['original']['Accepted runs'] = cell(n, n, len(original_rows))
    except Exception as exc:
        summary['experiments']['Physical E3']['original_status'] = 'failed: ' + str(exc)
    for name, value in data.items():
        if name in ('P0', 'P1', 'E123', 'E4'):
            records = value[0]
            valid = sum(r.get('status') == 'VALID' or r.get('valid') is True or r.get('validity') == 'VALID' for r in records)
        elif name == 'LA':
            records = value
            valid = sum(r.get('analysis_status') == 'ok' for r in records)
        else:
            records, valid = [value], 1
        summary['parts'][name].update(valid=valid, total=len(records), records=records)
        if not valid:
            summary['parts'][name]['status'] = 'failed: no valid runs'
    for name, exp in summary['experiments'].items():
        part_name = 'E123' if name in pipeline.COLUMNS else name.removeprefix('cyclic-')
        if part_name in summary['parts']:
            exp['status'] = summary['parts'][part_name]['status']
    for exp in pipeline.COLUMNS:
        if 'E123' in data and not any(r['experiment'] == exp for r in data['E123'][0]):
            summary['experiments'][exp]['status'] = 'not run'
    if 'E4' in data:
        for domain, metrics in [('local', ('detection_mcu_us', 'failsafe_mcu_us')),
                                ('mapped', ('detection_us', 'failsafe_us'))]:
            lines = [r'\begin{tabular}{@{}llll@{}}', r'\toprule',
                     r'Fault & Valid/total & First P50/P95/max (ms) & Safe P50/P95/max (ms) \\', r'\midrule']
            for fault in ('F1', 'F2', 'F3', 'F4', 'F5'):
                members = [r for r in data['E4'][0] if r['fault'] == fault]
                valid = [r for r in members if r['validity'] == 'VALID']
                cells = []
                for metric in metrics:
                    values = [number(r.get(metric)) / 1000 for r in valid if number(r.get(metric)) is not None]
                    cells.append(' / '.join(f'{v:.3f}' for v in e4.distribution(values)) if values else 'unavailable')
                lines.append(' & '.join([fault, f'{len(valid)}/{len(members)}'] + cells) + r' \\')
            (out / f'E4_{domain}.tex').write_text('\n'.join(lines + [r'\bottomrule', r'\end{tabular}']) + '\n')
    try:
        summary['plots'] = plot_outputs(out, data)
    except Exception as exc:
        summary['plots'] = 'failed: ' + str(exc)
    dump(out / 'rerun_summary.json', summary)
    render(summary, out)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--outdir', required=True, type=Path)
    args = parser.parse_args()
    # matplotlib and imports must never create caches in raw or tracked directories.
    with tempfile.TemporaryDirectory(prefix='rerun-mpl-') as cache:
        os.environ['MPLCONFIGDIR'] = cache
        os.environ['XDG_CACHE_HOME'] = cache
        try:
            summary = build(args.root, args.outdir)
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    for name, part in summary['parts'].items():
        print(f"{name}: {part['status']} ({part.get('valid', 0)}/{part.get('total', 0)})")
    print('Reports: ' + str(args.outdir.resolve()))


if __name__ == '__main__':
    main()
