<!-- COVER -->
**ĐẠI HỌC BÁCH KHOA HÀ NỘI**
**BÁO CÁO BÀI TẬP LỚN**
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
Báo cáo trình bày nền tảng thực thi Edge-AI không đồng nhất đang trong quá trình triển khai cho học phần Hệ điều hành. Nhóm dùng Raspberry Pi chạy Ubuntu để xử lý suy luận, trong khi STM32 chạy FreeRTOS giám sát độc lập qua UART. Nhóm khảo sát ảnh hưởng của lập lịch, tranh chấp tài nguyên và hàng đợi tới độ tươi. Các câu hỏi xoay quanh tải, cấu hình, hàng đợi và phản ứng khi Linux lỗi. Kết quả sơ bộ ghi nhận ưu tiên thời gian thực cải thiện đuôi trễ đánh thức, nhưng tranh chấp bộ nhớ vẫn còn và thay kết quả tại bridge chưa giải quyết được tồn đọng trước suy luận. UART và GPIO giúp đối chiếu log, phân biệt mất heartbeat với kết quả cũ dù heartbeat vẫn đến. Công việc tiếp theo tập trung vào nguồn điện, phép đo lặp và đối chiếu thời gian độc lập.
**Từ khóa:** hệ điều hành; Linux; FreeRTOS; UART; lập lịch; độ tươi dữ liệu; giám sát độc lập.
<!-- PAGE -->
<!-- TOC -->
<!-- PAGE -->

# CHƯƠNG 1. GIỚI THIỆU

## 1.1 Động lực và bài toán

Trong hệ thống Edge-AI, kết quả đúng chưa chắc còn hữu ích, bởi đầu vào có thể đã thay đổi trong lúc Raspberry Pi xử lý ảnh hoặc chờ bridge gửi kết quả tới nơi. Linux thuận tiện vì có sẵn thư viện và công cụ chạy mô hình, tuy vậy tiến trình còn phải chia sẻ CPU, bộ nhớ và các hàng đợi với công việc khác. Thông lượng chưa phải độ tươi. Đầu ra còn phải theo kịp trạng thái hiện tại.

Raspberry Pi 5 chạy Ubuntu Server 24.04 ARM64 tính toán, còn STM32F446RE chạy FreeRTOS nhận dữ liệu và quyết định đầu ra mô phỏng. Qua UART, nhóm theo dõi AI như tải tính toán phục vụ nghiên cứu lập lịch, tranh chấp tài nguyên và truyền thông. MCU không chạy suy luận. Chúng em nghiên cứu cơ chế OS thay vì đề xuất mạng nơ-ron mới.

## 1.2 Câu hỏi nghiên cứu và đóng góp

Nhóm đặt các câu hỏi:
- RQ1: Tải cạnh tranh làm thay đổi thời gian phục vụ và chuyển giao dữ liệu như thế nào?
- RQ2: Điều chỉnh ưu tiên, gán CPU và khóa bộ nhớ khôi phục được phần nào của độ trễ?
- RQ3: FIFO và latest-value tác động thế nào đến độ tươi; nên thay thế dữ liệu ở đâu?
- RQ4: Khi Pi ngừng cung cấp dịch vụ, MCU phát hiện và chuyển đầu ra về trạng thái an toàn mô phỏng khi nào?

Nhóm gắn dấu thời gian để lần theo dữ liệu từ Pi tới MCU và tìm chỗ chờ, trong khi bộ giám sát giữ quyền điều khiển dựa trên cả hoạt động của bridge lẫn độ mới của kết quả. Kết quả sơ bộ hướng việc phân tích về thời gian đầu vào đã chờ trước suy luận, vì thay dữ liệu ở bridge chỉ tác động tới đoạn sau. Những lượt đo thất bại cũng được giữ để tìm lỗi nguồn điện và mốc thời gian.

# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG TRÌNH LIÊN QUAN

## 2.1 Lập lịch Linux và tranh chấp tài nguyên

CFS chia thời gian CPU theo trọng số và lịch sử sử dụng, còn EEVDF tiếp tục mục tiêu công bằng qua điều kiện đủ tư cách và thời hạn ảo. Tuy nhiên, công bằng không bảo đảm hoàn thành đúng hạn, nên bridge trên Pi vẫn có thể phải chờ ngay cả khi gói dữ liệu cần gửi đã sẵn sàng. Cấu hình thực tế phải được xác nhận. Log vì vậy cần ghi phiên bản kernel và chính sách của luồng.

SCHED_FIFO dùng ưu tiên thời gian thực cố định, cho phép luồng sẵn sàng có ưu tiên cao chiếm CPU của công việc ưu tiên thấp hơn. Vì bridge chỉ xử lý ngắn, nhóm kỳ vọng dữ liệu được chuyển sớm sau đánh thức; tuy vậy, một luồng chạy quá lâu có thể khiến các công việc khác không được phục vụ. Ưu tiên còn phụ thuộc cấu hình. Nhóm cần xét quyền đặt ưu tiên, giới hạn băng thông thời gian thực và cấu hình nhóm [1].

