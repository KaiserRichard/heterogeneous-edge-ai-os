# TICKET R-VI-6: student feedback round (Phần, glossary, English terms, page breaks, draw.io-style figures)

Do not git commit. Append a short note to logs/R-VI-summary.md. Keep all earlier hard rules (no paths/run ids/evidence tags,
"đang trong quá trình triển khai", "kết quả sơ bộ", no invented numbers, keep the 7 tables and their numbers,
natural connected prose: keep `python3 report_vi/style_check.py` within the TICKET5 targets).

The student's feedback, translated:
1. Name the top-level sections "Phần 1", "Phần 2", ... not "Chương". -> headings "PHẦN 1. GIỚI THIỆU" ... "PHẦN 8. KẾT LUẬN";
   in-text cross references say "Phần 3", "mục 3.2"; figure/table numbering may stay "Hình 3.1 / Bảng 5.1" style.
2. Even though the report is Vietnamese, many technical terms must stay in English (a lot of them). Do NOT force-translate
   terms a Vietnamese engineer says in English: scheduler, real-time, latency, tail latency, jitter, deadline, throughput,
   priority, preemption, context switch, CPU pinning/affinity, memory locking, page fault, cache, process, thread, task,
   ISR (interrupt service routine), queue, FIFO, latest-value, buffer, heartbeat, watchdog, timeout, failsafe, fallback,
   supervisor, bridge, frame, header, payload, CRC, UART, baud rate, timestamp, clock domain, Age of Information (AoI),
   inference, workload, stress test, benchmark, round-trip time ... Use them directly in sentences (italic not needed).
   Vietnamese stays the grammar and the explanation.
3. Add, right after MỤC LỤC, a section "DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT": a 3-column table
   | Thuật ngữ / Viết tắt | Tiếng Anh đầy đủ | Giải thích | covering every abbreviation and English term used in the report
   (about 30-45 rows, alphabetical, short one-line Vietnamese explanations). No page number issues: it is front matter.
4. Each Phần starts on a new page (page break before every Heading 1 PHẦN and before TÀI LIỆU THAM KHẢO).
   Implement in build_docx.py (pageBreakBefore on the Heading 1 style or explicit break), not with empty paragraphs.
5. The current illustrations (figures/V14.jpg, V15.jpg, V20.jpg) look childish; they were made for slides. Replace them with
   clean technical diagrams that look hand-drawn in draw.io: white background, black/dark-grey 1-1.5 px lines, plain
   rectangles (slightly rounded is ok), arrows, Arial/Helvetica-like font, at most two accent colours (one blue #1f5fa8,
   one red #c0392b), no gradients, no shadows, no icons or cartoons. Draw them with matplotlib using the system
   `python3` (matplotlib 3.10 is installed there; no other new dependency) in report_vi/figures/draw_figures.py,
   output PNG at 200 dpi, labels in Vietnamese mixed with the English terms. Figures (every label must match the text):
   - Hình 3.1 Kiến trúc hệ thống: Raspberry Pi 5 (Ubuntu, Linux workload ONNX Runtime MobileNetV2 -> bridge) --UART-->
     STM32F446RE (FreeRTOS: UART ISR -> bounded buffer -> RX task -> supervisor -> output/LED), with the authority
     boundary marked (dashed line) and HEARTBEAT / INFERENCE messages on the link.
   - Hình 3.2 Cấu trúc frame UART: SOF0 | SOF1 | header | payload | CRC (use only field names/sizes stated in content.md or
     /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides_course/main.tex and protocol/; if a size is
     not stated, omit the size).
   - Hình 3.3 FIFO và latest-value: two small queue diagrams showing backlog of old results vs replacement of unsent result.
   - Hình 2.1 AoI: a simple sawtooth line plot (age vs time) with a dashed freshness threshold line; conceptual, no data,
     axes labelled "Thời gian" and "Tuổi dữ liệu (AoI)".
   Update captions (no meta remarks like "không chứa kết quả đo" beyond what a normal caption says) and references in text.
6. Also write report_vi/IMAGE_PROMPTS.md: for each of the 4 figures an English prompt the student can paste into an image
   generator to redraw it in the same style (draw.io/technical-diagram style, white background, black lines, max blue+red,
   flat, no 3D, no cartoon, exact label text listed, aspect ratio). Keep each prompt under 120 words.
7. Length: Word page count must stay at most 20 pages including the glossary and the new page breaks (the previous version
   was exactly 20 pages at ~6,670 Word words without them). So cut body prose to roughly 4,900-5,200 words: tighten,
   merge, drop repetition; keep every table, number and figure; figures max 13 cm wide, 7.5 cm tall.
Rebuild report_vi/BaoCao_HDH_Nhom3Stars.docx, rerun validation + forbidden-text scan + style_check.
