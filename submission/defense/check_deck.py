#!/usr/bin/env python3
"""Artifact consistency checks; visual review remains required."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
tex=(HERE/'main.tex').read_text().replace(r'\input{rerun_2026-10-20.tex}', (HERE/'rerun_2026-10-20.tex').read_text());aux=(HERE/'main.aux').read_text();log=(HERE/'main.log').read_text()
errors=re.findall(r'^!.*|^.*(?:Overfull|Underfull|Missing character|undefined).*',log,re.M)
assert not errors,errors
assert len(re.findall(r'\\begin\{frame\}',tex))==35
assert r'\inserttotalframenumber {35}' in (HERE/'main.nav').read_text()
labels=re.findall(r'\\newlabel\{fig:([^}]+)\}\{\{(\d+)\}',aux)
assert [int(n) for _,n in labels]==list(range(1,12)),labels
assert set(re.findall(r'\\ref\{fig:([^}]+)\}',tex))==set(k for k,_ in labels)
notes=(HERE/'SPEAKER_NOTES.md').read_text()
times=re.findall(r'^\| (\d+) \| .*? \| (\d+) \|',notes,re.M)
assert [int(n) for n,_ in times]==list(range(1,27))
assert sum(int(s) for _,s in times)==1200
assert len(re.findall(r'^## \d+ —',notes,re.M))==26
manifest=json.loads((HERE/'qa/source_hashes.json').read_text())
for p,digest in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
records=json.loads((HERE/'qa/evidence.json').read_text())
assert sum(r['validity']=='VALID' for r in records['e4_runs'])==27
assert len(records['analyzer'])==15 and sum(r['matching'] for r in records['analyzer'])==10
assert len(list((HERE/'preview').glob('page-*.png')))==35
rerun_manifest=json.loads((HERE/'qa/rerun_2026-10-20_sources.json').read_text())
for p,digest in rerun_manifest.items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
assert (HERE/'image-prompts/NEEDS.md').read_text().strip()=='NONE'
print(f'PASS: clean log; 35 pages; 11 uniquely numbered/referenced figures; 26 scripts = 1,200 s; {len(manifest)} source hashes unchanged; {len(rerun_manifest)} rerun source hashes checked; original E4 27/34, analyzer 10/15. Visual review: see REVIEW_LOG.md.')