Gán CPU giảm di chuyển nhưng không tách được bộ nhớ dùng chung giữa các lõi, nên luồng trên CPU riêng vẫn có thể chậm khi tải nền liên tục đọc ghi. MemGuard nghiên cứu cô lập băng thông bộ nhớ [2], giúp giải thích giới hạn ấy dù đồ án không cài cơ chế kernel của công trình. cgroups gom tiến trình và giới hạn tài nguyên tải nền, nhưng hạn mức CPU quá thấp cũng gây throttling. Với đường xử lý nhạy cảm về thời gian, mlockall giữ trang trong RAM nhằm giảm rủi ro lỗi trang. Tuy nhiên, khóa bộ nhớ không loại được chi phí tính toán, cache miss hoặc tranh chấp nhớ, nên nhóm vẫn kiểm tra lỗi trả về và ghi trạng thái khóa thực tế khi chạy thử.

## 2.2 PREEMPT_RT và giới hạn suy diễn

PREEMPT_RT giảm những vùng không thể bị chiếm quyền và thay đổi cách xử lý một phần công việc trong kernel. Nhóm chỉ dự kiến thử kernel Real-time Ubuntu đóng gói ở cấu hình P3, không sửa hoặc tự biên dịch kernel. Vì các kết quả sơ bộ hiện có đều được thu trên kernel tiêu chuẩn, nhóm chưa thể dùng chúng để kết luận về PREEMPT_RT hoặc lợi ích của P3 với bridge trên Pi. Phần so sánh này cần được đo riêng.

## 2.3 Độ tươi dữ liệu và giá trị của kết quả

Độ tươi dữ liệu (Age of Information, AoI) tại thời điểm quan sát là thời gian từ lúc sinh dữ liệu mới nhất có ích mà bên nhận đang giữ [3], [4]. Nếu MCU chưa nhận được kết quả mới, tuổi của kết quả cũ vẫn tăng dù không có gói nào đang được giao. Chính sự tăng tuổi giữa hai lần cập nhật làm AoI khác độ trễ của riêng một gói, nên nhóm không dùng trung vị độ trễ chuyển giao để thay cho trung bình AoI. Khoảng không có cập nhật vẫn phải tính. Nếu chỉ xét gói giao thành công, nhóm sẽ bỏ qua khoảng mất dữ liệu và phần thời gian sau cập nhật cuối.

Trong Hình 2.1, tuổi tăng theo thời gian rồi giảm khi bên nhận có cập nhật mới. Tuy nhiên, gói vừa tới đã mang theo thời gian chờ và truyền trước đó, nên tuổi không mặc nhiên trở về không. Vì đầu vào trên Pi đã có tuổi khi MCU nhận kết quả, AoI trung bình phải được tích phân trên cửa sổ xác định, với cách xử lý rõ ràng cho khoảng trước cập nhật đầu tiên và những lúc ngừng chuyển giao.

![Hình 2.1. Minh họa AoI và ngưỡng độ tươi; hình khái niệm, không chứa kết quả đo.](figures/V20.jpg)

## 2.4 Simplex và FreeRTOS trên MCU

Simplex tách khối phức tạp khỏi bộ điều khiển hoặc giám sát đáng tin cậy, quy định quyền tác động [5], [6]. Theo cách phân quyền đó, Pi chỉ đề xuất còn MCU quyết định đầu ra mô phỏng; tuy vậy, timeout và trạng thái FAILSAFE chưa đủ để coi hệ thống đã có chứng minh Simplex hình thức. Phạm vi bảo đảm hiện còn giới hạn. Mô hình đối tượng, miền an toàn, giả thiết lỗi và bằng chứng thời gian vẫn cần phân tích riêng.

FreeRTOS cung cấp lập lịch ưu tiên có chiếm quyền cùng các cơ chế bàn giao dữ liệu hữu hạn. Trên STM32, dữ liệu qua ngắt nhận, tác vụ phân tích, giám sát rồi tới đầu ra. Tác vụ ưu tiên cao vẫn có thể bị trễ nếu ngắt bị che hoặc công việc trước đó kéo dài hơn dự kiến. Mặc dù cấp phát tĩnh và giao trạng thái cho một chủ sở hữu giúp giảm biến thiên, chúng em vẫn phải đo stack, thời gian thực thi và kiểm tra hành vi khi bộ đệm đầy.

# CHƯƠNG 3. THIẾT KẾ HỆ THỐNG

## 3.1 Kiến trúc và ranh giới quyền điều khiển

Dữ liệu đi qua source → suy luận → bridge trên Pi, qua UART rồi tới RX → supervisor → GPIO trên STM32. Logger thu dấu thời gian và trạng thái để tái dựng hành trình dữ liệu khi tải nền Linux cạnh tranh với tính toán và chuyển giao. MCU vẫn kiểm tra hạn khi logger không hoạt động, nên log thiếu có thể khiến nhóm chưa đủ bằng chứng kết luận dù bộ giám sát vẫn chạy.

Supervisor là nơi duy nhất được ghi đầu ra, còn kết quả suy luận hợp lệ chỉ cung cấp dữ liệu cho quyết định ấy. Heartbeat cho biết bridge còn gửi dữ liệu; INFERENCE mới cho biết có kết quả đủ mới để dùng hay không. Nếu MobileNetV2 ngừng tạo kết quả trong khi bridge vẫn gửi heartbeat, tuổi kết quả cũ phải tiếp tục tăng. Đầu ra hiện là chỉ thị GPIO. Hệ thống chưa có cơ cấu chấp hành vật lý hoặc watchdog phần cứng độc lập.

## 3.2 Khung UART và loại bản tin

