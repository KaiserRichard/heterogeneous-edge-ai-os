---
name: academic-beamer-deck
description: Build a professional, paper-structured academic slide deck as a LaTeX Beamer (XeLaTeX) document, plus a batch of AI image-generation prompts for its illustrations, with a render-and-inspect QA loop. Use when asked to make or revise a thesis/course/research presentation that must read like a scientific paper.
---

# Skill: academic Beamer deck + AI image batch

Use this file as the full instruction set ("skill") for an agent (ChatGPT Work, a ChatGPT
project, Codex, or another assistant). It is self-contained. Companion files in this folder:

- `template/preamble-reference.tex` – the proven preamble of a deck built with this skill
  (palette, fonts, spacing, figure macros, TikZ styles). Reuse it; remove project-specific
  diagram macros you do not need.
- `template/render.swift` – PDF → PNG renderer for macOS (`swift render.swift main.pdf preview`).
- `template/review_loop.sh`, `LAYOUT_BRIEF.md`, `REVIEWER_BRIEF.md` – builder/reviewer loop
  (two Codex accounts) used for the final layout polish.
- The finished example deck: `slides/main.tex` (45 pages) and its playbook
  `slides/SLIDE_PLAYBOOK.md` in the same repository.

---

## 0. First reply: capability check and intake (do this before any work)

Different agents can do different things. Start by stating, in a short list, what you can do
in this environment, and choose the matching mode:

| Capability | If YES | If NO |
|---|---|---|
| Run a shell / install or use TeX Live (`xelatex`, `latexmk`) | Mode A: build and render the PDF yourself | Mode B: deliver `.tex` + files; the user builds with `latexmk -xelatex main.tex` and sends you screenshots/PDF pages for review |
| View images (rendered pages, user images) | Inspect every page yourself | Ask the user for screenshots of specific pages |
| Generate images | You may generate illustrations directly | Produce the image-prompt batch (Section 6) for another tool |
| Access the repository (GitHub connector / files) | Read sources and write `slides/` directly | Ask the user to upload the source documents |

Then ask only for what is missing (one message, numbered):
1. Topic, language of slide text (e.g. Vietnamese), audience (lecturer reading alone? live
   talk?), target length (pages), deadline.
2. Source documents (design docs, research notes, results). Which numbers are measured, which
   are design values, which are published by others.
3. Cover data: title (native + English subtitle), team name, members + student IDs, leader,
   supervisor (e.g. "GVHD: TS. …"), class code.
4. Existing images (folder + whether names match V-ids) and whether new AI images are wanted.
5. Forbidden content (e.g. "do not mention project X"), required sections, style preferences.

Do not start writing frames until the outline (Section 2) is approved by the user.

---

## 1. Non-negotiable principles

1. **Evidence:** never invent measurements, results or citations. Design values are written as
   planned ("dự kiến"), host/unit-test results as such ("kiểm thử trên máy tính"), published
   numbers with a citation and the words "their result, not ours" when relevant.
2. **Paper logic:** the deck reads like a scientific paper: motivation → problem → objectives/RQs
   → theory → design → evaluation method → progress → conclusion → references.
3. **Every figure serves an argument** and is explained in the text.
4. **Look before you claim:** "done" is only allowed after every rendered page has been inspected
   at full size and the QA checklist (Section 8) passes.
5. **One editor at a time:** only one agent edits `main.tex` at any moment.

---

## 2. Outline (deliver first, get approval)

Deliver a numbered outline: page number, section/subsection title, one-line message, planned
figure (V-id or TikZ), source of each claim. Default structure:

1. Cover
2. Mục lục / Table of contents
3. `1. Giới thiệu` divider → 1.1 Động lực nghiên cứu (1–2 slides) → 1.2 Vấn đề đặt ra →
   1.3 Mục tiêu và câu hỏi nghiên cứu
4. `2. Cơ sở lý thuyết` → one subsection per concept the design depends on (with citations).
   No separate "related work" section.
