# R-VI — Vietnamese course report

Completed 2026-10-17 without a git commit. Only report_vi/ and this log were changed.

## Deliverables

- report_vi/BaoCao_HDH_Nhom3Stars.docx
- report_vi/content.md: Vietnamese report with the exact requested cover details and section order.
- report_vi/build_docx.py: offline standard-library OOXML builder.
- report_vi/validate_docx.py and validation.json: reproducible structural checks.
- report_vi/figures/: copied V14, V15, V20; conceptual illustrations, with captions and provenance.
- report_vi/README.md and source_manifest.json: rebuild instructions, limitations, source hashes.

## Content and evidence

Read PROJECT.md and AGENTS.md; used the final slides_course/main.tex (including notes),
approved Vietnamese deck, required guides/roadmaps, stage report and retained results.
6094 whitespace-delimited body words including tables and source lines; seven tables,
three numbered figures. Eight bibliography entries come from the supplied deck
bibliographies, with in-text IEEE citations. Every quantitative result has a source
folder/deck attribution; table notes explain aggregation and scope.

The report describes the system as “đang trong quá trình triển khai” and all measured
findings as “kết quả sơ bộ.” It preserves đã đo / đã tính / dự kiến / chưa biết,
FLAGGED/INVALID exclusions, under-voltage, v1/v2 rule changes, PTY vs physical scope,
reason-specific timing, and GPIO vs actuator limits. RUN is explicitly mapped to
FRESH in current code/logs. IRQ/bounded-buffer design is distinguished from current
DMA reception. Original UART E3 and the final-deck rerun are separate datasets;
rerun numbers cite the deck's release path rather than misattributing them to the
older retained folder. Historical “no analyzer yet” statements are reconciled with
later captures without promoting collection-wide validity.

## Validation performed

`python3 report_vi/validate_docx.py` passed: ZIP CRC; all XML/.rels parsed with
xml.dom.minidom; internal relationship targets; A4/margins; required styles;
TOC/updateFields; cover section without footer and following section with PAGE;
seven tables and three embedded images; word-count range; identical bytes over
two builds. Also ran the ticket's direct python -c zipfile/minidom validation.
No pip, network, third-party Python package, hardware execution or commit.

## Remaining verification limit

There are 20 explicit page layout blocks including cover, abstract and TOC.
Actual Word-rendered pagination could not be checked: no Word/LibreOffice renderer
is available on this host. The JSON deliberately leaves rendered_page_count null.
Open in Word and update fields before submission; font metrics/TOC may change
pagination. All hardware findings were read from retained sources, not remeasured.

## R-VI-2 — length and polish, 2026-10-17

Rebuilt report_vi/BaoCao_HDH_Nhom3Stars.docx without a commit. Retained exactly
three forced breaks after cover, abstract and TOC; removed every body break.
Chapters flow continuously with heading keepNext/spacing and no pageBreakBefore.
No blank Markdown paragraphs become empty layout paragraphs. Tables have no
keepNext; rows remain individually intact and headers repeat across pages.
All seven tables and three figures remain; figures preserve aspect ratio within
12 cm width and 8 cm height. Body reduced from 6094 to 5597 whitespace words,
including tables and source notes. Repeated framing was trimmed; numerical table
cells, evidence labels, FLAGGED/INVALID and under-voltage qualifications remain.
Repository citations in prose were replaced with neutral wording; provenance is
in table notes or a short final appendix. Vietnamese implementation-status and
preliminary-result language remains.

Updated the stdlib-only validator and README. Validation passed: two identical
builds, ZIP CRC, every XML/.rels parsed with minidom, relationship targets,
A4/margins/fonts/styles/TOC/footer, exactly three front-matter breaks, no chapter
pageBreakBefore, no table keepNext, and all figure extents within limits. Also
reran the ticket's direct python -c ZIP/XML check on the rebuilt artifact.