Hình 3.1 mô tả khung chung, còn Bảng 1 liệt kê kích thước và vai trò của từng trường. SOF xác định ranh giới để parser kiểm độ dài và CRC trước khi giao cho logic chính sách; cụ thể, giới hạn payload 64 byte ở Bảng 1 giúp loại khung có độ dài sai. Trong khi số thứ tự giúp nhận ra dữ liệu cũ, trùng hoặc khoảng bị mất, CRC chỉ kiểm tra toàn vẹn truyền nên kết quả suy luận sai nhưng khung đúng vẫn có thể qua.

![Hình 3.1. Khung UART; hình mô tả cấu trúc, không xác nhận pinout hoặc chất lượng liên kết.](figures/V15.jpg)

Bảng 1. Cấu trúc khung truyền UART.
| Trường | Kích thước và vai trò |
|---|---|
| SOF | 2 byte: A5 5A, đồng bộ khung |
| version, type | Mỗi trường 1 byte; phân biệt phiên bản và bản tin |
| seq, len | 2 byte thứ tự; 1 byte độ dài payload |
| payload | Tối đa 64 byte, các trường nhiều byte little-endian |
| CRC | 2 byte CRC-16/CCITT-FALSE; phủ version đến payload |

HEARTBEAT mang thông tin sống còn và định danh phiên, trong khi INFERENCE mang kết quả, thứ tự đầu vào và tuổi lúc gửi để kiểm tra độ tươi. Để đối chiếu hoạt động hai bên, nhóm dùng ECHO_REQ/ECHO_RESP ước lượng quan hệ đồng hồ, đồng thời nhận MCU_STATUS chứa trạng thái và bộ đếm của bộ giám sát. Parser phân biệt theo loại bản tin. Cụ thể, STATE_EVENT ghi chuyển trạng thái còn INF_RX ghi thời điểm nhận suy luận.

## 3.3 Máy trạng thái và phiên làm việc

MCU kiểm soát đầu ra qua INIT, RUN, HOLD và FAILSAFE, trong đó RUN còn được gọi là FRESH vì dữ liệu ở trạng thái này đủ mới để sử dụng. INIT giữ đầu ra an toàn mô phỏng. Chỉ khi có cả liveness và kết quả hợp lệ, MCU mới đủ điều kiện sử dụng RUN/FRESH. Khi tuổi vượt ngưỡng và cần dữ liệu mới, HOLD ngăn cập nhật đầu ra, còn FAILSAFE được chốt để lưu lượng tốt trở lại chưa tự động đưa hệ thống về hoạt động.

Bridge khởi động lại không được kế thừa lịch sử phiên cũ. Session phân biệt lần khởi động, còn generation được gắn nội bộ vào dữ liệu đang chờ trong hàng đợi để loại dữ liệu thuộc generation cũ khi đổi phiên hoặc tái kích hoạt. Supervisor phải kiểm tra hết hạn trước khi xử lý dữ liệu vừa tới, vì một bản tin sát hạn có thể che mất sự kiện timeout nếu đảo thứ tự. Firmware hiện chưa cung cấp tự động rearm từ xa, dù lõi portable đã có khả năng này; chức năng trên bo mạch vẫn chưa hoàn tất.

## 3.4 FIFO và latest-value

FIFO giữ thứ tự dữ liệu đến, nhưng tuổi có thể tăng dần nếu nguồn sinh nhanh hơn khả năng phục vụ. Với nhiệm vụ cần biết trạng thái hiện tại, latest-value thay dữ liệu đang chờ bằng dữ liệu mới nhất để tránh tiếp tục xử lý đầu vào đã cũ. Sự khác nhau trong Hình 3.2 chỉ nằm ở phần dữ liệu chờ, bởi suy luận đang chạy vẫn được hoàn tất thay vì bị hủy khi có đầu vào mới [4].

![Hình 3.2. FIFO và latest-value đối với dữ liệu chờ; minh họa chính sách, không phải số liệu.](figures/V14.jpg)

Nếu chỉ đặt latest-value tại bridge, nhóm chỉ thay được kết quả đã suy luận xong và đang chờ gửi, trong khi đầu vào của kết quả vừa hoàn tất có thể đã chờ lâu trước MobileNetV2. Vì vậy, nhóm thử rút các datagram sẵn có trước suy luận, giữ đầu vào hợp lệ mới nhất và đếm số bỏ, đồng thời giữ cùng tải, nguồn và lập lịch để tách tác động của vị trí hàng đợi.

# CHƯƠNG 4. HIỆN THỰC

## 4.1 Đường ống Linux và tải suy luận

Source, inference, bridge và receiver trao đổi qua IPC Unix datagram, nhờ đó mỗi tiến trình đảm nhận một đoạn trong đường đi của dữ liệu. Cụ thể, source đánh dấu đầu vào trước khi inference nhận dữ liệu, tiền xử lý rồi gọi ONNX Runtime với MobileNetV2; kết quả sau đó được đưa sang bridge để đóng khung UART. Khi kiểm tra logic trên host, chúng em có thể dùng tải tổng hợp thay cho runtime và mô hình thật. Nhờ vậy, nhóm tách được chờ đầu vào, tính toán và chờ chuyển giao khỏi nhau.

