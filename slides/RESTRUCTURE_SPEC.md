# Slide deck restructure spec (v3) — rewrite slides/main.tex to this spec

Owner feedback (2026-10-07): the current deck is ugly, the structure is incoherent and does not
read like a scientific paper, the Vietnamese wording is clumsy, and image sizes were ignored.
This spec replaces the current structure completely. Keep the preamble (theme, palette,
`\slideimg`, TikZ styles, bibliography entries) and the existing TikZ diagrams where reused;
rewrite every frame.

## A. Global rules (apply to every slide)

1. **Paper structure.** Sections are numbered and follow a scientific paper:
   1 Giới thiệu, 2 Cơ sở lý thuyết, 3 Thiết kế hệ thống, 4 Phương pháp đánh giá,
   5 Tiến độ và kế hoạch, 6 Kết luận. No "related work" section, no "future work",
   no "out of scope" list.
2. **Section divider slides.** After the table of contents, each section starts with one
   simple divider slide showing only the big centered heading, e.g. "1. Giới thiệu"
   (use `\AtBeginSection` with a clean section page; no progress bar clutter, no TOC on it).
3. **Frame titles are numbered noun phrases**, not claim sentences:
   "1.1 Động lực nghiên cứu", "3.4 Bộ giám sát trên STM32". Short, natural, academic Vietnamese.
4. **Footer:** remove the section name in the bottom-left completely. Keep only the page
   number "n/N" at the bottom right.
5. **Abbreviations:** expand inline, in the sentence where the term first appears in a main
   slide, in the form `CPU (Central Processing Unit)`. Never a separate footnote line under the
   content, never "FreeRTOS: Free RTOS". Do NOT expand anything on the cover, the table of
   contents, divider slides or references. Remove the glossary slide.
6. **Citations:** numbered LaTeX citations `\cite{...}` rendering as [1], [2]... Cite where a
   claim or published number comes from, not on every line. Remove ALL "Nguồn: ...", "PROJECT §",
   "SYSTEM_GUIDE §", "deck gốc", "Kernel Real-time Ubuntu đóng gói chỉ dùng cho P3" style lines.
7. **Evidence tags:** remove the bracket tags ([THIẾT KẾ], [TÍNH TOÁN], [KIỂM THỬ HOST],
   [CÔNG BỐ]) and the "cách đọc bằng chứng" legend. Instead write naturally: "dự kiến" for design
   values, "kiểm thử trên máy tính" for host tests, and a citation [n] for published numbers.
   Never present a design value as a measurement.
8. **Images:** an image is either large and meaningful or removed.
   - Minimum: an image occupies at least ~45% of slide width (two-column layout) or full width.
     Never two or three small images stacked in one column.
   - If an important image does not fit next to text, give it its own slide (image full
     width + 1–2 lines of text).
   - Every kept image gets a caption below it: "Hình n: ..." (auto-numbered figure counter,
     Vietnamese, one line). TikZ diagrams also get "Hình n".
   - Drop decorative images that add nothing: V07, V13, V16, V21, V24 (use tables instead).
     V04 is optional (its MCU board is drawn green); keep only if it fits slide 1.2 well.
   - Before using an image, open it and check its content against slides/images/MAPPING.md
     (note: V17 = two timers, V18 = state machine).
9. **Text density:** max 4 bullets per slide, max 2 lines per bullet, font never below
   `\small` for readable content. Details go in `\note{}` (Vietnamese speaker notes).
10. **Language:** natural, formal Vietnamese as in a Vietnamese university thesis. Technical
    terms stay in English (scheduler, SCHED_FIFO, heartbeat, failsafe, latest-value buffer,
    PREEMPT_RT, ...). Avoid literal translations and awkward word order; read every sentence
    aloud before keeping it. Prefer the exact wording given in section C below.
11. Page budget: about 22 content slides + cover + TOC + 6 dividers + references + closing.

## B. Cover and table of contents

**Cover (slide 1)** — no abbreviation expansions, no footnote line:
```
NỀN TẢNG THỰC THI EDGE-AI KHÔNG ĐỒNG NHẤT          (large, navy, bold)
Heterogeneous Edge-AI Runtime                     (smaller, teal, below)
Linux và FreeRTOS trên Raspberry Pi 5 và STM32     (small, muted)

Nhóm thực hiện: 3 Stars
GVHD: TS. Nguyễn Quang Minh
Mã lớp bài tập: 173876
```
Image V01 large on the right half (about 48% width, ~75% height), not a thumbnail. No member
list, no date line unless it fits naturally under the class code.