Target remains 17–19 Word pages. Actual rendered pagination and Word statistics
cannot be measured here: no Word/LibreOffice renderer is available. validation.json
explicitly records rendered_page_count=null. Open in Word and update fields for
final pagination verification; no claim that the target has already been rendered.

## R-VI-3 — clean submission version, 2026-10-17

Rewrote the Vietnamese prose and rebuilt the submission DOCX without a commit.
Removed repository paths, source appendix, internal evidence labels and production
instructions from document text. Added the requested centered cover and members
table, uppercase chapter headings, 1 cm body indentation, 6 pt paragraph spacing,
and 12 pt italic captions. Retained seven report tables with identical numeric
tokens and all three figures; the cover adds one separate members table.
Body length is 5808 whitespace words including tables. ZIP/XML, relationships,
formatting, forbidden-text grep and reproducible-build checks passed. Updated
README, validator and validation.json. Actual 16–19-page Word pagination remains
unverified because no Word/LibreOffice renderer is available; no hardware rerun.

R-VI-4 — 2026-10-17: Rewrote prose across all eight chapters and abstract, grouped RQ prompts, explained specific table rows, retained every original numeric value/heading/table/figure and preliminary/implementation framing; rebuilt DOCX without changing builder/layout or committing; 5980 body / 6420 total whitespace words (under 3% growth), structural/reproducible-build/ZIP/XML/forbidden-text and preservation checks PASS; appended this line; Word pagination remains unverified because local Word automation failed.


## R-VI-5 — connected prose rewrite, 2026-10-17

Edited only `report_vi/content.md` as the source, regenerated the DOCX and
`validation.json`, and appended this log; no commit. Existing edits to README,
builder, validator and other files were preserved, not authored by this ticket.
Reworked the argument across all eight chapters using causal and contrastive
links, with longer explanations interspersed with short statements and related
ideas grouped into paragraphs. Removed the rhetorical question outside the RQ
list and corrected the accidental “Lượttime” spelling to “Runtime”.

Exact `python3 report_vi/style_check.py` output before editing:

```text
sentences=259 mean=16.3 median=17 stdev=8.6 share>=28=0.07 share<=12=0.30
paragraphs=51 mean_sentences_per_para=5.1
```

Exact `python3 report_vi/style_check.py` output after editing:

```text
sentences=204 mean=24.7 median=24.0 stdev=9.3 share>=28=0.38 share<=12=0.12
paragraphs=50 mean_sentences_per_para=4.1
```

All requested ranges pass. The checker itself was not edited. It splits on blank
lines, so the source now separates headings from prose and keeps cover/front
matter and bibliography entries in consecutive non-prose blocks. Their displayed
text and individual Word paragraphs remain intact because the builder consumes
lines. This prevents bibliography author initials from counting as short prose
sentences; the raw before/after outputs therefore differ in selection as well as
writing. An independent check selecting actual body prose lines confirms the
rewrite rather than relying on this formatting effect: before mean=18.58, stdev=5.61, share>=28=0.054, share<=12=0.158, sentences/paragraph=4.55;
after mean=24.91, stdev=9.33, share>=28=0.394, share<=12=0.116,
198 sentences / 49 paragraphs = 4.04 sentences per paragraph. This also passes
every requested range.

Preservation checks PASS against the exact pre-ticket content: every heading,
table row, numbered caption, figure and RQ list entry matches; no numeric token
occurrence was lost. Both implementation-in-progress and preliminary-results
framing remain. Body length including tables is 6230 whitespace words versus
5980 before (+4.2%); no findings or measured results were added.

Ran `python3 report_vi/validate_docx.py`: PASS for two byte-identical builds,
ZIP CRC, XML/.rels parsing, relationship targets, A4 layout/styles/TOC/footer,
seven report tables plus cover table, three figures and continuous body flow.
Forbidden-text scan PASS for the validator's internal-material pattern; separate
scans of Markdown and extracted DOCX text found none of the four banned phrases,
zero occurrences of “Do đó” / “Điều này cho thấy”, and no prose rhetorical
questions outside the preserved RQ list.

