# Slide Playbook: how to build an academic Beamer deck like this one

Written 2026-10-07 from the full history of building `slides/main.tex` (Vietnamese, XeLaTeX,
moloch, 45 pages). Part 1 is a ready-to-paste master prompt. Parts 2–10 are the skills and rules
behind it, in detail. Part 11 lists the mistakes we made and how to avoid them.

---

## Part 1. Master prompt (paste this to the AI, then attach the content sources)

> You are building an academic presentation deck as a LaTeX Beamer document compiled with
> XeLaTeX. You must produce a deck that reads like a scientific paper and looks like a
> professional conference talk. Follow the playbook below exactly (Parts 2–11). Work in this
> order: (1) read all content sources and extract the argument; (2) write the outline as numbered
> sections/subsections and get it approved; (3) write the preamble; (4) write the frames;
> (5) build; (6) render every page to PNG and inspect each page at full size; (7) fix; repeat
> 5–7 until the QA checklist (Part 9) passes. Never report "done" without having looked at every
> rendered page. Never invent measurements or citations. Language of slide text: <LANGUAGE>;
> keep standard technical terms in English. Audience: <AUDIENCE, e.g. supervising lecturer
> reading alone>. Length: <N> pages.
> Inputs: <list of source docs>, images in `slides/images/Vxx.jpg` with `MAPPING.md`
> describing what each image shows, team/cover data: <...>.

---

## Part 2. Toolchain skills

- **LaTeX/Beamer:** `\documentclass[aspectratio=169,12pt,t]{beamer}` (16:9, 12 pt base, all frames
  top-aligned by default). Theme `moloch` (maintained fork of metropolis) with
  `progressbar=none, sectionpage=none`; custom section pages via `\AtBeginSection`.
- **XeLaTeX + fontspec** for Unicode (Vietnamese diacritics). Use a system font that has all
  glyphs, e.g. `\setsansfont{Avenir Next}[BoldFont={Avenir Next Demi Bold}]` on macOS. Verify with
  `fc-list :lang=vi family` and by grepping `main.log` for `Missing character`.
- **Build:** `latexmk -xelatex -interaction=nonstopmode main.tex`. Clean: `latexmk -c`.
- **Log hygiene:** `grep -E "^!|Overfull|Underfull|Missing character|undefined" main.log` must
  return nothing.
- **Rendering for visual QA:** convert each PDF page to PNG and look at it. On macOS without
  poppler, a 30-line Swift PDFKit script (`slides/render.swift`):
  `swift render.swift main.pdf preview` → `preview/page-01.png …`. Make a contact sheet with
  Python PIL to see the whole deck at once, then open suspicious pages at full size.
- **Packages used:** tikz (+ libraries arrows.meta, positioning, calc, fit, backgrounds,
  decorations.pathreplacing), booktabs, array (ragged-right `p` columns), amsmath, siunitx,
  etoolbox, graphicx.
- **Images:** keep JPEG q85 at ≤1920 px (`sips -Z 1920`, `sips -s format jpeg`) — PNG photos made
  the PDF 40 MB; JPEG brought it to ~6–9 MB.
- **Git:** `.gitignore` for aux files, `main.pdf`, `preview/`. Commit source + images only.

---

## Part 3. Preamble design (the visual system)

Define everything once in the preamble; never fix layout per slide with ad-hoc hacks.

1. **Palette tokens** (`\definecolor`): navy `#1F3A5F` (structure, titles), teal `#2A9D8F`
   (accents, normal operation), orange `#E76F51` (faults/failure ONLY), paper `#FAFAF7`
   background, ink `#22262B` text, muted `#6B7280` captions/footer, rule `#D6D9DE`. Map them to
   beamer colors (`normal text`, `frametitle`, `structure`, `block title/body`, `footline`,
   bibliography entries).
2. **Frame title:** navy full-width bar, white bold `\large` text, numbered noun phrase.
3. **Footer:** only `n/N` page number bottom-right in muted `\small`. No section name, no logo,
   no navigation symbols (`\setbeamertemplate{navigation symbols}{}`).