Với phiên đo nền dùng MobileNetV2-12 và ONNX Runtime 1.31.0, nhóm giữ cùng mô hình, đầu vào, số luồng và thiết lập runtime để các điều kiện có thể so sánh được. Thêm luồng có thể tận dụng CPU khi Pi nhàn rỗi, nhưng cũng làm suy luận cạnh tranh với tiến trình tạo tải. Vì thế, tăng số luồng chưa chắc rút ngắn thời gian khi hệ thống bận, và nhóm phải tách tổng thời gian phục vụ khỏi thời gian gọi suy luận khi đọc kết quả [7]. Bridge xuất nối tiếp không chặn, hỗ trợ FIFO hoặc latest-value, đồng thời phát heartbeat và trao đổi echo. Khi UART mới ghi được một phần khung, bridge phải hoàn tất khung đang phát rồi mới thay dữ liệu chờ, bởi thay ngay giữa chừng sẽ khiến bên nhận thấy một khung bị ghép sai. Logger nối đầu vào với kết quả bằng dấu thời gian và bộ đếm, nên dù log ghi chậm, nhóm vẫn dùng thời điểm sự kiện để phân tích thay vì lúc ghi ra đĩa.

## 4.2 Cấu hình và môi trường thực thi

Trong quy trình thực hiện, host macOS phục vụ biên soạn, kiểm tra portable và biên dịch chéo, còn ứng dụng Linux cùng tải chạy trên Pi và firmware FreeRTOS chạy trên STM32. Vì test parser trên Mac chỉ kiểm tra logic khung, độ trễ UART vật lý trên Pi và thời gian đánh thức đều phải được xác nhận trên đúng nền tảng đích. Nhóm so sánh cấu hình mặc định P0 với cấu hình tối ưu thời gian thực P1. Trong thí nghiệm phần mềm, P1 đặt source ở FIFO ưu tiên 60 và bridge ở FIFO ưu tiên 70 trên CPU 1, còn suy luận giữ SCHED_OTHER trên CPU 0. Bridge được ưu tiên cao hơn để phục vụ chuyển giao; phương án ban đầu đặt tiến trình này ở ưu tiên 50. P2 giới hạn hạn mức CPU và P3 chưa có kết quả sơ bộ so sánh được chấp nhận trong đợt này.

## 4.3 Firmware: từ nhận byte đến quyết định

Thiết kế ban đầu đi theo ISR → bộ đệm hữu hạn → RX task → supervisor → output. Để dễ kiểm soát thời gian, ngắt chỉ nhận byte rồi bàn giao phần phân tích khung và quyết định đầu ra cho tác vụ; firmware mặc định hiện đã chuyển sang nhận DMA vòng. Chế độ IRQ vẫn được giữ để đối chiếu với DMA, bởi cả hai cách đều phải bàn giao dữ liệu ngoại vi sang tác vụ trước khi thực hiện giám sát.

RX task lấy dữ liệu để dựng khung và kiểm CRC, rồi chuyển sự kiện kèm dấu thời gian và generation cho supervisor. Khi bộ đệm đầy, bộ đếm mất hoặc dấu gián đoạn phải phản ánh được sự thiếu hụt, vì dữ liệu bị mất không được âm thầm làm mới liveness. Supervisor giữ quyền sở hữu trạng thái, còn tác vụ trạng thái truyền các bản ghi đã chụp để UART TX không chặn quyết định. Bộ nhớ được cấp phát tĩnh. Nhờ vậy, nhóm giảm phụ thuộc heap và dễ kiểm tra giới hạn tài nguyên hơn.

Với DMA, log ghi thời điểm RX đọc byte CRC cuối, tức là sau khi byte đã tới chân UART. Vì chu kỳ đánh thức, jitter lập lịch và thời gian rút cả lô dữ liệu có thể làm khoảng cách này tăng, dấu thời gian trong log không phải thời điểm đến phần cứng. Nếu bỏ lỡ cả vòng DMA hoặc có lỗi UART, firmware phải xử lý bảo thủ thay vì tiếp tục coi dữ liệu là liên tục. Kiểm thử host mới kiểm tra con trỏ vòng. Tranh chấp bus và hoạt động ngoại vi vẫn cần xác nhận trên bo mạch.

## 4.4 Công cụ đo và miền đồng hồ

Nhóm dùng cyclictest để đo đánh thức timer và stress-ng để tạo tải, còn log đường ống cho biết hành trình của từng kết quả. Echo hỗ trợ ước lượng ánh xạ đồng hồ, còn logic analyzer quan sát trực tiếp UART và GPIO để đối chiếu hai miền thời gian riêng của Pi và TIM2. Hai dấu thời gian chưa thể lấy hiệu trực tiếp. Phép trừ chỉ có ý nghĩa khi cùng đồng hồ hoặc đã ánh xạ và nêu phần bất định [8].

Để ước lượng tuổi nguồn trên MCU, nhóm cộng tuổi lúc gửi, thời gian từ lúc nhận đến hiện tại và khoản dự phòng truyền; tuy nhiên, khoản dự phòng chỉ là giả thiết cấu hình, chưa phải cận trên được đo đạc chứng minh. Tài liệu cũ còn dùng khác nhau giữa MONOTONIC và MONOTONIC_RAW, nên khi tái lập phải kiểm tra clock thật của producer lẫn bộ theo dõi. Hai clock không thể trộn chỉ vì cùng mang tên monotonic; tương tự, độ dư khớp echo nhỏ cũng chưa đủ chứng minh đường truyền đối xứng hoặc thời gian ánh xạ chính xác tuyệt đối.

# CHƯƠNG 5. ĐÁNH GIÁ SƠ BỘ

## 5.1 Phương pháp và môi trường đo

