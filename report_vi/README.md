# Báo cáo Hệ điều hành — Nhóm 3 Stars

Bản nộp là `BaoCao_HDH_Nhom3Stars.docx`; sửa nội dung tại `content.md`.
Dựng lại từ gốc kho mã bằng `python3 report_vi/build_docx.py`.
Kiểm tra bằng `python3 report_vi/validate_docx.py`; kết quả lưu ở `validation.json`.
Chỉ dùng thư viện chuẩn Python; ba ảnh được lưu sẵn trong `figures/`.

Bản Word có bìa riêng, tóm tắt, mục lục, tám chương và tài liệu tham khảo.
Bảy bảng nội dung giữ nguyên số liệu; bìa có thêm bảng ba thành viên.
Ba hình là minh họa khái niệm. Nội dung bản nộp không có đường dẫn kho mã,
nhãn đánh giá nội bộ hoặc phụ lục nguồn dữ liệu.

Khổ A4, lề trên/dưới/trái/phải 2.5/2/3/2 cm, Times New Roman 13 pt,
giãn dòng 1.3, thụt đầu dòng 1 cm và cách đoạn 6 pt. Tiêu đề chương 14 pt;
chú thích 12 pt nghiêng, giữa dòng. Chú thích bảng nằm trên bảng và chú thích
hình nằm dưới hình. Bìa không có số trang; phần tóm tắt bắt đầu trang 1.
Ba ngắt trang tách bìa, tóm tắt và mục lục; các chương chảy liên tục.
Mục lục là trường TOC có các mục lưu sẵn; Word cập nhật trường và số trang khi mở.

Thân bài khoảng 5,800 từ tách bằng khoảng trắng, kể cả bảng, gần độ dài bản trước.
Mục tiêu là 16–19 trang A4. Không có Word/LibreOffice trong môi trường hiện tại,
vì vậy số trang thực tế chưa được xác nhận; `rendered_page_count` vẫn là null.
Kiểm tra tự động bao gồm ZIP/XML, quan hệ nội bộ, bố cục, văn bản cấm và hai lần
dựng có kết quả giống nhau. Công việc này không chạy lại phép đo phần cứng.
`source_manifest.json` là hồ sơ nguồn biên soạn trước đó, không nhúng vào bản Word.