**Mục lục (slide 2)** — plain, one column, large:
```
Mục lục
1. Giới thiệu
2. Cơ sở lý thuyết
3. Thiết kế hệ thống
4. Phương pháp đánh giá
5. Tiến độ và kế hoạch
6. Kết luận
```
Nothing else on this slide.

## C. Content slides (title — content — visual)

### 1. Giới thiệu
**1.1 Động lực nghiên cứu** — left text, right V02 (large) "Hình 1: Thông lượng và tính tất định".
- Các hệ thống AI biên (edge AI) thường chạy mạng nơ-ron trên Linux vì có thư viện và tài nguyên tính toán mạnh.
- Linux được tối ưu cho thông lượng (throughput), không bảo đảm thời điểm hoàn thành của từng tác vụ.
- Khi kết quả AI dùng cho điều khiển, kết quả đúng nhưng đến trễ cũng có thể gây nguy hiểm.

**1.2 Vấn đề đặt ra** — two large images side by side, each with caption: V03
"Hình 2: Kết quả bị trễ mà bên nhận không biết" and V04 "Hình 3: Linux ngừng phản hồi".
Two short statements above them:
- Dữ liệu cũ: khi tài nguyên bị tranh chấp, kết quả đến muộn nhưng vẫn được xem là hợp lệ.
- Lỗi im lặng: khi Linux bị treo, không tiến trình nào trên Linux đáng tin để phát hiện lỗi đó.
(If V04 is dropped, put V03 large and state the second problem in text.)

**1.3 Mục tiêu và câu hỏi nghiên cứu** — text only, or with V06 if space allows (else V06 goes to 2.1).
- Mục tiêu: xây dựng và đánh giá một nền tảng thực thi kết hợp Linux (Raspberry Pi 5) với
  FreeRTOS (STM32), trong đó vi điều khiển giám sát độc lập kết quả từ Linux.
- RQ1: Tranh chấp tài nguyên trên Linux làm tăng độ trễ của đường dữ liệu đến mức nào?
- RQ2: Các cơ chế sẵn có của hệ điều hành (lập lịch thời gian thực, ghim CPU, cgroups, kernel PREEMPT_RT) khôi phục được bao nhiêu?
- RQ3: Bộ giám sát trên STM32 phát hiện lỗi và chuyển sang trạng thái an toàn nhanh đến đâu?
Last line (small): "Nhóm không viết hệ điều hành mới mà cấu hình và đo các cơ chế sẵn có."

### 2. Cơ sở lý thuyết
**2.1 Kiến trúc Simplex** — V06 large + text. "Hình 4: Kiến trúc Simplex".
- Hệ thống gồm một thành phần phức tạp, hiệu năng cao và một thành phần giám sát đơn giản, đáng tin cậy, chạy trên phần cứng riêng \cite{bak2009}.
- Bộ giám sát có quyền quyết định cuối cùng; đầu ra của thành phần phức tạp chỉ là đề xuất.
- Trong đồ án: Raspberry Pi 5 là thành phần phức tạp, STM32 là bộ giám sát.

**2.2 Lập lịch thời gian thực trên Linux** — V11 large "Hình 5: Lập lịch mặc định và sau tinh chỉnh".
- Bộ lập lịch mặc định của Linux chia sẻ CPU công bằng nên tác vụ quan trọng có thể phải chờ.
- SCHED_FIFO cho tác vụ ưu tiên cố định; ghim CPU (CPU affinity) và cgroups giới hạn tác vụ nền.
- Kernel PREEMPT_RT giảm các đoạn không thể ngắt trong kernel. Trên Raspberry Pi 5 dưới tải nặng, độ trễ xấu nhất của SCHED_FIFO giảm từ 1,8 ms xuống 0,22 ms \cite{arxiv2604}.

**2.3 Tranh chấp tài nguyên trên vi xử lý đa nhân** — V05 large "Hình 6: Các nhân dùng chung cache và băng thông bộ nhớ".
- Raspberry Pi 5 có 4 nhân Cortex-A76 dùng chung bộ nhớ đệm L3 2 MB và bộ nhớ LPDDR4X.
- Ghim CPU quyết định tác vụ chạy ở nhân nào, nhưng không cô lập được băng thông bộ nhớ \cite{yun2013memguard}.
- Tác vụ AI trên CPU bị chậm đáng kể khi nhân khác tranh chấp bộ nhớ \cite{bechtel2018deeppicar}.

**2.4 Tuổi thông tin (Age of Information)** — V20 large "Hình 7: Tuổi thông tin theo thời gian (minh họa)".
- AoI (Age of Information) tại thời điểm t: Δ(t) = t − u(t), với u(t) là thời điểm lấy mẫu của dữ liệu mới nhất đã nhận \cite{kaul2012infocom}.
- AoI tăng tuyến tính giữa hai lần nhận và giảm khi có dữ liệu mới.
- Chỉ số đánh giá: AoI trung bình, AoI đỉnh, tỉ lệ thời gian AoI vượt ngưỡng τ.
- Ưu tiên dữ liệu mới nhất giúp giảm AoI trung bình so với hàng đợi FIFO \cite{kaul2012queues}.

