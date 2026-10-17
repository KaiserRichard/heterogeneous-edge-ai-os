# TICKET R-VI-8: use the student's redrawn figures

Do not git commit. No GUI apps, no osascript. Append one line to logs/R-VI-summary.md.

The student generated three figures and put them in
/Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/images/:
Hinh_3_1_System_architecture.png (+.svg), Hinh_3_2_UART_frame.png (+.svg), Hinh_3_3_Queue_policies.png (+.svg).
1. Copy the three PNGs (and SVGs) into report_vi/figures/ under the same names. Trim the white margins of the PNG copies
   (system python3 with matplotlib.image imread/imsave is fine; keep a ~15 px white border) so they do not waste page space.
   Do not otherwise alter the drawings.
2. In content.md, point Hình 3.1, 3.2, 3.3 at these files instead of architecture.png, frame.png, queues.png.
   Keep Hình 2.1 (aoi.png) as is. Make sure captions/text still match the labels in the student's drawings.
3. Keep figure size limits (max 12 cm wide, 6.5 cm tall, aspect preserved). Rebuild the .docx, rerun validation,
   the forbidden-text scan and the pPr/rPr schema-order check.
