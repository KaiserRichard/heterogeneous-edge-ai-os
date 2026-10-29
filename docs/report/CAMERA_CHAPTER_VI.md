# Nguồn camera và pipeline ưu tiên độ mới của dữ liệu

*Bản tiếng Việt dùng cho báo cáo nộp. Các kết quả phần cứng của camera vẫn đang chờ đo; những số liệu lịch sử dưới đây luôn kèm nguồn và phạm vi đo.*

## Động cơ và phạm vi

Nguồn Linux trước đây tạo `frame_id` và timestamp tổng hợp. Cách này kiểm tra được scheduling và IPC, nhưng không có pixel và timestamp không cho biết cảnh được phơi sáng lúc nào. Thay nguồn tổng hợp bằng Pi Camera v2 (IMX219) giúp đo ý nghĩa của độ tuổi từ lúc nhận ảnh đến lúc có kết quả, đồng thời vẫn giữ trọng tâm hệ điều hành: scheduling, queueing, IPC và freshness. Inference chỉ đóng vai trò workload; chương này không đánh giá độ chính xác của model. Xem [mục tiêu dự án](../../PROJECT.md), [roadmap camera](../CAMERA_ROADMAP.md) và [ticket CAM1](../tickets/CAM1_CAMERA_SOURCE.md).

## Thiết kế

### Capture và mốc gốc AoI

`hea_cam` dùng callback hoàn tất request của libcamera để nhận frame. Backend yêu cầu kích thước và frame rate đã chọn, lấy `FrameMetadata::sequence` làm `frame_id`, ánh xạ camera buffer, đồng bộ thao tác đọc DMA buffer và bỏ phần padding theo stride khi sao chép pixel RGB. Ngay đầu callback, chương trình ghi `t_recv_mono_ns` bằng `CLOCK_MONOTONIC`. `controls::SensorTimestamp` của request đánh dấu thời điểm bắt đầu phơi sáng dòng đầu tiên; CAM1 giữ nguyên giá trị đó trong `t_sensor_ns` và truyền nguyên giá trị làm `t_input_ns`.

libcamera định nghĩa `SensorTimestamp` thuộc clock domain `CLOCK_BOOTTIME`. Thiết kế chỉ xem timestamp này là mốc AoI thuộc `CLOCK_MONOTONIC` khi Pi không suspend; trong điều kiện đó, phép ánh xạ là đồng nhất: $t_{sensor}^{mono} \approx t_{sensor}^{boot}$. Metadata lúc khởi động lưu một cặp mẫu `CLOCK_BOOTTIME` / `CLOCK_MONOTONIC`. Giả định về mốc sensor bị bác bỏ nếu có offset đo được

\[
\delta_i = t_{recv,mono,i} - t_{sensor,i}
\]

không dương hoặc không bị chặn quanh một chu kỳ frame cộng thời gian đọc sensor. OS-T1 cụ thể hóa kiểm tra: mọi offset phải dương và P99 phải nhỏ hơn $T_f+10\,ms$, với $T_f=1/fps$. Một cặp mẫu lúc khởi động không chứng minh quan hệ hai clock giữ nguyên suốt cả lần chạy. Nếu kiểm tra thất bại, phương án dự phòng trong roadmap là dùng `t_recv_mono_ns` làm mốc AoI và ghi rõ việc thay thế; CAM1 hiện giữ timestamp sensor thô và analyzer báo kiểm tra không đạt, không tự ý sửa timestamp. [README camera](../../linux/camera/README.md) mô tả giả định clock và giới hạn của mẫu khởi động.

### Ring pixel có giới hạn và record input giữ nguyên

Pixel đi qua shared-memory slot ring có kích thước giới hạn; Unix datagram từ source đến inference vẫn là `hea_input` little-endian 12 byte hiện tại: `{ frame_id: u32, t_input_ns: u64 }` (`<IQ`). Ảnh quá lớn để đặt vào notification này: chỉ gửi ID và timestamp giúp giữ nguyên IPC record, đồng thời không đưa payload ảnh vào socket queue. Inference mở shared-memory object theo tên và đọc slot được chọn bởi `frame_id % N`.

