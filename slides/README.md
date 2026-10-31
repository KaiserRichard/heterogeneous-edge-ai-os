# Slides v4 — chỉnh sửa theo review

`main.tex` có **37 trang**, theo cấu trúc sáu mục của `RESTRUCTURE_SPEC.md`; các câu tiếng Việt, cách tách 1.1 và caption được `REVISION_V4.md` quy định có ưu tiên. XeLaTeX/Beamer moloch, tỷ lệ 16:9, canvas 208 × 117 mm; giữ font của class 12pt, không dùng `shrink` hay scale toàn frame. Nội dung dùng Avenir Next, mã dùng Menlo; caption dùng Avenir Next Condensed 10pt để giữ nguyên câu dài trong một hoặc hai dòng. Lề văn bản 6 mm; chân trang chỉ có n/N.

## Thay đổi theo review

| Yêu cầu | Thay đổi |
|---|---|
| G1 | Thụt cấp 1/cấp 2 còn 1,1/1,2 em; giảm khoảng cách nhãn và khoảng cách danh sách. |
| G2 | Class `t`, cột `[T]`; mọi trang nội dung căn trên và văn bản căn trái. Chỉ bìa, sáu trang chuyển mục và lời cảm ơn dùng bố cục giữa. |
| G3 | Mỗi hình nội dung được giải thích trong văn bản cùng trang; caption riêng ngay dưới hình, dài một hoặc hai dòng. 1.2 dùng hai minipage, không còn hai caption xếp dưới cả hàng ảnh. |
| G4 | Phóng lớn ảnh hai cột; V10 trải toàn chiều rộng, khung UART gần toàn chiều rộng; V08/V17 đủ lớn để đọc các khối/đường thời gian. Cắt viền trống khi nhúng V06/V08/V10, giữ tỷ lệ và giữ nguyên file nguồn. |
| G5 | Mục tiêu/câu hỏi là hai bullet cha; RQ1–RQ3 và các vai trò Simplex là bullet con. |
| G6 | Dùng nguyên văn V4 ở các trang được chỉ định; định nghĩa thông lượng, tính tất định, Simplex, bộ lập lịch, AoI, bộ đệm, SOF/CRC, cgroups và các mốc đo. |
| S1–S2 | Bìa hai dòng cân giữa, subtitle/rule, đủ ba thành viên với chữ nhỏ hơn dòng GVHD; mục lục `Large`, giãn dòng. |
| S3 | 1.1 tách đúng hai trang: động lực điều khiển và đối chiếu xa lộ/đường ray; câu nhu cầu kiến trúc in đậm. Thêm vòng cảm biến–AI–điều khiển có lời giải thích. |
| 1.2 / S6 | Giữ nguyên mô tả dữ liệu cũ/lỗi im lặng và caption V4; mục tiêu bao gồm không sửa/viết kernel, RQ phân cấp, bỏ câu trailing cũ; thêm sơ đồ vị trí RQ. |
| S8 | Simplex được định nghĩa trước, phân vai đề xuất/quyết định, phần cứng độc lập và ánh xạ Pi/STM32; caption nguyên văn nằm dưới ảnh. |
| S9 | Hai trang 2.2: đọc Stock/Tuned theo V11, rồi PREEMPT_RT và biểu đồ hai giá trị công bố. Phân biệt ưu tiên 99 trong nghiên cứu với P1 dự kiến ưu tiên 50. |
| S10 | V05 (a) bên cạnh TikZ BCM2712 (b): 4 × Cortex-A76, L2 riêng 512 KB, L3 chung 2 MB, bộ điều khiển bộ nhớ → LPDDR4X; RP1 ngoài BCM2712 qua PCIe 2.0 ×4. Mỗi hình có caption riêng. |
| S-rest | 3.1 đọc kiến trúc trái→phải; 3.2 caption bốn đường nối; 3.3 đọc trạm 1–9 và giới hạn ngoặc AoI; 3.4 giải thích các nhánh; 3.5 đọc hai hàng FIFO/latest-value; 3.6 giải thích khung/CRC; 3.7–3.8 giải thích chuyển trạng thái và hai bộ định thời; 3.9 giải thích T1–T4 trước công thức. 4.x làm rõ chỉ số/giả thuyết và đo ngoài Linux; 5.x phân biệt tiến độ phần mềm với phần cứng, thêm trình tự kiểm chứng. |
| S31 | 6.1 giữ bốn bullet kết luận V4, có kiến trúc bên phải; bổ sung ý nghĩa nền tảng chi phí thấp, tái lập, giảng dạy và phép đo bằng đồng hồ ngoài Linux. |

## Build và render trên macOS

```sh
cd slides
latexmk -xelatex -interaction=nonstopmode main.tex
swift render.swift main.pdf preview
```

Cần TeX Live có moloch, các font trên và macOS Swift/PDFKit. `render.swift` giữ nguyên, xuất PNG từng trang ở 1280 × 720. Khi sandbox chặn cache Swift mặc định, đặt cache bên trong `slides/`:

```sh
swift -module-cache-path .swift-module-cache render.swift main.pdf preview
```

Cache là sản phẩm build, có thể xóa sau khi render. PDF/preview/log là sản phẩm build, không phải ảnh nguồn. Ghi chú thuyết trình ở `\note{}`; các tùy chọn xuất notes ở đầu `main.tex`.

Kiểm tra log:

