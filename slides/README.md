# Deck báo cáo tiến độ bằng tiếng Việt

`main.tex` dùng XeLaTeX, Beamer/moloch, tỷ lệ 16:9 và cỡ chữ nền 12pt. Nội dung gồm **25 trang chính + 4 trang phụ lục = 29 trang PDF**. Không có trang chuyển mục tự động. Mục lục nằm ngay sau bìa; tên mục và số trang hiện ở chân mọi trang. Văn bản nội dung, ghi chú và nhãn sơ đồ bằng tiếng Việt; tên trạng thái, trường giao thức, thuật ngữ kỹ thuật và caption ảnh giữ tên gốc. Nhan đề, tác giả, thông tin xuất bản và liên kết của sáu tài liệu tham khảo đã kiểm chứng được giữ để tra cứu chính xác.

Nguồn nội dung: `PROJECT.md`, deck cũ, `docs/SLIDES_OVERVIEW.md`, `docs/SYSTEM_GUIDE.md`, `docs/SYSTEM_OVERVIEW.md`, `docs/research/R1.md`–`R8.md` và `DESIGN_CHANGES.md`. Tiến độ phản ánh bảng công việc trong SYSTEM_GUIDE ngày 06/10/2026, không phải một lần kiểm thử lại mã nguồn. Khi nguồn cũ khác quyết định mới, dùng P3 = P1 trên kernel RT, supervisor hai bộ đếm với FAILSAFE giữ chốt, và latest-value chỉ thay kết quả chưa gửi.

## Biên dịch và xem trước

```sh
cd slides
latexmk -xelatex -interaction=nonstopmode main.tex
swift render.swift main.pdf preview
```

Cần TeX Live có theme `moloch`, font macOS Avenir Next (đậm: Avenir Next Demi Bold), Menlo và Swift/PDFKit. Avenir Next được kiểm tra qua log XeLaTeX về glyph tiếng Việt. Mũi tên dùng ký hiệu toán để không phụ thuộc glyph mũi tên của font sans.

Nếu sandbox chặn cache Swift mặc định, giữ cache trong thư mục slide:

```sh
swift -module-cache-path .swift-module-cache render.swift main.pdf preview
```

Kiểm tra cả log XeLaTeX và output bộ chuyển PDF:

```sh
rg 'Overfull|Underfull|Missing character|Warning|^!' main.log
```

`main.pdf`, log và `preview/` là sản phẩm build được Git bỏ qua. Sau render có thể xóa `.swift-module-cache/`. Ghi chú nằm trong `\note{}`; bỏ comment một trong hai dòng `\setbeameroption` ở đầu file để tạo PDF có ghi chú ở màn hình bên phải hoặc chỉ ghi chú. Số trang 29 áp dụng cho bản mặc định không hiển thị ghi chú.

## Cấu trúc

| Mục | Trang PDF | Nội dung |
|---|---:|---|
| Giới thiệu | 1–4 | Bìa, Mục lục/chú giải, vấn đề, câu hỏi và phạm vi |
| Cơ sở lý thuyết và nghiên cứu liên quan | 5–6 | Simplex, AoI, PREEMPT_RT, tranh chấp đa lõi |
| Thiết kế hệ thống | 7–17 | Kiến trúc, phần cứng, vòng đời kết quả, tiến trình Linux, task FreeRTOS, workload, P0–P3, buffer, UART, supervisor, đồng hồ |
| Phương pháp đánh giá | 18–22 | Metrics, E1–E4, fault injection, H1–H4, nguy cơ sai lệch và kiểm soát nhiệt |
| Tiến độ và kế hoạch | 23–24 | Trạng thái theo bảng công việc, lộ trình theo phụ thuộc và nghiệm thu |
| Kết luận | 25 | Sản phẩm bàn giao, giới hạn và bước tiếp theo |
| Phụ lục | 26–29 | Hai trang tài liệu tham khảo, bảng thuật ngữ, ảnh bổ trợ |

Không đặt ngày hoàn thành hoặc gán vai trò thành viên vì nguồn chưa chốt. Các chân GPIO/UART là sơ đồ đề xuất cần xác nhận trên bo; các ngưỡng supervisor phải hiệu chỉnh sau baseline.

