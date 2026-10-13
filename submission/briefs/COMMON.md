# Common rules for all three OS submission deliverables

Repository: this worktree (branch feat/os-submission, based on release/os-final = final code
and results). Write ONLY inside your own deliverable folder under `submission/`. Do not run
git commands that change index/branches/commits. Do not edit third_party/, results/, code.

Sources of truth (read; never invent): PROJECT.md, AGENTS.md, README.md, docs/STAGE_REPORT.md,
docs/SYSTEM_GUIDE.md, docs/SYSTEM_OVERVIEW.md, docs/ROADMAP*.md, results/README.md and every
results/<dated>/ summary, analysis/, tools/, linux/, stm32/, protocol/, git log.
Long study deck (reference only, read-only, outside this worktree):
/Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides_course/
(main.tex, main.pdf, build_deck.py, images/, measured_evidence.py, REVIEW_LOG.md). Reuse its
preamble/palette/fonts/figure macros so all decks look like one family, and reuse its images
(images/V*.jpg, W*.png/jpg) and generated figures where they fit. The original Vietnamese
deck slides/ is the visual model (rated very highly). Skill: `git show
fbc1ed3:prompts/academic-beamer-deck/SKILL.md` and its template files.

Evidence discipline: label every result MEASURED / FLAGGED (from INVALID runs) / PLANNED /
UNKNOWN exactly as results/README.md and STAGE_REPORT.md define (including the v1 vs v2
validity-rule note). Never promote FLAGGED to a clean result. Observed maxima are not
worst-case bounds. Firmware review fixes are compiled but NOT flashed/verified on the rig.
Figures must be generated from the retained raw/summary data by a script you keep in your
folder (or reused from slides_course), not drawn by hand. English only.

Images: if you need a NEW illustration (not a data figure, not an exact TikZ diagram), first
write `<your folder>/image-prompts/NEEDS.md` in the same format as
slides_course/image-prompts/BATCH.md (shared STYLE GUIDE + HARDWARE REFERENCE, one fenced
prompt per id, ids prefixed with your deliverable letter, e.g. D01/R01/P01, save path in your
images/ folder). If none needed, write NEEDS.md containing "NONE". Do this within your first
steps. Missing images must compile as a visible placeholder box.

Quality loop: build with latexmk -xelatex, render pages to PNG
(swift /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/render.swift
main.pdf preview), inspect every page at full size, fix, repeat until clean: no LaTeX
errors, no Overfull boxes, no overflow/overlap/tiny text, every figure referenced and
explained. Keep REVIEW_LOG.md in your folder (rounds, defects, fixes, final verdict).

Purpose rule (owner, 2026-10-13): each deliverable serves exactly one purpose. Cut or add slides/sections freely so everything serves that purpose; target sizes are guides, not quotas. Reviewers: flag any slide/section that does not serve the deliverable purpose as MAJOR.
