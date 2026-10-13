#!/usr/bin/env python3
"""Regenerate defense plots and tables from retained evidence; never alter sources."""
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', str(HERE / '.mpl-cache'))
import bisect, binascii, csv, hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = HERE.parents[1]
RES = ROOT / 'results'
SOURCES = set()
def read(p):
    SOURCES.add(p)
    with p.open() as f: return list(csv.DictReader(f))
def quant(v,q): return sorted(v)[math.ceil(len(v)*q)-1]
def load_module(name,p):
    SOURCES.add(p)
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Avenir Next','DejaVu Sans'], 'font.size':17,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#22262B','text.color':'#22262B','figure.facecolor':'#FAFAF7','axes.facecolor':'#FAFAF7','pdf.fonttype':42})
TEAL='#2A9D8F';NAVY='#1F3A5F'
FAULT='#E76F51'
def save(fig,key):
    fig.tight_layout(pad=.6);fig.savefig(HERE/'images'/f'{key}.pdf');plt.close(fig)
# Cyclictest: median per-run quantiles in retained condition summaries.
cyc=[read(next((RES/'2026-10-11_cyclictest').glob(f'*_P{i}/summary_by_condition.csv'))) for i in [0,1]]
loads=['B0_idle','CPU_c23','B1_stream_c2','C1_cache2M_c2','B2_memrate_c23']
# Retained summary row order is independent of display order.
print('Cyclic fields:',list(cyc[0][0]))
by=[{r['condition'].split('_',1)[1]:r for r in rows} for rows in cyc]
x=list(range(5));fig,ax=plt.subplots(figsize=(11,3.2))
for k,c in enumerate([NAVY,TEAL]):
    vals=[float(by[k][n]['p99_us']) for n in loads]
    ax.bar([i+(k-.5)*.34 for i in x],vals,.34,label=f'P{k}',color=c)
    for i,v in zip(x,vals):ax.text(i+(k-.5)*.34,v*1.13,f'{v:g}',ha='center',fontsize=13)
ax.set_xticks(x,['Idle','CPU','Stream','Cache','Memrate']);ax.set_yscale('log');ax.set_ylim(5,1200);ax.set_ylabel('Wake-up P99 (µs)');ax.legend(ncol=2);ax.grid(axis='y',alpha=.18);save(fig,'cyclic')
# Inference table: accepted subset only, as published.
p=RES/'2026-10-11_inference_baseline/SUMMARY.md';SOURCES.add(p)
inf=[]
for line in p.read_text().splitlines():
    if line.startswith('| idle |') or line.startswith('| cpu stress'):
        a=[s.strip() for s in line.strip('|').split('|')];inf.append(a)
fig,ax=plt.subplots(figsize=(11,3.2))
for rows,label,c in [(inf[:4],'Idle',NAVY),(inf[4:],'CPU stress 2–3',TEAL)]:
    ax.plot([int(r[1]) for r in rows],[float(r[4]) for r in rows],marker='o',linewidth=2.5,label=label,color=c)
    for r in rows:ax.text(int(r[1]),float(r[4])+(5 if label!='Idle' else -10),f'{float(r[4]):g}',ha='center',fontsize=13)