4. **Text size and rhythm:** body `\normalsize` (12 pt) everywhere; `\linespread{1.12}`;
   one global item spacing: first-level `\itemsep=.55em`, second-level `.25em`, `\parsep=0pt`
   (patch `\itemize` with etoolbox so every list is identical). Indent small:
   `\leftmargini=1.1em`, `\leftmarginii=1.2em`, `\labelsep=.35em`.
   Bullets: small teal square; sub-bullets: muted dash.
5. **Margins:** `\setbeamersize{text margin left=6mm,text margin right=6mm}`.
6. **Section divider:** `\AtBeginSection{\begin{frame}[c]\centering{\Huge\bfseries\color{navy}
   \thesection. \insertsectionhead}\end{frame}}` — big centred heading only.
7. **Figure numbering:** own counter + macros so every figure gets "Hình n:" automatically and a
   repeated figure keeps its original number:
   - `\figcap{text}` → increments counter, prints centred muted `\small` caption under the figure.
   - `\figagain{key}` / `\repeatassetcap{key}` → prints the SAME number and caption again
     (no increment) when a figure must be shown twice.
8. **Image macro with placeholder:** `\slideimg[maxheight]{width}{Vxx}{label}` includes
   `images/Vxx.jpg` (or `.png`) with `keepaspectratio`, otherwise draws a grey labelled box of the
   same size so the deck compiles before images exist.
9. **Take-away box:** `\takeaway{…}` — a light block with a teal left rule, used for the one
   conclusion line of a slide. Replaces "• ⇒ …".
10. **TikZ styles** (`\tikzset`): `box` (navy outline, white fill, rounded 2pt), `flow` (navy arrow,
    Stealth tip), `faultflow` (orange arrow), `lbl` (label with paper-coloured background and
    inner sep so it never hides a line). All diagram fonts `\normalsize`.
11. **Tables:** booktabs rules only (`\toprule \midrule \bottomrule`), ragged-right `L{width}`
    columns, `\arraystretch≈1.0–1.2`.

---

## Part 4. Deck structure (scientific-paper skill)

The deck must follow the logic of a paper, with numbered sections and subsections:

1. **Cover** — native-language title (large, centred, symmetric line break), English subtitle
   centred below, then a centred team block ("Nhóm thực hiện: …", members with student IDs,
   "GVHD: …", class code) in sizes that balance each other; one meaningful image only if it keeps
   the cover balanced. No term explanations on the cover.
2. **Table of contents** — a vertical column of equal boxes, each with a coloured number square
   and the section name, filling the slide height evenly. Nothing else on it.
3. **1. Introduction** — 1.1 Motivation (can take 2 slides), 1.2 Problem, 1.3 Objectives and
   research questions.
4. **2. Background/theory** — only the concepts the design depends on, each with citations.
   No separate "related work" section; fold citations in here.
5. **3. System design** — architecture, hardware, data flow, mechanisms, protocol, supervisor,
   clock sync — one subsection per mechanism.
6. **4. Evaluation method** — metrics, experiments, fault-injection method, hypotheses.
7. **5. Progress and plan** — what is done (honestly labelled), next steps.
8. **6. Conclusion** — paper-style (see Part 5).
9. **References** — ONE slide, compact.
10. Optional thank-you slide.

Remove: "out of scope"/non-goals lists, "future work" for things not started, glossary slides,
internal source notes ("Nguồn: PROJECT §…"), evidence-tag legends.

---

## Part 5. Writing skills

- **Motivation must motivate.** Build an argument chain: context (why this kind of system
  matters) → the gap in today's approach (define the key concept, e.g. throughput vs
  determinism) → the concrete consequence (late/stale data, silent failure) → why it is a safety
  problem, not only performance → what nobody has measured → one bold sentence: why this project
  is needed.
- **Define before use.** The first bullet that introduces a concept starts with "X là …"
  ("Simplex là kiến trúc …"). Then roles, then mapping to our system.
- **Titles:** numbered short noun phrases ("2.1 Kiến trúc Simplex"), not long claim sentences.
- **Bullets:** ≤ 5–6 lines per text column, ≤ 2 levels, ~12 words each, simple complete
  phrases. Named parts get their own top-level bullet with nested items (e.g. "Mục tiêu:" and
  "Câu hỏi nghiên cứu:" with RQ1–RQ3 as sub-bullets).
