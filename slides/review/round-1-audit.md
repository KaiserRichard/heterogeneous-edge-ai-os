# Round 1 verification record

Built with `latexmk -xelatex -interaction=nonstopmode main.tex`: exit 0, targets up to date; current main.log contains no LaTeX errors or overfull boxes. Rendered all 45 pages with `swift -module-cache-path preview/.swift-module-cache render.swift main.pdf preview` (exit 0). Opened each page image individually at its native 1280 × 719 resolution, including all dividers and the closing page. The initial default-cache Swift invocation failed under sandbox restrictions; the workspace-cache invocation succeeded.

`main.tex` SHA-1 before and after review: bd634c6f77d35daecf395c5c9016f8265ece269e. No edits to main.tex.

## Caption inventory in page order

p4: Hình 1: Vòng cảm biến–AI–điều khiển: dữ liệu phải đến kịp thời trước khi tác động lên hệ vật lý.
p5: Hình 2: Xa lộ tối ưu lưu lượng; đường ray bảo đảm giờ đến.
p6: Hình 3: Hai miền thực thi: kết hợp năng lực tính toán với giám sát thời gian thực.
p7: Hình 4: Dữ liệu cũ: kết quả xếp hàng và đến nơi khi đã lỗi thời.
p8: Hình 5: Lỗi im lặng: Linux ngừng phản hồi, bên nhận giữ giá trị cũ.
p9: Hình 6: Phạm vi RQ1–RQ3: đo tác động của tải, cấu hình Linux và thời gian phản ứng của STM32.
p10: Hình 6: Phạm vi RQ1–RQ3: đo tác động của tải, cấu hình Linux và thời gian phản ứng của STM32. (repeat; identical caption)
p12: Hình 7: Simplex: bộ giám sát quyết định đầu ra.
p13: Hình 7: Simplex: bộ giám sát quyết định đầu ra. (repeat; identical caption)
p14: Hình 8: Mặc định và sau tinh chỉnh: mỗi hàng là một nhân CPU; trục ngang là thời gian.
p15: Hình 8: Mặc định và sau tinh chỉnh: mỗi hàng là một nhân CPU; trục ngang là thời gian. (repeat; identical caption)
p16: Hình 9: Kết quả công bố [6]: độ trễ xấu nhất giảm với PREEMPT_RT; đây không phải số đo nền tảng của nhóm.
p17: Hình 10: Lưu lượng cạnh tranh làm nhân 0 chậm.
p17: Hình 11: BCM2712: L2 riêng, L3 và bộ nhớ chung.
p18: Hình 12: Tranh chấp trên đường truyền chung làm tác vụ ở nhân 0 bị chậm.
p19: Hình 13: AoI minh họa, không phải số đo: tuổi tăng giữa hai lần nhận; vùng cam vượt ngưỡng.
p20: Hình 13: AoI minh họa, không phải số đo: tuổi tăng giữa hai lần nhận; vùng cam vượt ngưỡng. (repeat; identical caption)
p22: Hình 14: Hai miền Linux và FreeRTOS nối bằng UART; bộ giám sát quyết định đầu ra.
p23: Hình 15: Bốn đường nối dự kiến: TX, RX, GND và GPIO đồng bộ.
p24: Hình 16: Chín trạm: theo dấu mẫu đầu vào từ Linux đến đầu ra và phản hồi STM32.
p25: Hình 17: P0–P1: tinh chỉnh; P2 và P3 là hai nhánh độc lập từ P1.
p26: Hình 18: FIFO giữ dữ liệu cũ; bộ đệm một ô giữ kết quả mới nhất chưa gửi.
p27: Hình 19: SOF (Start of Frame) là hai byte bắt đầu; header gồm phiên bản, loại, số thứ tự và độ dài;
p28: Hình 20: HOLD khi dữ liệu cũ; FAILSAFE khi mất heartbeat hoặc hết thời gian chờ.
p29: Hình 21: Hai bộ định thời độc lập cung cấp trạng thái cho bộ giám sát.
p30: Hình 22: Heartbeat vẫn đều nhưng tuổi kết quả vượt ngưỡng độ mới.
p31: Hình 23: Trao đổi T1–T4 qua UART để ước lượng độ lệch đồng hồ.
p35: Hình 24: Heartbeat dừng tại lỗi; một quyết định trạng thái đi trước đầu ra an toàn.
p36: Hình 24: Heartbeat dừng tại lỗi; một quyết định trạng thái đi trước đầu ra an toàn. (repeat; identical caption)
p40: Hình 25: Trình tự thực hiện: chỉ đo E1–E4 sau khi đường truyền và đồng bộ được kiểm chứng.
p42: Hình 14: Hai miền Linux và FreeRTOS nối bằng UART; bộ giám sát quyết định đầu ra. (repeat; identical caption)
p43: Hình 26: Từ thiết kế đã hoàn thành đến triển khai và đánh giá bằng số đo.

All distinct figures advance from 1 through 26 without gaps. Repeats on p10, p13, p15, p20, p36 and p42 retain their original number and caption. Visible numbered text references match their targets. Other pages have no figure captions.

## Owner fixes v6 audit

1. PASS: numbering, repetitions and text references checked throughout; inventory above.
2. PASS: cover title is high and centered; group/GVHD/class text uses the same large size; all names remain on one line; V01 and the information block are centered against each other.
3. PASS: one vertical sequence of six equal rows, navy numbered squares, pale rounded title boxes and large left-aligned text.
4. FAIL: p5 has the requested overall ordering, centered figure/caption and bottom takeaway, but both explanation columns wrap and the caption-to-explanation gap is cramped. High severity under the owner-fix rule.
5. FAIL: the deck-wide check found further explanation/diagram spacing and labeling defects listed in the review. Numbering and cover font-size corrections themselves pass.
6. FAIL: p26 has a centered figure and bottom takeaway, but its explanations wrap and crowd the caption. The adapted top/bottom labels match its vertically stacked diagram; the remaining spacing/line-count requirements do not pass.
7. PASS: exactly one references slide, p44, with two columns and compact entries; no continuation reference pages.

## Other mandatory checks

The state diagram on p28 correctly labels FRESH to FAILSAFE as “Mất heartbeat” and HOLD to FAILSAFE as “Hết thời gian chờ”; p29 repeats those meanings correctly. Vietnamese diacritics render correctly. References use the owner's explicitly permitted smaller type. No immediate bullet-plus-arrow structure mark was found; arrows inside process sequences are semantic transitions.

The verdict and actionable defects are recorded identically in latest.md and round-1.md. Severity is included in each defect's description.
