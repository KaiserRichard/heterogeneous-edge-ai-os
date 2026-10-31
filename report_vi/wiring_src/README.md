# Hình đấu nối bàn thử OS (OS-FIX3)

Nguồn hình: `os_bench_breadboard.yaml`; đầu ra: `../figures/os_bench_wiring.{svg,pdf,png}`.
Dùng công cụ breadboard theo `SKILL.md`, với waypoint viết tay, không tự định tuyến.
Các kết nối lấy từ pinout đã được chủ bench xác nhận trong OS-FIX3; không suy từ hình cũ.
Không có CAN trong hình OS. Hình bo Pi 4B đại diện Pi 5 (cùng header 40 chân).

## Bảng chân và màu dây

| Dây | Từ | Đến | Màu |
|---|---|---|---|
| UART TX | Pi pin 8, GPIO14 TXD | Nucleo D2, PA10 USART1 RX | Cam |
| UART RX | Pi pin 10, GPIO15 RXD | Nucleo D8, PA9 USART1 TX | Vàng |
| Mass chung | Pi pin 6 GND | Nucleo CN5 GND | Đen |
| USB | Pi USB-A | ST-LINK mini-USB | Xám |
| Camera | Pi Camera v2, đầu 15 chân | Pi 5 CAM/DISP 0, đầu 22 chân | Ribbon trắng/xám |
| I2C SCL | Nucleo D10, PB6 | GY-521 SCL | Cyan |
| I2C SDA | Nucleo CN7-21, PB7 | GY-521 SDA | Xanh ngọc |
| FRESH | Nucleo D4, PB5 | bb.a23; 330 Ω e23–f23; LED xanh lá i23–i24 | Xanh lá |
| HOLD | Nucleo D5, PB4 | bb.a25; 330 Ω e25–f25; LED vàng i25–i26 | Vàng cam |
| FAILSAFE | Nucleo D6, PB10 | bb.a27; 330 Ω e27–f27; LED đỏ i27–i28 | Nâu |
| Frame hợp lệ | Nucleo D9, PC7 | bb.a29; 150 Ω e29–f29; LED xanh dương i29–i30 | Chàm |
| Cathode FRESH | bb.j24 | bb.B-24 | Đen |
| Cathode HOLD | bb.j26 | bb.B-26 | Đen |
| Cathode FAILSAFE | bb.j28 | bb.B-28 | Đen |
| Cathode frame | bb.j30 | bb.B-30 | Đen |
| Cấp 3V3 | Nucleo POWER 3V3 | bb.T+19 | Đỏ |
| Cấp GND | Nucleo POWER GND | bb.T-21 | Đen |
| Nối thanh GND | bb.T-1 | bb.B-1 | Đen |
| Nối thanh 3V3 | bb.T+30 | bb.B+30 | Đỏ |
| IMU VCC | bb.B+13 | GY-521 VCC | Đỏ |
| IMU GND | bb.B-12 | GY-521 GND | Đen |

UART: 921600 baud. FAILSAFE chốt đến rearm. LED xanh dương đảo mỗi frame được chấp nhận.
MPU6050 đã đấu dây nhưng firmware OS chưa dùng; lấy mẫu thuộc OS-T7 dự kiến.
Vị trí bo, lỗ breadboard và vị trí đầu camera trên hình Pi 4B chỉ minh họa.

## Dựng lại

Chạy từ gốc worktree; Python cần CairoSVG, PyYAML và Pillow (Pillow dùng để xem crop).
Có thể dùng venv sẵn của nguồn công cụ theo chỉ dẫn OS-FIX3, chỉ đọc, hoặc tạo venv ở scratch:

```sh
python3 -m venv /private/tmp/os-fix3-venv
/private/tmp/os-fix3-venv/bin/pip install -r report_vi/wiring_src/wiring_diagram/requirements.txt
/private/tmp/os-fix3-venv/bin/python report_vi/wiring_src/wiring_diagram/wiring_diagram.py report_vi/wiring_src/os_bench_breadboard.yaml --output-dir report_vi/figures --strict
/private/tmp/os-fix3-venv/bin/python -m unittest discover -s report_vi/wiring_src/wiring_diagram/tests
python3 report_vi/build_docx.py
python3 report_vi/style_check.py
python3 report_vi/validate_docx.py
```

Công cụ và sáu tệp Fritzing được sao từ nguồn chỉ đọc được chỉ định trong OS-FIX3;
`parts/PARTS_CREDITS.md` ghi nguồn và giấy phép. Chỉ bổ sung hỗ trợ ribbon dọc,
cỡ chữ tiêu đề bo và khoảng cách chú giải khi tăng chữ; bộ kiểm tra hình học giữ nguyên.
Module camera là SVG đơn giản tự vẽ, không phải bản vẽ kích thước thực.
Toàn bộ hình phái sinh chia sẻ theo CC-BY-SA 3.0.

## Kiểm tra hình

`strict_check.txt`: 21 đường nối, `crossings: 13`, `check: PASS` (13 giao cắt vuông góc được phép).
Đã xem toàn PNG và crop 1:1: header Pi, header Nucleo trên/dưới, GY-521, breadboard,
camera/ribbon. Không có đoạn dây dùng chung, chữ bị dây cắt hay nội dung bị cắt mép hình.
Đỏ chỉ cho 3V3, đen chỉ cho GND; màu thân LED không phải màu dây tín hiệu.

DOCX nhúng PNG nguyên vẹn, rộng khoảng 16 cm (toàn vùng chữ A4), giữ tỉ lệ;
chú giải 34 px tương đương khoảng 6,3 pt ở kích thước in, đối chiếu thêm bảng pinout trong báo cáo.
UNVERIFIED: không thử phần cứng theo phạm vi ticket; chưa kiểm tra phân trang bằng Word/LibreOffice.

Kết quả cục bộ: 7 test công cụ PASS; build DOCX PASS; style check PASS;
validate DOCX PASS, gồm kiểm tra PNG nhúng trùng byte nguồn và đúng tỉ lệ 16,00 × 13,26 cm.
Tổng thô 6.506 từ; ngân sách nội dung 6.499 từ sau khi trừ đúng 7 từ credit giấy phép bắt buộc
trong caption (các caption khác vẫn được tính). Không sửa bảng pinout hay hai vị trí ảnh.