Ring có một writer. Đây là cơ chế slot theo kiểu seqlock: khi ghi, writer chuyển sequence counter từ chẵn sang lẻ, ghi `frame_id` và pixel, sau đó công bố counter chẵn. Reader sao chép có giới hạn một lần rồi kiểm tra counter lại. Counter đang lẻ hoặc đã đổi được ghi nhận là `torn`; slot ổn định nhưng chứa `frame_id` khác được ghi nhận là `overwritten`. Cả hai trường hợp đều được đếm và bỏ qua. Cách này không chặn producer bằng lock và ngăn inference dùng ảnh bị sao chép dở hoặc đã bị thay thế. Mặc định ring có bốn slot; ring có giới hạn nhưng không đảm bảo không mất frame. [README camera](../../linux/camera/README.md) mô tả ABI, atomic access, giới hạn và vòng đời của ring.

Freshness cũng được áp dụng tại input queue. Với `--input-policy latest`, trước mỗi inference, tiến trình rút hết các notification đang chờ và chọn notification hợp lệ mới nhất. Nếu inference chậm hơn capture, frame cũ bị thay thế và ghi `skipped_stale`; ring slot cũng có thể bị ghi đè trước khi ảnh được sao chép. Bridge có chính sách latest-value riêng cho inference result đang chờ gửi. Các chính sách này giới hạn backlog cũ bằng cách bỏ bớt công việc, đổi lại có thể mất tính đầy đủ. Chúng không làm inference nhanh hơn và không đảm bảo deadline. Xem mã và tùy chọn trong [`infer_server.py`](../../linux/inference/infer_server.py).

### Đường đi của một frame

```mermaid
sequenceDiagram
    participant S as IMX219 / libcamera
    participant C as Callback hea_cam
    participant R as Shared-memory ring
    participant I as infer_server
    participant B as hea_bridge
    participant M as STM32 FreeRTOS supervisor
    S->>C: Request hoàn tất: sequence, SensorTimestamp, RGB buffer
    C->>C: Ghi t_recv_mono_ns; sao chép RGB; giữ t_sensor_ns làm t_input_ns
    C->>R: Công bố frame_id và pixel (lẻ → dữ liệu → chẵn)
    C->>I: hea_input 12 byte(frame_id, t_input_ns)
    I->>I: Chọn notification hợp lệ mới nhất; kiểm tra và preprocess ring slot
    I->>B: Inference result datagram(frame_id, t_input, t_done, class, confidence)
    B->>M: Result và heartbeat được đóng khung UART
    M->>M: Kiểm tra reception; theo dõi heartbeat và freshness; cập nhật FRESH / HOLD / FAILSAFE
```

Sơ đồ thể hiện đường đi đầy đủ theo thiết kế. Inference ở camera mode dùng `CLOCK_MONOTONIC`, trong khi bridge hiện tại dùng `CLOCK_MONOTONIC_RAW` cho age validation và clock synchronization. `hea_input` giữ nguyên byte layout không làm hai clock domain có thể thay thế cho nhau. Cần xử lý ranh giới này trước khi dùng nhánh camera để kết luận AoI đầu-cuối qua bridge và supervisor hiện tại. Xem giới hạn tích hợp trong [README camera](../../linux/camera/README.md).

### Age of Information và ví dụ tính một chu kỳ răng cưa

Gọi $g_i$ là timestamp phơi sáng của frame sau khi ánh xạ sang clock domain của consumer, và $r_i$ là thời điểm nhận result thành công. Nếu $u(t)$ là thời điểm tạo frame của result mới nhất đã có tại thời điểm $t$, Age of Information được tính là

\[
\Delta(t)=t-u(t), \qquad
\bar{\Delta}(H)=\frac{1}{H}\int_0^H \Delta(t)\,dt.
\]

Ngay sau lần nhận thứ $i$, tuổi dữ liệu là $\Delta_i=r_i-g_i$. Trong khoảng đến lần nhận kế tiếp, tuổi tăng tuyến tính. Với khoảng cách giữa hai lần nhận $Y_i=r_i-r_{i-1}$, diện tích phần tương ứng dưới đường AoI là

\[
A_i=\Delta_{i-1}Y_i+\frac{Y_i^2}{2}, \qquad
\bar{\Delta}_i=\frac{A_i}{Y_i}=\Delta_{i-1}+\frac{Y_i}{2}.
\]

Ví dụ tính toán dưới đây không phải kết quả camera; đây là hai lần nhận inference đầu tiên trong run phần mềm/pty được lưu tại [`E3_P1_B2_memrate_c23_fifo_r1/pipeline/rx.csv`](../../results/2026-10-11_e1_e2_e3_pty/20261008T103412Z_e_onnx/E3_P1_B2_memrate_c23_fifo_r1/pipeline/rx.csv). Timestamp trong file cho $g_0=2{,}996{,}803{,}181{,}824\,ns$, $r_0=2{,}996{,}965{,}095{,}880\,ns$, $g_1=2{,}996{,}903{,}236{,}621\,ns$ và $r_1=2{,}997{,}105{,}784{,}491\,ns$. Do đó $\Delta_0=161.914056\,ms$, $Y_1=140.688611\,ms$, và