5. `3. Thiết kế hệ thống` → architecture, hardware/wiring, data flow, each mechanism, protocol,
   supervisor/state machine, synchronisation …
6. `4. Phương pháp đánh giá` → metrics, experiments, fault/measurement method, hypotheses
7. `5. Tiến độ và kế hoạch` → done (honestly labelled), next steps
8. `6. Kết luận`
9. Tài liệu tham khảo (ONE slide)
10. Optional thank-you slide

Never include: out-of-scope/non-goal lists, "future work" for unstarted items, glossary slides,
internal notes like "Nguồn: PROJECT §…", evidence-tag legends, section names in the footer.

---

## 3. Preamble (visual system) – define once, never hack per slide

Start from `template/preamble-reference.tex`. Required elements:

- `\documentclass[aspectratio=169,12pt,t]{beamer}`; `\usetheme[progressbar=none,
  sectionpage=none]{moloch}`; XeLaTeX + `fontspec` with a font covering the language
  (macOS: Avenir Next; check `fc-list :lang=vi family`).
- Palette tokens: navy `#1F3A5F` (structure), teal `#2A9D8F` (accent/normal), orange `#E76F51`
  (faults only), paper `#FAFAF7`, ink `#22262B`, muted `#6B7280`, rule `#D6D9DE`.
- Frame title: navy full-width bar, white bold `\large`. Footer: only `n/N` bottom-right, muted.
  No navigation symbols. Margins 6 mm.
- Text: body `\normalsize` (12 pt) everywhere, `\linespread{1.12}`, one global list spacing
  (level 1 `\itemsep=.55em`, level 2 `.25em`, `\parsep=0pt`, patched into `\itemize` with
  etoolbox), indent `\leftmargini=1.1em`, `\leftmarginii=1.2em`, `\labelsep=.35em`. Teal square
  bullets, muted dash sub-bullets.
- Section divider via `\AtBeginSection`: centred `\Huge` navy "n. Title", nothing else.
- Figure system: counter `slidefigure`; `\figcap{…}` (increments, centred muted `\small`
  "Hình n: …" directly under the figure); `\figagain{key}` (repeats a figure with its ORIGINAL
  number); `\slideimg[maxh]{width}{Vxx}{label}` (includes `images/Vxx.jpg|png` with
  keepaspectratio, else a grey labelled placeholder so the deck always compiles).
- `\takeaway{…}`: light block with a teal left rule for the single conclusion line of a slide.
- TikZ styles: `box`, `flow` (navy Stealth arrow), `faultflow` (orange), `lbl` (label with paper
  background and inner sep). booktabs tables with ragged-right `L{width}` columns.

---

## 4. Writing rules

- Titles: numbered short noun phrases ("2.1 Kiến trúc Simplex"), never long claim sentences.
- Motivation as an argument chain: context → gap (define the key concept, e.g. throughput vs
  determinism) → consequence (late/stale data, silent failure) → why it is a safety problem →
  what is unmeasured → one bold sentence: why this project is needed.
- Define before use: "X là …" in the first bullet that introduces X; then roles; then mapping to
  our system.
- ≤ 6 lines per text column, ≤ 2 levels, ~12 words per bullet. Named parts ("Mục tiêu:",
  "Câu hỏi nghiên cứu:") are separate top-level bullets with nested items (RQ1–RQ3).
- Abbreviations expanded once, inline, at first use in a main slide: "CPU (Central Processing
  Unit)". Terms explained inside the sentence: "… giới hạn bằng cgroups (control groups — cơ chế
  giới hạn tài nguyên cho nhóm tiến trình) …". Never on cover/TOC/references; never a trailing
  definitions paragraph.
- One take-away per slide in `\takeaway{}` or a separate `$\Rightarrow$` line; never "• ⇒ …".
- Conclusion like a paper: problem and importance → contributions → potential/significance
  (who benefits, cost, reproducibility, teaching value) → status in one line → next test.
