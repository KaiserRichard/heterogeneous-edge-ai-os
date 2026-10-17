"""Rough prose-rhythm check for content.md (Vietnamese syllables counted as words)."""
import re, statistics, pathlib
t = pathlib.Path(__file__).with_name('content.md').read_text()
paras = [p for p in t.split('\n\n') if p.strip() and not p.lstrip().startswith(('#', '|', '!', '-', '<', '1.', '2.', '3.', '4.', 'Bảng', 'Hình'))]
sents = [x for p in paras for x in re.split(r'(?<=[.?!])\s+', p.strip()) if x]
L = [len(x.split()) for x in sents]
print(f"sentences={len(L)} mean={statistics.mean(L):.1f} median={statistics.median(L)} stdev={statistics.pstdev(L):.1f} "
      f"share>=28={sum(l >= 28 for l in L)/len(L):.2f} share<=12={sum(l <= 12 for l in L)/len(L):.2f}")
sp = [len(re.split(r'(?<=[.?!])\s+', p.strip())) for p in paras]
print(f"paragraphs={len(sp)} mean_sentences_per_para={statistics.mean(sp):.1f}")
