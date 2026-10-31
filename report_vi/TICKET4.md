# TICKET R-VI-4: prose pass so it reads like a human student wrote it

Do not git commit. Append one line to logs/R-VI-summary.md. Edit only report_vi/content.md (builder/layout stay as they are),
then rebuild report_vi/BaoCao_HDH_Nhom3Stars.docx and rerun validation + the forbidden-text scan.

The cleanup worked, but the prose still reads machine-written. Concrete problems seen in chapter 1:
- Every sentence is 10-15 words with the same rhythm: "Linux thuận tiện cho mô hình và thư viện, nhưng ... . Do đó, ... ."
- Four identical lines "Câu hỏi RQ1 của nhóm là: ...", "Câu hỏi RQ2 của nhóm là: ...". Write them as one short numbered
  list introduced by a real sentence, or weave them into a paragraph.
- Telegraphic, abstract phrasing ("Đóng góp ở mức học phần gồm ...", "Kết quả sơ bộ giúp phát hiện hàng đợi sai vị trí").

Go through EVERY chapter and rewrite paragraph by paragraph:
- Mix sentence lengths: some long sentences (25-40 words) joined with "vì", "nên", "trong khi", "tuy vậy", "cụ thể là",
  some short ones. Paragraphs of 4-7 sentences that develop one idea with a concrete example from this system
  (Raspberry Pi 5, STM32F446RE, UART, MobileNetV2, heartbeat, hàng đợi FIFO...).
- Explain tables in the text the way a student would: point at the specific rows/numbers that matter and say why
  ("Ở Bảng 5.1, khi có tải memrate, P99 của cấu hình P0 tăng lên 613 µs, trong khi P1 chỉ 239 µs ...").
- Use "nhóm" and occasionally "chúng em"; avoid impersonal stacked nominalisations and calqued English.
- No sentence starting with "Do đó," more than twice in the whole report; no "Điều này cho thấy" more than twice;
  no "Tóm lại", "Nhìn chung", "Đáng chú ý", "Cần lưu ý rằng".
- Keep every number, table, figure, heading structure, the "đang trong quá trình triển khai" framing and
  "kết quả sơ bộ" wording. Do not add numbers. Keep total length so Word stays at 16-19 pages
  (now 19 pages / 6,285 Word words; do not grow by more than ~3%).