- Natural academic register of the target language; keep standard technical terms in English;
  detail goes into `\note{}` speaker notes.
- Citations: numbered `\cite{}` at the claim, moderate density, entries verified against
  primary records (publisher, DBLP, arXiv) with exact authors/venue/year/pages. References on ONE
  slide (`\footnotesize`, two columns if needed, no `allowframebreaks`).

---

## 5. Figure rules (the most-criticised area – follow exactly)

1. Text references every figure: "Hình 4 cho thấy …". Delete figures that support no point.
2. Caption directly under its own figure, centred, `\small`, muted, ideally one line, explanatory:
   "Hình 4: Kiến trúc Simplex — thành phần phức tạp chỉ đề xuất; bộ giám sát quyết định."
3. One figure = one number. Continuation slides "(tiếp)" do not repeat a figure; if unavoidable,
   use `\figagain` (same number). Numbers strictly increase — check automatically (grep captions
   in the `.aux`/rendered text) before finishing.
4. Size: two-column slides use 0.48/0.48 columns with the image as wide as its column; wide/short
   images go full width; never 2–3 small images stacked in one column; related images side by
   side as (a)/(b) subfigures, each with its own caption.
5. Comparison-image pattern: image centred → caption → one row "Trái: …" / "Phải: …" each on ONE
   line under its half → take-away at the bottom, with ~0.5em gaps.
6. Technical drawings in TikZ (protocol frames, state machines, timing exchanges, SoC block
   diagrams, profile ladders, timelines). AI images for metaphors, scenes and hardware
   illustrations.
7. TikZ hygiene: grid layout; straight arrows; horizontal labels beside arrows with clearance
   (`node[midway, above, inner sep=3pt, fill=paper]`); no sloped labels across nodes; nothing
   overlaps; components inside the correct domain boxes; maths consistent (equal slopes for
   Δ(t)=t−u(t) sawtooth); queues show arrival order and dequeue side correctly; every arrow label
   technically correct.

---

## 6. AI image batch (always deliver this, even if TikZ covers the technical figures)

When the deck needs illustrations, produce an image-prompt batch so any image tool (ChatGPT image
generation, etc.) can create them. Deliverables, under `slides/image-prompts/`:

- `README.md`: table V-id | slide | unique subject | aspect ratio | part (A/B) | save path
  `slides/images/Vxx.png`; the workflow below; a dedup check that no two subjects overlap.
