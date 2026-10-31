<!-- COVER -->
**ĐẠI HỌC BÁCH KHOA HÀ NỘI**
![HUST](figures/logo_hust.jpg)
**BÁO CÁO BÀI TẬP LỚN GIỮA KỲ**
**HỌC PHẦN: HỆ ĐIỀU HÀNH**
**NỀN TẢNG THỰC THI EDGE-AI KHÔNG ĐỒNG NHẤT**
*Heterogeneous Edge-AI Runtime*
Nhóm thực hiện: 3 Stars
| Họ và tên | MSSV |
|---|---|
| Nguyễn Quốc Khánh (nhóm trưởng) | 20233464 |
| Nguyễn Trung Hiếu | 20233398 |
| Nguyễn Quang Vinh | 20233718 |
Giảng viên hướng dẫn: TS. Nguyễn Quang Minh
Mã lớp bài tập: 173876
Hà Nội, 10/2026
<!-- PAGE -->
<!-- ABSTRACT -->
Báo cáo giữa kỳ đến ngày 31/10/2026 trình bày nền tảng Edge-AI đang trong quá trình triển khai. Raspberry Pi chạy Ubuntu xử lý inference; STM32 chạy FreeRTOS giám sát qua UART. Nhóm khảo sát scheduler, tranh chấp tài nguyên và queue. Kết quả sơ bộ: OS-T1/OS-T2 PASS; OS-T3/OS-T4 FAIL theo tiêu chí đã định. Dữ liệu cho thấy ưu tiên CPU chưa cô lập được tranh chấp nhớ và vị trí loại đầu vào cũ ảnh hưởng đến tuổi dữ liệu. Các phép đo phần mềm và phản ứng GPIO được phân biệt với kết quả UART vật lý.

**Từ khóa:** hệ điều hành; Linux; FreeRTOS; UART; scheduler; freshness; giám sát độc lập.
<!-- PAGE -->
<!-- TOC -->
<!-- PAGE -->
<!-- GLOSSARY -->

| Viết tắt | Tiếng Anh đầy đủ | Giải thích |
|---|---|---|
| AI | Artificial Intelligence | Trí tuệ nhân tạo. |
| AoI | Age of Information | Tuổi dữ liệu hữu ích mới nhất. |
| CPU | Central Processing Unit | Bộ xử lý trung tâm. |
| CRC | Cyclic Redundancy Check | Mã kiểm tra dư vòng. |
| CSI | Camera Serial Interface | Giao tiếp nối tiếp camera. |
| DMA | Direct Memory Access | Truyền trực tiếp ngoại vi–bộ nhớ. |
| FIFO | First In, First Out | Vào trước, ra trước. |
| GND/VCC | Ground / Supply voltage | Mass chung / điện áp cấp nguồn. |
| GPIO | General-Purpose Input/Output | Chân vào/ra số đa dụng. |
| I2C | Inter-Integrated Circuit | Giao tiếp nối tiếp liên mạch. |
| IMU | Inertial Measurement Unit | Bộ đo quán tính. |
| IPC | Inter-Process Communication | Giao tiếp giữa các tiến trình. |
| IRQ | Interrupt Request | Yêu cầu ngắt. |
| ISR | Interrupt Service Routine | Hàm phục vụ ngắt. |
| LED | Light-Emitting Diode | Điốt phát quang. |
| MCU | Microcontroller Unit | Vi điều khiển. |
| ONNX | Open Neural Network Exchange | Định dạng trao đổi mô hình. |
| OS | Operating System | Hệ điều hành. |
| P50/P95/P99 | 50th / 95th / 99th percentile | Các phân vị 50, 95, 99. |
| PTY | Pseudo-terminal | Thiết bị đầu cuối giả. |
| RAM | Random Access Memory | Bộ nhớ truy cập ngẫu nhiên. |
| RTOS | Real-Time Operating System | Hệ điều hành thời gian thực. |
| RTT | Round-Trip Time | Thời gian khứ hồi. |
| RX/TX | Receive / Transmit | Nhận / phát dữ liệu. |
| SCL/SDA | Serial Clock Line / Serial Data Line | Đường xung nhịp / dữ liệu I2C. |
| SOF | Start of Frame | Dấu bắt đầu khung. |
| UART | Universal Asynchronous Receiver-Transmitter | Bộ thu phát nối tiếp bất đồng bộ. |
| USART | Universal Synchronous/Asynchronous Receiver-Transmitter | Bộ thu phát đồng bộ/bất đồng bộ. |

# PHẦN 1. GIỚI THIỆU

## 1.1 Động lực và bài toán

