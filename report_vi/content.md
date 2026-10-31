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
Báo cáo giữa kỳ cập nhật đến ngày 31/10/2026, trình bày nền tảng thực thi Edge-AI không đồng nhất đang trong quá trình triển khai cho học phần Hệ điều hành. Nhóm dùng Raspberry Pi chạy Ubuntu để xử lý inference, trong khi STM32 chạy FreeRTOS giám sát độc lập qua UART. Nhóm khảo sát ảnh hưởng của scheduler, tranh chấp tài nguyên và queue tới freshness. Các câu hỏi xoay quanh tải, cấu hình, queue và phản ứng khi Linux lỗi. Kết quả sơ bộ ghi nhận priority real-time cải thiện tail latency đánh thức, nhưng tranh chấp bộ nhớ vẫn còn và thay kết quả tại bridge chưa giải quyết được tồn đọng trước inference. UART và GPIO giúp đối chiếu log, phân biệt mất heartbeat với kết quả cũ dù heartbeat vẫn đến. Hai lượt camera 30 fps và 10 fps ngày 30–31/10 đáp ứng tiêu chí OS-T1, còn lượt inference hợp lệ với governor performance đạt OS-T2 ở cấu hình 2 luồng. OS-T3/OS-T4 giữ trạng thái FAIL; dữ liệu T3 cho thấy hồi quy P1 khi tải băng thông nhớ, còn T4 chưa đo trực tiếp AoI trung bình theo thời gian.
**Từ khóa:** hệ điều hành; Linux; FreeRTOS; UART; scheduler; freshness; giám sát độc lập.
<!-- PAGE -->
<!-- TOC -->
<!-- PAGE -->
<!-- GLOSSARY -->

| Thuật ngữ / Viết tắt | Tiếng Anh đầy đủ | Giải thích |
|---|---|---|
| A | Ampere | Đơn vị cường độ dòng điện. |
| AI / Edge-AI | Artificial Intelligence / Edge Artificial Intelligence | Trí tuệ nhân tạo, xử lý tại thiết bị biên. |
| AoI | Age of Information | Tuổi dữ liệu hữu ích mới nhất ở bên nhận. |
| ARM | Advanced RISC Machine | Tên lịch sử của kiến trúc bộ xử lý Arm. |
| ARM64 | 64-bit ARM architecture | Kiến trúc bộ xử lý Arm 64 bit trên Pi. |
| BOOTTIME | Boot time | Thời gian từ lúc khởi động, kể cả khi suspend. |
| Buffer / queue / backlog | Buffer / queue / backlog | Bộ đệm, hàng đợi và dữ liệu tồn đọng. |
| CAN | Controller Area Network | Mạng truyền thông điều khiển; ngoài phạm vi báo cáo. |
| CCITT | International Telegraph and Telephone Consultative Committee | Ủy ban tư vấn điện báo và điện thoại quốc tế. |
| CCITT-FALSE | International Telegraph and Telephone Consultative Committee, FALSE variant | Tên biến thể CRC dùng trong khung UART. |
| CFS | Completely Fair Scheduler | Bộ lập lịch công bằng hoàn toàn của Linux. |
| cgroups / quota / throttling | Control groups / quota / throttling | Nhóm tài nguyên, hạn mức và việc bị hạn chế phục vụ. |
| CISS | Conference on Information Sciences and Systems | Hội nghị khoa học thông tin và hệ thống. |
| CLOCK_BOOTTIME | Boot-time clock | Đồng hồ Linux tính cả thời gian suspend. |
| CLOCK_MONOTONIC | Monotonic clock | Đồng hồ đơn điệu Linux, không tính thời gian suspend. |
| CPU | Central Processing Unit | Bộ xử lý trung tâm. |
| CPU pinning / affinity | Central Processing Unit pinning / Central Processing Unit affinity | Ràng buộc CPU mà process hoặc thread được chạy. |
| CRC | Cyclic Redundancy Check | Mã kiểm tra dư vòng để phát hiện lỗi dữ liệu. |
| CRC-16 | 16-bit Cyclic Redundancy Check | Mã kiểm tra dư vòng dài 16 bit. |
| Deadline / timeout | Deadline / timeout | Hạn hoàn thành và khoảng chờ tối đa. |
| DMA | Direct Memory Access | Truyền dữ liệu trực tiếp giữa ngoại vi và bộ nhớ. |
| ECHO_REQ | Echo Request | Bản tin yêu cầu phản hồi để đối chiếu đồng hồ. |
| ECHO_RESP | Echo Response | Bản tin phản hồi dùng đối chiếu đồng hồ. |
| EEVDF | Earliest Eligible Virtual Deadline First | Ưu tiên deadline ảo sớm nhất trong nhóm đủ điều kiện. |
| FIFO | First In, First Out | Hàng đợi hoặc chính sách phục vụ theo thứ tự đến. |
| FPS | Frames Per Second | Số khung hình mỗi giây. |
| FreeRTOS | Free Real-Time Operating System | Hệ điều hành thời gian thực dùng trên MCU. |
| GB | Gigabyte | Đơn vị dung lượng bộ nhớ. |
| GPIO | General-Purpose Input/Output | Chân vào/ra số đa dụng. |
| HB | Heartbeat | Bản tin sống xác nhận bridge còn hoạt động. |
| Heartbeat / liveness / freshness | Heartbeat / liveness / freshness | Bản tin sống, khả năng hoạt động và độ mới dữ liệu. |
| HUST | Hanoi University of Science and Technology | Đại học Bách khoa Hà Nội. |
| Hz | Hertz | Đơn vị tần số, số chu kỳ mỗi giây. |
| I2C | Inter-Integrated Circuit | Giao tiếp nối tiếp giữa các mạch tích hợp. |
| IEEE | Institute of Electrical and Electronics Engineers | Viện kỹ sư điện và điện tử. |
| IMU | Inertial Measurement Unit | Bộ đo quán tính. |
| INF_RX | Inference Receive | Sự kiện nhận kết quả suy luận tại MCU. |
| Inference / workload / MobileNetV2 | Inference / workload / MobileNet version 2 | Suy luận, tải tính toán và mô hình được sử dụng. |
| INFOCOM | International Conference on Computer Communications | Hội nghị quốc tế về truyền thông máy tính. |
| INIT | Initialization | Trạng thái khởi tạo, giữ đầu ra an toàn mô phỏng. |
| IPC / datagram / Unix | Inter-Process Communication / datagram / Unix | Giao tiếp process bằng các thông điệp rời theo cơ chế Unix. |
| IRQ | Interrupt Request | Yêu cầu ngắt từ phần cứng. |
| ISR | Interrupt Service Routine | Hàm phục vụ ngắt. |
| Jan. | January | Tháng một trong tài liệu tham khảo. |
| Jitter / latency / tail latency | Jitter / latency / tail latency | Biến thiên thời gian, độ trễ và đuôi phân bố trễ. |
| latest-value / latest | Latest value / latest | Chỉ giữ dữ liệu chờ mới nhất. |
| LED | Light-Emitting Diode | Điốt phát quang dùng báo trạng thái đầu ra. |
| len | Length | Trường độ dài payload trong khung UART. |
| MCU | Microcontroller Unit | Vi điều khiển giám sát độc lập. |
| MCU_STATUS | Microcontroller Unit Status | Bản tin trạng thái và bộ đếm của vi điều khiển. |
| Memory locking / mlockall / page fault | Memory locking / lock all memory / page fault | Giữ trang trong RAM nhằm giảm lỗi trang khi thực thi. |
| MONOTONIC / MONOTONIC_RAW / TIM2 | Monotonic / raw monotonic / Timer 2 | Đồng hồ đơn điệu Linux và bộ định thời trên STM32. |
| ms | Millisecond | Mili giây, một phần nghìn giây. |
| MSSV | Student Identification Number | Mã số sinh viên. |
| ns | Nanosecond | Nano giây, một phần tỷ giây trong tên timestamp. |
| ONNX | Open Neural Network Exchange | Định dạng trao đổi mô hình học máy. |
| ORT | Open Neural Network Exchange Runtime | Môi trường thực thi mô hình ONNX. |
| OS | Operating System | Hệ điều hành. |
| P50 | 50th percentile | Phân vị 50, trung vị của phép đo. |
| P95 | 95th percentile | Phân vị 95 của phép đo. |
| P99 | 99th percentile | Phân vị 99, mô tả đuôi phân bố phép đo. |
| Parser / session / generation / rearm | Parser / session / generation / rearm | Phân tích frame, phiên, thế hệ nội bộ và tái kích hoạt. |
| payload | Payload | Phần dữ liệu của khung truyền. |
| pp. | Pages | Các trang được trích trong tài liệu tham khảo. |
| PREEMPT_DYNAMIC | Dynamic preemption | Cấu hình preemption động của kernel Linux. |
| PREEMPT_RT | Real-time preemption | Cấu hình preemption thời gian thực của kernel Linux. |
| PTY | Pseudo-terminal | Cặp thiết bị đầu cuối giả để kiểm thử phần mềm. |
| RAM | Random Access Memory | Bộ nhớ truy cập ngẫu nhiên. |
| RFC | Request for Comments | Tài liệu công bố đặc tả hoặc thảo luận kỹ thuật. |
| RGB | Red, Green, Blue | Ba kênh màu đỏ, lục và lam của pixel. |
| RISC | Reduced Instruction Set Computing | Kiến trúc tính toán với tập lệnh rút gọn. |
| RQ1 / RQ2 / RQ3 / RQ4 | Research Question 1 / Research Question 2 / Research Question 3 / Research Question 4 | Bốn câu hỏi nghiên cứu của báo cáo. |
| RTAS | Real-Time and Embedded Technology and Applications Symposium | Hội nghị công nghệ và ứng dụng nhúng, thời gian thực. |
| RTOS | Real-Time Operating System | Hệ điều hành thời gian thực. |
| RTSS | Real-Time Systems Symposium | Hội nghị về hệ thống thời gian thực. |
| RTT | Round-Trip Time | Thời gian khứ hồi của trao đổi bản tin. |
| runtime | Runtime | Môi trường thực thi workload suy luận. |
| RX | Receive | Chiều nhận dữ liệu. |
| s | Second | Giây, đơn vị thời gian. |
| SCHED_FIFO | Scheduling: First In, First Out | Chính sách lập lịch thời gian thực theo thứ tự đến. |
| SCHED_OTHER | Scheduling: Other | Chính sách lập lịch Linux thông thường. |
| Scheduler | Scheduler | Bộ lập lịch của hệ điều hành. |
| sec. | Section | Mục được trích trong tài liệu tham khảo. |
| seq | Sequence | Số thứ tự bản tin trong khung UART. |
| SIGSTOP | Stop Signal | Tín hiệu tạm dừng tiến trình khi tiêm lỗi. |
| Simplex / supervisor / watchdog | Simplex / supervisor / watchdog | Phân quyền điều khiển, khối giám sát và cơ chế canh lỗi. |
| SNTP | Simple Network Time Protocol | Giao thức đồng bộ thời gian mạng đơn giản. |
| SoC | System on Chip | Hệ thống tích hợp trên một vi mạch. |
| SOF | Start of Frame | Dấu đồng bộ bắt đầu khung truyền UART. |
| STATE_EVENT | State Event | Bản ghi sự kiện chuyển trạng thái supervisor. |
| TS. | Doctor | Tiến sĩ, học vị của giảng viên hướng dẫn. |
| TX | Transmit | Chiều phát dữ liệu. |
| UART | Universal Asynchronous Receiver-Transmitter | Bộ thu phát nối tiếp bất đồng bộ. |
| V | Volt | Đơn vị điện áp. |
| µs | Microsecond | Micro giây, một phần triệu giây. |