\[
A_1=(161.914056)(140.688611)+\frac{(140.688611)^2}{2}
   =32{,}676.106273\,ms^2,
\qquad \bar{\Delta}_1=232.258362\,ms.
\]

Ngay trước lần cập nhật thứ hai, AoI của result cũ là $302.602667\,ms$; khi result mới đến, AoI giảm xuống $202.547870\,ms$. Đây là một chu kỳ giữa hai lần nhận trong run dùng input tổng hợp trước đây, không phải phép đo camera hay trung bình toàn run. Trung bình theo thời gian của cả campaign phải cộng diện tích trong cửa sổ đo đã khởi tạo rồi chia cho độ dài cửa sổ đó.

## Kịch bản kiểm thử

Một run chỉ hợp lệ khi `vcgencmd get_throttled` bằng `0x0` trước và sau, governor là `performance`, phiên SSH rảnh và metadata được lưu. Chỉ trừ timestamp trong cùng clock domain: `CLOCK_MONOTONIC` của Pi hoặc timer của MCU. Số liệu khác clock cần đường đồng bộ và phải được gắn nhãn. Mặc định mỗi cấu hình có ba lần chạy, mỗi lần 5 phút, trừ khi kịch bản quy định thời lượng khác. Bảng gốc nằm trong [TEST_SCENARIOS_VI.md](../TEST_SCENARIOS_VI.md).

| Mã | Cấu hình và quy trình | Chỉ số và tiêu chí đạt |
|---|---|---|
| OS-T1 | Pi 5 + Pi Camera v2, không tải; 640×480 ở 30 fps và 10 fps, mỗi cấu hình 5 phút; lưu sensor/receive timestamp và cặp BOOTTIME/MONOTONIC lúc khởi động. | Trung bình chu kỳ frame lệch danh định ≤ 1%; jitter tuyệt đối P99 < 2 ms; rơi frame < 0,1%; `t_recv−t_sensor` dương và P99 < $T_f+10\,ms$; độ lệch BOOTTIME−MONOTONIC ổn định. Một cặp đầu run không chứng minh được tính ổn định; cần ghi thêm cặp gần cuối hoặc để tiêu chí này ở trạng thái chưa xác minh. |
| OS-T2 | P0 stock, MobileNetV2 ONNX, camera 10 fps; 1.000 warm-up, sau đó 5.000 inference có đo cho mỗi cấu hình 1, 2 và 4 threads; ghi throttle và nhiệt độ SoC. | Throttle `0x0` trước/sau; P50/P95/P99 inference và nhiệt độ tối đa; thread setting được chọn có P99/P50 < 1,5. |
| OS-T3 | So sánh P0 với P1 (`SCHED_FIFO`, ghim CPU, cgroup `cpu.max`, `mlockall`) khi có stressor CPU, VM, cache và I/O. | P50/P99 camera-to-result, tỉ lệ lỡ deadline (deadline = frame period), cyclictest max; P99 của P1 không tệ hơn P0 ở từng stressor và tỉ lệ lỡ deadline P1 ≤ 1%. Báo cáo cả trường hợp ngược lại. |
| OS-T4 | Camera 30 fps, inference chậm hơn frame period; so sánh FIFO ở input/bridge, latest-value ở cả hai phía và cấu hình trộn; mỗi cấu hình ba lần. | AoI trung bình theo thời gian và AoI đỉnh, lỡ deadline, queue length; AoI trung bình của latest-value phải thấp hơn FIFO trong mọi run. Quan sát queue FIFO tăng; nếu không thì giả thuyết không đạt. |
| OS-T5 | UART Pi ↔ Nucleo OS firmware; gửi 10.000 frame hợp lệ, chèn frame sai CRC, cụt và sai version, đo echo RTT. | Nhận mọi frame hợp lệ, không nhận frame lỗi, RTT P99 < 5 ms. Chạy ở 921600 baud (OS firmware); giá trị 115200 trước đây trong bảng kịch bản đã được sửa ngày 30/10/2026. |
| OS-T6 | Pipeline camera đầy đủ và OS firmware; tạo lỗi bridge bị kill, inference `SIGSTOP`, FIFO CPU hog và result cũ nhưng heartbeat còn sống; mỗi lỗi 10 lần rồi rearm. Dùng logic analyzer quan sát D4 FRESH, D5 HOLD, D6 FAILSAFE, D9 hoạt động link. | Mọi lần đến đúng state; phản ứng ≤ ngân sách timer + một tick; FAILSAFE giữ latch đến khi rearm; không FAILSAFE giả trong 30 phút chạy bình thường. |
| OS-T7 (mở rộng) | FW3 chạy task MPU6050 200 Hz khi UART rảnh, nhận frame hợp lệ liên tục và nhận burst frame lỗi. | Jitter chu kỳ theo MCU timer P99 < 100 μs, không lỡ mẫu, thời gian phản ứng OS-T6 không đổi. |
| OS-T8 (mở rộng) | FW4 gửi state supervisor khi đổi và mỗi 100 ms qua CAN1; CAN2 trên cùng board nhận; lặp lại lỗi OS-T6. Bridge Pi–MCU vẫn dùng UART. | Nhận mọi lần đổi state; P99 từ đổi state đến CAN2 < 1 ms; TEC/REC bằng 0. |