Kết quả Edge-AI có thể đã cũ khi tới nơi sử dụng. Scheduler (bộ lập lịch) Linux chia sẻ CPU, bộ nhớ và queue (hàng đợi) nên throughput (thông lượng) cao chưa bảo đảm freshness (độ mới dữ liệu). Raspberry Pi 5 chạy Ubuntu Server 24.04 ARM64 xử lý workload (tải công việc); STM32F446RE chạy RTOS FreeRTOS giám sát qua UART. MCU không chạy inference (suy luận); mục tiêu là nghiên cứu OS.

## 1.2 Câu hỏi nghiên cứu

- RQ1: Tải cạnh tranh thay đổi service time (thời gian phục vụ) và chuyển giao thế nào?
- RQ2: Priority (độ ưu tiên), CPU pinning (ràng buộc lõi) và memory locking (khóa trang nhớ) cải thiện latency (độ trễ) ra sao?
- RQ3: FIFO và latest-value (chỉ giữ giá trị mới nhất) ảnh hưởng freshness thế nào; nên thay dữ liệu ở đâu?
- RQ4: Khi Pi ngừng phục vụ, MCU phát hiện và đưa đầu ra về trạng thái an toàn mô phỏng khi nào?

Nhóm gắn timestamp (dấu thời gian) để tìm điểm chờ từ Pi tới MCU. Supervisor (khối giám sát) quyết định đầu ra dựa trên hoạt động của bridge (cầu nối) và tuổi kết quả.

# PHẦN 2. CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG TRÌNH LIÊN QUAN

## 2.1 Lập lịch và tranh chấp tài nguyên

CFS phân chia CPU theo trọng số và lịch sử sử dụng; EEVDF xét điều kiện đủ tư cách và deadline (hạn hoàn thành) ảo. SCHED_FIFO cho thread (luồng) ưu tiên cao chiếm quyền công việc thấp hơn nhưng có thể khiến task (tác vụ) khác thiếu CPU. Phân tích cần ghi kernel, chính sách thread, quyền đặt priority và giới hạn băng thông real-time (thời gian thực) [1]. CPU pinning không cô lập bộ nhớ dùng chung; MemGuard nghiên cứu cô lập băng thông nhớ [2], chỉ được dùng để giải thích. cgroups (nhóm tài nguyên) có quota (hạn mức) thấp gây throttling (hạn chế phục vụ); mlockall giữ trang trong RAM, giảm page fault (lỗi trang), không loại cache miss (trượt bộ nhớ đệm).

## 2.2 PREEMPT_RT

PREEMPT_RT giảm vùng kernel không thể bị chiếm quyền. P3 dự kiến dùng Real-time Ubuntu đóng gói, không sửa hoặc tự biên dịch kernel. Dữ liệu sơ bộ trên kernel tiêu chuẩn chưa cho phép kết luận về P3.

## 2.3 Tuổi dữ liệu

AoI là tuổi dữ liệu hữu ích mới nhất bên nhận giữ [3], [4]. Tuổi tăng khi ngừng cập nhật và giảm khi có kết quả mới, nhưng không về 0 vì dữ liệu đã chờ và truyền. AoI trung bình là diện tích dưới đường tuổi chia thời lượng đã khởi tạo, tính cả khoảng ngừng nhận và hai đầu cửa sổ; latency trung bình của gói không thay được đại lượng này.

![Hình 2.1. Age of Information và freshness threshold.](figures/aoi.png)

## 2.4 Simplex và FreeRTOS

Simplex phân quyền giữa khối tính toán phức tạp và bộ điều khiển đáng tin cậy [5], [6]: Pi đề xuất, MCU quyết định output (đầu ra). Timeout (thời hạn chờ) và FAILSAFE chưa chứng minh an toàn hình thức. FreeRTOS dùng priority cố định và preemption (chiếm quyền), nhưng task vẫn trễ khi ngắt bị che hoặc công việc trước kéo dài. Cấp phát tĩnh chưa thay được phép đo stack (ngăn xếp) và execution time (thời gian thực thi).

# PHẦN 3. THIẾT KẾ HỆ THỐNG

## 3.1 Kiến trúc và quyền điều khiển

Đường đi: ONNX Runtime/MobileNetV2 → bridge → UART → ISR → buffer (bộ đệm) hữu hạn → RX task → supervisor → GPIO/LED. Logger (bộ ghi log) theo dõi hành trình; thiếu log vẫn có thể thiếu bằng chứng giám sát. Supervisor độc quyền ghi output. Heartbeat (bản tin sống) xác nhận bridge hoạt động; INFERENCE cung cấp kết quả kiểm freshness. Chưa có cơ cấu chấp hành hoặc watchdog (cơ chế canh lỗi) phần cứng độc lập.

![Hình 3.1. Kiến trúc hệ thống và ranh giới quyền điều khiển.](figures/Hinh_3_1_System_architecture.png)

## 3.2 Khung UART

