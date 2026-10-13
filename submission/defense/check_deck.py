#!/usr/bin/env python3
"""Artifact consistency checks; visual review remains required."""
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
tex=(HERE/'main.tex').read_text();aux=(HERE/'main.aux').read_text();log=(HERE/'main.log').read_text()
errors=re.findall(r'^!.*|^.*(?:Overfull|Underfull|Missing character|undefined).*',log,re.M)
assert not errors,errors
assert len(re.findall(r'\\begin\{frame\}',tex))==30
assert r'\inserttotalframenumber {30}' in (HERE/'main.nav').read_text()
labels=re.findall(r'\\newlabel\{fig:([^}]+)\}\{\{(\d+)\}',aux)
assert [int(n) for _,n in labels]==list(range(1,12)),labels
assert set(re.findall(r'\\ref\{fig:([^}]+)\}',tex))==set(k for k,_ in labels)
notes=(HERE/'SPEAKER_NOTES.md').read_text()
times=re.findall(r'^\| (\d+) \| .*? \| (\d+) \|',notes,re.M)
assert [int(n) for n,_ in times]==list(range(1,22))
assert sum(int(s) for _,s in times)==1020
assert len(re.findall(r'^## \d+ —',notes,re.M))==21
manifest=json.loads((HERE/'qa/source_hashes.json').read_text())
for p,digest in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
records=json.loads((HERE/'qa/evidence.json').read_text())
assert sum(r['validity']=='VALID' for r in records['e4_runs'])==27
assert len(records['analyzer'])==15 and sum(r['matching'] for r in records['analyzer'])==10
assert len(list((HERE/'preview').glob('page-*.png')))==30
assert (HERE/'image-prompts/NEEDS.md').read_text().strip()=='NONE'
print(f'PASS: clean log; 30 pages; 11 uniquely numbered/referenced figures; 21 scripts = 1,020 s; {len(manifest)} source hashes unchanged; E4 27/34, analyzer 10/15. Visual review: see REVIEW_LOG.md.')