ax.set_xticks([1,2,3,4]);ax.set_xlabel('Intra-op threads');ax.set_ylabel('Inference P99 (ms)');ax.set_ylim(20,125);ax.legend();ax.grid(alpha=.18);save(fig,'inference')
cam=next((RES/'2026-10-11_e1_e2_e3_pty').glob('*/summary'))
# Retain the settings and load definitions used by the revised method/profile slides.
SOURCES.update(cam.parent.glob('E2_P[01]_B0_idle_latest_r1/settings.json'))
SOURCES.update(cam.parent.glob('E1_*_r1/condition.json'))
SOURCES.update((RES/'2026-10-11_cyclictest/20261008T091937Z_cyc_P0').glob('*_r1/stress_cmd.txt'))
SOURCES.update([ROOT/'docs/STAGE_REPORT.md',RES/'README.md'])
for name in ['E1','E2','E3']:
    rows=read(cam/f'{name}_table.csv');fig,ax=plt.subplots(figsize=(11,3.1))
    if name=='E1':
        vals=[float(r['Delivery latency'].split('/')[1]) for r in rows];labels=['Idle','Stream','Memrate','Cache','CPU'];ylabel='Delivery P99 (ms)'
    elif name=='E2':
        vals=[float(r['Delivery latency'].split('/')[1]) for r in rows];labels=['P0 idle','P0 mem','P0 cache','P1 idle','P1 mem','P1 cache'];ylabel='Delivery P99 (ms)'
    else:
        vals=[float(r['Time-average AoI'].split()[0]) for r in rows];labels=['Idle FIFO','Idle latest','Mem FIFO','Mem latest'];ylabel='Mean held-value AoI (ms)'
    colors=[NAVY if (name=='E2' and i<3) or (name=='E3' and i%2==0) else TEAL for i in range(len(vals))]
    ax.bar(labels,vals,color=colors,width=.6)
    for i,v in enumerate(vals):ax.text(i,v*1.13,f'{v:g}',ha='center',fontsize=14)
    ax.set_yscale('log');ax.set_ylim(20,max(vals)*2.1);ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.18);save(fig,name)
# Later real-UART rerun is retained but still has no accepted clean runs.
rerun=next((RES/'2026-10-12_e3_real_uart_rerun').glob('*/summary/per_run.csv'))
rerun_rows=read(rerun);SOURCES.add(rerun.with_name('README.md'))
assert len(rerun_rows)==18 and all(r['valid']=='False' for r in rerun_rows)
# E4 original acceptance retained; reason-based local durations recomputed from raw.
original=next((RES/'2026-10-12_e4_faults').glob('*/e4_runs.csv'))
runs=[]
def event_values(d,meta,valid,scope,stored=None):
    ev=read(d/'pipeline/state_events.csv')
    if (d/'capture/state_events.csv').exists():ev+=read(d/'capture/state_events.csv')
    ev=sorted(ev,key=lambda r:int(r['mcu_us']))
    affected=[r for r in ev if r['new'] in ['2','3'] and (not r['t_mcu_pi_est_ns'] or meta['onset_pi_ns']<=float(r['t_mcu_pi_est_ns'])<=meta['observation_end_pi_ns'])]
    rec=dict(fault=meta['fault'],run=str(d.relative_to(ROOT)),validity=valid,scope=scope)
    if affected:
        for key,r in [('first',affected[0]),('failsafe',next(r for r in affected if r['new']=='3'))]:
            ref='last_hb_mcu_us' if r['reason']=='3' else 'last_inf_mcu_us'
            rec[key+'_reason']=int(r['reason']);rec[key+'_local_ms']=(int(r['mcu_us'])-int(r[ref]))/1000
            rec[key+'_mapped_ms']=(float(r['t_mcu_pi_est_ns'])-meta['onset_pi_ns'])/1e6 if r['t_mcu_pi_est_ns'] else None
        if stored:
            rec['first_mapped_ms']=float(stored['detection_us'])/1000;rec['failsafe_mapped_ms']=float(stored['failsafe_us'])/1000
    return rec
for r in read(original):
    if r['fault']=='F5':continue
    d=original.parent/r['run'];p=d/'run.json';SOURCES.add(p);meta=json.loads(p.read_text())
    runs.append(event_values(d,meta,r['validity'],'original E4',r if r['validity']=='VALID' else None))
for folder,fault in [('2026-10-12_f5_stale','F5'),('2026-10-12_f4_extra','F4')]:
    for p in sorted((RES/folder).rglob('run.json')):
        SOURCES.add(p);meta=json.loads(p.read_text());d=p.parent
        if meta.get('fault')!=fault:continue
        if meta['status']!='COMPLETE':runs.append(dict(fault=fault,run=str(d.relative_to(ROOT)),validity='INVALID',scope='short window'));continue
        power=read(d/'power.csv');baseline=int(power[0]['throttled'],0)
        bad=any(int(r['throttled'],0)&15 or (int(r['throttled'],0)&0xf0000)&~baseline for r in power)
        echoes=read(d/'pipeline/echo.csv');rms=max(float(r['rms_residual_us']) for r in echoes if r['accepted']=='1' and r['rms_residual_us'])
        valid='INVALID' if bad or rms>200 else 'VALID'
        runs.append(event_values(d,meta,valid,'short-window transitions; no recovery qualification'))