Parser (bộ phân tích khung) tìm SOF, kiểm độ dài và CRC trước khi giao cho chính sách. CRC kiểm toàn vẹn; số thứ tự phát hiện dữ liệu cũ, trùng hoặc mất. Supervisor vẫn phải kiểm tuổi và phiên; frame (khung) hợp lệ chưa bảo đảm inference đúng.

![Hình 3.2. Cấu trúc frame UART và phạm vi kiểm tra CRC.](figures/Hinh_3_2_UART_frame.png)

Bảng 1. Cấu trúc frame truyền UART.
| Trường | Kích thước và vai trò |
|---|---|
| SOF | 2 byte: A5 5A, đồng bộ khung |
| version, type | Mỗi trường 1 byte; phân biệt phiên bản và bản tin |
| seq, len | 2 byte thứ tự; 1 byte độ dài payload |
| payload | Tối đa 64 byte, các trường nhiều byte little-endian |
| CRC | 2 byte CRC-16/CCITT-FALSE; phủ từ version đến payload |

HEARTBEAT mang định danh phiên; INFERENCE mang kết quả, thứ tự đầu vào và tuổi lúc gửi. ECHO_REQ/ECHO_RESP đối chiếu đồng hồ; MCU_STATUS chứa trạng thái, bộ đếm; STATE_EVENT ghi chuyển trạng thái; INF_RX ghi timestamp nhận inference. Payload (phần dữ liệu khung) tối đa 64 byte.

## 3.3 Trạng thái và phiên

INIT giữ output an toàn mô phỏng. RUN, còn gọi FRESH, đòi hỏi liveness (tín hiệu còn hoạt động) và kết quả hợp lệ. HOLD ngăn cập nhật khi tuổi vượt ngưỡng. FAILSAFE được chốt dù lưu lượng phục hồi. Session (phiên) phân biệt lần bridge khởi động; generation (thế hệ dữ liệu) loại dữ liệu chờ cũ khi đổi phiên hoặc rearm (tái kích hoạt). Supervisor kiểm timeout trước bản tin mới. Lõi portable (khả chuyển) hỗ trợ rearm; firmware trên bo chưa hoàn tất và chưa tự động rearm từ xa.

## 3.4 FIFO và latest-value

FIFO có thể tăng backlog (tồn đọng) nếu nguồn nhanh hơn khả năng phục vụ. Latest-value thay dữ liệu chờ; inference đang chạy vẫn hoàn tất [4]. Đặt latest-value ở bridge chỉ thay kết quả chờ gửi. Nhóm vì vậy thử rút datagram (thông điệp rời) trước inference, giữ đầu vào hợp lệ mới nhất và đếm đầu vào bỏ, với cùng tải, nguồn và scheduler.

![Hình 3.3. FIFO giữ backlog; latest-value thay kết quả chưa gửi.](figures/Hinh_3_3_Queue_policies.png)

# PHẦN 4. HIỆN THỰC

## 4.1 Pipeline Linux

Source (nguồn), inference, bridge và receiver (bộ nhận) là các process (tiến trình) trao đổi qua IPC Unix datagram trong pipeline (đường ống xử lý). Source đánh dấu đầu vào; inference tiền xử lý, gọi ONNX Runtime rồi gửi kết quả cho bridge đóng frame. Host dùng workload tổng hợp khi kiểm logic.

Baseline dùng MobileNetV2-12 và ONNX Runtime 1.31.0, đối chiếu cùng đầu vào, số luồng và runtime (môi trường thực thi). Nhóm tách service time khỏi call time (thời gian gọi mô hình) [7]. Bridge ghi nối tiếp không chặn, hỗ trợ FIFO/latest-value, heartbeat và echo (trao đổi phản hồi). Frame đang phát phải hoàn tất trước khi thay dữ liệu chờ để tránh ghép sai. Logger nối dữ liệu bằng timestamp/bộ đếm; phân tích dùng thời điểm sự kiện.

## 4.2 Cấu hình thực thi

macOS dùng biên soạn, kiểm tra portable và biên dịch chéo; workload chạy trên Pi, firmware FreeRTOS trên STM32. Test parser ở host chưa xác nhận UART vật lý. P0 là mặc định; P1 điều chỉnh real-time: source FIFO priority 60, bridge FIFO priority 70 trên CPU 1, inference SCHED_OTHER trên CPU 0. Bridge được ưu tiên chuyển giao; phương án đầu dùng priority 50. P2 giới hạn quota CPU; P3 chưa có kết quả được chấp nhận.

## 4.3 Firmware

ISR → buffer → RX task → supervisor → output giữ ngắt ngắn, giao phân tích cho task. Firmware mặc định dùng DMA vòng, giữ IRQ đối chiếu. RX task dựng frame, kiểm CRC rồi giao sự kiện kèm timestamp và generation. Buffer đầy phải ghi mất dữ liệu hoặc gián đoạn; dữ liệu mất không được làm mới liveness. Supervisor sở hữu trạng thái; task trạng thái truyền bản ghi đã chụp để TX không chặn quyết định. Bộ nhớ cấp phát tĩnh.