Nhóm đo riêng đánh thức định kỳ, suy luận độc lập, đường ống phần mềm và phản ứng trên bo mạch. Số lượt thu được không đồng nghĩa số lượt đủ điều kiện cho mọi cách phân tích: ở Bảng 2, E1/E2/E3 PTY đạt 45/45 theo kiểm tra phần mềm ban đầu nhưng chỉ 0/45 đủ theo dõi bổ sung. Mỗi điều kiện được ghi đầu vào, tải nền, cấu hình lập lịch và chế độ điều chỉnh tần số. Mẫu cùng lượt không phải lần lặp độc lập. Vì vậy, phân vị lấy trung vị giữa lượt, còn giá trị lớn nhất lấy cực đại quan sát.

Bảng 2. Tổng hợp số lượt đo và phạm vi sử dụng.
| Nhóm thí nghiệm | Số lượt và phạm vi chấp nhận |
|---|---|
| cyclictest | 30/30 theo kiểm tra ban đầu; 3/15 mỗi cấu hình đủ theo dõi bổ sung, chỉ khi nhàn rỗi |
| Suy luận độc lập | 21/24; loại 3 lượt 4 luồng vì điện áp thấp trực tiếp |
| E1/E2/E3 PTY | 45/45 theo kiểm tra phần mềm ban đầu; 0/45 đủ theo dõi bổ sung |
| E3b đầu vào latest | 3/12; cả 6 lượt có tải đều bị loại |
| E3 UART ban đầu | 0/18; cờ nguồn, clock và thiếu sự kiện có thể chồng nhau |
| E4 gốc | 17/25 mục; gồm 5 mục F5 chưa thực hiện |
| F5 riêng | 5/5 cho chuyển trạng thái cửa sổ ngắn |

Pi dùng kernel 6.8.0-1064-raspi, PREEMPT_DYNAMIC và nguồn 5 V / 3 A. Trong baseline suy luận, điện áp dưới tải được ghi ở mức 4.66–4.92 V, nên nhóm giữ thông tin này để đối chiếu với các lượt có vấn đề nguồn. Baseline dùng chế độ điều chỉnh tần số ondemand trong khi chiến dịch pipeline dùng performance, nên chênh lệch giữa hai tập còn chịu khác biệt cấu hình và không thể quy cho riêng IPC. Sau khi kiểm tra lại cách thu thập, nhóm yêu cầu theo dõi hệ thống bằng đồng hồ đơn điệu thô với khoảng cách mẫu không quá 1.5 s. Tiến trình tạo tải phải được xác nhận còn hoạt động và phép khớp đồng hồ không được cũ quá 5 s. Đồng hồ lịch trên Pi lệch khoảng 3 ngày, nhưng các khoảng thời gian vẫn được tính bằng đồng hồ đơn điệu.

## 5.2 Đánh thức timer và suy luận độc lập

Ở Bảng 3, nhóm dùng cyclictest với luồng đo trên CPU 0, timer cách nhau 1 ms và bộ nhớ được khóa. Với mỗi lượt kéo dài 120 s và 3 lần lặp cho mỗi điều kiện, nhóm đối chiếu P0 dùng SCHED_OTHER với P1 dùng FIFO ưu tiên 50 đã được kiểm tra trên luồng đo. Hai hàng nhàn rỗi và tải bộ nhớ giúp đối chiếu mức trễ thường gặp với phần đuôi phân bố.

Bảng 3. Kết quả sơ bộ cyclictest, đơn vị µs; P50/P99 là trung vị giữa lượt đo, giá trị lớn nhất là cực đại quan sát.
| Tải | P0 P50 | P0 P99 | P0 lớn nhất | P1 P50 | P1 P99 | P1 lớn nhất |
|---|---|---|---|---|---|---|
| Nhàn rỗi | 53 | 57 | 2659 | 3 | 9 | 92 |
| memrate CPU 2–3 | 55 | 613 | 5170 | 5 | 239 | 1094 |

Khi có memrate ở Bảng 3, P99 của P0 tăng từ 57 lên 613 µs, còn P1 tăng từ 9 lên 239 µs. Mặc dù P1 giảm đuôi trễ so với P0, tải nhớ vẫn gây ảnh hưởng; hơn nữa, trung vị P0 còn chịu timer slack nên khoảng cách P50 chưa thể quy hết cho thời gian chờ bộ lập lịch. Quan sát này phù hợp với việc các lõi chia sẻ tài nguyên, tuy vậy đây chưa phải phép đo trực tiếp băng thông nhớ. Kết quả đánh thức timer cũng không đại diện cho thời gian suy luận hoặc độ trễ UART.

Bảng 4. Thời gian gọi MobileNetV2 ở các điều kiện tải và số luồng, đơn vị ms.
| Tải / luồng ORT | Lặp hợp lệ | P50 | P99 | Lớn nhất |
|---|---|---|---|---|
| Nhàn rỗi / 1 | 3 | 44.0 | 48.0 | 57.0 |
| Nhàn rỗi / 3 | 3 | 29.4 | 38.5 | 52.8 |
| Nhàn rỗi / 4 | 1 | 31.4 | 70.7 | 94.1 |
| Tải CPU / 1 | 3 | 45.1 | 53.7 | 65.5 |
| Tải CPU / 4 | 2 | 60.3 | 100.5 | 150.3 |

Mỗi lượt ở Bảng 4 tính giờ 1000 lần gọi sau 50 lần chạy làm nóng. Khi nhàn rỗi, P50 giảm từ 44.0 ms với 1 luồng xuống 29.4 ms với 3 luồng, cho thấy thêm luồng có thể giúp lời gọi mô hình hoàn tất sớm hơn. Dưới tải CPU, hàng 4 luồng lại có P50 là 60.3 ms, cao hơn 45.1 ms của hàng 1 luồng. Vì lợi ích phụ thuộc tranh chấp và số lượt hợp lệ cũng khác nhau, nhóm tách tiền xử lý khỏi lời gọi mô hình để tránh gộp các phần công việc vào cùng kết luận.

