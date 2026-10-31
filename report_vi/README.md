# Báo cáo Hệ điều hành — Nhóm 3 Stars

Bản giữa kỳ C1-T19: `BaoCao_HDH_Nhom3Stars_GiuaKy.docx`, cập nhật ngày 30/10/2026.
Bản nộp cũ `BaoCao_HDH_Nhom3Stars.docx` được giữ nguyên. Nguồn chung: `content.md`.
Từ gốc worktree:

```sh
python3 report_vi/build_docx.py
python3 report_vi/validate_docx.py
python3 report_vi/style_check.py
```

Builder và validator dùng thư viện chuẩn, không cần python-docx. Validator dựng
hai lần vào tên giữa kỳ, kiểm tra tái lập và ghi `validation_giuaky.json`.
`c1_t19_sources.json` ghi nguồn chương camera, nguồn trạng thái T1–T4 và hash bản
DOCX cũ để kiểm tra không ghi đè. Các snapshot trong `src_update/` vẫn ghi chờ đo;
PASS/FAIL mới được ghi theo cập nhật của nhóm, số đo chưa có nguồn là “đang cập nhật”.
Kết quả ảnh cố định/tổng hợp/PTY lịch sử được phân biệt với kết quả camera.
OS-T8 trong nguồn là mở rộng CAN; kế hoạch hiện chỉ rà soát phạm vi vì giới hạn
hiện tại cấm CAN. Không chạy lại phép đo phần cứng trong ticket báo cáo.

Bản giữa kỳ giữ bìa HUST, tóm tắt, mục lục, thuật ngữ và cấu trúc các Phần cũ;
chèn Phần 5 về nguồn camera nên các phần sau được đánh số lại đến Phần 9.
Thân bài khoảng 5.670 từ tách bằng khoảng trắng, kể cả bảng; gồm tám bảng nội dung,
bảng thành viên, bảng thuật ngữ 25 dòng và bốn hình. `style_check.py` giữ các ngưỡng
nhịp văn TICKET5. Khổ A4, lề trên/dưới/trái/phải 2.5/2/3/2 cm; Times New Roman
13 pt, giãn dòng 1.2; hình tối đa 12 × 6.5 cm. Mục lục được cập nhật khi mở Word.
Mỗi Phần và tài liệu tham khảo bắt đầu trang mới; bìa không đánh số trang.

Kiểm tra ZIP/XML không thay thế dàn trang Word; chưa xác nhận số trang bản giữa kỳ.
`validation.json` và `source_manifest.json` là hồ sơ bản trước, được giữ nguyên.
Hình 2.1 dùng `figures/aoi.png`; Hình 3.1–3.3 dùng bản vẽ sinh viên, giữ SVG gốc.
