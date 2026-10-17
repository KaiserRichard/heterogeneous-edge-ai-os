# TICKET R-VI-3: clean, human-sounding final version for submission

Do not git commit. Append a short note to logs/R-VI-summary.md.

The student opened the .docx and rejected it: "I asked for a final version to submit, why is there all this junk in the file?
Send me a clean file. Also the Word file looks too AI-written, make it look more human."

Rewrite report_vi/content.md (and adjust build_docx.py) so the .docx is a normal, clean Vietnamese student course report
(báo cáo bài tập lớn môn Hệ điều hành) that can be submitted as-is.

## Remove completely from the document
- Every file path, repository path, run-folder name, timestamped run id, CSV/MD/TeX file name, branch name, ticket id,
  "Nguồn: results/..." notes under tables, and the "Phụ lục: Nguồn dữ liệu" appendix.
- Internal evidence tags and bookkeeping words: FLAGGED, INVALID, MEASURED, SIM, PLANNED, "đã đo / đã tính / dự kiến"
  used as labels, "v2 validity rule", references to "deck", "bản trình bày", "conductor", "provenance", "Không có kết quả
  mới được tạo ra trong quá trình soạn báo cáo", notes addressed to the reader about how the report was produced.
  Where it matters, say it in plain words once: e.g. "một số lượt đo dưới tải bị ảnh hưởng do nguồn cấp sụt áp nên
  chỉ được dùng để tham khảo".
- Any placeholder, HTML comment leaking into the text, or English meta-text.

## Style: write like a careful Vietnamese engineering student, not an AI
- Connected prose paragraphs with varied sentence length; explain cause and effect. Use bullets rarely (at most 3 short
  lists in the whole report), never "**Label:** text" bullets.
- No formulaic openers/closers ("Tóm lại,", "Nhìn chung,", "Điều này cho thấy..." at every paragraph end), no repeated
  hedging. State limitations once, clearly, in chapter 6.
- Use "nhóm" / "chúng em" naturally ("Nhóm đã đo...", "chúng em nhận thấy..."). English technical terms in parentheses
  only on first use (e.g. độ tươi dữ liệu (Age of Information, AoI)).
- Profiles: name them in words on first use, e.g. "cấu hình mặc định (P0)" and "cấu hình tối ưu thời gian thực (P1)".
- Framing stays: the system is still being deployed ("đang trong quá trình triển khai"), results are preliminary
  ("kết quả sơ bộ / bước đầu"). Do not claim full deployment.
- Keep all numbers that are in the current content.md and their meaning exactly (they were verified against data).
  Do not add new numbers. Keep the 7 tables (they may be reformatted with clear Vietnamese headers and units) and the 3 figures.

## Layout (standard HUST student report)
- Cover page centered: "ĐẠI HỌC BÁCH KHOA HÀ NỘI" / "TRƯỜNG CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG" is NOT known, so use only
  "ĐẠI HỌC BÁCH KHOA HÀ NỘI"; then "BÁO CÁO BÀI TẬP LỚN", "HỌC PHẦN: HỆ ĐIỀU HÀNH", big title
  "NỀN TẢNG THỰC THI EDGE-AI KHÔNG ĐỒNG NHẤT", a members table (Họ và tên | MSSV) with the 3 members (Nguyễn Quốc Khánh
  20233464 nhóm trưởng; Nguyễn Trung Hiếu 20233398; Nguyễn Quang Vinh 20233718), "Giảng viên hướng dẫn: TS. Nguyễn Quang Minh",
  "Mã lớp bài tập: 173876", bottom "Hà Nội, 10/2026". No "(HUST)", no "Heterogeneous Edge-AI Runtime" clutter except as a subtitle in italics.
- Then: TÓM TẮT (+ Từ khóa), MỤC LỤC, DANH MỤC HÌNH VẼ / DANH MỤC BẢNG BIỂU optional (skip if it costs a page beyond 20),
  then chapters "CHƯƠNG 1. GIỚI THIỆU" ... "CHƯƠNG 8. KẾT LUẬN", "TÀI LIỆU THAM KHẢO". Sub-headings 1.1, 1.2.
- Times New Roman 13 pt body, line spacing 1.3, justified, first-line indent 1 cm, 6 pt after paragraphs,
  headings bold (H1 14 pt uppercase, H2 13 pt bold, H3 13 pt bold italic), captions 12 pt italic centered
  ("Hình 3.1. ..." above? -> figure captions below figure, table captions above table), page numbers centered in footer
  from the abstract on, none on the cover.
- Target 16-19 A4 pages in Word (previous version: 19 pages at ~6,350 Word words incl. tables). Keep about the same length.
- Rebuild report_vi/BaoCao_HDH_Nhom3Stars.docx with the stdlib builder; rerun ZIP/XML validation; also run
  grep checks proving none of the removed items remain in word/document.xml (paths, ".md", ".csv", "results/", FLAGGED, INVALID, MEASURED).
