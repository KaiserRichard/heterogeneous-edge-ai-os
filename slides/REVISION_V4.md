# Slide revision v4 (owner feedback 2026-10-07 16:05) — apply on top of RESTRUCTURE_SPEC.md

The deck is "good enough to submit" but needs these fixes. Section B gives exact text for the
slides the owner reviewed; section C applies the same principles to every other slide. Where
this file and RESTRUCTURE_SPEC.md differ, this file wins.

## A. Global layout and writing rules (all slides)

1. **Top-left alignment.** Content starts at the top-left under the title, never vertically
   centered in the middle of the slide. Use the `t` class option
   (`\documentclass[aspectratio=169,12pt,t]{beamer}`) or `[t]` on every frame.
2. **Bullet indentation:** the gap between the left margin and the bullet is too large.
   Reduce it: `\setlength{\leftmargini}{1.1em}`, `\setlength{\leftmarginii}{1.2em}`
   (set inside `\AtBeginDocument` or per itemize via `\setbeamersize`/enumitem-free method that
   works with Beamer), and keep text margins at 6 mm.
3. **Hierarchy.** A slide with several parts (e.g. "Mục tiêu" and "Câu hỏi nghiên cứu") uses one
   top-level bullet per part and sub-bullets (smaller, `itemize` level 2) for its items.
4. **Every image must do work.** An image is only kept if the text on the same slide explains
   what to look at, referencing it explicitly ("Hình 5 (trên): ..."). The presenter must be able
   to read the slide text as a script for the image. No image "for decoration".
5. **Captions.** Each image has its own caption directly below it (use a `minipage` per image:
   image, then caption). Never stack two captions together under one image row. Captions are
   descriptive (1–2 lines): what the figure shows and what the reader should notice, not a bare
   name. Format: "Hình n: <name>: <what it shows>."
6. **Image size and proportion.** Size images by height with `keepaspectratio`; an image is
   either ≥ 45% of the slide width beside text, or full width on its own row. Wide-and-short
   images (e.g. the data-flow pipeline) go full width. If text plus image do not fit, split
   into two slides (same title with "(tiếp)") rather than shrink.
7. **Real schematics over AI pictures where accuracy matters.** When a slide explains real
   hardware, add a precise TikZ schematic as a sub-figure next to the AI illustration
   (Hình 6a / 6b style, each with its own caption).
8. **Fill empty slides** with a relevant figure, not with extra words; never leave a slide with
   two lines of text floating in the middle.
9. Keep: Vietnamese text, English technical terms, abbreviations expanded inline on first use,
   numbered citations [n], no evidence tags, no "Nguồn:" lines, footer = page number only.

## B. Slides with exact text

### Slide 1 — Bìa
- Title **centered** and visually symmetric, two balanced lines:
  `NỀN TẢNG THỰC THI EDGE-AI` / `KHÔNG ĐỒNG NHẤT` (large, bold, navy), then centered
  `Heterogeneous Edge-AI Runtime` (teal) and a thin teal rule.
- Below, two columns. Left (left-aligned):
  ```
  Nhóm thực hiện: 3 Stars                     (normal size, bold label)
      Nguyễn Quốc Khánh – 20233464 (Nhóm trưởng)   (\small, indented)
      Nguyễn Trung Hiếu – 20233398
      Nguyễn Quang Vinh – 20233718
  GVHD: TS. Nguyễn Quang Minh                 (normal size)
  Mã lớp bài tập: 173876                      (normal size)
  ```
  Member names must be smaller than the GVHD line. Right: V01, large (fills the column height).
  No abbreviation expansions on the cover.

### Slide 2 — Mục lục
Same plain list 1–6, left-aligned, but larger (`\Large`, generous line spacing). Nothing else.

### 1.1 Động lực nghiên cứu — rewrite as TWO slides