- `PART_A.md` and `PART_B.md`: half of the images each, so two separate chat sessions can work
  in parallel. Each file is self-contained and begins with the SAME two blocks:
  - **STYLE GUIDE:** flat technical illustration, off-white background `#FAFAF7`, palette navy /
    teal / orange-for-faults-only, clean outlines, generous whitespace, large readable labels,
    only the labels listed in the prompt, no fake tiny text, no logos, no watermark, no
    photorealistic people, no invented numbers or measurements, one image per prompt.
  - **HARDWARE REFERENCE** (if real boards appear): exact appearance verified from official
    documentation, with explicit negatives (e.g. "Raspberry Pi 5 = GREEN PCB, 2× micro-HDMI, blue
    USB 3.0 + black USB 2.0, Ethernet, USB-C, 40-pin header; NOT blue/red/black, NO full-size HDMI.
    STM32 Nucleo-F446RE = WHITE PCB, ST-LINK section with mini-USB, blue USER + black RESET; NOT
    green, NOT a Blue Pill.").
- One fenced prompt per image, each with:
  ```text
  Generate exactly ONE image for Vxx. Do not create variants or a second image.
  UNIQUE SUBJECT: <one line>
  MUST NOT SHOW: <neighbouring subjects by V-id, charts with numbers, boards if abstract>
  ASPECT RATIO: 16:9 | 1:1 | 4:3
  Apply the STYLE GUIDE and HARDWARE REFERENCE supplied above.
  COMPOSITION: <layout, elements, what is highlighted in orange if a fault>
  BOARD KEY FACTS: <repeat the short hardware facts, only if boards appear>
  ALLOWED LABELS ONLY: <comma-separated labels>
  No added measurements, numbers, captions, watermarks or miniature text.
  ```
- Workflow written in README: paste STYLE GUIDE + HARDWARE REFERENCE first and ask for an
  acknowledgement without an image; then one prompt per message; save each image as `Vxx.png`
  before the next; never "continue" or several prompts at once; if an image repeats, open a new
  chat and paste the setup blocks again.
- Plan each image for its slot: state on which slide and at what size it will appear (half slide,
  full width, square) so the composition fits; prefer one strong image per slide over several
  small ones.
- After images arrive: generators rename files; map them to V-ids by looking at the content,
  record `slides/images/MAPPING.md` (original name | what it shows | fits slot? | hardware check),
  downscale (`sips -Z 1920`) and convert to JPEG q85; regenerate only images with wrong hardware,
  duplicated content or garbled text.

---

## 7. Build and inspect loop

Mode A (you can run commands):
1. `cd slides && latexmk -xelatex -interaction=nonstopmode main.tex`
2. `grep -E "^!|Overfull|Underfull|Missing character|undefined" main.log` → must be empty.
3. `swift render.swift main.pdf preview` (or `pdftoppm -png -r 110 main.pdf preview/page`).
4. Look at a contact sheet of all pages, then open every page at full size; fix; repeat.
5. Optional polish: run the builder/reviewer loop (`template/review_loop.sh`) for at most two
   rounds: a strict reviewer scores every page 1–5 with exact fixes and `VERDICT: PASS/FAIL`; the
   builder fixes every item. Then let the human owner give page-specific feedback and fix only
   those pages.

Mode B (no shell): deliver complete files; tell the user the exact build command; ask for
screenshots of all pages (or the PDF) and review them against Section 8 before declaring done.

---

## 8. QA checklist (all must hold on every page)

- [ ] Build clean: 0 errors, 0 overfull/underfull, 0 missing characters, 0 undefined citations.
- [ ] Content starts top-left; slide evenly filled; no accidental empty band or empty half.
- [ ] Body 12 pt; identical bullet spacing on all slides; small indent; ≤ 6 lines per column.
- [ ] Nested bullets for named parts; no "• ⇒"; no trailing definitions paragraph.
- [ ] Every figure large, centred, captioned directly below, numbered uniquely, referenced in text.
- [ ] Nothing overlaps (labels, arrows, nodes, captions, text).
- [ ] Abbreviations expanded once at first main use; none on cover/TOC/references.
- [ ] Numbers carry their status; no invented data; citations verified.
- [ ] Cover centred and balanced (title larger and high; team block centred, members slightly
      smaller than the supervisor line); TOC as an even column of numbered boxes; references on
      one slide.
- [ ] Natural wording; titles are numbered noun phrases; conclusion paper-style.

---

## 9. Output contract (what to hand back each time)

1. Files changed (paths) and a one-line summary per file.
2. Page list: number + title.
3. Build status (copy the grep result) and how many pages you inspected visually.
4. Figures used / dropped, and the figure-number check result.
5. Open issues you could not fix, with the reason.
6. If images are needed: the image-prompt batch location and which V-ids to (re)generate.

---

## 10. Known pitfalls (from real mistakes)

- Long claim-sentence titles and stacked evidence tags make the deck look like notes.
- Splitting a slide and repeating its figure with a new number confuses readers.
- `\scriptsize` to make text fit is unreadable; split the slide instead.
- PNG photos inflate the PDF (40 MB); use JPEG.
- `codex exec` waits on stdin unless run with `</dev/null`; detect quota errors by the exact
  "usage limit" message, not by the word "quota" anywhere in the output.
- Opening the PDF while it is rebuilding shows an error; wait for the build.
- Never reset or overwrite `main.tex` while another agent is working on it; never discard work
  the owner has already reviewed.