## Bằng chứng và khả năng đọc

- `[THIẾT KẾ]`: cấu hình, giả thiết hoặc chính sách dự kiến; chưa phải số đo phần cứng.
- `[TÍNH TOÁN]`: giá trị từ công thức với điều kiện đã nêu.
- `[KIỂM THỬ HOST]`: kết quả phần mềm được nguồn ghi nhận trên host; không đại diện cho UART thật.
- `[CÔNG BỐ]`: thông số hoặc kết quả từ nguồn khác, giữ nguồn cạnh nhận định.

Số trang, mã V/P/E/H/R, tên linh kiện, phân vị theo định nghĩa và thông tin hành chính là định danh, không phải kết quả benchmark. Không có số đo mới của bộ Pi–STM32 được thêm vào deck. Thư mục xuất bản giữ nguyên các năm/trang và URL đã xác minh.

Nội dung đọc được dùng từ `\footnotesize` trở lên; không dùng `\scriptsize`, `\tiny` hoặc scale cả trang. Palette: navy `#1F3A5F`, teal `#2A9D8F`; orange `#E76F51` chỉ dành cho lỗi/FAILSAFE. TikZ giữ bậc profile, frame UART, máy trạng thái supervisor, trao đổi T1–T4 và các trục thời gian.

## Ánh xạ ảnh V01–V24

Đặt ảnh vào `slides/images/V01.jpg` … `V24.jpg` (macro nhận cả `.jpg` và `.png`, ưu tiên `.jpg`). Macro `\slideimg` giữ tỷ lệ ảnh và hiển thị placeholder nếu chưa có file đúng tên. **Mỗi V-id xuất hiện đúng một lần**; chủ đề và caption English của deck gốc giữ nguyên. Không sửa `slides/image-prompts/`. Ảnh có tên mô tả khác chưa được macro tự động sử dụng.

| V-id | Trang PDF | Chủ đề / caption gốc |
|---|---:|---|
| V01 | 1 | Title visual: Pi 5 (green) + Nucleo (white) on one link |
| V02 | 3 | Late result under load |
| V03 | 3 | Delay invisible to receiver |
| V04 | 3 | Linux hang |
| V05 | 6 | BCM2712: private L2, shared L3 and DRAM |
| V06 | 5 | Related work map |
| V07 | 4 | Three research questions |
| V08 | 7 | System architecture: two domains |
| V09 | 8 | Hardware rig photo/illustration |
| V10 | 9 | End-to-end data path |
| V11 | 13 | Stock vs tuned scheduling |
| V12 | 13 | Profile ladder illustration |
| V13 | 29 | Profiles detail |
| V14 | 14 | FIFO queue vs 1-slot latest value |
| V15 | 29 | UART frame illustration |
| V16 | 11 | Supervisor |
| V17 | 16 | Two timers |
| V18 | 29 | Supervisor detail |
| V19 | 29 | Clock sync illustration |
| V20 | 18 | AoI sawtooth |
| V21 | 19 | Experiment matrix |
| V22 | 8 | Wiring detail |
| V23 | 20 | Logic analyzer on fault, decision, output pins |
| V24 | 24 | Progress timeline |

Bảng tiến trình Linux ở trang 10, workload ở trang 12, giao thức ở trang 15 và đồng hồ ở trang 17 dùng bảng/TikZ, không thêm ảnh hoặc thay chủ đề V-id. Thêm ảnh sau này cần biên dịch và render lại để kiểm tra độ dễ đọc.

## Kết quả kiểm tra bản mặc định

Bản 29 trang đã được biên dịch bằng lệnh XeLaTeX ở trên, render bằng Swift/PDFKit và xem toàn bộ trang, cùng các trang bảng/sơ đồ ở kích thước lớn. `main.log` và output build không còn lỗi, cảnh báo overfull/underfull, thiếu glyph hoặc liên kết ngoài biên trang. Có 25 trang chính, 4 trang phụ lục, 29 ghi chú, 24 V-id duy nhất với caption gốc và sáu mục thư mục giữ nguyên. Đây là kiểm tra tài liệu; không phải kiểm chứng hệ thống trên Pi/STM32.
