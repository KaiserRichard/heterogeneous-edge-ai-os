# TICKET R-VI-9: cover with HUST logo, blank page, figure size, table padding

Do not git commit. No GUI apps, no osascript, headless Python only. Append one line to logs/R-VI-summary.md.
Only change the layout/builder (build_docx.py, content.md markers, figures/). Do not change the prose or numbers.

Student feedback (the student opened the .docx in Word on macOS):
1. Cover: they added the HUST logo at
   /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/images/logo_hust.jpg (copy it into report_vi/figures/).
   Make a classic HUST report cover: double-line page border on the cover page only (cover is its own section; use
   w:pgBorders with w:val="double" or "thinThickSmallGap", offsetFrom="page", ~24 pt from edge), centered:
   "ĐẠI HỌC BÁCH KHOA HÀ NỘI" (bold 14), a short horizontal rule, the logo (about 3.0 cm wide, aspect kept),
   "BÁO CÁO BÀI TẬP LỚN" (bold 16), "HỌC PHẦN: HỆ ĐIỀU HÀNH" (bold 14), title "NỀN TẢNG THỰC THI EDGE-AI
   KHÔNG ĐỒNG NHẤT" (bold 20, blue #1f5fa8 is fine or black), subtitle italic "Heterogeneous Edge-AI Runtime",
   then the members table, "Giảng viên hướng dẫn: TS. Nguyễn Quang Minh", "Mã lớp bài tập: 173876",
   and "Hà Nội, 10/2026" at the bottom. Everything must fit on page 1 (A4) with the border.
2. Page 3 is blank in Word. Cause: front matter uses separate paragraphs with <w:br w:type="page"/>; when the TOC fills page 2
   the break paragraph spills onto page 3 and leaves it empty. Remove all explicit page-break paragraphs; instead put
   <w:pageBreakBefore/> on the front-matter headings (TÓM TẮT not needed since it follows the cover section break,
   MỤC LỤC, DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT) and keep it on Heading 1 / TÀI LIỆU THAM KHẢO.
   Also make sure there is no empty paragraph directly before any section break or heading with pageBreakBefore.
3. Figures look far too small on the page. Insert all figures at the full text width (page width 21 cm minus margins
   3 cm left and 2 cm right = 16 cm), height capped at 10 cm (scale down only if taller), aspect preserved.
4. Table text touches the cell borders in Word. Add cell padding for all tables: tblCellMar left/right 115 twips (~0.2 cm),
   top/bottom 60 twips, and vertical-align center for header cells. Keep the glossary readable (3 columns, set column widths
   roughly 25% / 35% / 40% instead of equal widths).
5. Keep the pPr/rPr schema-order sorting, updateFields, validation, forbidden-text scan. Rebuild report_vi/BaoCao_HDH_Nhom3Stars.docx.