### 3. Thiết kế hệ thống
**3.1 Kiến trúc tổng thể** — V08 nearly full width "Hình 8: Kiến trúc hệ thống". Two lines below:
Linux: nguồn dữ liệu, suy luận, bridge, tác vụ gây tải. FreeRTOS: nhận UART, giám sát, báo trạng thái, đầu ra an toàn. Kết nối: một đường UART và một đường GPIO đồng bộ.

**3.2 Phần cứng và đấu nối** — V22 (or V09) large left, table right "Hình 9: Đấu nối Raspberry Pi 5 và STM32".
Table (dự kiến): GPIO14 (TX, chân 8) → PA10 (RX); GPIO15 (RX, chân 10) ← PA9 (TX); GND chân 6 — GND; GPIO17 (chân 11) → PA0 (TIM2\_CH1, đồng bộ).
Bullets: Raspberry Pi 5 4 GB, Ubuntu Server 24.04; Nucleo-F446RE (Cortex-M4F, 180 MHz), FreeRTOS; GPIO (General-Purpose Input/Output) expanded here.

**3.3 Luồng dữ liệu của một kết quả** — V10 full width "Hình 10: Hành trình của một kết quả suy luận".
One line: mỗi kết quả mang thời điểm lấy mẫu đầu vào để tính tuổi thông tin tại STM32.
Workload line: MobileNetV2 (ONNX, FP32) trên ONNX Runtime CPU, chu kỳ đầu vào dự kiến 100 ms; tài liệu công bố cho Pi 5 khoảng 20–50 ms mỗi lần suy luận.

**3.4 Các cấu hình runtime** — V12 left large "Hình 11: Bốn cấu hình runtime", table right:
| Cấu hình | Nội dung |
| P0 | Linux mặc định |
| P1 | SCHED_FIFO (ưu tiên 50), ghim CPU, giới hạn cgroups, khóa bộ nhớ (mlockall) |
| P2 | P1 + latest-value buffer |
| P3 | P1 trên kernel Real-time Ubuntu (PREEMPT_RT) |
Line: mỗi phép so sánh chỉ thay đổi một yếu tố: P0→P1, P1→P2, P1→P3.

**3.5 Latest-value buffer** — V14 large "Hình 12: Hàng đợi FIFO và bộ đệm giá trị mới nhất".
- Hàng đợi FIFO: khi quá tải, kết quả xếp hàng và đến nơi khi đã cũ.
- Latest-value buffer: kết quả mới ghi đè kết quả cũ chưa gửi.
- Kỳ vọng: giảm AoI trung bình, nhưng không bảo đảm cận trên cứng.

**3.6 Giao thức truyền UART** — existing TikZ frame diagram, full width "Hình 13: Cấu trúc khung truyền".
Two columns below: Loại bản tin (HEARTBEAT, INFERENCE, ECHO\_REQ/ECHO\_RESP, MCU\_STATUS);
Kiểm thử trên máy tính: phát hiện toàn bộ lỗi một bit, khôi phục đồng bộ 99,99% khung dưới nhiễu ngẫu nhiên.
Expand CRC (Cyclic Redundancy Check) here.

**3.7 Bộ giám sát trên STM32** — existing TikZ state machine, large, left ~60% "Hình 14: Máy trạng thái của bộ giám sát". Right:
- Hai bộ định thời độc lập: heartbeat (bridge còn hoạt động) và độ mới của kết quả.
- Dữ liệu cũ: FRESH → HOLD; mất heartbeat: chuyển thẳng FAILSAFE.
- FAILSAFE được chốt, chỉ thoát khi có lệnh khởi động lại rõ ràng.
- Khung trùng lặp hoặc sai CRC không làm mới bộ định thời.

**3.8 Vì sao cần hai bộ định thời** — V17 full width "Hình 15: Heartbeat vẫn đều nhưng kết quả đã cũ".
One sentence: bridge vẫn gửi heartbeat nhưng có thể chuyển tiếp kết quả cũ, nên chỉ heartbeat là không đủ. Task FreeRTOS: supervisor ưu tiên cao nhất, chu kỳ 1 kHz.

