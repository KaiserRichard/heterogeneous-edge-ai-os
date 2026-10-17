# TICKET R-VI-7: fit in 20 pages (no GUI apps)

Do not git commit. Do NOT open, launch or script any GUI application (Microsoft Word, WPS, Pages, Preview, osascript).
Headless Python only. Append a short note to logs/R-VI-summary.md.

Measured: the current .docx renders to 24 Word pages (6,777 Word words incl. the glossary table and tables), with line spacing 1.3
and 13 pt tables. The conductor has since changed build_docx.py to line spacing 1.2 (w:line=288), paragraph after 4 pt and
table text 11 pt, and added schema-order sorting of pPr/rPr (keep both). That alone is estimated to save ~2 pages; the
target is <= 20 pages, so:
1. Cut body prose from ~5,190 to about 4,500 words (style_check.py must still pass the TICKET5 targets). Cut repetition first,
   then secondary detail; keep every table, number, figure, the RQ list, the "đang trong quá trình triển khai" framing.
2. Glossary: keep only terms actually used in the text, at most ~32 rows, explanations <= 12 words, 11 pt text (GlossaryText 22).
3. Figures max 12 cm wide and 6.5 cm tall.
4. Set <w:updateFields w:val="true"/> in word/settings.xml so Word refreshes the TOC when the student opens the file
   (the TOC must still contain a correct static entry list as fallback).
5. Rebuild, rerun validation, forbidden-text scan and style_check. Also check every w:pPr/w:rPr child order is schema-valid.