# PHẦN 1. GIỚI THIỆU

## 1.1 Động lực và bài toán

Trong hệ thống Edge-AI, kết quả đúng đã cũ khi tới nơi sử dụng, bởi đầu vào tiếp tục thay đổi trong lúc Pi xử lý hoặc chờ bridge. Linux có thư viện chạy mô hình nhưng process phải chia sẻ CPU, bộ nhớ và queue, nên throughput cao chưa bảo đảm đầu ra theo kịp hiện tại. Đây là bài toán của nhóm. Raspberry Pi 5 chạy Ubuntu Server 24.04 ARM64 xử lý workload, còn STM32F446RE chạy FreeRTOS giám sát qua UART; MCU không chạy inference vì mục tiêu là nghiên cứu OS.

## 1.2 Câu hỏi nghiên cứu và đóng góp

Nhóm đặt các câu hỏi:
- RQ1: Tải cạnh tranh làm thay đổi service time và chuyển giao dữ liệu như thế nào?
- RQ2: Điều chỉnh priority, CPU pinning và memory locking khôi phục được phần nào của latency?
- RQ3: FIFO và latest-value tác động thế nào đến freshness; nên thay thế dữ liệu ở đâu?
- RQ4: Khi Pi ngừng cung cấp dịch vụ, MCU phát hiện và chuyển đầu ra về trạng thái an toàn mô phỏng khi nào?

Nhóm gắn timestamp để lần theo dữ liệu từ Pi tới MCU và tìm chỗ chờ, trong khi supervisor giữ quyền điều khiển dựa trên cả hoạt động của bridge lẫn độ mới của kết quả. Kết quả sơ bộ hướng việc phân tích về thời gian đầu vào đã chờ trước inference, vì thay dữ liệu ở bridge chỉ tác động tới đoạn sau. 

# PHẦN 2. CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG TRÌNH LIÊN QUAN

## 2.1 Lập lịch Linux và tranh chấp tài nguyên

