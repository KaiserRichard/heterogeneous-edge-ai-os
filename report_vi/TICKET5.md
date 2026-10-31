# TICKET R-VI-5: real prose rewrite (previous pass still too choppy)

Do not git commit. Edit only report_vi/content.md, rebuild the .docx, rerun validation + forbidden-text scan,
and run `python3 report_vi/style_check.py` before and after; put both outputs in logs/R-VI-summary.md.

Problem: the text is still a chain of short, flat, declarative sentences (now mean ~18 words, only 16% >= 25 words).
It reads like compressed notes, which is exactly what the student called "AI-looking". Shortening sentences was the wrong fix.

Required result (measured by style_check.py on body prose):
- mean sentence length 22-28 words, stdev >= 9, share of sentences >= 28 words between 0.25 and 0.45,
  share <= 12 words between 0.08 and 0.20, paragraphs average 4-6 sentences.
- Total body length about the same as now (Word must stay <= 19 pages): merge sentences rather than add content.

How a Vietnamese engineering student would write 1.1 (style anchor, adapt freely, do not copy into other sections):
"Trong các hệ thống Edge-AI, một kết quả suy luận đúng chưa chắc đã có ích, bởi khi kết quả đến được nơi sử dụng thì
trạng thái thực tế có thể đã thay đổi. Với nền tảng của nhóm, Raspberry Pi có thể đã xử lý xong một ảnh nhưng kết quả
vẫn phải nằm chờ trong bridge trước khi được gửi xuống vi điều khiển. Linux là lựa chọn thuận tiện vì có sẵn thư viện và
công cụ để chạy mô hình; tuy vậy, tiến trình suy luận phải chia sẻ CPU, bộ nhớ và các hàng đợi với nhiều công việc khác,
nên thông lượng cao không đồng nghĩa với việc đầu ra luôn theo kịp hiện tại. Đây chính là điểm xuất phát của đề tài."

Rules: connect ideas with causal/contrastive links (vì, nên, do vậy, tuy nhiên, trong khi đó, bởi, mặc dù, nhờ đó, cụ thể),
let each paragraph build an argument, reference tables and figures inside sentences with the numbers that matter.
Keep every number, table, figure, heading, the RQ list (a short numbered list is fine), the "đang trong quá trình triển khai"
framing and "kết quả sơ bộ". Banned: "Tóm lại", "Nhìn chung", "Đáng chú ý", "Cần lưu ý rằng"; at most 2x "Do đó" and 2x
"Điều này cho thấy". No rhetorical questions.