**1.1 Động lực nghiên cứu** (no image or V01-style image not reused; text + small TikZ
"cảm biến → AI → điều khiển" loop diagram on the right is fine):
- Trí tuệ nhân tạo (AI, Artificial Intelligence) đang được đưa xuống thiết bị biên (edge): robot, drone, xe tự hành, máy công nghiệp chạy mạng nơ-ron ngay trên máy tính nhúng chạy Linux.
  - Lý do: phản hồi nhanh, không phụ thuộc mạng, dữ liệu không rời thiết bị.
- Kết quả AI không chỉ để hiển thị mà được dùng để **điều khiển** cơ cấu vật lý (động cơ, phanh, cánh tay robot).
- Với hệ điều khiển, một kết quả **đúng nhưng đến muộn** cũng nguy hiểm như một kết quả sai.
- Câu hỏi đặt ra: hệ điều hành chạy AI có bảo đảm được *thời điểm* kết quả đến hay không?

**1.1 Động lực nghiên cứu (tiếp): thông lượng và tính tất định** — V02 large on the right, text left:
- Thông lượng (throughput): tổng lượng công việc hoàn thành trong một đơn vị thời gian.
- Tính tất định (determinism): khả năng bảo đảm mỗi tác vụ hoàn thành trong một thời hạn biết trước, kể cả trong trường hợp xấu nhất.
- Hình 1 (trái): xa lộ chở được rất nhiều xe, nhưng không ai biết chính xác khi nào một xe cụ thể đến nơi. Linux giống như vậy: tối ưu thông lượng.
- Hình 1 (phải): đường ray có tín hiệu và đồng hồ, mỗi chuyến tàu đến đúng giờ. Hệ điều khiển cần tính chất này.
- ⇒ Cần một kiến trúc giữ sức mạnh tính toán của Linux nhưng thêm một thành phần thời gian thực bảo đảm an toàn. Xu hướng này đã có trong công nghiệp: nhiều SoC (System on Chip) tích hợp cả nhân chạy Linux và nhân vi điều khiển chạy RTOS (Real-Time Operating System), ví dụ STM32MP1, NXP i.MX 8M.
Caption: "Hình 1: Thông lượng và tính tất định: xa lộ (trái) tối ưu tổng lưu lượng; đường ray (phải) bảo đảm thời điểm đến của từng chuyến."

### 1.2 Vấn đề đặt ra
Text (top), each bullet tied to its figure:
- **Dữ liệu cũ (Hình 2):** khi Linux bị tranh chấp tài nguyên, các kết quả xếp hàng chờ gửi như phong bì trên băng chuyền. Kết quả đến bên nhận đã cũ (màu cam), nhưng bên nhận không biết tuổi của nó và vẫn dùng như dữ liệu mới.
- **Lỗi im lặng (Hình 3):** bên trái, Linux gửi tín hiệu đều đặn; bên phải, Linux bị treo và vi điều khiển tiếp tục dùng giá trị cuối cùng mà không hay biết. Một bộ kiểm tra chạy trên chính Linux cũng bị treo theo.
- ⇒ Cần đo tuổi của dữ liệu và cần một bộ giám sát **nằm ngoài Linux**.
Figures: two minipages side by side (≈ 48% each), each with its own caption underneath:
- "Hình 2: Dữ liệu cũ: kết quả phải chờ trong hàng đợi và đến nơi khi đã lỗi thời."
- "Hình 3: Lỗi im lặng: Linux ngừng phản hồi, bên nhận vẫn giữ giá trị cũ."
(V04 shows a green MCU board; acceptable as an abstract MCU.)

### 1.3 Mục tiêu và câu hỏi nghiên cứu
- **Mục tiêu:** xây dựng và đánh giá một nền tảng thực thi kết hợp Linux (Raspberry Pi 5) và FreeRTOS (STM32), trong đó vi điều khiển giám sát độc lập kết quả từ Linux, chỉ bằng cách cấu hình và đo các cơ chế sẵn có của hệ điều hành, không sửa hay viết lại kernel.
- **Câu hỏi nghiên cứu:**
  - RQ1: Tranh chấp tài nguyên trên Linux làm tăng độ trễ của đường dữ liệu đến mức nào?
  - RQ2: Các cơ chế sẵn có (lập lịch thời gian thực, ghim CPU, cgroups, kernel PREEMPT_RT) khôi phục được bao nhiêu?
  - RQ3: Bộ giám sát trên STM32 phát hiện lỗi và chuyển sang trạng thái an toàn nhanh đến đâu?
