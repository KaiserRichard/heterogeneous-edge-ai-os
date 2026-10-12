#!/usr/bin/env python3
"""Independent E4 hardware timebase cross-check. UNVERIFIED ON HARDWARE."""
import argparse
import bisect
import csv
import json
import re
from pathlib import Path


def read_trace(path):
    """Return sparse atomic snapshots (seconds, D0..D3); reject unknown pins."""
    rows = []
    if path.suffix.lower() == '.csv':
        with path.open() as stream:
            for row in csv.DictReader(stream):
                rows.append((float(row['time']), tuple(int(row[f'D{i}']) for i in range(4))))
    else:
        scale, codes, pins, tick = None, {}, [None]*4, 0
        header = True
        pending = False
        def flush():
            if pending:
                rows.append((tick * scale, tuple(pins)))
        with path.open() as stream:
            # VCD tokens permit multiline timescale/definitions.
            tokens = (word for line in stream for word in line.split())
            for token in tokens:
                if token == '$timescale':
                    value = next(tokens)
                    match = re.fullmatch(r'(\d+)(s|ms|us|ns|ps)', value)
                    if match:
                        number, unit = match.groups()
                    else:
                        number, unit = value, next(tokens)
                    scale = int(number) * {'s':1, 'ms':1e-3, 'us':1e-6, 'ns':1e-9, 'ps':1e-12}[unit]
                elif token == '$var':
                    kind, width, code, name = [next(tokens) for _ in range(4)]
                    if name in [f'D{i}' for i in range(4)] and width == '1':
                        codes[code] = int(name[1])
                elif token == '$enddefinitions':
                    header = False
                elif not header and token.startswith('#'):
                    flush()
                    tick = int(token[1:]); pending = False
                elif not header and token[:1] in '01xXzZ' and token[1:] in codes:
                    pins[codes[token[1:]]] = int(token[0]) if token[0] in '01' else None
                    pending = True
            flush()
    if not rows or any(any(v not in (0, 1) for v in pins) for _, pins in rows):
        raise ValueError(f'{path}: missing/unknown D0..D3')
    if any(b[0] <= a[0] for a, b in zip(rows, rows[1:])):
        raise ValueError('timestamps must increase')
    return rows


def uart_ends(rows, baud=921600):
    """Decode 8N1 start/data/stop centers, returning end of valid stop bits."""
    edges = []
    previous = None
    for t, pins in rows:
        if pins[2] != previous:
            edges.append((t, pins[2])); previous = pins[2]
    times = [t for t, _ in edges]
    def level(t):
        return edges[bisect.bisect_right(times, t)-1][1]
    ends, busy = [], -1
    resync = False
    bit = 1/baud
    for index, (start, value) in enumerate(edges):
        if index == 0 or value != 0 or start < busy:
            continue
        if resync and start - edges[index-1][0] < bit:
            continue
        end = start + 10*bit
        busy = end - .1*bit
        if end > rows[-1][0]:
            continue
        if level(start+.5*bit) == 0 and level(start+9.5*bit) == 1:
            ends.append(end)
            resync = False
        else:
            # Discard the whole failed character, then require an idle bit.
            busy = end
            resync = True
    return ends