Pagination remains unverified. Microsoft Word is installed, but a fresh
`osascript` version query failed with a macOS service connection error and
“Can't get application Microsoft Word” (-1728); no LibreOffice executable is
available. No claim that the <=19-page requirement has been verified: the JSON
keeps `rendered_page_count=null`. Layout settings and the three front-matter
breaks were preserved; actual pagination still requires Word rendering. The
existing preview PDF was not regenerated and is not evidence for this revision.
No hardware measurements were rerun.

## R-VI-6 — student feedback, 2026-10-17

Renamed eight chapters to PHẦN; retained conventional English engineering terms,
added an alphabetically ordered 45-row front-matter glossary, and implemented
Heading 1 pageBreakBefore for all Phần and references. Tightened body to 5,189
whitespace words including tables. All seven original body tables match verbatim;
comparison against the pre-ticket source found no lost numeric token occurrence.
Replaced three slide illustrations with four 200-dpi matplotlib diagrams (AoI,
architecture, frame and queues), capped at 13 × 7.5 cm. Reviewed all four images;
CRC coverage excludes SOF and CRC, FIFO sends oldest first, and current DMA versus
conceptual ISR distinction remains in prose. Added four <120-word English redraw
prompts, updated README and validator, and rebuilt the DOCX. No commit.

Style before: sentences=204 mean=24.7 median=24.0 stdev=9.3 share>=28=0.38
share<=12=0.12; paragraphs=50 mean_sentences_per_para=4.1.
Style after: sentences=144 mean=25.6 median=26.0 stdev=9.3 share>=28=0.42
share<=12=0.10; paragraphs=36 mean_sentences_per_para=4.0. TICKET5 targets pass.
Validation passes: byte-identical builds, ZIP/XML/relationships, dimensions,
page-break style, tables, four figures, glossary sorting/count, required framing,
forbidden internal text and banned prose phrases. Prompt lengths pass.

The <=20-page requirement remains unverified: Word automation failed with macOS
service connection errors and -1728; LibreOffice is unavailable. validation.json
honestly retains rendered_page_count=null. No hardware measurements were rerun.


### TICKET R-VI-7 — rút gọn, headless Python

- Thân bài 5,189 → 4,565 từ (kể cả bảng); giữ nguyên bảy bảng nội dung,
  mọi heading, số liệu, bốn hình, danh sách RQ và framing đang triển khai/kết quả sơ bộ.
- Thuật ngữ còn 25 dòng, chỉ giữ từ dùng trong thân bài; giải thích ≤12 từ,
  GlossaryText 22 (11 pt). Hình ≤12 × 6.5 cm. Giữ giãn dòng 1.2, cách đoạn
  4 pt, bảng 11 pt, schema-order sorting và updateFields=true; TOC tĩnh khớp headings.
- Trước: sentences=144 mean=25.6 median=26.0 stdev=9.3 share>=28=0.42 share<=12=0.10;
  paragraphs=36 mean_sentences_per_para=4.0.
- Sau: sentences=136 mean=23.2 median=23.0 stdev=9.1 share>=28=0.34 share<=12=0.13;
  paragraphs=33 mean_sentences_per_para=4.1. Tất cả mục tiêu TICKET5 PASS,
  nay được assert trong style_check.py.
- Rebuild hai lần giống byte; validation và forbidden-text scan PASS; kiểm tra
  thứ tự schema của toàn bộ 779 pPr/rPr PASS. So sánh nguồn trước/sau xác nhận
  bảng, heading, hình, RQ và tập token số của thân bài được giữ nguyên.
- Không mở/chạy/script ứng dụng GUI, không git commit. Mục tiêu ≤20 trang;
  số trang sau rút gọn chưa được đo, rendered_page_count=null.