- **Abbreviations:** expand once, inline, at first use in a main slide: "CPU (Central Processing
  Unit)". Explain a term inside the sentence: "… giới hạn bằng cgroups (control groups — cơ chế
  giới hạn tài nguyên cho nhóm tiến trình) …". Never a trailing paragraph of definitions, never
  on cover/TOC/references.
- **Take-aways:** one per slide max, in `\takeaway{}` or as a separate line with `$\Rightarrow$`;
  never a bullet followed by an arrow.
- **Conclusion like a paper:** restate the problem and why it matters; contributions of the
  design; potential and significance (who benefits, cost, reproducibility, teaching value);
  current status in one line; what is tested next.
- **Language quality:** natural academic register of the target language; no calques, no odd
  English–native mixes; re-read every slide aloud before finishing.
- **Speaker notes:** detail goes into `\note{}` in the same language, not onto the slide.

---

## Part 6. Evidence and citation discipline

- Never present a design value as a measurement. Write "dự kiến" (planned) for design values,
  "kiểm thử trên máy tính" for host-test results, and a citation for published numbers
  ("theo [6], 1,8 ms → 0,22 ms") — and say explicitly it is their result, not ours.
- Charts of published numbers must be labelled as such in the caption.
- Citations: numbered `\cite{}` → [1], [2] at the claim; moderate density. Verify every
  bibliography entry against a primary record (publisher, DBLP, arXiv) before using it; record
  exact authors, venue, year, pages. Do not cite internal repo files.
- References on ONE slide: `\footnotesize` entries, one or two lines each, two columns if
  needed, no `allowframebreaks`.

---

## Part 7. Figure skills (the most criticised area)

1. **Every figure serves an argument.** The slide text says what to look at: "Hình 4 cho thấy …".
   If a figure cannot be tied to a point, delete it (decorative AI images were removed).
2. **Caption directly below its own figure**, centred, `\small`, muted, one line preferred,
   explanatory: "Hình 4: Kiến trúc Simplex — thành phần phức tạp chỉ đề xuất; bộ giám sát đơn giản
   quyết định cuối cùng." Never two captions stacked under one image row; for two images use
   subfigures (a)/(b) each with its own caption.
3. **One figure, one number.** A figure shown again (e.g. on a "(tiếp)" slide) keeps its number
   (`\figagain`), or better is not repeated and is referenced in text ("như Hình 6"). Numbers
   strictly increase; check this automatically before finishing.
4. **Size and balance:** in two-column slides use 0.48/0.48 columns with the image as wide as its
   column; wide/short images get a full-width layout; never two or three small images stacked in
   one column; no image floating in empty space. Image + caption + explanation row + take-away
   must be evenly spaced (leave ~0.5em between caption and the next row).
5. **Image + explanation pattern (e.g. a left/right comparison image):** image centred → caption
   below → one row with "Trái: …" and "Phải: …" each on ONE line under the matching half →
   take-away at the bottom.
6. **Prefer TikZ for anything technical** (protocol frame, state machine, timing exchange,
   block diagrams such as the SoC memory hierarchy, profile ladder, timelines): it is accurate,
   editable and matches the palette. Use AI images only as illustrations/metaphors.
7. **TikZ hygiene:** lay nodes on a clear grid; straight arrows; horizontal labels beside arrows
   with clearance (`node[midway, above, inner sep=3pt, fill=paper]`); no sloped labels crossing
   node borders; no label on top of an arrow or another label; group components in explicit
   domain boxes and keep each node inside its correct domain (e.g. Failsafe/Output inside the
   STM32 box); for plots, keep the maths consistent (a sawtooth Δ(t)=t−u(t) has the same slope on
   every rising segment); queues show arrival order and dequeue direction correctly (oldest at
   the send end).
8. **Correctness of labels:** every arrow label must be technically right (e.g. HOLD→FAILSAFE is
   "Hết thời gian chờ", only FRESH→FAILSAFE is "Mất heartbeat").

---

## Part 8. AI image generation skills (when illustrations are needed)

