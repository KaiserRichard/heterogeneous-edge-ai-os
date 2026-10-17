# TICKET R-VI: Vietnamese course report (.docx, 15-20 pages)

Read AGENTS.md first. Do not git commit. Write logs/R-VI-summary.md when done.

## Goal
Write the Operating Systems course report in VIETNAMESE (proper diacritics) as a Word .docx of 15-20 A4 pages,
ordered like a research paper and report.

## Cover / front matter (copy exactly)
- Trường: Đại học Bách khoa Hà Nội (HUST); Học phần: Hệ điều hành
- Đề tài: NỀN TẢNG THỰC THI EDGE-AI KHÔNG ĐỒNG NHẤT (Heterogeneous Edge-AI Runtime)
- Nhóm thực hiện: 3 Stars
  - Nguyễn Quốc Khánh – 20233464 (Nhóm trưởng)
  - Nguyễn Trung Hiếu – 20233398
  - Nguyễn Quang Vinh – 20233718
- Giảng viên hướng dẫn: TS. Nguyễn Quang Minh
- Mã lớp bài tập: 173876
- Hà Nội, tháng 10/2026

## Sections, in this order
Tóm tắt (abstract, ~200 words + Từ khóa) ; Mục lục ;
1 Giới thiệu (động lực, bài toán, câu hỏi nghiên cứu RQ1-RQ4, đóng góp, cấu trúc báo cáo) ;
2 Cơ sở lý thuyết và các công trình liên quan (lập lịch Linux CFS/EEVDF, SCHED_FIFO, PREEMPT_RT, cgroups, CPU pinning, mlockall; Age of Information / freshness; Simplex architecture; FreeRTOS on MCU; cite only sources already cited in the decks/docs) ;
3 Thiết kế hệ thống (kiến trúc Raspberry Pi 5 / Ubuntu + STM32F446RE / FreeRTOS, ranh giới quyền điều khiển, giao thức khung UART: SOF/header/payload/CRC, các loại bản tin, supervisor FSM INIT/RUN/HOLD/FAILSAFE, chính sách FIFO vs latest-value) ;
4 Hiện thực (Linux workload ONNX Runtime MobileNetV2, bridge, firmware ISR -> bounded buffer -> RX task -> supervisor -> output; công cụ đo) ;
5 Đánh giá sơ bộ (phương pháp đo, môi trường, bảng kết quả thật từ results/ và các deck; mỗi số ghi nguồn thư mục run; ghi rõ KẾT QUẢ SƠ BỘ, các run bị FLAGGED/INVALID do under-voltage phải nói rõ) ;
6 Thảo luận và hạn chế ;
7 Hướng phát triển (lộ trình A-F) ;
8 Kết luận ;
Tài liệu tham khảo (IEEE style, only real references found in the decks/docs bibliographies).

## Hard rules
- The user requires: DO NOT claim the system is fully deployed. Describe it as "đang trong quá trình triển khai";
  label every result as "kết quả sơ bộ"; keep the deck's evidence labels (đã đo / đã tính / dự kiến / chưa biết) in Vietnamese.
- No invented numbers. Every number must come from the sources below; cite the run directory or deck for it.
- Length target: 15-20 A4 pages at Times New Roman 13 pt, line spacing 1.3, margins 2.5/2/3/2 cm (top/bottom/left/right)
  => roughly 5500-7000 Vietnamese words of body text plus 4-8 tables and 3-5 figures with numbered Vietnamese captions
  (Hình 1, Bảng 1 ...), each referenced in the text.
- Figures: reuse images from slides/images/*.jpg (see slides/images/MAPPING.md) and/or
  /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides_course/images/*.png (see its MAPPING.md). Copy the ones you use into report_vi/figures/.
- Python standard library only (no network, no pip). Build the .docx yourself with zipfile + hand-written OOXML
  (document.xml, styles.xml with Heading 1/2/3 and Caption styles, numbering for bullets, tables with borders,
  embedded images via word/media + relationships, page numbers in footer, a TOC field that Word updates on open
  (w:updateFields in settings.xml), cover page with no page number, page break after cover/abstract/TOC).
- Keep content in report_vi/content.md (or a few .md files) and a builder report_vi/build_docx.py that converts
  that markdown subset (headings, paragraphs, bullets, bold/italic, tables, images with captions) to
  report_vi/BaoCao_HDH_Nhom3Stars.docx. Run it and validate the zip opens and XML parses (python -c with zipfile + xml.dom.minidom).

## Sources (read these; final deck first)
1. /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides_course/main.tex  (FINAL deck, English, 10/2026; read the \note{} texts too)
2. slides/main.tex  (approved Vietnamese deck 07/10/2026; reuse its Vietnamese terminology)
3. docs/STAGE_REPORT.md, docs/SYSTEM_GUIDE.md, docs/SYSTEM_OVERVIEW.md, docs/ROADMAP.md, docs/ROADMAP_TO_WBROBOT_AND_ARTICLE.md, PROJECT.md, README.md
4. results/README.md and results/*/ (summaries, csv) for measured numbers.

## Scope
Only create/modify files under report_vi/ and logs/R-VI-summary.md.