Timestamp RX được ghi khi đọc byte CRC cuối, sau khi byte tới UART; chu kỳ đánh thức, jitter (biến thiên thời gian) và việc rút cả lô gây lệch so với phần cứng. Bỏ lỡ vòng DMA hoặc lỗi UART phải được xử lý như gián đoạn dữ liệu.

## 4.4 Công cụ và đồng hồ

Cyclictest đo đánh thức, stress-ng tạo tải, log theo dõi pipeline. Echo ánh xạ đồng hồ Pi với TIM2; logic analyzer (máy phân tích logic) đối chiếu UART/GPIO [8]. Tuổi nguồn ước lượng gồm tuổi lúc gửi, thời gian sau nhận và dự phòng truyền chưa được chứng minh là cận trên. MONOTONIC và MONOTONIC_RAW cần kiểm riêng; sai số dư echo nhỏ chưa chứng minh đường truyền đối xứng.

## 4.5 Bố trí bàn thử và pinout

Bench (bàn thử) ở Hình 4.1 dùng UART 3,3 V, TX/RX chéo, mass chung. Camera nối ribbon 22-to-15 pin tới CAM/DISP 0. IMU MPU6050 nối I2C1, firmware OS chưa dùng; lấy mẫu thuộc OS-T7.

![Hình 4.1. Sơ đồ đấu nối bàn thử OS (hình vẽ breadboard; vị trí bo minh họa, kết nối theo bảng pinout). Hình bo mạch: Fritzing parts, CC-BY-SA 3.0.](figures/os_bench_wiring.png)

Bảng 2. Pinout kết nối bàn thử OS.
| Phía Pi / ngoại vi | Tín hiệu và vai trò | Chân Nucleo |
|---|---|---|
| Pi 8 / GPIO14 | TXD → USART1 RX, 921600 baud | PA10 / D2 |
| Pi 10 / GPIO15 | RXD ← USART1 TX, 921600 baud | PA9 / D8 |
| 6 | GND chung | GND |
| CAM/DISP 0 | Camera v2 IMX219 qua ribbon 22-to-15 pin | — |
| LED xanh lá | FRESH | D4 / PB5 |
| LED vàng | HOLD | D5 / PB4 |
| LED đỏ | FAILSAFE, chốt đến khi rearm | D6 / PB10 |
| LED xanh dương | Đảo mức mỗi frame được chấp nhận | D9 / PC7 |
| LD2 trên bo | FRESH | PA5 |
| MPU6050 SCL | I2C1, đã nối; OS-T7 dự kiến | PB6 / D10 |
| MPU6050 SDA | I2C1, đã nối; firmware OS chưa dùng | PB7 / CN7 chân 21 |
| MPU6050 VCC/GND | VCC/GND; chưa ghi vị trí chân header nguồn | VCC/GND |

Hình 4.2 và 4.3 ghi lại bàn thử thực tế và cận cảnh module camera.

![Hình 4.2. Bàn thử thực tế: Raspberry Pi 5 (4 GB, vỏ có quạt), NUCLEO-F446RE, breadboard với LED trạng thái và MPU6050, Pi Camera v2 nối qua cáp ribbon tới CAM/DISP 0.](figures/os_bench_photo_annotated.png) {width=16cm}

![Hình 4.3. Cận cảnh Pi Camera Module v2 (IMX219) và cáp ribbon 15 chân phía camera.](figures/photos/camera_closeup.jpg) {width=7.5cm}

# PHẦN 5. NGUỒN CAMERA VÀ PIPELINE ƯU TIÊN ĐỘ MỚI

## 5.1 Capture và timestamp

Nguồn tổng hợp chỉ tạo frame_id và timestamp. Pi Camera v2 (IMX219) qua CSI bổ sung pixel thật để khảo sát scheduling (lập lịch), IPC và queue; nhóm không đánh giá độ chính xác mô hình. Số đo camera ở Bảng 3. Riêng offset sensor→receive lượt 30 fps có P50/P99/cực đại 10,411/12,157/14,676 ms; ở hai tốc độ, offset luôn dương và P99 dưới chu kỳ cộng 10 ms.

hea_cam dùng callback (hàm gọi lại) hoàn tất request (yêu cầu) của libcamera, lấy sequence của buffer làm frame_id và ghi t_recv_mono_ns bằng CLOCK_MONOTONIC ngay đầu callback. Pixel RGB được sao chép sau đồng bộ đọc DMA và loại padding (phần đệm) theo stride (bước dòng). SensorTimestamp đánh dấu bắt đầu phơi sáng dòng đầu, giữ nguyên trong t_sensor_ns và t_input_ns. Đồng hồ này là CLOCK_BOOTTIME; chỉ giả định đồng nhất với MONOTONIC khi Pi không suspend (tạm ngưng), có cặp đối chiếu đầu/cuối lượt.

