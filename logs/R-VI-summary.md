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