CFS phân chia CPU theo trọng số và lịch sử sử dụng, còn EEVDF xét điều kiện đủ tư cách cùng deadline ảo để tiếp tục mục tiêu công bằng. Tuy nhiên, bridge vẫn có thể chờ dù dữ liệu đã sẵn sàng. SCHED_FIFO cho thread sẵn sàng có priority cao preemption công việc thấp hơn, nên phù hợp với đoạn chuyển giao ngắn nhưng có nguy cơ làm task khác thiếu CPU; vì thế nhóm phải ghi kernel, chính sách thread, quyền đặt priority và giới hạn băng thông real-time khi phân tích [1]. CPU pinning giảm di chuyển thread nhưng không cô lập shared memory, nên CPU riêng vẫn chịu tải đọc ghi từ lõi khác. MemGuard nghiên cứu cô lập băng thông nhớ [2]; nhóm chỉ vận dụng để giải thích, không cài cơ chế kernel. cgroups giới hạn workload nhưng quota thấp gây throttling. mlockall giữ trang trong RAM nhằm giảm page fault, song không loại được cache miss hay tranh chấp nhớ, vì vậy trạng thái memory locking thực tế vẫn phải ghi lại.

## 2.2 PREEMPT_RT và giới hạn suy diễn

PREEMPT_RT giảm những vùng không thể bị preemption và thay đổi cách xử lý một công việc trong kernel. Nhóm chỉ dự kiến thử kernel Real-time Ubuntu đóng gói ở cấu hình P3, không sửa hoặc tự biên dịch kernel. Vì kết quả sơ bộ đều được thu trên kernel tiêu chuẩn, nhóm chưa thể dùng chúng để kết luận về PREEMPT_RT hoặc lợi ích của P3 với bridge trên Pi. 

## 2.3 Độ tươi dữ liệu và giá trị của kết quả

Age of Information (AoI) là tuổi dữ liệu hữu ích mới nhất bên nhận giữ [3], [4]. Khi chưa có cập nhật, tuổi vẫn tăng dù không có gói đang truyền, nên latency một gói không thay được AoI trung bình. Hình 2.1 biểu diễn tuổi tăng rồi giảm khi nhận cập nhật, nhưng không về không vì dữ liệu đã chờ và truyền. Phép tích phân phải tính cả khoảng ngừng cập nhật và hai đầu cửa sổ.

![Hình 2.1. Age of Information và freshness threshold.](figures/aoi.png)

## 2.4 Simplex và FreeRTOS trên MCU

Simplex phân quyền giữa khối tính toán phức tạp và bộ điều khiển đáng tin cậy [5], [6], nên Pi chỉ đề xuất còn MCU quyết định output. Tuy nhiên, timeout và FAILSAFE chưa tạo thành chứng minh an toàn hình thức. Mô hình đối tượng và giả thiết lỗi vẫn cần xác định. Với FreeRTOS, priority cố định scheduler hỗ trợ preemption nhưng task vẫn trễ khi ISR bị che hoặc công việc trước kéo dài; cấp phát tĩnh chỉ giảm biến thiên, không thay phép đo stack và execution time.

# PHẦN 3. THIẾT KẾ HỆ THỐNG

## 3.1 Kiến trúc và ranh giới quyền điều khiển

Hình 3.1 mô tả Linux workload (ONNX Runtime, MobileNetV2) → bridge trên Pi, qua UART tới UART ISR → bounded buffer → RX task → supervisor → output/LED trên STM32. Logger ghi timestamp để tái dựng hành trình dưới tải, nhưng thiếu log có thể khiến nhóm chưa đủ bằng chứng dù MCU vẫn giám sát. Supervisor độc quyền ghi output; heartbeat xác nhận bridge hoạt động, còn INFERENCE cung cấp kết quả để kiểm tra freshness. Đầu ra mới là GPIO. Hệ thống chưa có cơ cấu chấp hành hoặc watchdog phần cứng độc lập.

![Hình 3.1. Kiến trúc hệ thống và ranh giới quyền điều khiển.](figures/Hinh_3_1_System_architecture.png)

## 3.2 Khung UART và loại bản tin

Hình 3.2 và Bảng 1 mô tả frame UART: parser tìm SOF, kiểm độ dài và CRC trước khi giao cho logic chính sách. Giới hạn payload là 64 byte. CRC kiểm toàn vẹn, còn số thứ tự giúp nhận ra dữ liệu cũ, trùng hoặc mất, nên supervisor vẫn phải kiểm tuổi và phiên. Frame hợp lệ chưa bảo đảm nội dung inference đúng.

![Hình 3.2. Cấu trúc frame UART và phạm vi kiểm tra CRC.](figures/Hinh_3_2_UART_frame.png)

Bảng 1. Cấu trúc frame truyền UART.
| Trường | Kích thước và vai trò |
|---|---|
| SOF | 2 byte: A5 5A, đồng bộ khung |
| version, type | Mỗi trường 1 byte; phân biệt phiên bản và bản tin |
| seq, len | 2 byte thứ tự; 1 byte độ dài payload |
| payload | Tối đa 64 byte, các trường nhiều byte little-endian |
| CRC | 2 byte CRC-16/CCITT-FALSE; phủ version đến payload |

HEARTBEAT mang thông tin sống còn và định danh phiên, trong khi INFERENCE mang kết quả, thứ tự đầu vào và tuổi lúc gửi để kiểm tra freshness. Để đối chiếu hoạt động hai bên, nhóm dùng ECHO_REQ/ECHO_RESP ước lượng quan hệ đồng hồ, nhận MCU_STATUS chứa trạng thái và bộ đếm của supervisor. STATE_EVENT ghi chuyển trạng thái còn INF_RX ghi timestamp nhận inference.

## 3.3 Máy trạng thái và phiên làm việc

MCU có INIT, RUN, HOLD và FAILSAFE; RUN còn gọi FRESH khi dữ liệu đủ mới. INIT giữ output an toàn mô phỏng, còn RUN đòi hỏi cả liveness và kết quả hợp lệ. Khi tuổi vượt ngưỡng, HOLD ngăn cập nhật output. FAILSAFE được chốt, nên lưu lượng tốt trở lại chưa tự khôi phục hoạt động.

Session phân biệt lần bridge khởi động, còn generation gắn vào dữ liệu chờ để loại dữ liệu cũ khi đổi phiên hoặc tái kích hoạt. Supervisor kiểm hết hạn trước khi xử lý bản tin mới, tránh bỏ sót timeout sát hạn. Lõi portable hỗ trợ rearm. Firmware trên bo chưa hoàn tất chức năng này và chưa cung cấp tự động rearm từ xa.

## 3.4 FIFO và latest-value

FIFO giữ thứ tự dữ liệu đến, nhưng tuổi có thể tăng dần nếu nguồn sinh nhanh hơn khả năng phục vụ. Với nhiệm vụ cần biết trạng thái hiện tại, latest-value thay dữ liệu đang chờ bằng dữ liệu mới nhất để tránh tiếp tục xử lý đầu vào đã cũ. Sự khác nhau trong Hình 3.3 chỉ nằm ở phần dữ liệu chờ, bởi inference đang chạy vẫn được hoàn tất thay vì bị hủy khi có đầu vào mới [4].