## 5.2 Ring pixel và chính sách đầu vào

Pixel nằm trong shared-memory ring (vòng bộ nhớ chia sẻ) hữu hạn, mặc định bốn slot (ô). Unix datagram chỉ mang frame_id 4 byte và t_input_ns 8 byte, little-endian, giữ nguyên record (bản ghi) IPC và tránh đưa ảnh vào socket queue. Reader (bên đọc) chọn slot theo frame_id modulo số slot. Writer (bên ghi) duy nhất đổi sequence counter (bộ đếm thứ tự) chẵn→lẻ, ghi dữ liệu rồi công bố chẵn. Reader sao chép có giới hạn và kiểm lại counter.

Counter lẻ hoặc thay đổi được đếm torn (đọc không nhất quán); slot ổn định nhưng khác frame_id được đếm overwritten (đã ghi đè), rồi bỏ. Input-policy latest rút notification (thông báo) chờ, chọn đầu vào hợp lệ mới nhất, đếm skipped_stale. Bridge có latest-value riêng cho kết quả. Cơ chế này loại dữ liệu cũ, không tăng tốc inference hay bảo đảm deadline.

## 5.3 Mốc AoI

Với g_i là thời điểm phơi sáng đã ánh xạ sang đồng hồ consumer (bên sử dụng) và r_i là thời điểm nhận, tuổi sau cập nhật bằng r_i − g_i. Áp dụng tích phân AoI ở Phần 2. Camera/inference dùng MONOTONIC, bridge dùng MONOTONIC_RAW để kiểm tuổi và đồng bộ; chưa được trừ trực tiếp các mốc để diễn giải AoI camera đầu-cuối trên MCU.

# PHẦN 6. ĐÁNH GIÁ SƠ BỘ

## 6.1 Kiểm thử camera

Lần thử OS-T2 ngày 31/10 thất bại do Python hệ thống thiếu onnxruntime, đã bị xóa trước lưu trữ.

Bảng 3. Số đo và đối chiếu tiêu chí OS-T1–OS-T4 trên Raspberry Pi 5.
| Kiểm thử | Trạng thái theo tiêu chí | Chỉ số thực đo |
|---|---|---|
| OS-T1 — timing nguồn IMX219 và timestamp sensor | PASS — cả hai tốc độ khung, độ ổn định clock và điều kiện hợp lệ đạt tiêu chí. | 30 fps, n=9.000: chu kỳ TB 33,3229 ms (lệch −0,0314%); jitter P99 0,0303 ms; rơi 0/9.000; offset sensor→receive P99 12,157 ms. 10 fps, n=3.000: chu kỳ TB 99,957 ms; jitter P99 0,359 ms; rơi 0/3.000; offset P99 10,54 ms; BOOTTIME−MONOTONIC đầu/cuối −1,093/−1,018 µs; throttle 0x0 trước/sau. |
| OS-T2 — baseline inference trên frame camera | PASS — lượt governor performance hợp lệ; chọn 2 luồng vì P99/P50 = 1,27 < 1,5. | MobileNetV2 ONNX; 1.000 warm-up + 5.000 mẫu/thiết lập; throttle 0x0. P50/P95/P99 (ms), P99/P50: 1 luồng 44,72/46,42/52,25; 1,17. 2 luồng 31,05/33,89/39,31; 1,27. 4 luồng 30,36/33,88/50,18; 1,65. Các lượt ondemand ngày 29/10 vẫn được liệt kê là không hợp lệ. |
| OS-T3 — tranh chấp bộ nhớ/cache, P0 so với P1 | FAIL — không đạt cả yêu cầu P1 P99 ≤ P0 P99 ở mọi tải và tỷ lệ lỡ hạn P1 ≤ 1%; 3/5 lượt dự kiến. | E2, trung vị 3 lượt, service P99 P0→P1 (ms): nhàn 59,89→59,61; stream 355,27→355,42; memrate 408,25→421,86. Với deadline bằng chu kỳ nguồn 100 ms, tỷ lệ lỡ hạn P0/P1: nhàn 0/0; stream 1,0/1,0; memrate 1,0/1,0 (1,0 tương ứng 100%). Tranh chấp nhớ/cache kéo inference lên khoảng 320–420 ms; P1 điều chỉnh CPU, không dành riêng nhớ/cache. Chiến dịch không thu cyclictest max. |
| OS-T4 — FIFO/latest-value và tích hợp bridge | FAIL — AoI giảm ở mọi lượt nhưng chưa chứng minh FIFO tăng không giới hạn; chưa chạy mixed hay UART vật lý có MCU. | E3B, P1, bridge latest, 3 lượt mỗi input-policy. AoI trung bình theo thời gian (ms), FIFO/latest: nhàn 191,8–192,1/92,6–93,4; memrate 321,3–336,7/223,4–234,6. Trung vị AoI đỉnh: nhàn 236,4/135,2; memrate 456,1/351,9 ms. Tỷ lệ lỡ hạn >100 ms: nhàn khoảng 99,8%/0%; memrate 100%/100%. Latest bỏ 398–444 đầu vào cũ/lượt khi nhàn và 1.315–1.344 khi memrate. Không ghi độ dài queue; AoI FIFO nhàn ổn định khoảng 192 ms, số khung rơi bằng 0, gợi ý backlog hữu hạn. Liên kết là PTY, không có MCU. |

