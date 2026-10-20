#!/usr/bin/env python3
"""Read-only evidence extraction; writes only beside this script."""
from pathlib import Path
import csv, hashlib, json, math, re
from decimal import Decimal
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'generated'; OUT.mkdir(exist_ok=True)
manifest={}
def read(p):
    p=Path(p); b=p.read_bytes(); manifest[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest(); return b.decode()
def rows(p): return list(csv.DictReader(read(p).splitlines()))
def esc(s):
    return str(s).replace('\\',r'\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('>',r'$>$')
def readable_ms(value):
    """Expand retained scientific notation exactly, without adding precision."""
    return re.sub(r'\d+(?:\.\d+)?[eE][+-]?\d+',
                  lambda match: format(Decimal(match.group()), 'f'), value)

def table(name,heads,data,caption,widths=None):
    spec=widths or ('l'+'r'*(len(heads)-1))
    s='\\begin{table}[H]\n\\centering\\small\n\\caption{'+caption+'}\\label{tab:'+name+'}\n\\begin{tabular}{'+spec+'}\n\\toprule\n'
    s+=' & '.join(map(esc,heads))+r' \\'+ '\n\\midrule\n'
    s+='\n'.join(' & '.join(map(esc,r))+r' \\' for r in data)
    s+='\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    (OUT/(name+'.tex')).write_text(s)
def mdrows(p):
    return [[x.strip() for x in l.strip('|').split('|')] for l in read(p).splitlines() if l.startswith('|')][2:]
p=ROOT/'results/2026-10-11_cyclictest/SUMMARY.md'
r=mdrows(p)
table('timer',['Load','P0 P99','P0 max','P1 P99','P1 max'],[[a[0],a[2],a[4],a[6],a[8]] for a in r],r'MEASURED under v1: timer wake-up latency ($\mu$s), three repeats per cell.')
table('infer',['Load','Threads','Valid','P50','P99','Max'],mdrows(ROOT/'results/2026-10-11_inference_baseline/SUMMARY.md'),r'MEASURED accepted subset: inference-call latency (ms).')
base=ROOT/'results/2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/summary'
r=rows(base/'E1_table.csv')
labels=['Idle','Stream','Memrate','Cache 2M','CPU']
table('e1',['Load','Service P50/P99/max','Delivery P50/P99/max'],[[l,readable_ms(a['Service latency']),readable_ms(a['Delivery latency'])] for l,a in zip(labels,r)],'MEASURED under v1: E1 P0 software/PTY latency (ms); three repeats.')
r=rows(base/'E2_table.csv')
table('e2',['Profile/load','Service P50/P99/max','Delivery P50/P99/max'],[[a['Profile']+' / '+['idle','memrate','cache'][i%3],readable_ms(a['Service latency']),readable_ms(a['Delivery latency'])] for i,a in enumerate(r)],'MEASURED under v1: E2 software/PTY latency (ms); three repeats.')
r=rows(base/'E3_table.csv')
table('e3',['Load/policy','Mean age (ms)','Peak (ms)','Received','Replaced'],[[('Idle' if i<2 else 'Memrate')+'/'+a['Policy'],a['Time-average AoI'].split()[0],readable_ms(a['Peak AoI'].split()[0]),a['Delivered count'],a['Replaced count']] for i,a in enumerate(r)],'MEASURED under v1: E3 held-value AoI and median per-run counts.')
table('e3_thresholds',['Load/policy','Time >100 ms (s)','Time >150 ms (s)','Misses >100/>150 ms'],
      [[('Idle' if i<2 else 'Memrate')+'/'+a['Policy'],
        *a['Age-violation time'].removesuffix(' s').split('/'),a['Deadline misses']]
       for i,a in enumerate(r)],
      'MEASURED under v1: E3 strict-threshold outcomes; medians per run over three repeats. Miss denominators count CRC-valid inference receptions including drain.')
def nr(a,p): return sorted(a)[math.ceil(len(a)*p)-1]
r=[]
for p in sorted((ROOT/'results/2026-10-12_e3b_input_latest').glob('*_e3b/E3B*B2*/pipeline/rx.csv')):
    rr=rows(p); age=[(int(a['t_rx_ns'])-int(a['t_input_ns']))/1e6 for a in rr if a.get('t_input_ns') and a.get('t_rx_ns') and a.get('type','INFERENCE') in ('INFERENCE','2','0x02')]
    if not age:
        age=[(int(a['t_rx_ns'])-int(a['t_input_ns']))/1e6 for a in rr if a.get('t_input_ns') and a.get('t_rx_ns')]
    name=p.parent.parent.name
    skips=sum(a.get('status')=='skipped_stale' for a in rows(p.parent/'infer.csv'))
    r.append([name.split('_')[-2]+'/'+name.split('_')[-1],len(age),f'{nr(age,.5):.1f}',f'{nr(age,.99):.1f}',skips])
table('e3b',['Input/repeat','Receptions','P50 (ms)','P99 (ms)','Skipped'],r,r'FLAGGED: all six loaded E3b runs fail live-power validity. Per-run input-to-software-reception age $(t_{rx,ns}-t_{input,ns})/10^6$ (ms); nearest-rank quantiles over CRC-valid inference receptions including shutdown drain.')
r=[]
for p in sorted((ROOT/'results/2026-10-12_e3_real_uart').glob('*_e3real/E3_REAL*B2*/pipeline/inf_rx.csv')):
    rr=rows(p); age=[float(a['age_mcu_us'])/1000 for a in rr if a.get('age_mcu_us')]
    name=p.parent.parent.name; bits=name.split('_'); ip=bits[bits.index('input')+1]; bp=bits[bits.index('bridge')+1]
    r.append([ip+'/'+bp+'/'+bits[-1],len(age),f'{nr(age,.5):.3f}',f'{nr(age,.99):.3f}'])
table('real',['Input/bridge/repeat','Receptions','P50 (ms)','P99 (ms)'],r,'FLAGGED: loaded real-UART E3 MCU source-age estimates.')
# Inventory the later campaign separately; its generic heading does not confer validity.
rerun=ROOT/'results/2026-10-12_e3_real_uart_rerun/20261012T160628Z_e3real2'
rr=rows(rerun/'summary/per_run.csv')
read(rerun/'campaign.json')
read(rerun/'summary/README.md')
accepted=sum(a['valid']=='True' for a in rr)
power=sum('live throttling/power bits' in a['validity'] for a in rr)
failed=sum('pipeline' in a['validity'].lower() for a in rr)
(OUT/'real_rerun_note.tex').write_text(
    r'\textbf{Separate FLAGGED rerun (U2).} The later \texttt{20261012T160628Z} campaign retains '
    +f'{len(rr)} further attempts, {accepted} accepted: all {power} have live-power exclusions and {failed} also have pipeline failures. '
    +r'Its diagnostic ages and state durations are excluded from the comparison presented here and are not pooled with U. They do not validate HOLD occupancy under clean conditions. Appendix A identifies the retained summaries.'+'\n')
base4=ROOT/'results/2026-10-12_e4_faults/20261012T093526Z_e4'
r=[]
for fault in ['F1','F2','F3','F4']:
    accepted=[a for a in rows(base4/'e4_runs.csv') if a['fault']==fault and a['validity']=='VALID']
    first=[]; safe=[]
    for a in accepted:
        p=base4/a['run']/'pipeline/state_events.csv'
        if fault=='F1' or not p.exists(): p=base4/a['run']/'capture/state_events.csv'
        ev=rows(p)
        for dest,target in [('2',first),('3',safe)]:
            candidates=[v for v in ev if v['new']==dest and v['reason'] in ('3','9','10')]
            if candidates:
                v=candidates[0]; ref='last_hb_mcu_us' if v['reason']=='3' else 'last_inf_mcu_us';target.append((int(v['mcu_us'])-int(v[ref]))/1000)
    fmt=lambda x: '---' if not x else f'{nr(x,.5):.3f} / {max(x):.3f}'
    r.append([fault,len(accepted),fmt(first),fmt(safe),'HB' if fault!='F3' else 'Result'])
table('e4',['Fault','Valid','HOLD P50/max','FAILSAFE P50/max','Safe ref.'],r,'MEASURED: original E4 reason-based MCU-local intervals (ms).')
r=[]
for p in sorted((ROOT/'results/2026-10-12_f5_stale').glob('*_f5/r*/F5-r01/pipeline/state_events.csv')):
    ev=rows(p); hold=next(a for a in ev if a['reason']=='9'); safe=next(a for a in ev if a['reason']=='10')
    r.append([p.parents[2].name,f"{(int(hold['mcu_us'])-int(hold['last_inf_mcu_us']))/1000:.3f}",f"{(int(hold['mcu_us'])-int(hold['last_hb_mcu_us']))/1000:.3f}",f"{(int(safe['mcu_us'])-int(safe['last_inf_mcu_us']))/1000:.3f}"])
table('f5',['Repeat','Result to HOLD','HB age at HOLD','Result to FAILSAFE'],r,'MEASURED: F5 short-window transitions (ms), five accepted runs.')
# Recorded acquisition provenance is distinct from firmware image identity.
provenance={}
for folder in ['2026-10-11_cyclictest','2026-10-11_inference_baseline','2026-10-11_e1_e2_e3_pty','2026-10-12_e3b_input_latest','2026-10-12_e3_real_uart','2026-10-12_e4_faults','2026-10-12_f5_stale','2026-10-12_f4_extra']:
    files=sorted((ROOT/'results'/folder).rglob('meta_before.json'))
    files+=sorted((ROOT/'results'/folder).rglob('metadata-before.json'))
    commits={}
    for p in files:
        data=json.loads(read(p)); commit=data.get('git_commit','UNKNOWN')
        commits.setdefault(commit,[]).append(str(p.relative_to(ROOT)))
    provenance[folder]=commits
(OUT/'acquisition-commits.json').write_text(json.dumps(provenance,indent=2)+'\n')
# Later collections remain diagnostic; summarize retained rows without revalidation.
r=[]
for name in ['run_F1','run_F2','run_F4','check_F2']:
    p=ROOT/'results/2026-10-12_logic_analyzer'/name/'la_e4.csv'; rr=rows(p)
    r.append([name,len(rr),'FLAGGED'])
table('analyzer',['Collection','Summary rows','Status'],r,'FLAGGED: retained analyzer summary inventory; rows are not acceptance counts.')
r=[]
for p in sorted((ROOT/'results/2026-10-12_hw_bringup').glob('hw_smoke*/summary.json')):
    a=json.loads(read(p));r.append([p.parent.name,'FLAGGED'])
table('smoke',['Retained smoke','Timing qualification'],r,'FLAGGED: all seven bring-up summaries exclude their runs.', 'lr')
(OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Generated {len(list(OUT.glob("*.tex")))-1} tables and one rerun note from {len(manifest)} source files.')