- Write prompts in two self-contained halves for two chat sessions, each starting with an
  identical STYLE GUIDE (flat technical illustration, palette, off-white background, no fake
  text, no watermark) and HARDWARE REFERENCE (exact board appearance verified from official
  docs, plus explicit negatives: "Pi 5 is NOT blue, has NO full-size HDMI; Nucleo is WHITE, not a
  Blue Pill").
- Per image: "Generate exactly ONE image for Vxx", UNIQUE SUBJECT, MUST NOT SHOW (naming the
  neighbouring V-ids), aspect ratio, allowed labels only.
- Workflow: paste setup once; one prompt per message; save as `Vxx`; never "continue"; on
  repetition start a new chat.
- Generators rename files; map them back to V-ids by looking at the content and record the map in
  `images/MAPPING.md` (original name, what it shows, fit, hardware check).

---

## Part 9. QA checklist (must pass before saying "done")

Build: 0 errors, 0 overfull/underfull boxes, 0 missing characters, 0 undefined citations.
For EVERY rendered page at full size:
- [ ] Content starts top-left; no large accidental empty band; nothing crammed in a corner.
- [ ] Body text is 12 pt; spacing between bullets identical to other slides; small indent.
- [ ] ≤ 6 lines per column; nested bullets for named parts.
- [ ] Each figure is large, centred in its column, caption directly below it, numbered, unique.
- [ ] No overlap anywhere (labels, arrows, nodes, captions, text).
- [ ] Every figure is referenced and explained in the text.
- [ ] Abbreviations expanded once at first main use; none on cover/TOC/references.
- [ ] No "• ⇒", no trailing definition paragraphs, no internal "Nguồn:" notes.
- [ ] Numbers carry their status (planned / host-tested / cited); nothing invented.
- [ ] Cover symmetric and balanced; TOC boxes even; references on one slide.
- [ ] Wording natural; titles numbered noun phrases.

---

## Part 10. Multi-agent workflow (how the final quality was reached)

- **Spec first:** a slide-by-slide spec file (`RESTRUCTURE_SPEC.md`) with exact titles, bullets,
  captions and image choices, then owner-feedback files (`REVISION_V4.md`,
  `OWNER_FIXES_V6.md`) that take precedence.
- **Builder/reviewer loop** (`slides/review_loop.sh`): a builder agent edits `main.tex` following
  `LAYOUT_BRIEF.md`; a separate strict reviewer agent (different account) builds, renders every
  page, scores each page 1–5 against the rubric and writes `review/latest.md` with page | defect |
  exact fix and a final `VERDICT: PASS/FAIL`; the builder fixes every item next round. Two rounds
  plus one targeted fix pass were enough; more rounds cost tokens with diminishing returns.
- **Only one agent edits `main.tex` at a time.** Stop a running job before starting another.
- **The human owner is the final reviewer:** after the loop, ask for page-specific feedback and
  fix only those pages.

---

## Part 11. Mistakes we made (avoid them)

1. Long claim-sentence titles and stacked evidence tags → looked like notes, not a paper.
2. Abbreviation explanations as a paragraph at the bottom of slides → ugly; expand inline.
3. Section name in the footer, glossary slide, "out of scope", "future work" → clutter.
4. Small images in narrow columns, two captions under one row, captions far from images.
5. Splitting a slide into "(tiếp)" and repeating the figure with a NEW number.
6. "• ⇒ conclusion" bullets; uneven line spacing from per-slide `\vspace` hacks.
7. Vertically centred content leaving the top half empty; empty right half on the cover.
8. TikZ labels sloped across nodes; wrong technical label on an arrow; wrong queue order;
   inconsistent sawtooth slopes; a component drawn in the wrong domain.
9. `\scriptsize` to make text fit → unreadable; split the slide instead.
10. PNG images → 40 MB PDF; use JPEG.
11. Tooling: `codex exec` waits on stdin unless given `</dev/null`; a quota check that greps for
    "quota" anywhere in the output gives false positives (match the exact usage-limit error);
    opening the PDF while it is being rebuilt shows an error; resetting files while a builder is
    running discards work the owner may already have seen.
