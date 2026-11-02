# TICKET TALK-VI: midterm presentation scripts (Vietnamese .docx)

No GUI apps, no osascript. Do not git commit. Python stdlib only (zipfile + hand-written OOXML; you may adapt
report_vi/build_docx.py including its schema_order). Work only in talk_vi/. Write logs/TALK-VI-summary.md.

## Request (student team lead Khánh, translated)
Write presentation scripts for Hiếu and Vinh, who will be the MAIN speakers (they talk more than Khánh), plus one copy for Khánh to read through.
Base each person's part on their real role. Be detailed about which report page says what, so they can picture it.

## Source of truth
talk_vi/report_source.docx (read it fully: extract text from word/document.xml; figures in word/media). talk_vi/page_map.md gives
printed page numbers: use them. talk_vi/old_split.md is the older split where Khánh spoke 8 min; it is superseded on speaking time,
but reuse its Q&A questions. Every number spoken must match the report exactly. Do not add numbers or claims not in the report.

## Roles (from the report cover; do not misattribute)
- Khánh (nhóm trưởng): kiến trúc; pipeline Linux (camera/inference/bridge); thiết kế/chạy kiểm thử trên Raspberry Pi 5; tổng hợp báo cáo.
- Hiếu: cấu hình Linux (ưu tiên/ghim CPU/tạo tải); đo đánh thức timer; tìm hiểu cơ sở lý thuyết.
- Vinh: firmware STM32/FreeRTOS (nhận UART/giám sát/LED); khung UART; lắp và đấu nối bàn thử.

## Decided split: 15 minutes, in this order (about 180 Vietnamese syllables per minute; wc -w counts syllables)
1. Khánh ~1.5 min: mở đầu, giới thiệu nhóm và ai nói gì; 1.1, 1.2 (p5); Hình 3.1 overview (p8) in two or three sentences; hand to Hiếu.
2. Hiếu ~3.5 min: 2.1, 2.2, 2.3 with Hình 2.1 (p6-7); 4.2 P0/P1 and 4.4 tools (p10); 6.3 Bảng 5, Bảng 6 (p18) with the distinction between wake-up latency and inference time. Hand to Vinh.
3. Vinh ~5.5 min: 2.4 Simplex and FreeRTOS short (p7); 3.1 control authority (p8); 3.2, Hình 3.2, Bảng 1 (p8); 3.3 states (p9); 4.3 firmware (p10);
   4.5, Hình 4.1, Bảng 2, Hình 4.2, 4.3 (p10-13); 6.5 Bảng 8 (p18-19), including why thresholds and reference points differ. Hand to Hiếu.
4. Hiếu ~3 min: 3.4 and Hình 3.3 (p9); Phần 5 briefly (p14); 6.1 Bảng 3 OS-T1..T4 with Hình 6.1-6.4 (p15-17); 6.4 Bảng 7 as the reason for moving the drop point (p18); 7.1 (p20).
   Hiếu did not build the camera pipeline or run these tests, so he says "nhóm" for them, never "em đã làm". Mark these slots in his copy as parts Khánh ran, with a short briefing so he can explain them, and a line saying Khánh takes deep questions.
5. Vinh ~1 min: 7.2 reliability limits only as they touch hardware (sụt áp, đồng hồ) (p20); Bảng 9 OS-T5, T6, T7 as the UART/firmware next steps (p21).
6. Khánh ~0.5-1 min: Phần 9 conclusion (p22); invite questions and moderate Q&A.
Totals: Hiếu ~6.5, Vinh ~6.5, Khánh ~2-2.5. Adjust slightly only if the text needs it, Khánh must stay the smallest.

## Honesty constraints (must survive into spoken lines)
System is still being deployed; results are preliminary (kết quả sơ bộ). OS-T1, OS-T2 PASS; OS-T3, OS-T4 FAIL by the predefined criteria: state this plainly, not as a success.
LED only simulates output; no actuator. OS-T3 has 3/5 planned runs. OS-T4 runs use PTY on the Pi, not physical UART with the MCU. Older UART runs (Bảng 8 context) had under-voltage/clock issues and are diagnostic only.
Never claim worst-case bounds. Do not call Bảng 8 a guarantee. Numbers from "trước camera" tables must be said to be pre-camera data.

## Deliverables in talk_vi/ (three .docx)
- KichBan_Khanh_BanTong.docx: the full script with all speakers in order, for Khánh to read through. Starts with a one-page plan: order table (lượt, người nói, thời lượng, mục báo cáo, trang), then every slot.
- KichBan_Hieu.docx: Hiếu's slots in full plus one-line cues of what the previous speaker ends on and who speaks next, then his Q&A.
- KichBan_Vinh.docx: same for Vinh.
Each slot block contains:
  - heading: "Lượt 2 — Hiếu (~3,5 phút)"
  - per beat a small 2-column table or labelled lines: "Trang báo cáo" (printed page + mục), "Trang này nói gì" (one or two sentences of what is on that page, so they can picture it), "Mở hình/bảng" (which figure or table to point at), and "Lời nói": the actual speech to read, natural spoken Vietnamese in first person ("em"/"nhóm em"), addressing "thầy và các bạn" (lecturer TS. Nguyễn Quang Minh).
  - handoff line at the end of each slot, spoken.
Speech style: spoken, short clauses, keep English technical terms where engineers say them (scheduler, priority, latency, payload, heartbeat, watchdog, frame, CRC, FAILSAFE), and explain each once in simple Vietnamese the first time that speaker uses it. No bullet stacks in "Lời nói". No filler or praise.
Q&A section per person (Hiếu and Vinh copies; all in Khánh copy): the questions from old_split.md assigned to the right person after this split, with a 2-4 sentence answer backed by the report, including page. Add "Câu dễ bị hỏi thêm" and a short "Không nói" list for each speaker drawn from the honesty constraints.
For Hiếu and Vinh add "Từ cần nắm" (max 10 terms each, with one-line Vietnamese meaning, only what their slots use).
Layout: A4, Times New Roman 13, headings bold, tables with cell padding 115 twips, no internal paths, ticket names, run folders or tool names anywhere. Filenames of the report are fine only as "Báo cáo giữa kỳ".
Print a word count per slot in logs/TALK-VI-summary.md and confirm it is within +-10% of the target (180 syllables/min). Validate: zip opens, XML parses, pPr/rPr/tblPr child order schema-valid.