![Hình 3.3. FIFO giữ backlog; latest-value thay kết quả chưa gửi.](figures/Hinh_3_3_Queue_policies.png)

Nếu chỉ đặt latest-value tại bridge, nhóm chỉ thay được kết quả đã inference xong và đang chờ gửi, trong khi đầu vào của kết quả vừa hoàn tất đã chờ lâu trước MobileNetV2. Vì vậy, nhóm thử rút các datagram sẵn có trước inference, giữ đầu vào hợp lệ mới nhất và đếm số bỏ, giữ cùng tải, nguồn và scheduler để tách tác động của vị trí queue.

# PHẦN 4. HIỆN THỰC

## 4.1 Đường ống Linux và tải suy luận

Source, inference, bridge và receiver trao đổi qua IPC Unix datagram, nhờ đó mỗi process đảm nhận một đoạn trong pipeline. Source đánh dấu đầu vào trước khi inference nhận dữ liệu, tiền xử lý rồi gọi ONNX Runtime với MobileNetV2; kết quả sau đó được đưa sang bridge để đóng frame UART. Khi kiểm tra logic trên host, chúng em có thể dùng workload tổng hợp thay cho runtime và mô hình thật. 

Với phiên đo nền dùng MobileNetV2-12 và ONNX Runtime 1.31.0, nhóm giữ cùng mô hình, đầu vào, số thread và thiết lập runtime để so sánh. Thêm luồng có thể tận dụng CPU khi Pi nhàn rỗi, nhưng cũng làm inference cạnh tranh với process tạo tải. Khi hệ thống bận, nhóm tách service time khỏi call time inference [7]. Bridge xuất nối tiếp không chặn, hỗ trợ FIFO hoặc latest-value, phát heartbeat và trao đổi echo. Khi UART mới ghi được một phần frame, bridge phải hoàn tất frame đang phát rồi mới thay dữ liệu chờ, bởi thay ngay giữa chừng sẽ khiến bên nhận thấy một frame bị ghép sai. Logger nối đầu vào với kết quả bằng timestamp và bộ đếm, nên dù log ghi chậm, nhóm vẫn dùng timestamp sự kiện để phân tích thay vì lúc ghi ra đĩa.

## 4.2 Cấu hình và môi trường thực thi

Host macOS dùng biên soạn, kiểm tra portable và biên dịch chéo; Linux workload chạy trên Pi, còn firmware FreeRTOS chạy trên STM32. Test parser trên host chưa xác nhận latency UART vật lý. Nhóm so sánh P0 mặc định với P1 điều chỉnh real-time; trong thử phần mềm, source dùng FIFO priority 60 và bridge dùng FIFO priority 70 trên CPU 1, còn inference giữ SCHED_OTHER trên CPU 0. Bridge được ưu tiên để chuyển giao; phương án đầu dùng priority 50. P2 giới hạn quota CPU và P3 chưa có kết quả sơ bộ được chấp nhận.

## 4.3 Firmware: từ nhận byte đến quyết định

Thiết kế ban đầu đi theo ISR → buffer hữu hạn → RX task → supervisor → output. Để dễ kiểm soát thời gian, ngắt chỉ nhận byte rồi bàn giao phần phân tích frame và quyết định đầu ra cho task; firmware mặc định hiện đã chuyển sang nhận DMA vòng. Chế độ IRQ vẫn được giữ để đối chiếu với DMA, bởi cả hai cách đều phải bàn giao dữ liệu ngoại vi sang task trước khi thực hiện giám sát. RX task lấy dữ liệu để dựng frame và kiểm CRC, rồi chuyển sự kiện kèm timestamp và generation cho supervisor. Khi buffer đầy, bộ đếm mất hoặc dấu gián đoạn phải phản ánh được sự thiếu hụt, vì dữ liệu bị mất không được làm mới liveness. Supervisor giữ quyền sở hữu trạng thái, còn task trạng thái truyền các bản ghi đã chụp để UART TX không chặn quyết định. Bộ nhớ được cấp phát tĩnh. Với DMA, log ghi timestamp RX đọc byte CRC cuối sau khi byte đã tới chân UART, nên chu kỳ đánh thức, jitter scheduler và thời gian rút cả lô dữ liệu khiến timestamp log khác thời gian đến phần cứng. Nếu bỏ lỡ cả vòng DMA hoặc có lỗi UART, firmware phải xử lý bảo thủ thay vì tiếp tục coi dữ liệu là liên tục. 

## 4.4 Công cụ đo và miền đồng hồ

Nhóm dùng cyclictest đo đánh thức, stress-ng tạo tải và log pipeline theo dõi kết quả. Echo ánh xạ đồng hồ Pi với TIM2, còn logic analyzer đối chiếu UART/GPIO; phép trừ khác miền phải nêu bất định [8]. Tuổi nguồn ước lượng gồm tuổi lúc gửi, thời gian sau nhận và dự phòng truyền chưa được chứng minh là cận trên. MONOTONIC và MONOTONIC_RAW phải được kiểm tra riêng. Độ dư echo nhỏ chưa chứng minh đường truyền đối xứng hoặc ánh xạ chính xác tuyệt đối.

# PHẦN 5. NGUỒN CAMERA VÀ PIPELINE ƯU TIÊN ĐỘ MỚI

## 5.1 Động cơ và capture

Nguồn tổng hợp trước đây chỉ tạo frame_id và timestamp, nên chưa phản ánh thời điểm cảnh được phơi sáng; nguồn Pi Camera v2 (IMX219) bổ sung pixel thật để khảo sát scheduling, IPC và queue trên workload thực tế; nhóm không đánh giá độ chính xác mô hình. Chương này rút gọn từ bản tiếng Việt của chương camera trong đợt cập nhật. Lượt 30 fps ngày 30/10 ghi nhận 9.000 khung, khoảng cách trung bình 33,3229 ms, jitter P99 0,0303 ms, không có sequence gap và offset sensor→receive P99 12,157 ms. Lượt 10 fps ngày 31/10 ghi nhận 3.000 khung, khoảng cách trung bình 99,957 ms, jitter P99 0,359 ms, không rơi khung và offset sensor→receive P99 10,54 ms. Cả hai lượt đáp ứng các ngưỡng timing; cặp BOOTTIME/MONOTONIC đầu và cuối lượt 10 fps giữ offset đọc lần lượt khoảng −1,09 và −1,02 µs, phù hợp với clock stability đã kiểm tra.