Nguồn: `2026-10-30_os_t1_camera`; `2026-10-31_os_t1_camera_10fps`; `2026-10-29_os_t2_infer` (không hợp lệ); `2026-10-31_os_t2_infer_performance`; `2026-10-30_os_t3_contention`; `2026-10-30_os_t4_policy` (timestamp phần mềm; không đo UART/MCU).

Hình 6.1–6.4 minh họa Bảng 3.

![Hình 6.1. OS-T1. Phân bố khoảng cách frame từ timestamp sensor trong hai lượt 30 fps và 10 fps.](figures/os_t1_frame_intervals.png)
![Hình 6.2. OS-T2. P50/P95/P99 latency suy luận theo số luồng.](figures/os_t2_latency_threads.png)
![Hình 6.3. OS-T3. Latency P99 camera→inference hoàn tất theo tải, so sánh P0/P1.](figures/os_t3_p0_p1.png)
![Hình 6.4. OS-T4. AoI tại RX theo FIFO/latest và tải.](figures/os_t4_fifo_latest.png)

## 6.2 Lịch sử

Trước camera: nguồn tổng hợp/ảnh cố định/PTY. Phân vị: trung vị lượt; cực đại: lớn nhất.

Bảng 4. Lượt cũ.
| Nhóm thí nghiệm | Số lượt và phạm vi chấp nhận |
|---|---|
| cyclictest | 30/30 ban đầu; theo dõi bổ sung: 3/15/cấu hình, chỉ nhàn |
| Suy luận độc lập | 21/24; loại 3 lượt 4 luồng: điện áp thấp |
| E1/E2/E3 PTY | 45/45 ban đầu; 0/45 đủ theo dõi bổ sung |
| E3b đầu vào latest | 3/12; loại cả 6 lượt có tải |
| E3 UART ban đầu | 0/18; lỗi nguồn/clock/thiếu sự kiện có thể chồng nhau |
| E4 gốc | 17/25; gồm 5 F5 chưa thực hiện |
| F5 riêng | 5/5 chuyển trạng thái cửa sổ ngắn |

Pi: 6.8.0-1064-raspi, PREEMPT_DYNAMIC, 5 V / 3 A; baseline 4.66–4.92 V. Ondemand/performance khác nhau, không quy chênh lệch riêng IPC. Theo dõi bổ sung: MONOTONIC_RAW ≤1.5 s/mẫu, xác nhận tải, khớp clock ≤5 s. Lịch lệch khoảng 3 ngày; thời lượng dùng clock đơn điệu.

## 6.3 Đánh thức và inference

Cyclictest: CPU 0, timer 1 ms, memory locking, 120 s/lượt, 3 lần/điều kiện; P0 SCHED_OTHER, P1 FIFO priority 50 đã kiểm trên thread.

Bảng 5. Cyclictest (µs).
| Tải | P0 P50 | P0 P99 | P0 lớn nhất | P1 P50 | P1 P99 | P1 lớn nhất |
|---|---|---|---|---|---|---|
| Nhàn rỗi | 53 | 57 | 2659 | 3 | 9 | 92 |
| memrate CPU 2–3 | 55 | 613 | 5170 | 5 | 239 | 1094 |

P1 giảm tail latency (đuôi phân bố trễ), còn ảnh hưởng tải nhớ. P50 P0 chịu timer slack (dung sai timer); không suy sang inference/UART hay băng thông nhớ.

Bảng 6. Thời gian gọi MobileNetV2 (ms).
| Tải / luồng ONNX Runtime | Lặp hợp lệ | P50 | P99 | Lớn nhất |
|---|---|---|---|---|
| Nhàn rỗi / 1 | 3 | 44.0 | 48.0 | 57.0 |
| Nhàn rỗi / 3 | 3 | 29.4 | 38.5 | 52.8 |
| Nhàn rỗi / 4 | 1 | 31.4 | 70.7 | 94.1 |
| Tải CPU / 1 | 3 | 45.1 | 53.7 | 65.5 |
| Tải CPU / 4 | 2 | 60.3 | 100.5 | 150.3 |

