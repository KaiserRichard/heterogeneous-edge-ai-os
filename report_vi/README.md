# Báo cáo Hệ điều hành — Nhóm 3 Stars

Bản nộp: `BaoCao_HDH_Nhom3Stars.docx`; nguồn biên soạn: `content.md`.
Từ gốc kho mã:

```sh
python3 report_vi/validate_docx.py
python3 report_vi/style_check.py
```

Hình 2.1 giữ nguyên `figures/aoi.png`. Hình 3.1–3.3 dùng bản vẽ của sinh viên
(`Hinh_3_1_System_architecture`, `Hinh_3_2_UART_frame`, `Hinh_3_3_Queue_policies`):
SVG được giữ nguyên; PNG chỉ cắt lề trắng, chừa khoảng 15 px mỗi cạnh.
Builder DOCX và validator chỉ dùng thư viện chuẩn. Validator dựng hai lần để
kiểm tra tái lập; kết quả ghi vào `validation.json`. `IMAGE_PROMPTS.md` lưu prompt tham khảo trước khi thay hình sinh viên.

Bản Word gồm bìa, tóm tắt, mục lục, bảng thuật ngữ 25 dòng, tám Phần và tài liệu
tham khảo. Bảy bảng nội dung giữ nguyên số liệu; có thêm bảng thành viên và bảng
thuật ngữ. Mỗi Phần và tài liệu tham khảo bắt đầu trang mới bằng thuộc tính
`pageBreakBefore` của Heading 1. Thuật ngữ là front matter, không đánh số Phần.

Khổ A4, lề trên/dưới/trái/phải 2.5/2/3/2 cm, Times New Roman 13 pt,
giãn dòng 1.2, thụt đầu dòng 1 cm và cách đoạn 4 pt. Tiêu đề Phần 14 pt;
chú thích 12 pt nghiêng. Bảng thuật ngữ dùng 11 pt, giãn dòng đơn để tiết kiệm
front matter; bảng nội dung dùng 11 pt. Builder hiện giới hạn hình nội dung ở 16 × 10 cm; logo bìa rộng 3 cm. Bìa không có số
trang; phần tóm tắt bắt đầu trang 1. Word cập nhật trường TOC khi mở tài liệu.

Thân bài khoảng 4,565 từ tách bằng khoảng trắng, kể cả bảng. Mục tiêu tối đa 20
trang gồm toàn bộ front matter. Số trang chưa được xác nhận bằng dàn trang sau lần rút gọn này. Bản trước
được đo là 24 trang với giãn dòng 1.3 và bảng 13 pt. TICKET7 chỉ cho phép
Python headless, không mở hay tự động hóa ứng dụng GUI; vì vậy
`rendered_page_count` vẫn là null. Kiểm tra XML không thay phép dàn trang.
Kiểm tra tự động bao gồm ZIP/XML, quan hệ, bố cục, văn bản cấm, số bảng và hình,
thuật ngữ, thứ tự con pPr/rPr, mục lục tĩnh và tính tái lập.
`style_check.py` kiểm tra và assert toàn bộ mục tiêu nhịp văn TICKET5. Không chạy lại phép đo phần cứng.
`source_manifest.json` là hồ sơ biên soạn trước đó, không nhúng vào bản Word.

Bổ sung ngày 20/10/2026: mục 5.5 giữ riêng sáu bảng đo lại A–F, không thay các
bảng gốc 2–7. Tổng số bảng nội dung hiện là 13, cộng bảng thành viên và thuật ngữ.
`build_docx.py` cập nhật mục này từ đầu ra đối chiếu trước khi dựng Word; mặc định
đọc `results/2026-10-20_rerun/compare/`, hoặc thư mục trong `RERUN_COMPARE_DIR`.
Xem `tools/rerun/README.md` để phân tích lại vào thư mục mới rồi dựng hai tài liệu.
Các ô E1–E3B hiện là pending và sẽ nhận số liệu cùng số lượt hợp lệ khi có dữ liệu.
Validator giữ ngân sách từ của phần gốc riêng; phần bổ sung làm tài liệu dài hơn,
nên mục tiêu 20 trang cũ chưa được xác nhận lại bằng dàn trang Word.