hea_cam nhận frame qua callback hoàn tất request của libcamera, dùng sequence của buffer làm frame_id và ghi t_recv_mono_ns bằng CLOCK_MONOTONIC ngay đầu callback; pixel RGB được sao chép sau khi đồng bộ đọc DMA buffer và loại padding theo stride. SensorTimestamp đánh dấu bắt đầu phơi sáng dòng đầu tiên, được giữ nguyên trong t_sensor_ns và truyền làm t_input_ns. Timestamp này thuộc CLOCK_BOOTTIME; chỉ giả định ánh xạ đồng nhất sang MONOTONIC khi Pi không suspend. Cần ghi cặp BOOTTIME/MONOTONIC đầu và cuối lượt, vì một cặp đầu lượt chưa chứng minh quan hệ hai clock ổn định.

## 5.2 Ring pixel và chính sách đầu vào

Pixel nằm trong shared-memory ring hữu hạn, mặc định bốn slot; Unix datagram vẫn chỉ mang frame_id 4 byte và t_input_ns 8 byte, little-endian. Tách pixel khỏi notification giữ nguyên record IPC, đồng thời tránh đưa cả ảnh vào socket queue. Reader chọn slot theo frame_id modulo số slot. Writer duy nhất chuyển sequence counter từ chẵn sang lẻ, ghi dữ liệu rồi công bố counter chẵn. Reader sao chép một lần có giới hạn và kiểm tra lại counter để tránh dùng ảnh không nhất quán.

Counter lẻ hoặc thay đổi được đếm là torn; slot ổn định nhưng chứa frame_id khác được đếm là overwritten và bỏ qua. Với input-policy latest, inference rút các notification đang chờ, chọn đầu vào hợp lệ mới nhất và đếm skipped_stale. Bridge có latest-value riêng cho kết quả chờ gửi. Đường đi là camera → ring và notification → inference → bridge → UART → supervisor. Cơ chế này giới hạn dữ liệu cũ bằng cách bỏ công việc, nhưng không làm inference nhanh hơn hoặc bảo đảm deadline.

## 5.3 Mốc AoI và điều kiện kiểm chứng

Gọi g_i là thời điểm phơi sáng đã ánh xạ sang đồng hồ consumer và r_i là thời điểm nhận kết quả. Ngay sau cập nhật, tuổi dữ liệu bằng r_i − g_i; trước cập nhật kế tiếp, tuổi tăng tuyến tính theo thời gian. AoI trung bình phải lấy diện tích dưới đường tuổi chia cho thời lượng cửa sổ đã khởi tạo, kể cả khoảng ngừng nhận. Không dùng latency trung bình của gói để thay thế phép tính này. Cách tính giữ nguyên ý nghĩa AoI đã nêu ở Phần 2.

Trong hai lượt OS-T1, offset t_recv − t_sensor luôn dương và P99 nhỏ hơn chu kỳ tương ứng cộng 10 ms: lượt 30 fps có P50/P99/cực đại 10,411/12,157/14,676 ms; lượt 10 fps có P99 10,54 ms. Lượt 10 fps ghi cặp BOOTTIME/MONOTONIC ở đầu và cuối, offset đọc lần lượt −1,093 và −1,018 µs; throttling bằng 0x0 trước/sau. Cùng với chu kỳ, jitter và số khung rơi đạt ngưỡng, OS-T1 đáp ứng đầy đủ tiêu chí. Camera/inference dùng MONOTONIC, trong khi bridge hiện dùng MONOTONIC_RAW để kiểm tuổi và đồng bộ, nên chưa được trừ trực tiếp các mốc này khi diễn giải AoI camera đầu-cuối trên MCU.

# PHẦN 6. ĐÁNH GIÁ SƠ BỘ

## 6.1 Tiến độ kiểm thử camera đến giữa kỳ

Bảng 2 tổng hợp số đo Pi ngày 29–31/10 và đối chiếu tiêu chí kiểm thử đã định trước. PASS/FAIL xét cả chỉ số lẫn điều kiện hợp lệ của lượt chạy. OS-T1 đạt ở cả 30 fps và 10 fps. OS-T2 đạt với governor performance ở cấu hình 2 luồng; các lượt ondemand ngày 29/10 vẫn được giữ và đánh dấu không hợp lệ. Một lần thử ngày 31/10 không chạy được do thiếu onnxruntime trong Python hệ thống và đã bị xóa trước khi lưu trữ. T3/T4 giữ FAIL theo kết quả và giới hạn metric đã ghi; số liệu AoI tại RX không đồng nghĩa với AoI trung bình theo thời gian.

Bảng 2. Số đo và đối chiếu tiêu chí OS-T1–OS-T4 trên Raspberry Pi 5.
| Kiểm thử | Trạng thái theo tiêu chí | Chỉ số thực đo |
|---|---|---|
| OS-T1 — timing nguồn IMX219 và timestamp sensor | PASS — cả hai tốc độ khung, độ ổn định clock và điều kiện hợp lệ đạt tiêu chí. | 30 fps, n=9.000: chu kỳ TB 33,3229 ms (lệch −0,0314%); jitter P99 0,0303 ms; rơi 0/9.000; offset sensor→receive P99 12,157 ms. 10 fps, n=3.000: chu kỳ TB 99,957 ms; jitter P99 0,359 ms; rơi 0/3.000; offset P99 10,54 ms; BOOTTIME−MONOTONIC đầu/cuối −1,093/−1,018 µs; throttle 0x0 trước/sau. |
| OS-T2 — baseline inference trên frame camera | PASS — lượt governor performance hợp lệ; chọn 2 luồng vì P99/P50 = 1,27 < 1,5. | MobileNetV2 ONNX; 1.000 warm-up + 5.000 mẫu/thiết lập; throttle 0x0. P50/P95/P99 (ms), P99/P50: 1 luồng 44,72/46,42/52,25; 1,17. 2 luồng 31,05/33,89/39,31; 1,27. 4 luồng 30,36/33,88/50,18; 1,65. Các lượt ondemand ngày 29/10 vẫn được liệt kê là không hợp lệ. |
| OS-T3 — tranh chấp bộ nhớ/cache, P0 so với P1 | FAIL; dữ liệu xác nhận hồi quy khi tải băng thông nhớ, đúng với nhãn nhóm. | Latency camera→inference hoàn tất P50/P99, trung vị 3 lượt (ms), P0→P1: nhàn 58,224/59,894→58,090/59,608; CPU stream 321,040/355,267→320,926/355,420; memory-rate 363,034/408,248→370,637/421,862. Tỉ lệ trễ hạn và cyclictest max không có trong summary nên chưa đối chiếu được hai chỉ số đó. |
| OS-T4 — FIFO/latest-value và tích hợp bridge | FAIL; chưa đủ bằng chứng đạt tiêu chí AoI trung bình theo thời gian và hàng FIFO tăng không giới hạn, phù hợp nhãn nhóm. | AoI tại RX P50/P99, trung vị 3 lượt (ms): nhàn FIFO 170,413/186,858; latest 169,997/186,508. Memory-rate FIFO 263,403/314,712; latest 265,366/300,181. Summary không ghi time-average/peak AoI, deadline-miss fraction hay queue length; dưới tải có khoảng 1.300 frame bị ring overwrite/lượt (đây không phải số đo độ dài hàng FIFO). |