assert len(runs)==34 and sum(r['validity']=='VALID' for r in runs)==27
fig,axes=plt.subplots(1,2,figsize=(12,3.5))
reason_styles={3:(FAULT,'s','3: heartbeat'),9:(NAVY,'^','9: inference HOLD'),10:(TEAL,'o','10: inference FAILSAFE')}
for ax,key,title in zip(axes,['first_local_ms','failsafe_local_ms'],['First state change','FAILSAFE state change']):
    reason_key=key.replace('_local_ms','_reason')
    for i,f in enumerate(['F1','F2','F3','F4','F5']):
        accepted=[r for r in runs if r['fault']==f and r['validity']=='VALID']
        for j,r in enumerate(accepted):
            color,marker,_=reason_styles[r[reason_key]]
            ax.scatter(i+(j-(len(accepted)-1)/2)*.11,r[key],color=color,marker=marker,s=75,edgecolors='#FAFAF7',linewidths=.7)
    ax.set_xticks(range(5),['F1','F2','F3','F4','F5'],fontsize=20)
    ax.tick_params(axis='y',labelsize=20)
    ax.set_title(title,fontsize=22)
    ax.set_ylabel('Receipt to event (ms)',fontsize=21)
    ax.set_ylim(60,520);ax.set_xlim(-.5,4.5);ax.set_yticks([100,200,300,400,500]);ax.grid(alpha=.18)
axes[0].annotate('F4: 6 HB / 1 HOLD',xy=(3,176),xytext=(1.3,285),fontsize=18,arrowprops=dict(arrowstyle='-',color=NAVY))
handles=[plt.Line2D([],[],color=c,marker=m,linestyle='None',markersize=9,label=label) for c,m,label in reason_styles.values()]
fig.legend(handles=handles,loc='upper center',ncol=3,fontsize=18,frameon=False,bbox_to_anchor=(.52,1.16))
# Reserve room for the reason key without shrinking axis typography.
fig.tight_layout(pad=.6);fig.savefig(HERE/'images/E4.pdf',bbox_inches='tight');plt.close(fig)
summary=[]
for f in ['F1','F2','F3','F4','F5']:
    accepted=[r for r in runs if r['fault']==f and r['validity']=='VALID']
    rec=dict(fault=f,n=len(accepted))
    for key in ['first_local_ms','failsafe_local_ms','first_mapped_ms','failsafe_mapped_ms']:
        v=[r[key] for r in accepted];rec[key]=[quant(v,.5),quant(v,.95),max(v)]
    summary.append(rec)
for domain in ['local','mapped']:
    lines=[r'\begin{tabular}{@{}lrrr@{}}\toprule Fault & Valid & First P50 / P95 / max & FAILSAFE P50 / P95 / max\\\midrule']
    for r in summary:
        n=f"{r['n']}/"+('14' if r['fault']=='F4' else '5')
        cells=[' / '.join(f'{v:.3f}' for v in r[k]) for k in [f'first_{domain}_ms',f'failsafe_{domain}_ms']]
        lines.append(r['fault']+' & '+n+' & '+' & '.join(cells)+r'\\[5pt]')
    lines.append(r'\bottomrule\end{tabular}');(HERE/'qa'/f'E4_{domain}.tex').write_text('\n'.join(lines)+'\n')
# Analyzer: reanalyze all 15 VCDs; decode frame types with CRC for reference match.
la=load_module('defense_la',ROOT/'tools/la/la_analyze.py')
def decode(rows,end):
    edges=[]
    for t,p in rows:
        if not edges or edges[-1][1]!=p[2]:edges.append((t,p[2]))
    times=[t for t,v in edges];bit=1/921600;busy=-1;data=[]
    def level(t):return edges[bisect.bisect_right(times,t)-1][1]
    for i,(t,v) in enumerate(edges):
        if i==0 or v or t<busy or t+10*bit>end:continue
        if level(t+.5*bit)==0 and level(t+9.5*bit)==1:
            data.append((t+10*bit,sum(level(t+(j+1.5)*bit)<<j for j in range(8))));busy=t+9.9*bit
    frames=[];i=0
    while i+9<=len(data):
        b=bytes(v for _,v in data[i:i+7]);n=9+b[6]
        if b[:2]==b'\xa5\x5a' and i+n<=len(data):
            frame=bytes(v for _,v in data[i:i+n])
            if binascii.crc_hqx(frame[2:-2],65535)==int.from_bytes(frame[-2:],'little'):
                frames.append(dict(end=data[i+n-1][0],type=b[3]));i+=n;continue
        i+=1
    return frames