Mỗi lượt: 1000 lời gọi sau 50 lần làm nóng. Lợi ích thêm luồng phụ thuộc tải; số lượt khác nhau.

## 6.4 Pipeline và queue

Đầu vào→receiver Pi qua PTY, 3 lần/ô; không phải UART vật lý.

Bảng 7. E1/E2/E3 qua PTY (ms).
| Phép đo / điều kiện | P50 chuyển giao / AoI trung bình (ms) | P99 chuyển giao / AoI đỉnh (ms) |
|---|---|---|
| E1 P0 idle: chuyển giao | 44.37 | 48.47 |
| E1 P0 memrate: chuyển giao | 6626 | 13980 |
| E2 P0 cache: chuyển giao | 66.81 | 73.57 |
| E2 P1 cache: chuyển giao | 70.19 | 97.16 |
| E3 idle FIFO: AoI trung bình / đỉnh | 94.69 | 158 |
| E3 idle latest: AoI trung bình / đỉnh | 94.59 | 156 |
| E3 memrate FIFO: AoI trung bình / đỉnh | 6660 | 13660 |
| E3 memrate latest: AoI trung bình / đỉnh | 6958 | 14170 |

E3 thay thế bridge bằng 0: chờ trước inference chưa được giải quyết; E2 cache chưa cải thiện chung. E3b loại đầu vào trước inference; lỗi tách ở Bảng 4. Tỷ lệ thời gian/gói dùng thời lượng/số nhận; latest-value báo số sinh/giao/mất/thay.

## 6.5 UART và lỗi

E3 UART: 0/18 hợp lệ, 16/18 cảnh báo nguồn; mọi lượt tải nhớ sai clock. Đo lại 18 lượt đều sụt áp; latest đầu vào/bridge dưới tải: lượt đầu FAILSAFE suốt cửa sổ, sau HOLD 92.15%/91.44%. Chỉ dùng chẩn đoán.

Bảng 8. MCU chuyển FAILSAFE (ms).
| Lỗi | Lượt chấp nhận | Mốc tham chiếu | P50 | Lớn nhất |
|---|---|---|---|---|
| F1 kết thúc bridge | 5/5 | Heartbeat cuối | 100.456 | 100.641 |
| F2 SIGSTOP bridge | 5/5 | Heartbeat cuối | 100.577 | 100.596 |
| F3 SIGSTOP inference | 5/5 | Inference cuối | 475.754 | 475.815 |
| F5 ngừng inference, HB còn | 5/5 | Inference cuối | 475.596 | 475.917 |

Ngưỡng heartbeat/HOLD/FAILSAFE: 100/200/500 ms. Khác mốc: không gộp latency. Tuổi lúc gửi và dự phòng 5 ms giải thích khoảng sau nhận dưới 500 ms; HOLD khác heartbeat timeout.

GPIO: F1 86.938–95.541 ms; F2 86.947–98.676 ms (gồm lượt kiểm tra); F4 82.852–91.302 ms. Có 10/15 lần khớp heartbeat trong 0.07 ms; 5 lần có frame sau heartbeat cuối được chấp nhận.

# PHẦN 7. THẢO LUẬN VÀ HẠN CHẾ

## 7.1 Diễn giải theo câu hỏi

RQ1/RQ2: tải nhớ ảnh hưởng tail latency; priority chưa cô lập tài nguyên. Memory locking, affinity (ràng buộc CPU) và priority cần thử loại trừ riêng. RQ3: bỏ đầu vào trước inference tác động đoạn tuổi khác với bỏ kết quả tại bridge. RQ4: log MCU/GPIO cho thấy phản ứng, chưa xác lập cận trên. Trạng thái và nguyên nhân OS-T3/OS-T4 FAIL được giữ ở Bảng 3.

## 7.2 Độ tin cậy

Sụt áp, khác biệt governor (chế độ điều chỉnh tần số) và số luồng hạn chế so sánh. Cyclictest có tải thiếu xác nhận tải hoạt động liên tục; pipeline lịch sử thiếu theo dõi toàn cửa sổ. Mẫu điện áp định kỳ có thể bỏ lỡ nhiễu ngắn; cờ nguồn cũ phải tách khỏi cảnh báo trong lượt. Nhiều mẫu tương quan không thay được lần chạy độc lập.

Ánh xạ clock phụ thuộc echo và độ mới phép khớp. Task FIFO khi tiêm lỗi có thể làm bridge thiếu CPU, gián đoạn quan sát; thiếu STATE_EVENT chưa chứng minh MCU luôn FRESH. Nhóm không tự điền tỷ lệ thời gian. Bằng chứng chưa xác nhận an toàn robot, stack dài hạn, DMA không giới hạn hoặc watchdog độc lập. GPIO thấp là quy ước mô phỏng; tắt động cơ có thể làm robot mất cân bằng.

