# Phân công thuyết trình giữa kỳ — Nhóm 3 Stars

Mỗi thành viên thuyết trình phần mình đã triển khai, theo đúng phân công công việc trên bìa báo cáo.

Đề tài: Nền tảng thực thi Edge-AI không đồng nhất
Buổi trình bày: thứ Hai, 02/11/2026
Thời lượng: 15 phút trình bày, sau đó hỏi đáp.

## Bảng phân công

| Người trình bày | Nội dung phụ trách | Thời lượng | Ý chính cần nói |
|---|---|---|---|
| Nguyễn Quốc Khánh — nhóm trưởng | Mở đầu, kiến trúc, pipeline Linux/camera, kết quả, thảo luận, kế hoạch và kết luận [Phần 1; mục 3.1, 3.4, 4.1; Phần 5–9]. | Khoảng 8 phút | Đường đi camera–suy luận–bridge; thiết kế và chạy kiểm thử trên Raspberry Pi 5; OS-T1/T2 PASS, OS-T3/T4 FAIL; giới hạn bằng chứng và bước tiếp theo. |
| Nguyễn Trung Hiếu | Cơ sở lý thuyết, cấu hình thực thi và đo đánh thức timer [Phần 2; mục 4.2, 4.4, 6.3]. | Khoảng 4 phút | Độ ưu tiên, ghim CPU, tạo tải; cách đo đánh thức bằng cyclictest; ưu tiên CPU chưa cô lập bộ nhớ; phân biệt độ trễ đánh thức và suy luận. |
| Nguyễn Quang Vinh | Firmware STM32, khung UART, trạng thái giám sát; bố trí bàn thử và đấu nối [Phần 3.2–3.3, 4.3, 4.5]. | Khoảng 3 phút | Kiểm CRC, nhận dữ liệu và giám sát tách riêng; FRESH/HOLD/FAILSAFE; UART 921600 baud, LED và sơ đồ đấu nối. |

Tổng thời lượng nói: 15 phút. Khánh mở đầu khoảng 3 phút, Hiếu 4 phút, Vinh 3 phút, Khánh trở lại trình bày kết quả và kết thúc khoảng 5 phút. Khánh giới thiệu kiến trúc tổng thể và pipeline Linux/camera; Vinh giải thích chi tiết khung UART và trạng thái. Hiếu giải thích cấu hình thực thi và cách đo đánh thức; Khánh phân tích kết quả suy luận ở mục 6.3 và chính sách hàng đợi. Các phần giao nhau không cần trình bày lại.

## Chuẩn bị và hỏi đáp

Mỗi người chuẩn bị slide cho phần mình phụ trách và trả lời trước các câu hỏi thuộc phần đó. Số liệu phải khớp Bảng 3, mục 6.1 của báo cáo. Hỏi đáp dự kiến 5–10 phút, Khánh điều phối.

| Câu hỏi cần chuẩn bị | Người phụ trách |
|---|---|
| Vì sao ưu tiên CPU chưa cải thiện suy luận khi tải bộ nhớ? | Hiếu |
| Vì sao latest-value giảm tuổi dữ liệu nhưng OS-T4 vẫn FAIL? | Khánh |
| Đồng hồ Pi và STM32 khác nhau thì tính tuổi dữ liệu thế nào? | Khánh; Vinh bổ sung phía STM32 |
| Khi mất byte hoặc tràn bộ đệm UART, khối giám sát phản ứng ra sao? | Vinh |
| Vì sao dùng UART 921600 baud? LED thể hiện trạng thái gì? | Vinh |
| Kết quả nào đo qua PTY, kết quả nào đã có MCU? | Khánh |

| Việc cần hoàn thành trước buổi trình bày | Người làm | Hạn |
|---|---|---|
| Slide mở đầu, kiến trúc, pipeline Linux/camera, kết quả và kết luận [Phần 1; mục 3.1, 3.4, 4.1; Phần 5–9] | Khánh | Chủ nhật 01/11 |
| Slide lý thuyết, cấu hình thực thi và đo đánh thức timer [Phần 2; mục 4.2, 4.4, 6.3] | Hiếu | Chủ nhật 01/11 |
| Slide UART, firmware, bàn thử [Phần 3.2–3.3, 4.3, 4.5]; dùng ảnh trong báo cáo | Vinh | Chủ nhật 01/11 |
| Tập dượt, bấm giờ, chỉnh chuyển người | Cả nhóm | Tối Chủ nhật 01/11 |
