# Slides v3 — báo cáo tiến độ

`main.tex` theo nội dung của `RESTRUCTURE_SPEC.md`, với 34 trang: bìa, mục lục, 6 trang chuyển mục, 23 trang nội dung, 2 trang tài liệu tham khảo và lời cảm ơn. XeLaTeX/Beamer moloch, 16:9, Avenir Next và Menlo. Chân trang chỉ có n/N; hình nội dung được đánh số tự động từ Hình 1 đến Hình 17. Ghi chú thuyết trình tiếng Việt nằm trong `\note{}`.

Không bổ sung số đo phần cứng. Chu kỳ, cấu hình và đấu nối là dự kiến. Kiểm thử trên máy tính và tiến độ được ghi theo brief và tài liệu dự án, không phải chạy lại mã giao thức trong lần biên tập này. Các ảnh là minh họa; vị trí dây trên V22 không thay thế bảng chân đề xuất. Chưa kiểm chứng Raspberry Pi 5 hoặc STM32 thật.

## Build và render

```sh
cd slides
latexmk -xelatex -interaction=nonstopmode main.tex
swift render.swift main.pdf preview
```

Nếu cache mặc định của Swift bị sandbox chặn, dùng cache nằm trong thư mục này:

```sh
swift -module-cache-path .swift-module-cache render.swift main.pdf preview
```

Cần TeX Live có moloch, các font trên và macOS Swift/PDFKit. `render.swift` xuất mỗi trang ở 1280 × 720, giữ nguyên tỷ lệ. Có thể bật một trong hai tùy chọn ghi chú đầu `main.tex` để tạo bản có speaker notes.

Kiểm tra log:

```sh
rg 'Overfull|Underfull|Missing character|Warning|^!' main.log
```

Lần xác nhận cuối: build thành công; không có lỗi, overfull/underfull box, Missing character hay cảnh báo trong `main.log`. Đã mở từng trang PNG ở kích thước gốc, kiểm tra tỷ lệ ảnh, caption, chữ tiếng Việt, chân trang và bố cục; sửa các trang bị chật và kiểm tra lại. PDF/preview/cache là sản phẩm build, không phải tài sản hình ảnh nguồn.

## Danh sách trang

| Trang | Tiêu đề |
|---:|---|
| 1 | NỀN TẢNG THỰC THI EDGE-AI KHÔNG ĐỒNG NHẤT |
| 2 | Mục lục |
| 3 | 1. Giới thiệu |
| 4 | 1.1 Động lực nghiên cứu |
| 5 | 1.2 Vấn đề đặt ra |
| 6 | 1.3 Mục tiêu và câu hỏi nghiên cứu |
| 7 | 2. Cơ sở lý thuyết |
| 8 | 2.1 Kiến trúc Simplex |
| 9 | 2.2 Lập lịch thời gian thực trên Linux |
| 10 | 2.3 Tranh chấp tài nguyên trên vi xử lý đa nhân |
| 11 | 2.4 Tuổi thông tin (Age of Information) |
| 12 | 3. Thiết kế hệ thống |
| 13 | 3.1 Kiến trúc tổng thể |
| 14 | 3.2 Phần cứng và đấu nối |
| 15 | 3.3 Luồng dữ liệu của một kết quả |
| 16 | 3.4 Các cấu hình runtime |
| 17 | 3.5 Latest-value buffer |
| 18 | 3.6 Giao thức truyền UART |
| 19 | 3.7 Bộ giám sát trên STM32 |
| 20 | 3.8 Vì sao cần hai bộ định thời |
| 21 | 3.9 Đồng bộ đồng hồ giữa hai miền |
| 22 | 4. Phương pháp đánh giá |
| 23 | 4.1 Chỉ số đánh giá |
| 24 | 4.2 Các thí nghiệm |
| 25 | 4.3 Đo phản ứng khi có lỗi |
| 26 | 4.4 Giả thuyết |
| 27 | 5. Tiến độ và kế hoạch |
| 28 | 5.1 Kết quả đã đạt được |
| 29 | 5.2 Kế hoạch tiếp theo |
| 30 | 6. Kết luận |
| 31 | 6.1 Kết luận |
| 32 | Tài liệu tham khảo |
| 33 | Tài liệu tham khảo |
| 34 | Cảm ơn thầy và các bạn đã lắng nghe! |

## Ảnh

Dùng: V01, V02, V03, V04, V05, V06, V08, V10, V11, V12, V14, V17, V20, V22, V23.

Bỏ khỏi deck: V07, V09, V13, V15, V16, V18, V19, V21, V24. V09 không cần thêm vì đã dùng V22; V15/V18/V19 được thay bằng ba sơ đồ TikZ tái sử dụng (khung UART, máy trạng thái, T1–T4). V17 là minh họa hai bộ định thời, V18 là máy trạng thái. Đã mở từng ảnh dùng và đối chiếu `images/MAPPING.md` trước khi bố trí.

Không sửa `images/*`, `image-prompts/` hoặc brief. V08 và V10 chỉ cắt viền trống khi nhúng trong PDF, không sửa file và không kéo méo ảnh. Các ảnh còn lại dùng `\slideimg` với keepaspectratio.

## Các điểm không thể giữ đồng thời trong brief

- Bố cục hai cột và tối đa hai dòng mỗi bullet xung đột với một số câu nguyên văn dài ở cỡ chữ tối thiểu `\small`. Các trang 1.1, 2.1–2.4 và 4.3 đặt văn bản phía trên ảnh lớn; một số câu ở 1.3, 2.2, 3.7 và 3.9 vẫn dài hơn hai dòng để giữ đủ nội dung và không thu nhỏ chữ.
- Các caption dài được đặt trên toàn chiều rộng ngay dưới hàng hình; riêng hai caption trang 1.2 nằm thành hai dòng dưới cặp hình. Ảnh bìa không đánh số để Hình 1–17 đúng thứ tự được chỉ định trong mục C.
- Ảnh V01/V08/V10/V17 được giới hạn chiều cao để giữ tỷ lệ 16:9 và đủ chỗ cho chữ; không thể đồng thời lấp đầy chiều rộng/75% chiều cao như yêu cầu mà không kéo méo, cắt nội dung hoặc thêm trang. Hình nội dung vẫn chiếm khoảng 45% chiều rộng trở lên.
- Tài liệu tham khảo cần hai trang để giữ cỡ chữ tối thiểu. Giữ đủ sáu tài liệu, tác giả, nhan đề, năm, số trang và liên kết; tên hội nghị rút gọn thành tên chính thức RTAS/CISS/RTCSA.
- Khoảng 20–50 ms của workload đến từ bản thảo được R7 ghi nhận, không thuộc sáu tài liệu tham khảo gốc. Dòng workload liên kết trực tiếp đến bản thảo thay vì gán một số trích dẫn [1]–[6] không liên quan. Đây là ngoại lệ với quy tắc chỉ dùng citation đánh số.
- Giữ nguyên tiêu đề 3.8 dạng câu hỏi và danh sách sáu bước 5.2 theo mục C, dù quy tắc chung yêu cầu tiêu đề danh ngữ và tối đa bốn bullet.
- Không commit: yêu cầu trực tiếp của người dùng có ưu tiên hơn bước commit ở mục D của brief.