- Remove the separate line "Nhóm không viết hệ điều hành mới...". If the slide looks empty,
  add a small TikZ figure mapping RQ1–RQ3 onto the pipeline (Linux → UART → STM32).

### 2.1 Kiến trúc Simplex
- **Simplex** là kiến trúc an toàn chia hệ thống thành hai phần chạy song song [1]:
  - Thành phần phức tạp (complex subsystem): hiệu năng cao nhưng khó kiểm chứng, ví dụ mạng nơ-ron chạy trên Linux.
  - Bộ giám sát an toàn (safety supervisor): đơn giản, kiểm chứng được và luôn giữ quyền quyết định cuối cùng.
- Biến thể **System-Level Simplex** đặt hai phần trên hai phần cứng riêng, nên khi thành phần phức tạp bị lỗi hoặc treo, bộ giám sát vẫn hoạt động.
- Trong đồ án: Raspberry Pi 5 là thành phần phức tạp, STM32 là bộ giám sát.
Caption: "Hình 4: Kiến trúc Simplex: thành phần phức tạp (trái) chỉ đưa ra đề xuất; bộ giám sát an toàn trên phần cứng riêng (phải) quyết định tín hiệu cuối cùng gửi tới cơ cấu chấp hành."
Image ≥ 45% width.

### 2.2 Lập lịch thời gian thực trên Linux (V11 is the script)
- Bộ lập lịch (scheduler) là thành phần của hệ điều hành quyết định tác vụ nào được chạy trên CPU (Central Processing Unit) tại mỗi thời điểm.
- **Hình 5 (trên, mặc định):** bộ lập lịch mặc định của Linux chia đều thời gian CPU. Tác vụ quan trọng (xanh) bị xen kẽ với tác vụ nền (xám) và phải chờ (khoảng cam), nên thời điểm hoàn thành dao động.
- **Hình 5 (dưới, sau tinh chỉnh):** tác vụ quan trọng dùng chính sách SCHED_FIFO (ưu tiên cố định) và được ghim riêng một nhân; tác vụ nền bị giới hạn bằng cgroups, nên tác vụ quan trọng chạy đều đặn.
- Kernel PREEMPT_RT giảm các đoạn kernel không thể ngắt: trên Raspberry Pi 5 dưới tải nặng, độ trễ xấu nhất giảm từ 1,8 ms xuống 0,22 ms [5].
Caption: "Hình 5: Lập lịch mặc định (trên) và sau tinh chỉnh (dưới); mỗi hàng là một nhân CPU, trục ngang là thời gian."
If it does not fit, put the image full width on the left 55% and shorten bullets, or split.

### 2.3 Tranh chấp tài nguyên trên vi xử lý đa nhân
Two sub-figures side by side, each with its caption:
- (a) V05: "Hình 6a: Minh họa tranh chấp: ba nhân đọc ghi bộ nhớ liên tục làm nghẽn đường truyền chung (vùng cam), tác vụ ở nhân 0 bị chậm theo."
- (b) NEW TikZ block schematic of the Raspberry Pi 5 SoC BCM2712: four boxes "Cortex-A76" each with "L2 512 KB", one shared box "L3 2 MB", "Bộ điều khiển bộ nhớ" → "LPDDR4X", and "RP1 (I/O)" connected via "PCIe 2.0 ×4". Caption: "Hình 6b: Sơ đồ khối BCM2712 trên Raspberry Pi 5: bốn nhân có L2 riêng nhưng dùng chung L3 và bộ nhớ."
Text (short, above or below the figures):
- Bốn nhân Cortex-A76 có L2 riêng nhưng dùng chung L3 2 MB và bộ nhớ LPDDR4X (Hình 6b).
- Ghim CPU quyết định tác vụ chạy ở nhân nào, nhưng không cô lập được băng thông bộ nhớ (Hình 6a) [3]; tác vụ AI trên CPU bị chậm đáng kể khi nhân khác tranh chấp bộ nhớ [4].