Nguồn: `2026-10-30_os_t1_camera`; `2026-10-31_os_t1_camera_10fps`; `2026-10-29_os_t2_infer` (không hợp lệ); `2026-10-31_os_t2_infer_performance`; `2026-10-30_os_t3_contention`; `2026-10-30_os_t4_policy` (các tóm tắt pipeline ghi nhận timestamp phần mềm, không đo UART vật lý hoặc thời gian MCU).

![OS-T1. Phân bố khoảng cách frame từ timestamp sensor trong hai lượt 30 fps và 10 fps.](figures/os_t1_frame_intervals.png)
![OS-T2. P50/P95/P99 latency suy luận theo số luồng.](figures/os_t2_latency_threads.png)
![OS-T3. Latency P99 camera→inference hoàn tất theo tải, so sánh P0/P1.](figures/os_t3_p0_p1.png)
![OS-T4. AoI tại RX theo FIFO/latest và tải.](figures/os_t4_fifo_latest.png)

## 6.2 Phương pháp và môi trường đo lịch sử

Các bảng lịch sử dưới đây giữ dữ liệu trước đợt camera, gồm nguồn tổng hợp, ảnh cố định và PTY; chúng không xác nhận OS-T1–OS-T4 mới. Nhóm đo riêng đánh thức định kỳ, inference độc lập, pipeline phần mềm và phản ứng trên bo mạch. Số lượt thu được không đồng nghĩa số lượt đủ điều kiện cho mọi cách phân tích: ở Bảng 3, E1/E2/E3 PTY đạt 45/45 theo kiểm tra phần mềm ban đầu nhưng chỉ 0/45 đủ theo dõi bổ sung. Mỗi điều kiện được ghi đầu vào, tải nền, cấu hình scheduler và chế độ điều chỉnh tần số. Mẫu cùng lượt không phải lần lặp độc lập, vì vậy phân vị lấy trung vị giữa lượt, còn giá trị lớn nhất lấy cực đại quan sát.

Bảng 3. Tổng hợp số lượt đo và phạm vi sử dụng.
| Nhóm thí nghiệm | Số lượt và phạm vi chấp nhận |
|---|---|
| cyclictest | 30/30 theo kiểm tra ban đầu; 3/15 mỗi cấu hình đủ theo dõi bổ sung, chỉ khi nhàn rỗi |
| Suy luận độc lập | 21/24; loại 3 lượt 4 luồng vì điện áp thấp trực tiếp |
| E1/E2/E3 PTY | 45/45 theo kiểm tra phần mềm ban đầu; 0/45 đủ theo dõi bổ sung |
| E3b đầu vào latest | 3/12; cả 6 lượt có tải đều bị loại |
| E3 UART ban đầu | 0/18; cờ nguồn, clock và thiếu sự kiện có thể chồng nhau |
| E4 gốc | 17/25 mục; gồm 5 mục F5 chưa thực hiện |
| F5 riêng | 5/5 cho chuyển trạng thái cửa sổ ngắn |

Pi dùng kernel 6.8.0-1064-raspi, PREEMPT_DYNAMIC và nguồn 5 V / 3 A. Trong baseline inference, điện áp dưới tải được ghi ở mức 4.66–4.92 V, nên nhóm giữ thông tin này để đối chiếu với các lượt có vấn đề nguồn. Baseline dùng chế độ điều chỉnh tần số ondemand trong khi chiến dịch pipeline dùng performance, nên chênh lệch giữa hai tập còn chịu khác biệt cấu hình và không thể quy cho riêng IPC. Sau khi kiểm tra lại cách thu thập, nhóm yêu cầu theo dõi hệ thống bằng đồng hồ đơn điệu thô với khoảng cách mẫu không quá 1.5 s. Tiến trình tạo tải phải được xác nhận còn hoạt động và phép khớp đồng hồ không được cũ quá 5 s. Đồng hồ lịch trên Pi lệch khoảng 3 ngày, nhưng các khoảng thời gian vẫn được tính bằng đồng hồ đơn điệu.

## 6.3 Đánh thức timer và suy luận độc lập

Ở Bảng 4, nhóm dùng cyclictest với luồng đo trên CPU 0, timer cách nhau 1 ms và bộ nhớ được khóa. Với mỗi lượt kéo dài 120 s và 3 lần lặp cho mỗi điều kiện, nhóm đối chiếu P0 dùng SCHED_OTHER với P1 dùng FIFO priority 50 đã được kiểm tra trên luồng đo. Hai hàng đối chiếu latency thường gặp và phần đuôi.

Bảng 4. Kết quả sơ bộ cyclictest, đơn vị µs; P50/P99 là trung vị giữa lượt đo, giá trị lớn nhất là cực đại quan sát.
| Tải | P0 P50 | P0 P99 | P0 lớn nhất | P1 P50 | P1 P99 | P1 lớn nhất |
|---|---|---|---|---|---|---|
| Nhàn rỗi | 53 | 57 | 2659 | 3 | 9 | 92 |
| memrate CPU 2–3 | 55 | 613 | 5170 | 5 | 239 | 1094 |

Khi có memrate ở Bảng 4, P99 của P0 tăng từ 57 lên 613 µs, còn P1 tăng từ 9 lên 239 µs. Mặc dù P1 giảm tail latency so với P0, tải nhớ vẫn gây ảnh hưởng; hơn nữa, trung vị P0 còn chịu timer slack nên khoảng cách P50 chưa thể quy hết cho thời gian chờ bộ scheduler. Quan sát này phù hợp với việc các lõi chia sẻ tài nguyên, tuy vậy đây chưa phải phép đo trực tiếp băng thông nhớ. Kết quả đánh thức timer cũng không đại diện cho thời gian inference hoặc latency UART.

Bảng 5. Thời gian gọi MobileNetV2 ở các điều kiện tải và số thread, đơn vị ms.
| Tải / luồng ORT | Lặp hợp lệ | P50 | P99 | Lớn nhất |
|---|---|---|---|---|
| Nhàn rỗi / 1 | 3 | 44.0 | 48.0 | 57.0 |
| Nhàn rỗi / 3 | 3 | 29.4 | 38.5 | 52.8 |
| Nhàn rỗi / 4 | 1 | 31.4 | 70.7 | 94.1 |
| Tải CPU / 1 | 3 | 45.1 | 53.7 | 65.5 |
| Tải CPU / 4 | 2 | 60.3 | 100.5 | 150.3 |

Mỗi lượt ở Bảng 5 tính giờ 1000 lần gọi sau 50 lần chạy làm nóng. Khi nhàn rỗi, P50 giảm từ 44.0 ms với 1 luồng xuống 29.4 ms với 3 luồng, cho thấy thêm luồng có thể giúp lời gọi mô hình hoàn tất sớm hơn. Dưới tải CPU, hàng 4 luồng lại có P50 là 60.3 ms, cao hơn 45.1 ms của hàng 1 luồng. Vì lợi ích phụ thuộc tranh chấp và số lượt hợp lệ cũng khác nhau, nhóm tách tiền xử lý khỏi lời gọi mô hình để tránh gộp các công việc vào cùng kết luận.