## 5.3 Tranh chấp, điều chỉnh và chính sách hàng đợi

Để so sánh tải, cấu hình và chính sách dữ liệu chờ ở Bảng 5, nhóm tính độ trễ từ lúc sinh đầu vào tới lúc tiến trình nhận trên Pi tiếp nhận kết quả qua thiết bị đầu cuối giả PTY. Mỗi ô có 3 lần lặp để khảo sát hàng đợi và tính toán trước UART vật lý. Vì thế, những thay đổi trong bảng phản ánh đường ống phần mềm, chưa phải hiệu năng liên kết thật giữa Pi và STM32.

Bảng 5. Kết quả sơ bộ E1/E2/E3: độ trễ và AoI, đơn vị ms; không phải phép đo UART vật lý.
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

Trong Bảng 5, P50 chuyển giao E1 P0 tăng từ 44.37 ms khi idle lên 6626 ms dưới memrate. Ở E3 memrate, AoI trung bình của latest là 6958 ms, trong khi FIFO là 6660 ms; thay kết quả tại bridge chưa làm tuổi giảm. Bộ đếm thay thế tại bridge của các hàng E3 đều bằng 0 trong bảng tổng hợp, gợi ý dữ liệu đang chờ trước suy luận. Nhóm vì vậy đối chiếu từng giai đoạn trước khi quy nguyên nhân cho suy luận chậm, đồng thời giữ kết quả cache E2 vì P1 cũng chưa cải thiện chung.

Vì tuổi chưa xác định trước cập nhật có ích đầu tiên, nhóm tính AoI trung bình trên phần thời gian đã khởi tạo, giữ cả khoảng ngừng cập nhật và đuôi cuối cửa sổ. Nếu xét tỷ lệ thời gian vi phạm, mẫu số phải là thời lượng; nếu đếm gói lỡ hạn, mẫu số lại là số lần nhận. Hai mẫu số mang ý nghĩa khác nhau. Cách chọn phụ thuộc việc đánh giá thời gian dùng dữ liệu cũ hay số gói tới MCU quá hạn. Với latest-value, nhóm còn phải báo số sinh, giao, mất và bị thay, vì tuổi tốt hơn có thể đi cùng việc bỏ bớt dữ liệu chờ.

Từ kết quả trên, nhóm chuyển điểm loại dữ liệu chờ lên trước suy luận trong thí nghiệm đầu vào mới nhất E3b. Lý do là tuổi đã tích lũy trước khi MobileNetV2 bắt đầu chạy, nên bridge không thể lấy lại khoảng thời gian ấy dù kết quả được gửi ngay sau khi tính xong. Tuy vậy, thay vị trí hàng đợi mới chỉ là hướng kiểm tra tiếp, chưa đủ để chốt mức cải thiện. Các lượt được chấp nhận và các lượt bị loại của E3b vẫn được tách theo Bảng 2.

## 5.4 Liên kết thật, lỗi và đối chiếu đầu ra

Đợt E3 đầu trên UART vật lý có 0/18 lượt đủ điều kiện so sánh; 16/18 lượt xuất hiện cảnh báo nguồn và mọi lượt tải bộ nhớ đều có sai lệch khớp đồng hồ vượt ngưỡng. Trong 18 lượt đo lại, sụt áp vẫn xuất hiện ở tất cả các lượt; khi giữ dữ liệu mới nhất ở cả đầu vào lẫn bridge dưới tải, lượt đầu còn ở FAILSAFE suốt cửa sổ. Các lượt tiếp theo ở HOLD lần lượt 92.15% và 91.44%, cho thấy cần xem diễn biến trạng thái thay vì chỉ đếm kết quả nhận được. Nhóm giữ các lượt để chẩn đoán, chưa so sánh hiệu năng.

Vì FAILSAFE có nhiều nguyên nhân, Bảng 6 tách mốc heartbeat và inference; cụ thể, F1 và F2 đo từ heartbeat cuối để phản ánh việc bridge dừng gửi. F3 và F5 đo từ inference cuối để theo dõi kết quả không được cập nhật. Khi so thời gian giữa các hàng, nhóm phải đọc cột mốc tham chiếu trước, bởi bỏ qua cột này sẽ dễ nhầm mất liveness với kết quả vẫn được nhận nhưng đã cũ.

Bảng 6. Thời gian MCU chuyển sang FAILSAFE theo nguyên nhân lỗi, đơn vị ms.
| Lỗi | Lượt chấp nhận | Mốc tham chiếu | P50 | Lớn nhất |
|---|---|---|---|---|
| F1 kết thúc bridge | 5/5 | Heartbeat cuối | 100.456 | 100.641 |
| F2 SIGSTOP bridge | 5/5 | Heartbeat cuối | 100.577 | 100.596 |
| F3 SIGSTOP inference | 5/5 | Inference cuối | 475.754 | 475.815 |
| F5 ngừng inference, HB còn | 5/5 | Inference cuối | 475.596 | 475.917 |