def analyze(rows, run=None):
    rise = next((b[0] for a,b in zip(rows, rows[1:]) if a[1][3] == 0 and b[1][3] == 1), None)
    if rise is None:
        raise ValueError('no marker rising edge')
    before = [p for t,p in rows if t < rise]
    if not before or before[-1][:2] != (1,1):
        raise ValueError('marker must follow FRESH (11)')
    safe = next((t for t,p in rows if t >= rise and p[:2] == (0,0)), None)
    hold = next((t for t,p in rows if t >= rise and (safe is None or t <= safe) and p[:2] == (0,1)), None)
    end = safe if safe is not None else rows[-1][0]
    activity = [b[0] for a,b in zip(rows, rows[1:]) if b[0] < end and a[1][2] != b[1][2]]
    bytes_ = uart_ends(rows)
    last = next((t for t in reversed(bytes_) if t <= end), None)
    result = dict(t_marker_rise_s=rise, t_last_uart_activity_s=activity[-1] if activity else None,
                  t_last_uart_byte_s=last, t_hold_s=hold, t_safe_s=safe,
                  marker_safe_us=(safe-rise)*1e6 if safe is not None else None,
                  uart_hold_us=(hold-max(t for t in bytes_ if t <= hold))*1e6 if hold is not None and any(t <= hold for t in bytes_) else None,
                  uart_safe_us=(safe-last)*1e6 if safe is not None and last is not None else None,
                  status='observed' if safe is not None else 'censored: no safe transition',
                  evidence='UNVERIFIED ON HARDWARE', comparison='missing STATE_EVENT')
    for name in ('hold','safe'):
        result[f'mcu_{name}_us'] = None
        result[f'delta_{name}_us'] = None
    if run:
        meta = json.loads((run/'run.json').read_text())
        events = []
        for folder in ('pipeline','capture'):
            path = run/folder/'state_events.csv'
            if path.exists():
                with path.open() as stream:
                    events.extend(csv.DictReader(stream))
        # Match the first fault episode following the validated steady FRESH window.
        fresh = [int(r['mcu_us']) for r in events if r['new'] in ('1','FRESH')]
        departures = [int(r['mcu_us']) for r in events
                      if r['new'] in ('2','HOLD','3','FAILSAFE')
                      and fresh and int(r['mcu_us']) > min(fresh)]
        first = min(departures) if departures else float('inf')
        preceding = [t for t in fresh if t < first]
        cutoff = max(preceding) if preceding else -1
        events = [r for r in events if int(r['mcu_us']) > cutoff]
        result['comparison'] = 'MCU last accepted heartbeat vs analyzer last physical UART byte; references differ'
        if any(int(r['lost_count']) for r in events):
            result['comparison'] = 'INVALID: STATE_EVENT loss'
        else:
            for name, states in (('hold', ('2','HOLD')), ('safe', ('3','FAILSAFE'))):
                event = next((r for r in events if r['new'] in states), None)
                if event:
                    value = int(event['mcu_us'])-int(event['last_hb_mcu_us'])
                    result[f'mcu_{name}_us'] = value
                    measured = result[f'uart_{name}_us']
                    result[f'delta_{name}_us'] = measured-value if measured is not None else None
        brackets = [e['software_bracket_ns'] for e in meta.get('marker_edges', []) if e['value'] == 1]
        result['marker_software_bracket_us'] = max(brackets)/1000 if brackets else None
    else:
        result['marker_software_bracket_us'] = None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outdir', type=Path)
    args = parser.parse_args()
    reports, traces = [], []
    for capture in sorted(args.outdir.glob('*/capture.vcd')):
        rows = read_trace(capture)
        runs = list(capture.parent.glob('pi/F*/run.json'))
        report = analyze(rows, runs[0].parent if len(runs) == 1 else None)
        reports.append(dict(capture=capture.parent.name, **report)); traces.append(rows)
    if not reports:
        parser.error('no */capture.vcd files')
    with (args.outdir/'la_e4.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=reports[0]); writer.writeheader(); writer.writerows(reports)
    def num(v): return '--' if v is None else f'{v:.3f}'
    lines = ['% UNVERIFIED ON HARDWARE', r'\begin{tabular}{lrrrrr}', r'Capture & Marker-safe (us) & UART-safe (us) & MCU-safe (us) & Delta (us) & UART-HOLD (us) \\', r'\hline']
    for r in reports:
        lines.append(' & '.join([r['capture'].replace('_', r'\_')] + [num(r[k]) for k in ('marker_safe_us','uart_safe_us','mcu_safe_us','delta_safe_us','uart_hold_us')])+r' \\')
    (args.outdir/'la_e4.tex').write_text('\n'.join(lines+[r'\end{tabular}', '']))
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib unavailable: PNG omitted (no dependency installed)')
    else:
        rows = traces[0]; marker = reports[0]['t_marker_rise_s']
        fig, ax = plt.subplots(figsize=(12,4))
        # Display sparse UART edges; no expansion into millions of samples.
        for i, label in enumerate(('PA5 fresh','PB5 grace','UART RX','GPIO27 marker')):
            ax.step([(t-marker)*1000 for t,p in rows], [p[i]*.7+i for t,p in rows], where='post', label=label)
        ax.axvline(0, color='black', linestyle=':'); ax.set_xlabel('Analyzer time from marker (ms)')
        ax.set_yticks(range(4), ('PA5','PB5','UART','marker')); ax.set_title('UNVERIFIED ON HARDWARE — '+reports[0]['capture'])
        fig.tight_layout(); fig.savefig(args.outdir/'la_timing.png', dpi=160); plt.close(fig)
    print(f'{len(reports)} captures: {args.outdir}/la_e4.csv, la_e4.tex; UNVERIFIED ON HARDWARE')


if __name__ == '__main__':
    main()
