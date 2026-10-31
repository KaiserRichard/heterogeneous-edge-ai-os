# Phân công thuyết trình giữa kỳ — Nhóm 3 Stars

Đề tài: Nền tảng thực thi Edge-AI không đồng nhất (Heterogeneous Edge-AI Runtime)
Buổi trình bày: thứ Hai, 02/11/2026
Thời lượng: 15 phút trình bày, sau đó hỏi đáp.

## Nguyên tắc chia

- Mỗi người nói một khối liền mạch, không nhảy qua lại, để chỉ có 2 lần chuyển người.
- Người nói phần nào thì tự làm slide phần đó và trả lời câu hỏi đầu tiên về phần đó.
- Khánh mở đầu, giữ phần kết quả và kết luận (phần giảng viên hỏi nhiều nhất), và điều phối hỏi đáp.
- Số liệu nói ra phải khớp báo cáo (Bảng 2, mục 6.1); không làm tròn khác báo cáo.

## Bảng phân công

| STT | Nội dung (mục trong báo cáo) | Người trình bày | Thời lượng | Ý chính cần nói |
|---|---|---|---|---|
| 1 | Mở đầu, động lực, câu hỏi nghiên cứu (Phần 1) | Nguyễn Quốc Khánh | 2 phút | Vì sao tách Linux (suy luận) và STM32 (giám sát); câu hỏi về scheduler, tranh chấp tài nguyên, queue và freshness. |
| 2 | Kiến trúc tổng thể và luồng dữ liệu một kết quả (3.1–3.3) | Nguyễn Quốc Khánh | 2 phút | Camera → inference → bridge → UART → supervisor; hai miền đồng hồ. |
| 3 | Cơ sở lý thuyết: lập lịch real-time trên Linux, tranh chấp đa nhân, AoI (Phần 2) | Nguyễn Trung Hiếu | 2 phút | SCHED_FIFO/PREEMPT_RT, vì sao ưu tiên CPU không bảo vệ được băng thông bộ nhớ, định nghĩa AoI trung bình theo thời gian. |
| 4 | Hiện thực phía Linux: IPC, ring pixel, chính sách FIFO/latest-value, cấu hình P0/P1 (4.1–4.2, 5.2) | Nguyễn Trung Hiếu | 2 phút | Process tách rời, ring có sequence counter, latest-value bỏ dữ liệu cũ chứ không làm suy luận nhanh hơn. |
| 5 | Firmware STM32: ISR/DMA → RX task → supervisor, trạng thái FRESH/HOLD/FAILSAFE (4.3, 3.6–3.7) | Nguyễn Quang Vinh | 2 phút | Ngắt chỉ nhận byte, task kiểm CRC, dữ liệu mất không làm mới liveness, bộ nhớ cấp phát tĩnh. |
| 6 | Bàn thử và pinout: UART 921600 baud, LED D4/D5/D6/D9, camera, MPU6050 (4.5) | Nguyễn Quang Vinh | 1 phút | Chỉ hình 4.1 và ảnh bench; LED nào ứng với trạng thái nào. |
| 7 | Kết quả OS-T1–OS-T4 và cách đánh giá PASS/FAIL (6.1) | Nguyễn Quốc Khánh | 3 phút | T1, T2 PASS; T3, T4 FAIL và nguyên nhân; nói rõ lượt T2 lỗi ngày 31/10 đã bị xóa. |
| 8 | Hạn chế, kế hoạch tiếp theo, kết luận (Phần 7–9) | Nguyễn Quốc Khánh | 1 phút | Liên kết PTY chưa phải UART vật lý; OS-T5 UART, OS-T7 IMU; số lượt lặp còn thấp. |
| 9 | Hỏi đáp | Khánh điều phối; ai phụ trách phần nào trả lời trước | 5–10 phút | Khánh bổ sung nếu câu trả lời chưa đủ. |

Tổng thời lượng nói: Khánh khoảng 8 phút (≈ 55%), Hiếu khoảng 4 phút, Vinh khoảng 3 phút.

## Câu hỏi dễ gặp và người chuẩn bị

| Câu hỏi có thể gặp | Người chuẩn bị |
|---|---|
| Vì sao P1 (FIFO priority, pinning, mlockall) không cải thiện khi tải bộ nhớ? | Hiếu |
| Latest-value có luôn tốt hơn FIFO không? Vì sao T4 vẫn FAIL? | Khánh |
| Đồng hồ Pi và STM32 khác nhau thì tính tuổi dữ liệu thế nào? | Khánh |
| Khi buffer UART tràn hoặc mất byte thì supervisor phản ứng ra sao? | Vinh |
| Vì sao chọn 921600 baud và UART thay vì SPI/CAN? | Vinh |
| Đã đo trên UART thật và MCU chưa? | Khánh |

## Việc cần làm trước buổi trình bày

| Việc | Người làm | Hạn |
|---|---|---|
| Cập nhật slide kết quả OS-T1–OS-T4 và hình bench (bộ slide cũ chưa có số liệu giữa kỳ) | Khánh | Chủ nhật 01/11 |
| Slide phần 3–4 (lý thuyết, hiện thực Linux) | Hiếu | Chủ nhật 01/11 |
| Slide phần 5–6 (firmware, bàn thử) và chụp 2 ảnh bench | Vinh | Chủ nhật 01/11 |
| Tập dượt cả nhóm, bấm giờ, chỉnh chuyển người | Cả nhóm | Tối Chủ nhật 01/11 |