las=[]
for table in sorted((RES/'2026-10-12_logic_analyzer').glob('*/la_e4.csv')):
    for supplied in read(table):
        cap=table.parent/supplied['capture'];p=cap/'capture.vcd';SOURCES.add(p)
        trace=la.read_trace(p);run=next(cap.glob('pi/F*/run.json'));SOURCES.add(run)
        for p in (run.parent/'pipeline').glob('state_events.csv'):SOURCES.add(p)
        rec=la.analyze(trace,run.parent)
        for key in ['marker_safe_us','uart_safe_us','mcu_safe_us','delta_safe_us']:assert abs(rec[key]-float(supplied[key]))<1e-6
        frame=decode(trace,rec['t_safe_s'])[-1];assert abs(frame['end']-rec['t_last_uart_byte_s'])<1e-9
        rec.update(capture=str(cap.relative_to(ROOT)),last_frame_type=frame['type'],matching=frame['type']==1);las.append(rec)
assert len(las)==15 and sum(r['matching'] for r in las)==10
matched=[r['delta_safe_us'] for r in las if r['matching']];assert 47<min(matched)<max(matched)<68
fig,axes=plt.subplots(1,2,figsize=(12,3.1))
capture_key=['# Analyzer plot capture key','',
    'Figure 11 plots Δ = analyzer UART-byte-end → both GPIOs low interval minus MCU accepted-heartbeat receipt → FAILSAFE STATE_EVENT interval. Positive means the analyzer interval is longer. Capture indices restart in each panel; no matching-frame classification qualifies collection validity. Collection: FLAGGED.','',
    '| Panel / index | Capture | Last CRC-valid frame | Δ (µs) |','|---|---|---|---:|']
for ax,group,title in [(axes[0],[r for r in las if r['matching']],'10 final HEARTBEAT'),(axes[1],[r for r in las if not r['matching']],'5 different final frames')]:
    vals=[r['delta_safe_us']/(1 if ax is axes[0] else 1000) for r in group]
    for i,r in enumerate(group,1):
        panel='Matched' if r['matching'] else 'Different'
        frame={1:'HEARTBEAT',2:'INFERENCE',3:'ECHO_REQ'}[r['last_frame_type']]
        capture_key.append(f"| {panel} / {i} | {r['capture']} | {frame} | {r['delta_safe_us']:+.3f} |")
    ax.scatter(range(1,len(group)+1),vals,color=TEAL if ax is axes[0] else NAVY,s=65)
    ax.set_xticks(range(1,len(group)+1),[str(i) for i in range(1,len(group)+1)],fontsize=21)
    ax.tick_params(axis='y',labelsize=21)
    ax.set_xlabel('Capture index',fontsize=21)
    ax.set_title(title,fontsize=22);ax.set_ylabel('Δ (µs)' if ax is axes[0] else 'Δ (ms)',fontsize=23)
    ax.set_ylim(40,75) if ax is axes[0] else ax.set_ylim(-5.5,0)
    ax.grid(alpha=.18)
save(fig,'LA')
(HERE/'qa/LA_capture_key.md').write_text('\n'.join(capture_key)+'\n')
(HERE/'qa/evidence.json').write_text(json.dumps(dict(e4_runs=runs,e4_summary=summary,analyzer=las),indent=2)+'\n')
(HERE/'qa/source_hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCES)},indent=2)+'\n')
print(f'E4: 27/34 accepted. Analyzer: {len(las)} captures, {len(matched)} matching; delta {min(matched):.3f}–{max(matched):.3f} µs. Sources: {len(SOURCES)}')
