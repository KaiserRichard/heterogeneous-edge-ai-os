# Báo cáo Hệ điều hành — Nhóm 3 Stars

- Bản Word: `BaoCao_HDH_Nhom3Stars.docx`.
- Nội dung có thể sửa: `content.md`.
- Dựng lại: `python3 report_vi/build_docx.py` từ gốc kho mã.
- Kiểm tra: `python3 report_vi/validate_docx.py`; kết quả ở `validation.json`.

Chỉ dùng thư viện chuẩn Python, không tải mạng hoặc cài gói. Builder hỗ trợ heading,
đoạn văn, bullet, bold/italic, bảng, ảnh và caption, cùng các chỉ thị trang ở Markdown.
Các tệp đầu ra nằm trong report_vi. Không cần nguồn deck để dựng lại: ba ảnh đã sao chép
vào figures. Ảnh là minh họa khái niệm; nguồn và giới hạn được ghi trong báo cáo.

A4, Times New Roman 13 pt cho thân bài/bảng, giãn dòng 1.3; lề trên/dưới/trái/phải
2.5/2/3/2 cm. Heading và bìa lớn hơn, dòng nguồn 11 pt. Bìa là section riêng không có
footer; phần sau có trường PAGE. Mục lục là trường TOC với updateFields và các mục
cache để đọc được trước khi Word cập nhật. Khi mở bằng Word, cho phép cập nhật trường;
có thể chọn toàn văn và cập nhật trường để làm mới mục lục/số trang.

Bản R-VI-2 có đúng ba ngắt trang bắt buộc: sau bìa, tóm tắt và mục lục.
Các chương chảy liên tục; Heading 1 giữ với đoạn sau, không ép sang trang mới.
Thân bài có 5597 từ tách bởi khoảng trắng (gồm bảng và ghi chú nguồn), 7 bảng và
3 hình; mỗi hình giữ tỷ lệ và giới hạn 12 × 8 cm. Bảng không dùng keepNext,
cho phép chuyển trang giữa các hàng; hàng tiêu đề lặp lại. Đường dẫn kho mã được
chuyển vào phụ lục nguồn dữ liệu hoặc ghi chú bảng.

Mục tiêu là 17–19 trang Word. Chưa xác nhận phân trang thực tế vì môi trường không
có Word/LibreOffice renderer. Mở bằng Word và cập nhật mục lục để kiểm tra số trang;
`validation.json` giữ rendered_page_count là null, không dùng số ngắt làm số trang.

Kết quả đều là sơ bộ. Phân biệt tập E3 UART ban đầu trong results với rerun của deck
cuối; không đổi nhãn FLAGGED/INVALID hoặc coi kết quả PTY là UART vật lý. Quy tắc
v1/v2 và giới hạn bằng chứng được công bố trong phần đánh giá. Không chạy lại thí
nghiệm phần cứng cho công việc biên soạn này. `source_manifest.json` ghi hash của
các nguồn chính; đây là provenance tài liệu, không phải chứng nhận lại dữ liệu đo.