Nhóm đặt ngưỡng heartbeat 100 ms, HOLD tuổi nguồn 200 ms và FAILSAFE tuổi nguồn 500 ms để thử phản ứng giám sát. Ở Bảng 6, P50 của F5 là 475.596 ms dù ngưỡng FAILSAFE tuổi nguồn lớn hơn khoảng sau lần nhận cuối. Vì kết quả đã có tuổi lúc gửi và phép ước lượng còn cộng khoản truyền giả định 5 ms, khoảng sau lần nhận cuối không dùng chung mốc bắt đầu với tuổi nguồn. HOLD chưa phải heartbeat timeout. Tuổi nguồn có thể vượt ngưỡng trong khi bản tin heartbeat vẫn đến, nên cần đọc đúng nguyên nhân chuyển trạng thái.

Nhóm dùng bộ phân tích logic đo từ dấu lỗi tới cạnh GPIO an toàn để đối chiếu log. Khoảng quan sát là 86.938–95.541 ms ở F1, 86.947–98.676 ms ở F2 và 82.852–91.302 ms ở F4; F2 có cả lượt bắt tín hiệu kiểm tra. Trong các lần bắt, 10/15 lần khớp mốc heartbeat trong 0.07 ms, còn 5 lần khác có một khung tới sau heartbeat nên byte cuối trên dây không phải heartbeat cuối được MCU chấp nhận. Hai mốc giải thích chênh lệch thời gian của cùng lần lỗi.

# CHƯƠNG 6. THẢO LUẬN VÀ HẠN CHẾ

## 6.1 Câu trả lời trong phạm vi bằng chứng

Kết quả sơ bộ cho RQ1 ghi nhận đuôi trễ và thời gian phục vụ tăng dưới tải nhớ, trong khi RQ2 cho thấy ưu tiên giúp đánh thức nhưng chưa cô lập mọi tài nguyên của pipeline. P1 không cải thiện mọi ô đo. Vì khóa bộ nhớ, affinity và ưu tiên đổi cùng lúc, chúng em cần thử loại trừ từng yếu tố để tách hiệu quả riêng trước khi xác định nguyên nhân. Với RQ3, vị trí chờ quan trọng hơn tên FIFO hay latest-value tại bridge, bởi bỏ đầu vào cũ trước công việc tính toán tốn thời gian khác với bỏ kết quả đã tính xong. Mặc dù các lượt đo lại có lỗi nguồn chưa xác nhận được mức cải thiện, ở RQ4 nhóm đã có log chuyển trạng thái MCU và tín hiệu GPIO để đối chiếu độc lập. Dù vậy, timeout danh định chưa thể được coi là cận trên phản ứng trong mọi tình huống.

## 6.2 Độ tin cậy và khả năng khái quát

Sụt áp là nhiễu chính dưới tải, nên một số lượt chỉ để tham khảo cùng nhiệt độ, chế độ tần số và số luồng. Với cyclictest, phần có tải còn thiếu xác nhận tiến trình tạo tải hoạt động liên tục; các lượt pipeline lại thiếu độ phủ theo dõi toàn cửa sổ. Qua kiểm tra ban đầu chưa đủ khẳng định nhân quả; số lần lặp suy luận khác nhau do loại lượt lỗi nguồn. Theo dõi điện áp định kỳ vẫn có thể bỏ lỡ nhiễu ngắn giữa các mẫu, trong khi cờ nguồn lưu từ trước phải được tách khỏi cảnh báo xảy ra ngay trong lượt. Đuôi hiếm cần nhiều lần lặp hơn. Hàng nghìn mẫu liên tiếp vẫn có thể tương quan, nên số mẫu lớn chưa thay được số lần chạy độc lập.

Vì ánh xạ đồng hồ phụ thuộc trao đổi echo và độ mới của phép khớp, một tác vụ chiếm CPU theo FIFO lúc tiêm lỗi có thể khiến bridge bị đói CPU và chính đường quan sát cũng gián đoạn. Thiếu STATE_EVENT không có nghĩa MCU luôn FRESH; nhóm không tự điền tỷ lệ thời gian.

Các hình minh họa độ tươi, khung truyền và hàng đợi, chưa thay sơ đồ đấu dây hay đồ thị thực nghiệm. Bằng chứng hiện có cũng chưa xác nhận an toàn robot, biên độ stack dài hạn, độ tin cậy DMA không giới hạn hay watchdog độc lập. GPIO thấp chỉ là quy ước đầu ra của demo, bởi với robot cần giữ cân bằng, tắt toàn bộ động cơ có thể khiến hệ thống mất ổn định thay vì an toàn hơn. Vì vậy, nhóm chỉ diễn giải phản ứng đã quan sát trong phạm vi đầu ra mô phỏng.

# CHƯƠNG 7. HƯỚNG PHÁT TRIỂN

## 7.1 Lộ trình hoàn thiện hệ thống

Theo Bảng 7, công việc được sắp xếp theo bằng chứng cần hoàn thành: giai đoạn A tập trung khả năng tái lập phần mềm, còn B đòi hỏi xác nhận vật lý trên bo mạch. C chỉ có thể chốt phân tích OS khi phép đo và bất định đã được kiểm tra. D/E chuyển sang robot nên cần thêm điều kiện về giao tiếp và quyền tác động.