## 6.4 Tranh chấp, điều chỉnh và chính sách hàng đợi

Bảng 6 đo từ lúc sinh đầu vào tới khi receiver trên Pi nhận kết quả qua PTY, với 3 lần lặp mỗi ô. Phép đo khảo sát queue và tính toán. Đây là pipeline phần mềm. Kết quả chưa đại diện UART vật lý giữa Pi và STM32.

Bảng 6. Kết quả sơ bộ E1/E2/E3: latency và AoI, đơn vị ms; không phải phép đo UART vật lý.
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

Trong Bảng 6, P50 chuyển giao E1 P0 tăng từ 44.37 ms khi idle lên 6626 ms dưới memrate. Ở E3 memrate, AoI trung bình của latest là 6958 ms, trong khi FIFO là 6660 ms; thay kết quả tại bridge chưa làm tuổi giảm. Bộ đếm thay thế tại bridge của các hàng E3 đều bằng 0 trong bảng tổng hợp, gợi ý dữ liệu đang chờ trước inference. Nhóm vì vậy đối chiếu từng giai đoạn trước khi quy nguyên nhân cho inference chậm, giữ kết quả cache E2 vì P1 cũng chưa cải thiện chung.

AoI trung bình chỉ tính trên thời gian đã khởi tạo, gồm khoảng ngừng cập nhật và đuôi cửa sổ. Tỷ lệ thời gian vi phạm dùng mẫu số thời lượng. Tỷ lệ gói lỡ hạn dùng số lần nhận. Với latest-value, số sinh, giao, mất và bị thay phải được báo cùng tuổi dữ liệu.

Nhóm chuyển điểm loại đầu vào cũ lên trước inference trong E3b, nhưng các lượt được chấp nhận vẫn phải tách khỏi lượt lỗi nguồn theo Bảng 3.

## 6.5 Liên kết thật, lỗi và đối chiếu đầu ra

Đợt E3 đầu trên UART vật lý có 0/18 lượt đủ điều kiện so sánh; 16/18 lượt xuất hiện cảnh báo nguồn và mọi lượt tải bộ nhớ đều có sai lệch khớp đồng hồ vượt ngưỡng. Trong 18 lượt đo lại, sụt áp vẫn xuất hiện ở tất cả các lượt; khi giữ dữ liệu mới nhất ở cả đầu vào lẫn bridge dưới tải, lượt đầu còn ở FAILSAFE suốt cửa sổ. Các lượt tiếp theo ở HOLD lần lượt 92.15% và 91.44%, cho thấy cần xem diễn biến trạng thái thay vì chỉ đếm kết quả nhận được. Các lượt này chỉ dùng chẩn đoán.

Bảng 7 phân biệt mất liveness với dữ liệu cũ khi heartbeat vẫn đến. F1 và F2 lấy heartbeat cuối làm mốc. F3 và F5 lấy inference cuối. Vì khác mốc, các latency không được gộp để so trực tiếp hai cơ chế.

Bảng 7. Thời gian MCU chuyển sang FAILSAFE theo nguyên nhân lỗi, đơn vị ms.
| Lỗi | Lượt chấp nhận | Mốc tham chiếu | P50 | Lớn nhất |
|---|---|---|---|---|
| F1 kết thúc bridge | 5/5 | Heartbeat cuối | 100.456 | 100.641 |
| F2 SIGSTOP bridge | 5/5 | Heartbeat cuối | 100.577 | 100.596 |
| F3 SIGSTOP inference | 5/5 | Inference cuối | 475.754 | 475.815 |
| F5 ngừng inference, HB còn | 5/5 | Inference cuối | 475.596 | 475.917 |

Nhóm đặt ngưỡng heartbeat 100 ms, HOLD tuổi nguồn 200 ms và FAILSAFE tuổi nguồn 500 ms để thử phản ứng giám sát. Ở Bảng 7, P50 của F5 là 475.596 ms dù ngưỡng FAILSAFE tuổi nguồn lớn hơn khoảng sau lần nhận cuối. Vì kết quả đã có tuổi lúc gửi và phép ước lượng còn cộng khoản truyền giả định 5 ms, khoảng sau lần nhận cuối không dùng chung mốc bắt đầu với tuổi nguồn. HOLD chưa phải heartbeat timeout, bởi tuổi nguồn có thể vượt ngưỡng trong khi bản tin heartbeat vẫn đến, nên cần đọc đúng nguyên nhân chuyển trạng thái.

Logic analyzer đối chiếu log qua GPIO. Khoảng quan sát là 86.938–95.541 ms ở F1, 86.947–98.676 ms ở F2 và 82.852–91.302 ms ở F4; F2 có cả lượt bắt tín hiệu kiểm tra. Trong các lần bắt, 10/15 lần khớp mốc heartbeat trong 0.07 ms, còn 5 lần khác có một frame tới sau heartbeat nên byte cuối trên dây không phải heartbeat cuối được MCU chấp nhận. 

# PHẦN 7. THẢO LUẬN VÀ HẠN CHẾ

## 7.1 Câu trả lời trong phạm vi bằng chứng

Kết quả sơ bộ cho RQ1 ghi nhận tail latency tăng dưới tải nhớ, còn RQ2 cho thấy priority cải thiện đánh thức nhưng chưa cô lập tài nguyên. Memory locking, affinity và priority cần thử loại trừ riêng. Với RQ3, bỏ đầu vào trước inference tác động phần tuổi khác với bỏ kết quả tại bridge. RQ4 có log MCU/GPIO, nhưng timeout danh định chưa phải cận trên phản ứng.

## 7.2 Hạn chế của OS-T3 và OS-T4

OS-T3 FAIL: dưới memory-rate, latency P99 camera→inference hoàn tất của P1 tăng từ 408,248 lên 421,862 ms so với P0; CPU stream gần như không đổi nhưng không bù được hồi quy này. Summary không cung cấp deadline-miss fraction và cyclictest max nên kết luận không mở rộng sang hai chỉ số đó. OS-T4 cũng FAIL theo tiêu chí đã đặt trước: AoI tại RX P99 của latest thấp hơn FIFO ở hai cấu hình tổng hợp, nhưng một số lượt riêng không giảm và phép đo không tính AoI trung bình theo thời gian, AoI đỉnh hay tăng trưởng độ dài hàng FIFO. Đây chưa phải bằng chứng bác bỏ lợi ích latest-value; dữ liệu hiện có chưa đủ xác nhận giả thuyết kiểm thử. OS-T1 và OS-T2 đã đạt sau các lượt hợp lệ ngày 30–31/10; T3/T4 vẫn cần bổ sung các metric còn thiếu.

## 7.3 Độ tin cậy và khả năng khái quát