OS-T8 là phần mở rộng đã được chấp thuận trong roadmap: CAN chỉ xuất state từ MCU, không thay thế hoặc tham gia bridge UART.

## Kết quả và trạng thái bằng chứng

| Hạng mục | Trạng thái và bằng chứng | Kết luận được phép |
|---|---|---|
| OS-T1: timing camera và kiểm tra mốc AoI | **PENDING — chưa chạy với camera vật lý trên Pi.** Analyzer và fake backend đã có trong source; build real backend trên Pi và capture OS-T1 vẫn là việc phía bench. | Chưa có số đo camera về FPS, jitter, mất frame hoặc offset sensor-to-receive. |
| OS-T2: inference baseline trên camera | **PENDING — chưa chạy trên frame camera.** | Chưa có latency inference hoặc nhiệt độ với input camera. |
| OS-T3 / OS-T4 dùng camera | **PENDING.** E1–E3/E3b trước đây dùng source tổng hợp hoặc đường phần mềm/pty. | Chưa có so sánh contention hoặc FIFO/latest-value với camera. |
| Inference baseline ảnh cố định trước đây | Đã đo trong cấu hình cũ: P50/P99 khi idle là 44,0/48,0 ms (1 thread), 31,1/42,9 ms (2), 29,4/38,5 ms (3), và 31,4/70,7 ms (4; chỉ một repeat hợp lệ). | Chỉ dùng làm mốc tham khảo cho OS-T2. Các mẫu ảnh cố định có exposure/cấu hình khác, không phải kết quả OS-T2 camera. Nguồn: [`STAGE_REPORT.md`](../STAGE_REPORT.md#inference-workload-alone) và [`results/2026-10-11_inference_baseline/SUMMARY.md`](../../results/2026-10-11_inference_baseline/SUMMARY.md). |
| Nghiên cứu input latest-value trước đây (E3b) | Timestamp phần mềm/pty đã đo, nhưng mọi dòng loaded đều **INVALID / FLAGGED** do cờ nguồn/undervoltage xuất hiện trong lúc chạy. Age P50 của input FIFO nằm trong 6.527,4–8.676,0 ms, P99 trong 13.821,6–15.891,0 ms; input-latest có P50 189,3–190,7 ms, P99 254,0–267,9 ms, bỏ qua 171–173 input cũ. | Quan sát chẩn đoán ủng hộ việc chọn latest-value trước inference. Đây không phải bằng chứng nhân quả sạch và không kiểm tra camera ring. Nguồn: [`STAGE_REPORT.md`](../STAGE_REPORT.md#e3b-input-latest-value-fix-still-power-flagged), [`E3B_per_run.csv`](../../results/2026-10-12_e3b_input_latest/20261012T091415Z_e3b/summary/E3B_per_run.csv) và các `rx.csv` / validity theo run. |

Danh mục phần cứng trong roadmap ngày 29/10 ghi nhận camera chưa được kết nối, `imx219` không xuất hiện trong `dmesg`, và libcamera/rpicam chưa được cài. Roadmap cũng ghi Pi đó là bản 4 GB, trong khi kết quả inference cũ dùng board 8 GB. Đây là trạng thái ghi nhận tại thời điểm đó; cần kiểm tra lại khi bắt đầu chạy bench. Không được đổi nhãn kết quả của fake backend thành kết quả camera.

### Chuyển bench giữa firmware OS và WBR

Thực hiện theo [RUNBOOK_BENCH.md](../RUNBOOK_BENCH.md): owner xác nhận khi chuyển sang OS firmware, dùng quy trình `nucleo_switch.py` đã chuẩn bị cùng các bước BOOT0/RESET trong runbook, rồi đưa BOOT0 về GND và reset sau khi ghi. Runbook yêu cầu lưu bản sao firmware cũ, hash image và xác minh read-back. Muốn quay lại WBR thì dùng cùng quy trình với `wbr-agv_f446_home_canfix01.bin` và hash đã ghi. Link OS supervisor dùng 921600 baud; WBR dùng 115200 baud. Runbook mô tả trạng thái dự kiến là INIT/tắt LED, sau đó D4 xanh khi bridge chạy. Không bổ sung quy trình flash khác ở đây.

## Giới hạn

- Chưa xác minh capture camera vật lý, build libcamera trên Pi, frame timing được thương lượng, màu sensor, DMA coherency và overhead scheduling trên Pi; cần OS-T1 trên phần cứng. Khoảng trống trong capture-buffer sequence có thể không biểu lộ mọi frame mất ở bên trong camera pipeline.
- Giả định không suspend và kiểm tra offset dương/có giới hạn là điều kiện cần cho mốc sensor, nhưng không chứng minh hai clock tương đương trong cả run. Nếu kiểm tra thất bại, phải báo mốc receive-time dự phòng; không trình bày AoI từ sensor như kết quả hợp lệ.
- `hea_cam` sao chép pixel và ghi CSV trong completion callback; các chi phí này thuộc overhead của source. Ring có thể ghi đè frame và reader chủ động bỏ slot bị torn hoặc đã cũ.
- Camera mode và bridge hiện tại dùng clock domain Linux khác nhau (`CLOCK_MONOTONIC` và `CLOCK_MONOTONIC_RAW`). Cần giải quyết giao diện này trước khi dùng age ở bridge hoặc MCU làm AoI camera.
- Dữ liệu source tổng hợp, pty và dữ liệu bị gắn cờ lỗi nguồn điện không chứng minh hiệu năng camera, lợi ích latest-value khi tải trong điều kiện hợp lệ, độ tin cậy điện hoặc deadline xấu nhất. Baud rate trong OS-T5 cũng cần thống nhất trước khi chạy.

## Bảng thuật ngữ

| Thuật ngữ | Nghĩa trong chương này |
|---|---|
| AoI (Age of Information) | Tuổi thông tin: thời gian từ lúc tạo input mới nhất đến thời điểm đang xét. |
| libcamera | Thư viện Linux dùng để cấu hình camera và nhận frame qua request. |
| SensorTimestamp | Timestamp do camera pipeline cung cấp, gắn với lúc bắt đầu phơi sáng dòng đầu tiên. |
| `CLOCK_MONOTONIC` / `CLOCK_BOOTTIME` | Hai Linux clock domain; BOOTTIME tính cả thời gian suspend, MONOTONIC không tính. |
| Shared-memory ring | Vùng nhớ chia sẻ gồm các slot tuần hoàn để chuyển pixel với dung lượng giới hạn. |
| Seqlock | Cách kiểm tra reader có sao chép dữ liệu đồng thời với writer hay không bằng sequence counter lẻ/chẵn. |
| Latest-value | Chính sách giữ giá trị mới nhất và bỏ các giá trị cũ đang chờ xử lý. |
| IPC (Inter-Process Communication) | Cơ chế trao đổi dữ liệu giữa các process, ở đây là Unix datagram và shared memory. |
| UART (Universal Asynchronous Receiver-Transmitter) | Kết nối serial giữa Pi và Nucleo. |
| MCU (Microcontroller Unit) | Vi điều khiển; trong hệ thống này là STM32F446RE. |
| FreeRTOS | RTOS chạy trên STM32 để giám sát heartbeat và freshness độc lập với Linux. |
| Torn / overwritten | Lần đọc slot không nhất quán / slot đã chứa frame khác; frame đó bị bỏ qua. |
| P99 | Phân vị thứ 99 của tập phép đo. |
| WBR | Firmware robot hiện có được dùng làm image để chuyển qua lại trên bench. |
| CAN (Controller Area Network) | Bus chỉ dùng làm đầu ra state MCU trong OS-T8; bridge Pi–MCU vẫn là UART. |
