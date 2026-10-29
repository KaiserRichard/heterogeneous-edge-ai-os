# Kịch bản kiểm thử (Pi Camera v2 + bench)

Bản tiếng Việt của [TEST_SCENARIOS.md](TEST_SCENARIOS.md), dùng cho báo cáo nộp. Giữ nguyên
thuật ngữ kỹ thuật tiếng Anh; viết đầy đủ ở lần xuất hiện đầu: AoI (Age of Information – tuổi
thông tin), MCU (Microcontroller Unit – vi điều khiển), UART (Universal Asynchronous
Receiver-Transmitter), CRC (Cyclic Redundancy Check), RTT (Round-Trip Time), CAN (Controller
Area Network), LA (Logic Analyzer – máy phân tích logic).

Quy tắc chung:
- Một lần chạy chỉ HỢP LỆ khi `vcgencmd get_throttled` = `0x0` trước và sau, governor là
  `performance`, phiên SSH rảnh, và metadata được lưu. Lần chạy không hợp lệ vẫn được giữ và gắn nhãn.
- Chỉ trừ hai mốc thời gian cùng một đồng hồ: `CLOCK_MONOTONIC` của Pi hoặc timer của MCU.
- Bằng chứng lưu tại `results/<ngày>_<mã>/`: CSV thô, `meta.json`, lệnh chạy, `summary.json`.
  Tiêu chí đạt được cố định **trước** khi chạy. Mặc định 3 lần chạy × 5 phút mỗi cấu hình.

| Mã | Mục đích | Cấu hình | Các bước | Chỉ số | Tiêu chí đạt | Bằng chứng |
|---|---|---|---|---|---|---|
| OS-T1 | Nguồn camera đều và mốc gốc AoI hợp lệ | Pi 5 + Pi Camera v2, `hea_cam`, không tải | 1) 30 fps 640x480, 5 phút; 2) 10 fps, 5 phút; 3) ghi `t_sensor_ns`, `t_recv_mono_ns`, cặp BOOTTIME/MONOTONIC lúc khởi động | trung bình khoảng cách khung, jitter P99, số khung rơi, độ lệch `t_recv − t_sensor` | trung bình lệch < 1 % so với danh định; jitter P99 < 2 ms; rơi < 0,1 %; độ lệch > 0 và P99 < T + 10 ms | `results/<ngày>_os_t1_camera/frames.csv` |
| OS-T2 | Baseline suy luận sạch trên khung camera | hồ sơ P0, MobileNetV2 ONNX, 1/2/4 luồng, camera 10 fps | 1) ghi throttle; 2) 1000 lần khởi động + 5000 lần đo mỗi số luồng; 3) ghi throttle, nhiệt độ | P50/P95/P99 suy luận (ms), nhiệt độ tối đa | throttle 0x0 trước và sau; P99/P50 < 1,5 | `results/<ngày>_os_t2_infer/` |
| OS-T3 | Hồ sơ P1 có bảo vệ pipeline khi tranh chấp tài nguyên? | P0 vs P1 (SCHED_FIFO + ghim CPU + cgroup `cpu.max` + `mlockall`); stress-ng cpu/vm/cache/io | 1) không tải; 2) mỗi stressor × hồ sơ, 3 lần | độ trễ camera→kết quả P50/P99, tỉ lệ trễ hạn, cyclictest max (μs) | P99 của P1 ≤ P0 với mọi stressor và tỉ lệ trễ hạn P1 ≤ 1 %; trường hợp ngược được báo cáo | `results/<ngày>_os_t3_contention/` |
| OS-T4 | FIFO so với latest-value khi quá tải | camera 30 fps, suy luận chậm hơn chu kỳ khung | 1) FIFO cả hai phía; 2) latest cả hai phía; 3) kết hợp; mỗi cấu hình 3 lần | AoI trung bình theo thời gian, AoI đỉnh, tỉ lệ trễ hạn, độ dài hàng đợi | AoI của latest-value < FIFO ở mọi lần chạy; nếu không thì giả thuyết KHÔNG ĐẠT | `results/<ngày>_os_t4_policy/` |
| OS-T5 | Chỉ khung UART hợp lệ mới làm mới supervisor | Pi `/dev/ttyAMA0` 115200 ↔ Nucleo (firmware OS) | 1) 10 000 khung hợp lệ; 2) chèn khung sai CRC, cụt, sai phiên bản; 3) đo RTT | số khung nhận/loại theo nhóm, RTT P50/P99 (đồng hồ Pi) | 0 khung lỗi được chấp nhận; mọi khung hợp lệ được nhận; RTT P99 < 5 ms | `results/<ngày>_os_t5_uart/` |
| OS-T6 | Lỗi → HOLD/FAILSAFE trên LED, rồi rearm | pipeline đầy đủ; D4 xanh lá FRESH, D5 vàng HOLD, D6 đỏ FAILSAFE, D9 xanh dương hoạt động link | lỗi: tắt bridge, SIGSTOP suy luận, CPU hog FIFO, kết quả cũ với heartbeat sống; 10 lần mỗi lỗi; sau đó rearm | thời gian lỗi→trạng thái (timer MCU), trạng thái LED qua LA, thời gian rearm | mọi lần đạt trạng thái đúng; phản ứng ≤ ngân sách timer + 1 tick; FAILSAFE chốt đến khi rearm; 0 FAILSAFE giả trong 30 phút | `results/<ngày>_os_t6_faults/` + file LA |
| OS-T7 (mở rộng) | FreeRTOS giữ đúng chu kỳ tác vụ cảm biến khi supervisor xử lý UART dồn dập | tác vụ MPU6050 200 Hz (I2C1) | 1) link rảnh; 2) khung hợp lệ liên tục; 3) chuỗi khung lỗi | jitter chu kỳ (timer MCU), mẫu bị lỡ | jitter P99 < 100 μs, 0 mẫu lỡ; thời gian phản ứng OS-T6 không đổi | `results/<ngày>_os_t7_rtos_load/` |
| OS-T8 (mở rộng) | Trạng thái supervisor xuất ra khung CAN (chỉ đầu ra, bridge vẫn là UART) | CAN1 gửi trạng thái khi đổi + mỗi 100 ms; CAN2 cùng board nhận, 500 kbit/s | lặp lại các lỗi OS-T6, 10 lần mỗi lỗi | thời gian từ đổi trạng thái đến ngắt RX CAN2, bộ đếm lỗi CAN | mọi lần đổi trạng thái đều nhận được; P99 < 1 ms; TEC/REC = 0 | `results/<ngày>_os_t8_can/` |

Giới hạn kết luận: OS-T1/T2 chỉ nói về Pi; OS-T4 chỉ so sánh trên tải này; số đo OS-T6 trên
đồng hồ MCU không gồm thời gian phát hiện phía Pi nếu chưa nối dây đồng bộ PA0.