Sụt áp là nhiễu chính dưới tải, nên một số lượt chỉ để tham khảo cùng nhiệt độ, chế độ tần số và số thread. Với cyclictest, phần có tải còn thiếu xác nhận process tạo tải hoạt động liên tục; các lượt pipeline lại thiếu độ phủ theo dõi toàn cửa sổ. Theo dõi điện áp định kỳ vẫn có thể bỏ lỡ nhiễu ngắn giữa các mẫu, trong khi cờ nguồn lưu từ trước phải được tách khỏi cảnh báo xảy ra ngay trong lượt. Hàng nghìn mẫu liên tiếp vẫn có thể tương quan, nên số mẫu lớn chưa thay được số lần chạy độc lập. Vì ánh xạ đồng hồ phụ thuộc echo và độ mới của phép khớp, task FIFO khi tiêm lỗi có thể làm bridge thiếu CPU và gián đoạn đường quan sát, nên thiếu STATE_EVENT chưa chứng minh MCU luôn FRESH và nhóm không tự điền tỷ lệ thời gian.

Bằng chứng chưa xác nhận an toàn robot, stack dài hạn, DMA không giới hạn hoặc watchdog độc lập. GPIO thấp chỉ là quy ước demo. Với robot cần giữ cân bằng, tắt động cơ có thể gây mất ổn định. Phản ứng quan sát vì thế chỉ được diễn giải cho output mô phỏng.

# PHẦN 8. KẾ HOẠCH TIẾP THEO

## 8.1 Lịch dự kiến đến hết tháng 11/2026

Bảng 8 là kế hoạch, chưa phải kết quả đã đạt. Nhóm ưu tiên sửa OS-T3/T4 và xác nhận đường UART trước khi thử tải mở rộng trên FreeRTOS. Mọi phép đo mới cần lưu cấu hình, lệnh chạy, log thô và tóm tắt; metadata phải phân biệt Pi 4 GB hiện tại với bo 8 GB của tập lịch sử. Các mốc có thể điều chỉnh theo kết quả kiểm tra nhưng không đổi ngưỡng đạt sau khi xem dữ liệu. Báo cáo cuối kỳ và demo dự kiến hoàn tất ngày 30/11/2026.

Bảng 8. Kế hoạch kiểm thử và hoàn thiện cuối kỳ (dự kiến).
| Thời gian năm 2026 | Công việc và điều kiện hoàn thành |
|---|---|
| 01–07/11 | Củng cố số lượt hợp lệ T1/T2 nếu thời gian cho phép; bổ sung metric deadline/cyclictest cho T3 và time-average AoI/queue length cho T4; đo lại các cấu hình cần thiết |
| 08–12/11 | OS-T5: UART 921600 baud theo runbook; 10.000 frame hợp lệ, chèn CRC sai/cụt/sai version; không nhận frame lỗi, RTT P99 < 5 ms |
| 13–18/11 | OS-T6: kill bridge, SIGSTOP inference, FIFO CPU hog, dữ liệu cũ nhưng HB còn; 10 lần mỗi lỗi; đối chiếu LED/MCU, latch và rearm; chạy bình thường 30 phút |
| 19–23/11 | OS-T7 mở rộng sau T5/T6: task MPU6050 200 Hz khi UART rảnh, dồn frame tốt và frame lỗi; mục tiêu jitter P99 < 100 µs, không lỡ mẫu |
| 24–26/11 | OS-T8: rà soát kịch bản mở rộng trong nguồn và xác định phương án phù hợp phạm vi UART; chưa triển khai CAN vì ngoài giới hạn của báo cáo hiện tại |
| 27–30/11 | Lặp các phép đo còn thiếu, tổng hợp PASS/FAIL và bất định; hoàn thiện báo cáo cuối kỳ, slide và demo camera → inference → UART → LED |

## 8.2 Điều kiện phép đo và bench

Mỗi cấu hình mặc định có ba lượt năm phút, trừ khi kịch bản quy định riêng; mục tiêu củng cố bằng chứng vẫn là ít nhất năm lượt hợp lệ khi đủ thời gian. Nhóm kiểm throttle bằng 0x0 trước/sau, governor performance, metadata và tiến trình tạo tải trong toàn cửa sổ. OS-T2 dùng 1.000 lượt làm nóng rồi 5.000 lần inference mỗi số thread; đây là quy trình dự kiến đối chiếu log, không phải số mẫu đã xác nhận. Khi chuyển firmware, bench phải sao lưu image cũ, kiểm hash và read-back theo runbook. UART OS dùng 921600 baud, thay cho con số 115200 trong bảng kịch bản cũ.

# PHẦN 9. KẾT LUẬN

Báo cáo ghi nhận camera IMX219 đã hoạt động và trình bày số đo mới cho OS-T1–OS-T4. OS-T1 PASS ở 30 fps và 10 fps, gồm timing, clock và validity; OS-T2 PASS với governor performance ở 2 luồng, đạt P99/P50 = 1,27. Các lượt T2 ondemand trước đó vẫn được giữ với nhãn không hợp lệ. OS-T3 FAIL do P1 tăng AoI P99 dưới tải băng thông nhớ. OS-T4 vẫn FAIL vì chưa đo time-average AoI và tăng trưởng hàng FIFO theo tiêu chí, dù AoI tại RX P99 trung vị của latest thấp hơn FIFO trong hai cấu hình tổng hợp. Nền tảng Edge-AI không đồng nhất cho phép quan sát Linux xử lý workload biến thiên và FreeRTOS giám sát qua UART. Supervisor cần kiểm cả liveness và freshness; nhóm sẽ bổ sung các metric còn thiếu cho T3/T4.

# TÀI LIỆU THAM KHẢO
[1] Linux kernel documentation, “Real-Time group scheduling.” Truy cập ngày 10/10/2026.
[2] H. Yun, G. Yao, R. Pellizzoni, M. Caccamo, and L. Sha, “MemGuard: Memory bandwidth reservation system for efficient performance isolation in multi-core platforms,” in *IEEE RTAS*, 2013, pp. 55–64.
[3] S. K. Kaul, R. D. Yates, and M. Gruteser, “Real-time status: How often should one update?” in *IEEE INFOCOM*, 2012, pp. 2731–2735.
[4] S. K. Kaul, R. D. Yates, and M. Gruteser, “Status updates through queues,” in *CISS*, 2012, pp. 1–6.
[5] S. Bak, D. K. Chivukula, O. Adekunle, M. Sun, M. Caccamo, and L. Sha, “The System-Level Simplex Architecture for Improved Real-Time Embedded System Safety,” in *IEEE RTAS*, 2009, pp. 99–107.
[6] S. Bak, T. T. Johnson, M. Caccamo, and L. Sha, “Real-Time Reachability for Verified Simplex Design,” in *RTSS*, 2014, pp. 138–148.
[7] ONNX Runtime documentation, “Thread management.”
[8] D. Mills, “Simple Network Time Protocol (SNTP) Version 4,” RFC 4330, Jan. 2006, sec. 5.