# PHẦN 8. KẾ HOẠCH TIẾP THEO

## 8.1 Lịch dự kiến đến hết tháng 11/2026

Bảng 9 ưu tiên OS-T3/T4 và UART. Lưu cấu hình, lệnh, log thô, tóm tắt; metadata (thông tin mô tả) phân biệt Pi 4 GB hiện tại/8 GB lịch sử. Không đổi ngưỡng sau xem dữ liệu; hoàn tất dự kiến 30/11/2026.

Bảng 9. Kế hoạch kiểm thử và hoàn thiện cuối kỳ (dự kiến).
| Thời gian năm 2026 | Công việc và điều kiện hoàn thành |
|---|---|
| 01–07/11 | Củng cố T1/T2; bổ sung lượt và cyclictest max cho T3; ghi queue length (độ dài queue), chạy mixed (tải hỗn hợp) cho T4 |
| 08–12/11 | OS-T5: UART 921600 baud theo runbook; 10.000 frame hợp lệ, chèn CRC sai/cụt/sai version; không nhận frame lỗi, RTT P99 < 5 ms |
| 13–18/11 | OS-T6: kill bridge, SIGSTOP inference, FIFO CPU hog, dữ liệu cũ nhưng HB còn; 10 lần mỗi lỗi; đối chiếu LED/MCU, latch và rearm; chạy bình thường 30 phút |
| 19–23/11 | OS-T7 mở rộng sau T5/T6: task MPU6050 200 Hz khi UART rảnh, dồn frame tốt và frame lỗi; mục tiêu jitter P99 < 100 µs, không lỡ mẫu |
| 24–26/11 | OS-T8: rà soát kịch bản mở rộng trong phạm vi UART; không triển khai CAN |
| 27–30/11 | Bổ sung phép đo thiếu; tổng hợp PASS/FAIL, bất định; hoàn thiện báo cáo, slide và demo camera → inference → UART → LED |

## 8.2 Điều kiện phép đo và bench

Mặc định ba lượt năm phút; mục tiêu năm lượt hợp lệ, trừ kịch bản riêng. Kiểm throttle 0x0 trước/sau, governor performance, metadata, tải toàn cửa sổ. OS-T2 đối chiếu log với 1.000 warm-up (lượt làm nóng), 5.000 inference/số luồng. Đổi firmware cần sao lưu image (ảnh firmware), kiểm hash (mã băm) và read-back (đọc lại) theo runbook (hướng dẫn thao tác). UART dùng 921600 baud thay 115200 của bảng cũ.

# PHẦN 9. KẾT LUẬN

Nền tảng cho phép khảo sát workload Linux biến thiên và giám sát FreeRTOS qua UART. OS-T1/OS-T2 PASS; OS-T3/OS-T4 còn FAIL theo Bảng 3. Kết quả nhấn mạnh giới hạn của ưu tiên CPU và vai trò vị trí loại dữ liệu cũ. Supervisor cần kiểm cả liveness lẫn freshness. Nhóm sẽ bổ sung số lượt, cyclictest max, bằng chứng queue và kiểm chứng UART có MCU trước khi mở rộng kết luận.

# TÀI LIỆU THAM KHẢO
[1] Linux kernel documentation, “Real-Time group scheduling.” Truy cập ngày 10/10/2026.
[2] H. Yun, G. Yao, R. Pellizzoni, M. Caccamo, and L. Sha, “MemGuard: Memory bandwidth reservation system for efficient performance isolation in multi-core platforms,” in *IEEE RTAS*, 2013, pp. 55–64.
[3] S. K. Kaul, R. D. Yates, and M. Gruteser, “Real-time status: How often should one update?” in *IEEE INFOCOM*, 2012, pp. 2731–2735.
[4] S. K. Kaul, R. D. Yates, and M. Gruteser, “Status updates through queues,” in *CISS*, 2012, pp. 1–6.
[5] S. Bak, D. K. Chivukula, O. Adekunle, M. Sun, M. Caccamo, and L. Sha, “The System-Level Simplex Architecture for Improved Real-Time Embedded System Safety,” in *IEEE RTAS*, 2009, pp. 99–107.
[6] S. Bak, T. T. Johnson, M. Caccamo, and L. Sha, “Real-Time Reachability for Verified Simplex Design,” in *RTSS*, 2014, pp. 138–148.
[7] ONNX Runtime documentation, “Thread management.”
[8] D. Mills, “Simple Network Time Protocol (SNTP) Version 4,” RFC 4330, Jan. 2006, sec. 5.