### 6.1 Kết luận (paper-style conclusion; top-left aligned)
- AI trên thiết bị biên ngày càng điều khiển trực tiếp hệ thống vật lý, nên kết quả phải vừa đúng vừa kịp thời; Linux đơn thuần tối ưu thông lượng và không bảo đảm điều này.
- Đồ án đề xuất một nền tảng không đồng nhất Linux + FreeRTOS theo kiến trúc Simplex, với latest-value buffer, bộ giám sát hai bộ định thời và đồng bộ đồng hồ, chỉ dùng cơ chế sẵn có của hệ điều hành.
- Ý nghĩa: hướng kiến trúc này phù hợp xu hướng SoC tích hợp nhân ứng dụng và nhân thời gian thực; các phép đo sẽ chỉ ra cơ chế nào thực sự cần thiết và chi phí của chúng, làm cơ sở thiết kế cho robot, drone và máy công nghiệp dùng AI.
- Hiện trạng: đã hoàn thành thiết kế, thư viện giao thức và kế hoạch thí nghiệm; bước tiếp theo là triển khai trên phần cứng để trả lời RQ1–RQ3 bằng số liệu đo.
Right side: V08 (architecture recap) at ≥ 40% width with caption "Hình n: Kiến trúc đề xuất." so the slide is not empty.

## C. Apply the same principles to every other slide (3.x, 4.x, 5.x)
For each slide, check A1–A8 and fix. Specific guidance:
- **3.1 Kiến trúc tổng thể:** V08 large; bullets explain the figure left to right: Linux
  (nguồn dữ liệu → suy luận → bridge; tác vụ gây tải bên cạnh) → UART → FreeRTOS (nhận UART →
  giám sát → báo trạng thái / đầu ra an toàn), plus the GPIO sync line.
- **3.2 Phần cứng và đấu nối:** V22 ≥ 45% + pin table; caption names the four wires.
- **3.3 Luồng dữ liệu:** V10 full width; below it, 2–3 bullets walking stations 1→9 and the
  "Age of Information" bracket; text no longer dense — move workload details to 3.3 (tiếp) or notes.
- **3.4 Cấu hình runtime:** V12 + table; text says which arrow in the figure corresponds to which comparison.
- **3.5 Latest-value buffer:** V14; bullets reference "Hình (trên)" FIFO and "Hình (dưới)" latest value.
- **3.6 Giao thức UART:** TikZ frame full width; bullets explain SOF, header, payload, CRC and what
  "CRC bao phủ" means; host-test result line.
- **3.7 / 3.8 Bộ giám sát:** state machine bullets reference each transition; 3.8 explains V17
  row by row (heartbeat row keeps pulsing, freshness sawtooth crosses the threshold → stale detected).
- **3.9 Đồng bộ đồng hồ:** bullets explain T1..T4 on the figure, then the formulas.
- **4.3 Đo phản ứng khi có lỗi:** explain V23 row by row (heartbeat stops at Fault, State steps,
  Output changes; "Reaction time" = t_s − t_f).
- **5.1 / 5.2:** if a slide is sparse, keep it top-left; a small timeline TikZ is fine.
- Text-heavy slides (1.1, 2.2, 2.3, 3.3): split or cut, never shrink font.

## D. Done when
- Builds with no errors/overfull boxes; render all pages and inspect each against A1–A8.
- No content vertically centered; no stacked captions; every image referenced by the text.
- Commit "Slides v4: owner review fixes" on claude/project-thread-eq9yql and push.