Bảng 7. Các giai đoạn hoàn thiện và hướng mở rộng.
| Giai đoạn | Sản phẩm và điều kiện hoàn thành |
|---|---|
| A — phần mềm | Pipeline, MCU ảo, cấu hình và log; lặp hợp lệ, tái lập từ cấu hình |
| B — bo mạch | Firmware, UART trực tiếp, đồng hồ và GPIO; xác nhận vật lý |
| C — thực nghiệm OS | E1–E4 trên hệ thống thử nghiệm, phân tích bất định, báo cáo và demo |
| D — quan sát robot WBR | Hợp đồng thật, chuyển nền tảng và nhật ký; chưa cấp quyền tác động |
| E — tích hợp có kiểm soát | Xử lý dự phòng tại chỗ và thử lỗi có người giám sát |
| F — bài báo | Rà soát tính mới, nguồn sơ cấp và tài liệu và dữ liệu tái lập |

Trước mắt, nhóm cần khắc phục nguồn cấp rồi đo lại theo quy tắc hợp lệ mới, đồng thời lưu đầy đủ dữ liệu theo dõi. Để tránh điều chỉnh theo kết quả đã thấy, nhóm phải khóa ngưỡng trước khi so sánh cuối, đồng thời cân bằng thứ tự điều kiện và định nghĩa rõ phần làm nóng cùng cửa sổ đo. Vì mục tiêu vẫn là ít nhất 5 lần lặp hợp lệ mỗi điều kiện, các ô hiện có 3 lần lặp tiếp tục được gọi là kết quả sơ bộ thay vì hạ mục tiêu để khớp dữ liệu sẵn có.

Ở B/C, nhóm sẽ đối chiếu các kênh thời gian trên cùng thiết bị quan sát để tách lúc lỗi bắt đầu, lúc supervisor quyết định và lúc GPIO đổi mức. Để kiểm tra giới hạn còn lại của latest-value, E3 cần được đo lại với nguồn ổn định và log có đủ trạng thái đầu, sự kiện mất cùng phần cuối cửa sổ. Các ca thất bại vẫn được ghi lại. Ca khởi động lỗi và không cải thiện giúp nhóm nhận ra giới hạn hệ thống.

D/E cần hợp đồng giao tiếp và điều khiển robot trước khi cấp quyền tác động. Cách tách liveness khỏi freshness có thể tái dùng, nhưng thời hạn, ngưỡng và trạng thái an toàn phải đo lại theo đối tượng thật. Việc hoàn thành học phần không phụ thuộc tích hợp robot; giai đoạn F có thể phát triển từ kết quả OS ở C sau rà soát tính mới, nhưng khả năng tương thích WBR và việc bài báo được chấp nhận vẫn chưa biết.

# CHƯƠNG 8. KẾT LUẬN

Nền tảng Edge-AI không đồng nhất đang trong quá trình triển khai giúp nhóm quan sát Linux và FreeRTOS khi dữ liệu đến muộn. Pi đảm nhận tính toán biến thiên, còn MCU kiểm tra liveness và độ tươi trước khi quyết định đầu ra mô phỏng. Các hàng đợi và miền đồng hồ cũng phải được chỉ rõ mới giải thích được thời gian đo. Kết quả sơ bộ ghi nhận điều chỉnh ưu tiên chỉ giải quyết một phần nguồn trễ, vì đánh thức timer, tính toán, chờ đầu vào và chuyển giao là các đoạn khác nhau. Vì tải bộ nhớ vẫn có thể hạn chế lợi ích của ưu tiên, thêm luồng cũng không luôn làm MobileNetV2 chạy nhanh hơn trong lúc Pi đang bận. Tương tự, latest-value cuối đường ống chưa khôi phục được tuổi đã tích lũy trước suy luận. Nhóm vì thế tìm đoạn đang chờ và kiểm tra dữ liệu tới MCU còn hữu ích không.

Kết quả sơ bộ về lỗi hỗ trợ cách giám sát độc lập: bridge còn gửi heartbeat chưa đủ để kết quả cũ tiếp tục hợp lệ. Mốc đo vì vậy phải theo lý do chuyển trạng thái, còn GPIO cung cấp cách kiểm tra độc lập với log MCU để nhận ra khác biệt giữa byte cuối trên dây và heartbeat cuối được chấp nhận. Công việc tiếp theo của chúng em là ổn định nguồn cấp rồi lặp phép đo trong cùng điều kiện, đồng thời tiếp tục tách lượt thiếu bằng chứng khỏi phần so sánh.

# TÀI LIỆU THAM KHẢO
[1] Linux kernel documentation, “Real-Time group scheduling.” Truy cập ngày 10/10/2026.
[2] H. Yun, G. Yao, R. Pellizzoni, M. Caccamo, and L. Sha, “MemGuard: Memory bandwidth reservation system for efficient performance isolation in multi-core platforms,” in *IEEE RTAS*, 2013, pp. 55–64.
[3] S. K. Kaul, R. D. Yates, and M. Gruteser, “Real-time status: How often should one update?” in *IEEE INFOCOM*, 2012, pp. 2731–2735.
[4] S. K. Kaul, R. D. Yates, and M. Gruteser, “Status updates through queues,” in *CISS*, 2012, pp. 1–6.
[5] S. Bak, D. K. Chivukula, O. Adekunle, M. Sun, M. Caccamo, and L. Sha, “The System-Level Simplex Architecture for Improved Real-Time Embedded System Safety,” in *IEEE RTAS*, 2009, pp. 99–107.
[6] S. Bak, T. T. Johnson, M. Caccamo, and L. Sha, “Real-Time Reachability for Verified Simplex Design,” in *RTSS*, 2014, pp. 138–148.
[7] ONNX Runtime documentation, “Thread management.”
[8] D. Mills, “Simple Network Time Protocol (SNTP) Version 4,” RFC 4330, Jan. 2006, sec. 5.
