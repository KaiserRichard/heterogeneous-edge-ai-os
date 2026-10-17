# TICKET R-VI-2: fix length and polish (follow-up to report_vi/TICKET.md)

Do not git commit. Append to logs/R-VI-summary.md.

Measured by the conductor in Microsoft Word: the current .docx is 29 pages (Word statistics: 6,883 words incl. tables).
Requirement is 15-20 pages. Target 17-19 Word pages.

1. Remove all `<!-- PAGE -->` forced breaks except: after the cover, after the abstract, after the TOC.
   Chapters flow continuously (Heading 1 keeps keepNext + some space before; no page break before chapters).
   Make sure no empty paragraphs create blank space; tables and figures must not leave half-empty pages
   (keepNext only on captions/headings, not whole tables).
2. Trim body text to about 5,300-5,600 words (Word count incl. tables ~6,000). Cut repetition and hedging duplicates,
   not evidence. Keep every table/figure, but limit figures to max 12 cm width and 8 cm height.
3. In the body, do not cite repository file names (e.g. "Theo PROJECT.md", "docs/STAGE_REPORT.md").
   Use neutral wording ("theo tài liệu thiết kế của nhóm"). Run directories may stay only in table notes
   ("Nguồn: results/2026-10-12_e4_faults") or move to a short "Phụ lục: Nguồn dữ liệu" at the end.
4. Keep all hard rules from TICKET.md: Vietnamese, "đang trong quá trình triển khai", "kết quả sơ bộ", no invented numbers,
   stdlib-only builder. Rebuild report_vi/BaoCao_HDH_Nhom3Stars.docx and rerun the ZIP/XML validation.