```sh
rg 'Overfull|Underfull|Missing character|Warning|^!' main.log
```

Lần xác nhận 07/10/2026: build 37 trang thành công, không có lỗi, overfull/underfull, Missing character hay cảnh báo LaTeX; `git diff --check` sạch. Đã render và mở từng trang ở kích thước gốc để kiểm tra caption, tỷ lệ hình, nhãn sơ đồ, căn lề và chữ tiếng Việt; sửa rồi kiểm tra lại các trang thay đổi. Không chạy lại kiểm thử giao thức trong lần biên tập slide này.

## Danh sách trang

| Trang | Tiêu đề |
|---:|---|
| 1 | Bìa |
| 2 | Mục lục |
| 3 | 1. Giới thiệu |
| 4 | 1.1 Động lực nghiên cứu |
| 5 | 1.1 Động lực nghiên cứu (tiếp): thông lượng và tính tất định |
| 6 | 1.2 Vấn đề đặt ra |
| 7 | 1.3 Mục tiêu và câu hỏi nghiên cứu |
| 8 | 2. Cơ sở lý thuyết |
| 9 | 2.1 Kiến trúc Simplex |
| 10 | 2.2 Lập lịch thời gian thực trên Linux |
| 11 | 2.2 Lập lịch thời gian thực trên Linux (tiếp): PREEMPT_RT |
| 12 | 2.3 Tranh chấp tài nguyên trên vi xử lý đa nhân |
| 13 | 2.4 Tuổi thông tin (Age of Information) |
| 14 | 3. Thiết kế hệ thống |
| 15 | 3.1 Kiến trúc tổng thể |
| 16 | 3.2 Phần cứng và đấu nối |
| 17 | 3.3 Luồng dữ liệu của một kết quả |
| 18 | 3.4 Các cấu hình runtime |
| 19 | 3.5 Latest-value buffer |
| 20 | 3.6 Giao thức truyền UART |
| 21 | 3.7 Bộ giám sát trên STM32 |
| 22 | 3.8 Vì sao cần hai bộ định thời |
| 23 | 3.9 Đồng bộ đồng hồ giữa hai miền |
| 24 | 4. Phương pháp đánh giá |
| 25 | 4.1 Chỉ số đánh giá |
| 26 | 4.2 Các thí nghiệm |
| 27 | 4.3 Đo phản ứng khi có lỗi |
| 28 | 4.4 Giả thuyết |
| 29 | 5. Tiến độ và kế hoạch |
| 30 | 5.1 Kết quả đã đạt được |
| 31 | 5.2 Kế hoạch tiếp theo |
| 32 | 6. Kết luận |
| 33 | 6.1 Kết luận |
| 34 | Tài liệu tham khảo (1/3) |
| 35 | Tài liệu tham khảo (2/3) |
| 36 | Tài liệu tham khảo (3/3) |
| 37 | Cảm ơn thầy và các bạn đã lắng nghe! |

## Hình và tài liệu

Giữ các ảnh V01–V06, V08, V10–V12, V14, V17, V20, V22, V23. Các hình còn lại không được đưa vào deck. Hình chính giữ số 1–18 của mạch nội dung; hình bổ sung dùng hậu tố 1a (vòng điều khiển), 3a (RQ), 5a (số liệu công bố), 17a (trình tự). Cặp 6a/6b theo đúng thứ tự V4: minh họa trước, sơ đồ phần cứng sau.

Thông số sơ đồ được đối chiếu trực tiếp với [Raspberry Pi Documentation — BCM2712](https://www.raspberrypi.com/documentation/computers/processors.html#bcm2712) và [RP1 Peripherals](https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf), trích dẫn [7]. Công thức đồng hồ có [8], RFC 4330 mục 5. Sửa số citation bị lệch trong V4: kết quả PREEMPT_RT thuộc [6], MemGuard/DeepPicar thuộc [4]/[5]; không gán các phát biểu này cho tài liệu khác. Các câu tiếng Việt và giá trị công bố được giữ nguyên.

## Giới hạn còn lại

Không còn lỗi bố cục hoặc biên dịch đã phát hiện. Đấu nối, chu kỳ, cấu hình và các giả thuyết vẫn là thiết kế cần kiểm chứng trên Raspberry Pi 5/STM32F446RE; chưa có số đo phần cứng của nhóm. Kiểm thử host và tiến độ được ghi theo tài liệu dự án, không phải kết quả chạy lại trong lần sửa slide.

Ảnh là minh họa, không thay sơ đồ chân hay capture thực nghiệm. V08 đặt Status trước Failsafe về mặt hình vẽ; nội dung 3.1 làm rõ supervisor trực tiếp quyết định đầu ra, tác vụ báo trạng thái chạy riêng. V10 dừng ngoặc AoI tại giám sát, nội dung 3.3 làm rõ cần tính thêm đầu ra nếu chọn điểm đo đó. V17 minh họa tuổi giảm về 0; notes làm rõ tuổi thật giảm về trễ giao nhận. Robot/drone trong các câu nguyên văn V4 là ví dụ ứng dụng chung; đồ án là nền tảng đo cơ chế OS và đầu ra mô phỏng, không xây robot.

Chỉ sửa `main.tex` và `README.md`; không sửa `REVISION_V4.md`, `RESTRUCTURE_SPEC.md`, `images/*`, `image-prompts/` hoặc `render.swift`. Không commit/push theo yêu cầu trực tiếp của người dùng.
