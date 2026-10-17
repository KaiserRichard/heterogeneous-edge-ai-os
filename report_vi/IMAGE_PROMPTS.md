# Figure redraw prompts

## Hình 3.1 — System architecture

Draw a clean draw.io technical diagram, aspect ratio 7:4, white background, dark-grey 1–1.5 px lines, Arial, rectangles and arrows; only blue #1f5fa8 and red #c0392b accents. No gradients, shadows, icons, 3D or cartoons. Exact labels: “Raspberry Pi 5 · Ubuntu”, “Linux workload”, “ONNX Runtime”, “MobileNetV2”, “bridge”, “UART”, “HEARTBEAT”, “INFERENCE”, “STM32F446RE · FreeRTOS”, “UART ISR”, “bounded buffer”, “RX task”, “supervisor”, “output/LED”, “Ranh giới quyền điều khiển”. Connect workload → bridge → UART ISR → bounded buffer → RX task → supervisor → output/LED. Separate Pi and MCU with a dashed authority boundary; place message labels on UART.

## Hình 3.2 — UART frame

Draw a draw.io technical frame diagram, aspect ratio 35:13, white background, dark-grey 1–1.5 px lines, Arial, rectangular fields. Only blue #1f5fa8 and red #c0392b accents, flat; no gradients, shadows, icons, 3D or cartoons. Left-to-right exact labels: “SOF0”, “A5”, “SOF1”, “5A”, “header”, “version · type · seq · len”, “payload”, “≤ 64 byte”, “CRC”, “2 byte”. Above the two SOF fields place “SOF: 2 byte”. Under header through payload, excluding SOF and CRC, draw a bracket labelled exactly “CRC-16/CCITT-FALSE: version → payload”. Do not add unstated sizes.

## Hình 3.3 — Queue policies

Draw two draw.io queue diagrams, aspect ratio 7:3, white background, dark-grey 1–1.5 px lines, Arial, rectangles and arrows. Only blue #1f5fa8 and red #c0392b accents, flat; no gradients, shadows, icons, 3D or cartoons. Exact upper label: “FIFO: giữ backlog”. Upper queue left-to-right: “Kết quả mới”, “Kết quả chờ”, “Kết quả cũ”, then “Gửi UART”. Lower label: “Latest-value: thay kết quả chưa gửi”. Lower boxes: “Kết quả chưa gửi”, “Kết quả mới”; a replacement arrow labelled “Thay thế” points from new to unsent. Show “Gửi UART” after the new-result box. Replacement affects only unsent results.

## Hình 2.1 — Age of Information

Draw a conceptual draw.io line plot, aspect ratio 35:16, white background, dark-grey 1–1.5 px axes, Arial. Only blue #1f5fa8 and red #c0392b accents, flat; no gradients, shadows, icons, 3D or cartoons. Exact axis labels: “Thời gian”, “Tuổi dữ liệu (AoI)”. Show a blue sawtooth rising linearly between updates and dropping vertically to positive age at each update. Draw a dashed red horizontal threshold labelled exactly “Ngưỡng độ tươi”. No numeric ticks, data points, legend or measured values. Keep all text and lines uncluttered.