**3.9 Đồng bộ đồng hồ giữa hai miền** — existing TikZ T1–T4 diagram (or V19) left "Hình 16: Trao đổi bốn mốc thời gian", right formulas:
θ = ((T2 − T1) + (T3 − T4))/2, δ = (T4 − T1) − (T3 − T2); giả thiết trễ hai chiều đối xứng.
Bullets: đồng hồ Linux CLOCK_MONOTONIC_RAW (ns) và bộ định thời STM32 (µs); cạnh GPIO trên PA0 dùng làm chuẩn kiểm chứng độc lập.

### 4. Phương pháp đánh giá
**4.1 Chỉ số đánh giá** — table, no image:
| Nhóm | Chỉ số |
| Độ trễ | P50, P99, giá trị lớn nhất (từ lúc lấy mẫu đến lúc STM32 nhận) |
| Độ mới | AoI trung bình, AoI đỉnh, tỉ lệ vượt ngưỡng V(τ) |
| Phản ứng lỗi | thời gian phát hiện, thời gian kích hoạt, tổng thời gian đến đầu ra an toàn |
| Độ tin cậy | số deadline bị lỡ trên tổng số chu kỳ |

**4.2 Các thí nghiệm** — table (replaces V21):
| Thí nghiệm | So sánh | Mục đích |
| E1 | P0 khi rảnh và dưới tải CPU, bộ nhớ, cache, I/O | đo ảnh hưởng của tranh chấp |
| E2 | P0 với P1; P1 với P3 | hiệu quả của tinh chỉnh và kernel |
| E3 | P1 với P2 khi tải tăng | hiệu quả của latest-value buffer |
| E4 | dừng bridge, treo tiến trình, chiếm CPU | độ trễ chuyển sang failsafe |
Line: mọi lần chạy ghi nhiệt độ, tần số CPU; loại bỏ lần chạy bị giảm xung (throttling).

**4.3 Đo phản ứng khi có lỗi** — V23 large "Hình 17: Các mốc thời gian khi xảy ra lỗi", plus V09/V22 bench only if room (else omit).
- Đo thời điểm lỗi t_f, quyết định t_d và đầu ra an toàn t_s trên cùng một logic analyzer.
- Ngân sách dự kiến: timeout + chu kỳ supervisor + trễ điều phối + thực thi + trễ đầu ra.
- Log trên Linux không đo được lúc Linux treo, nên phải đo từ bên ngoài.

**4.4 Giả thuyết** — table H1–H4 (as before, natural wording):
H1 tranh chấp làm tăng P99 nhiều hơn hẳn P50; H2 tinh chỉnh khôi phục độ trễ đuôi do tranh chấp CPU nhưng không khôi phục được tranh chấp bộ nhớ; H3 latest-value buffer giảm AoI trung bình và thời gian vượt ngưỡng; H4 thời gian chuyển sang failsafe luôn nằm trong ngân sách với mọi loại lỗi.

### 5. Tiến độ và kế hoạch
**5.1 Kết quả đã đạt được** — table Hạng mục | Trạng thái:
Thiết kế và khảo sát tài liệu — hoàn thành; Thư viện giao thức + kiểm thử trên máy tính — hoàn thành;
Máy trạng thái giám sát (bản đầu, một bộ định thời) — có kiểm thử, cần nâng cấp hai bộ định thời;
CI và script cài đặt Raspberry Pi — hoàn thành, chưa chạy trên phần cứng; Firmware, bridge, thí nghiệm — chưa thực hiện.

**5.2 Kế hoạch tiếp theo** — numbered list (replaces V24): 1. Lắp đặt và kiểm tra phần cứng; 2. Bộ giám sát hai bộ định thời và đồng bộ đồng hồ; 3. Bridge trên Linux và firmware FreeRTOS; 4. Kiểm tra đường truyền và đồng bộ bằng GPIO; 5. Thực hiện E1–E4; 6. Viết báo cáo.

### 6. Kết luận
**6.1 Kết luận** — 3 bullets: đã xác định bài toán (độ trễ, độ mới, lỗi im lặng) và kiến trúc Simplex hai miền; đã hoàn thành thiết kế, giao thức và kế hoạch thí nghiệm có thể tái lập; giai đoạn tiếp theo là triển khai trên phần cứng và trả lời RQ1–RQ3 bằng số đo.

### Closing
**Tài liệu tham khảo** — one slide (two only if unavoidable), numbered [1]..[6], no explanations, no expansions.
**Cảm ơn thầy và các bạn đã lắng nghe!** — simple centered closing slide.

## D. Done when
- `latexmk -xelatex main.tex` builds with no errors and no overfull boxes.
- Render every page to PNG (slides/render.swift) and inspect each one: images large and not
  distorted, captions present, no text below `\small`, no bottom-left footer text, no "Nguồn:"
  lines, no evidence tags, abbreviations expanded inline only on first use.
- Commit on branch claude/project-thread-eq9yql with message "Slides v3: paper structure".
