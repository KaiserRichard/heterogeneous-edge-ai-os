# Đối chiếu kết quả đo lại — 2026-10-20

Giữ nguyên dữ liệu gốc. Lượt chấp nhận theo kiểm tra gốc (v1) và đo lại (v2) có thể khác nhau.

E4 gốc gộp các cửa sổ ngắn F4/F5; đo lại dùng chiến dịch đầy đủ, có kiểm tra phục hồi. LA chỉ đối chiếu mốc thời gian, không xác nhận tính hợp lệ của toàn bộ phép đo.

## cyclic-P0

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P0_B0_idle / max_us | 2659 | 2338 | 3/3 | 3/3 |
| P0_B0_idle / p50_us | 53 | 56 | 3/3 | 3/3 |
| P0_B0_idle / p99_us | 57 | 95 | 3/3 | 3/3 |
| P0_B1_stream_c2 / max_us | 3565 | 5442 | 3/3 | 3/3 |
| P0_B1_stream_c2 / p50_us | 56 | 56 | 3/3 | 3/3 |
| P0_B1_stream_c2 / p99_us | 300 | 675 | 3/3 | 3/3 |
| P0_B2_memrate_c23 / max_us | 5170 | 4109 | 3/3 | 3/3 |
| P0_B2_memrate_c23 / p50_us | 55 | 55 | 3/3 | 3/3 |
| P0_B2_memrate_c23 / p99_us | 613 | 1020 | 3/3 | 3/3 |
| P0_C1_cache2M_c2 / max_us | 4780 | 2830 | 3/3 | 3/3 |
| P0_C1_cache2M_c2 / p50_us | 54 | 54 | 3/3 | 3/3 |
| P0_C1_cache2M_c2 / p99_us | 203 | 403 | 3/3 | 3/3 |
| P0_CPU_c23 / max_us | 2636 | 2679 | 3/3 | 3/3 |
| P0_CPU_c23 / p50_us | 54 | 53 | 3/3 | 3/3 |
| P0_CPU_c23 / p99_us | 68 | 183 | 3/3 | 3/3 |

Trạng thái: ok.

## cyclic-P1

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P1_B0_idle / max_us | 92 | 52 | 3/3 | 3/3 |
| P1_B0_idle / p50_us | 3 | 5 | 3/3 | 3/3 |
| P1_B0_idle / p99_us | 9 | 14 | 3/3 | 3/3 |
| P1_B1_stream_c2 / max_us | 211 | 137 | 3/3 | 3/3 |
| P1_B1_stream_c2 / p50_us | 5 | 6 | 3/3 | 3/3 |
| P1_B1_stream_c2 / p99_us | 39 | 42 | 3/3 | 3/3 |
| P1_B2_memrate_c23 / max_us | 1094 | 980 | 3/3 | 3/3 |
| P1_B2_memrate_c23 / p50_us | 5 | 5 | 3/3 | 3/3 |
| P1_B2_memrate_c23 / p99_us | 239 | 196 | 3/3 | 3/3 |
| P1_C1_cache2M_c2 / max_us | 233 | 97 | 3/3 | 3/3 |
| P1_C1_cache2M_c2 / p50_us | 3 | 3 | 3/3 | 3/3 |
| P1_C1_cache2M_c2 / p99_us | 35 | 37 | 3/3 | 3/3 |
| P1_CPU_c23 / max_us | 73 | 88 | 3/3 | 3/3 |
| P1_CPU_c23 / p50_us | 3 | 3 | 3/3 | 3/3 |
| P1_CPU_c23 / p99_us | 11 | 13 | 3/3 | 3/3 |

Trạng thái: ok.

## E1

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P0 / B0_idle / fifo / latest / aoi_peak_ms | 154.218 | 153.079 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / aoi_time_average_ms | 94.5308 | 94.894 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / cpu_percent | 43.9918 | 44.0908 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_max_ms | 56.4706 | 65.0706 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_p50_ms | 44.3689 | 44.8809 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_p99_ms | 48.4731 | 45.7999 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / rss_mib | 93.5 | 94.6016 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / rx_received | 602 | 601 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / service_p50_ms | 44.2471 | 44.722 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / service_p99_ms | 48.2832 | 45.6076 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / source_generated | 602 | 601 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / aoi_peak_ms | 250.425 | 199.314 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / aoi_time_average_ms | 128.605 | 125.319 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / cpu_percent | 77.9606 | 75.95 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_max_ms | 203.404 | 120.467 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p50_ms | 76.9924 | 74.7254 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p99_ms | 89.0164 | 83.4012 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / rss_mib | 93.5078 | 94.5938 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / rx_received | 604 | 604 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / service_p50_ms | 76.4632 | 74.227 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / service_p99_ms | 88.5039 | 82.8712 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / source_generated | 604 | 604 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 14998.6 | 11299.5 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6709.7 | 5058.42 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9478 | 101.151 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 15120.4 | 11444.6 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6626.47 | 4963.16 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 13977.2 | 10752.7 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / rss_mib | 93.5117 | 94.6016 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / rx_received | 475 | 504 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6625.8 | 4937.75 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / service_p99_ms | 13976.5 | 10749.8 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / source_generated | 605 | 604 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 207.977 | 179.836 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 118.977 | 111.668 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / cpu_percent | 67.974 | 62.0333 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 121.841 | 117.105 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 68.0005 | 61.5274 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 98.8279 | 69.4513 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / rss_mib | 93.4961 | 95.0781 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / rx_received | 603 | 603 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 67.5769 | 61.2751 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 97.3025 | 69.1043 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / source_generated | 603 | 603 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / aoi_peak_ms | 180.983 | 179.9 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / aoi_time_average_ms | 95.4163 | 92.8742 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / cpu_percent | 45.9909 | 42.0825 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / delivery_max_ms | 80.982 | 79.894 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / delivery_p50_ms | 45.4063 | 42.7266 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / delivery_p99_ms | 48.2984 | 44.4777 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / rss_mib | 93.5195 | 94.5977 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / rx_received | 601 | 602 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / service_p50_ms | 45.1985 | 42.5029 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / service_p99_ms | 48.1294 | 44.2248 | 3/3 | 3/3 |
| P0 / CPU_c23 / fifo / latest / source_generated | 601 | 602 | 3/3 | 3/3 |

Trạng thái: ok.

## E2

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P0 / B0_idle / fifo / latest / aoi_peak_ms | 158.513 | 155.06 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / aoi_time_average_ms | 94.2121 | 95.276 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / cpu_percent | 43.9917 | 45.9044 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_max_ms | 58.5084 | 60.9639 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_p50_ms | 44.0216 | 45.219 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / delivery_p99_ms | 49.2938 | 46.8136 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / rss_mib | 93.5195 | 94.6016 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / rx_received | 602 | 601 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / service_p50_ms | 43.8955 | 45.065 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / service_p99_ms | 49.154 | 46.1914 | 3/3 | 3/3 |
| P0 / B0_idle / fifo / latest / source_generated | 602 | 601 | 3/3 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / aoi_peak_ms | not run: unmatched condition | 206.366 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / aoi_time_average_ms | not run: unmatched condition | 125.408 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / bridge_overwritten | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / cpu_percent | not run: unmatched condition | 76.0252 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_max_ms | not run: unmatched condition | 129.72 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p50_ms | not run: unmatched condition | 74.8461 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p99_ms | not run: unmatched condition | 84.9501 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / drops | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / overflows | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / rss_mib | not run: unmatched condition | 94.5938 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / rx_received | not run: unmatched condition | 604 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / service_p50_ms | not run: unmatched condition | 74.3148 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / service_p99_ms | not run: unmatched condition | 83.4967 | 0/0 | 3/3 |
| P0 / B1_stream_c2 / fifo / latest / source_generated | not run: unmatched condition | 604 | 0/0 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 13246.8 | 13688.3 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6597.91 | 6364.25 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / cpu_percent | 101.615 | 100.975 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 13405.9 | 13865.8 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6506.4 | 6116 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 13260.3 | 13169.4 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / rss_mib | 93.5352 | 94.5977 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / rx_received | 482 | 483 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6506.02 | 6115.52 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / service_p99_ms | 13259.7 | 13168.6 | 3/3 | 3/3 |
| P0 / B2_memrate_c23 / fifo / latest / source_generated | 605 | 605 | 3/3 | 3/3 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 206.22 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 117.144 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / cpu_percent | 67.9545 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 109.609 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 66.8116 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 73.572 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / drops | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / overflows | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rss_mib | 93.5312 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rx_received | 604 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 66.355 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 73.1049 | not run: unmatched condition | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / source_generated | 604 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 154.728 | 175.904 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 94.2617 | 95.3357 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / cpu_percent | 43.9918 | 45.8981 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 56.4093 | 75.9022 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 44.0693 | 45.2831 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 48.9765 | 47.1963 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rss_mib | 95.6836 | 96.7344 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rx_received | 602 | 601 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 43.9429 | 45.1402 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 48.8099 | 47.0138 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / source_generated | 602 | 601 | 3/3 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / aoi_peak_ms | not run: unmatched condition | 236.869 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / aoi_time_average_ms | not run: unmatched condition | 124.756 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / bridge_overwritten | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / cpu_percent | not run: unmatched condition | 75.7957 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / delivery_max_ms | not run: unmatched condition | 166.042 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / delivery_p50_ms | not run: unmatched condition | 73.8126 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / delivery_p99_ms | not run: unmatched condition | 83.2902 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / drops | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / overflows | not run: unmatched condition | 0 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / rss_mib | not run: unmatched condition | 96.9727 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / rx_received | not run: unmatched condition | 604 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / service_p50_ms | not run: unmatched condition | 73.317 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / service_p99_ms | not run: unmatched condition | 82.8464 | 0/0 | 3/3 |
| P1 / B1_stream_c2 / fifo / latest / source_generated | not run: unmatched condition | 604 | 0/0 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 13899.7 | 9095.13 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6275.52 | 4153.82 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9497 | 101.221 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 14072.8 | 9178.52 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6001.83 | 4034.2 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 12890.2 | 8357.15 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | 95.6836 | 97.0469 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | 484 | 531 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | 5999.68 | 4033.56 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | 12889.7 | 8356.5 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | 604 | 605 | 3/3 | 3/3 |
| P1 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 216.663 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 120.361 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / cpu_percent | 69.9786 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 136.083 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 70.1861 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 97.1552 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / drops | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / overflows | 0 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / rss_mib | 95.6758 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / rx_received | 603 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 69.7958 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 96.5842 | not run: unmatched condition | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / source_generated | 603 | not run: unmatched condition | 3/3 | 0/0 |

Trạng thái: ok.

## E3

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P1 / B0_idle / fifo / fifo / aoi_peak_ms | 158.011 | 154.303 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / aoi_time_average_ms | 94.688 | 95.964 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / cpu_percent | 43.9918 | 45.9899 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / delivery_max_ms | 58.0232 | 58.1748 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / delivery_p50_ms | 44.5754 | 45.8061 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / delivery_p99_ms | 50.0972 | 48.5414 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / rss_mib | 95.6836 | 96.7422 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / rx_received | 602 | 602 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / service_p50_ms | 44.4549 | 45.6626 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / service_p99_ms | 49.8964 | 47.4908 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / fifo / source_generated | 602 | 602 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 155.995 | 151.213 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 94.5942 | 96.3507 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / cpu_percent | 43.9918 | 45.9922 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 57.5863 | 57.2168 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 44.4957 | 46.2429 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 47.2564 | 48.1102 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rss_mib | 95.6836 | 96.7344 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rx_received | 602 | 602 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 44.3739 | 45.8842 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 47.0847 | 47.3178 | 3/3 | 3/3 |
| P1 / B0_idle / fifo / latest / source_generated | 602 | 602 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / aoi_peak_ms | 13659.1 | 10119.9 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / aoi_time_average_ms | 6660.08 | 3680.48 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / cpu_percent | 99.9468 | 101.008 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_max_ms | 13777.4 | 10234.9 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_p50_ms | 6422.85 | 3545.68 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_p99_ms | 13388 | 7639.13 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / rss_mib | 95.6797 | 96.7227 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / rx_received | 480 | 537 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / service_p50_ms | 6421.95 | 3544.89 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / service_p99_ms | 13387.4 | 7638.53 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / fifo / source_generated | 605 | 605 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 14172.3 | 6258.93 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6957.88 | 2645.45 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9467 | 101.062 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 14300.5 | 6326.27 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6782.73 | 2585.51 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 14133.4 | 5260.79 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / drops | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | 0 | 0 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | 95.6719 | 96.7344 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | 472 | 562 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6782.09 | 2584.73 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | 14132.9 | 5259.18 | 3/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | 605 | 605 | 3/3 | 3/3 |

Trạng thái: ok.

## E3B

| Phép đo / điều kiện | Gốc (2026-10-12) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 188.532 | 154.322 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 97.6337 | 96.2906 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | 0 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / cpu_percent | 47.9909 | 45.9953 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 88.5283 | 57.5778 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 47.0821 | 46.071 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 60.555 | 48.5623 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / drops | 0 | 0 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / overflows | 0 | 0 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rss_mib | 96.582 | 96.7383 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / rx_received | 601 | 601 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 46.9729 | 45.92 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 60.2678 | 47.4797 | 2/3 | 3/3 |
| P1 / B0_idle / fifo / latest / source_generated | 601 | 601 | 2/3 | 3/3 |
| P1 / B0_idle / latest / latest / aoi_peak_ms | 188.975 | 154.837 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / aoi_time_average_ms | 98.0681 | 96.3455 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / bridge_overwritten | 0 | 0 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / cpu_percent | 47.991 | 45.9987 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / delivery_max_ms | 88.9646 | 58.5684 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / delivery_p50_ms | 47.5318 | 46.2173 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / delivery_p99_ms | 61.7457 | 48.6732 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / drops | 0 | 0 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / overflows | 0 | 0 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / rss_mib | 96.5859 | 96.7266 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / rx_received | 602 | 601 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / service_p50_ms | 47.4159 | 46.0827 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / service_p99_ms | 61.5532 | 47.7673 | 1/3 | 3/3 |
| P1 / B0_idle / latest / latest / source_generated | 602 | 601 | 1/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | failed: no valid runs | 9029.5 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | failed: no valid runs | 2334.45 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | failed: no valid runs | 101.361 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | failed: no valid runs | 9102.36 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | failed: no valid runs | 2338.15 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | failed: no valid runs | 4698.46 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / drops | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | failed: no valid runs | 96.7109 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | failed: no valid runs | 568 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | failed: no valid runs | 2337.56 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | failed: no valid runs | 4697.8 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | failed: no valid runs | 605 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / aoi_peak_ms | failed: no valid runs | 367.777 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / aoi_time_average_ms | failed: no valid runs | 229.438 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / bridge_overwritten | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / cpu_percent | failed: no valid runs | 100.921 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / delivery_max_ms | failed: no valid runs | 245.114 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / delivery_p50_ms | failed: no valid runs | 168.857 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / delivery_p99_ms | failed: no valid runs | 225 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / drops | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / overflows | failed: no valid runs | 0 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / rss_mib | failed: no valid runs | 96.7266 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / rx_received | failed: no valid runs | 510 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / service_p50_ms | failed: no valid runs | 167.981 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / service_p99_ms | failed: no valid runs | 223.855 | 0/3 | 3/3 |
| P1 / B2_memrate_c23 / latest / latest / source_generated | failed: no valid runs | 605 | 0/3 | 3/3 |

Trạng thái: ok.

## E4

| Phép đo / điều kiện | Gốc (2026-10-12) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| F1 / failsafe_local_max_ms | 100.641 | 100.433 | 5/5 | 5/5 |
| F1 / failsafe_local_min_ms | 100.128 | 100.285 | 5/5 | 5/5 |
| F1 / failsafe_local_p50_ms | 100.456 | 100.427 | 5/5 | 5/5 |
| F1 / failsafe_local_p95_ms | 100.641 | 100.433 | 5/5 | 5/5 |
| F1 / failsafe_local_range_max_ms | 100.641 | 100.433 | 5/5 | 5/5 |
| F1 / failsafe_mapped_max_ms | 86.2085 | 86.769 | 5/5 | 5/5 |
| F1 / failsafe_mapped_min_ms | 85.2557 | 85.1027 | 5/5 | 5/5 |
| F1 / failsafe_mapped_p50_ms | 85.3566 | 85.9999 | 5/5 | 5/5 |
| F1 / failsafe_mapped_p95_ms | 86.2085 | 86.769 | 5/5 | 5/5 |
| F1 / failsafe_mapped_range_max_ms | 86.2085 | 86.769 | 5/5 | 5/5 |
| F1 / first_local_max_ms | 175.535 | 175.066 | 5/5 | 5/5 |
| F1 / first_local_min_ms | 175.041 | 174.409 | 5/5 | 5/5 |
| F1 / first_local_p50_ms | 175.317 | 174.931 | 5/5 | 5/5 |
| F1 / first_local_p95_ms | 175.535 | 175.066 | 5/5 | 5/5 |
| F1 / first_local_range_max_ms | 175.535 | 175.066 | 5/5 | 5/5 |
| F1 / first_mapped_max_ms | 83.5606 | 85.1427 | 5/5 | 5/5 |
| F1 / first_mapped_min_ms | 83.2088 | 84.1028 | 5/5 | 5/5 |
| F1 / first_mapped_p50_ms | 83.3418 | 84.7691 | 5/5 | 5/5 |
| F1 / first_mapped_p95_ms | 83.5606 | 85.1427 | 5/5 | 5/5 |
| F1 / first_mapped_range_max_ms | 83.5606 | 85.1427 | 5/5 | 5/5 |
| F2 / failsafe_local_max_ms | 100.596 | 100.419 | 5/5 | 5/5 |
| F2 / failsafe_local_min_ms | 100.465 | 100.275 | 5/5 | 5/5 |
| F2 / failsafe_local_p50_ms | 100.577 | 100.293 | 5/5 | 5/5 |
| F2 / failsafe_local_p95_ms | 100.596 | 100.419 | 5/5 | 5/5 |
| F2 / failsafe_local_range_max_ms | 100.596 | 100.419 | 5/5 | 5/5 |
| F2 / failsafe_mapped_max_ms | 86.1126 | 86.6685 | 5/5 | 5/5 |
| F2 / failsafe_mapped_min_ms | 85.1508 | 83.9839 | 5/5 | 5/5 |
| F2 / failsafe_mapped_p50_ms | 85.7147 | 84.8909 | 5/5 | 5/5 |
| F2 / failsafe_mapped_p95_ms | 86.1126 | 86.6685 | 5/5 | 5/5 |
| F2 / failsafe_mapped_range_max_ms | 86.1126 | 86.6685 | 5/5 | 5/5 |
| F2 / first_local_max_ms | 175.709 | 175.051 | 5/5 | 5/5 |
| F2 / first_local_min_ms | 175.086 | 174.45 | 5/5 | 5/5 |
| F2 / first_local_p50_ms | 175.206 | 174.911 | 5/5 | 5/5 |
| F2 / first_local_p95_ms | 175.709 | 175.051 | 5/5 | 5/5 |
| F2 / first_local_range_max_ms | 175.709 | 175.051 | 5/5 | 5/5 |
| F2 / first_mapped_max_ms | 83.7149 | 85.6685 | 5/5 | 5/5 |
| F2 / first_mapped_min_ms | 83.0141 | 82.8911 | 5/5 | 5/5 |
| F2 / first_mapped_p50_ms | 83.1509 | 83.0407 | 5/5 | 5/5 |
| F2 / first_mapped_p95_ms | 83.7149 | 85.6685 | 5/5 | 5/5 |
| F2 / first_mapped_range_max_ms | 83.7149 | 85.6685 | 5/5 | 5/5 |
| F3 / failsafe_local_max_ms | 475.815 | 475.078 | 5/5 | 5/5 |
| F3 / failsafe_local_min_ms | 475.24 | 474.113 | 5/5 | 5/5 |
| F3 / failsafe_local_p50_ms | 475.754 | 474.937 | 5/5 | 5/5 |
| F3 / failsafe_local_p95_ms | 475.815 | 475.078 | 5/5 | 5/5 |
| F3 / failsafe_local_range_max_ms | 475.815 | 475.078 | 5/5 | 5/5 |
| F3 / failsafe_mapped_max_ms | 385.888 | 386.227 | 5/5 | 5/5 |
| F3 / failsafe_mapped_min_ms | 383.128 | 382.986 | 5/5 | 5/5 |
| F3 / failsafe_mapped_p50_ms | 383.62 | 385.344 | 5/5 | 5/5 |
| F3 / failsafe_mapped_p95_ms | 385.888 | 386.227 | 5/5 | 5/5 |
| F3 / failsafe_mapped_range_max_ms | 385.888 | 386.227 | 5/5 | 5/5 |
| F3 / first_local_max_ms | 175.815 | 175.078 | 5/5 | 5/5 |
| F3 / first_local_min_ms | 175.24 | 174.113 | 5/5 | 5/5 |
| F3 / first_local_p50_ms | 175.754 | 174.937 | 5/5 | 5/5 |
| F3 / first_local_p95_ms | 175.815 | 175.078 | 5/5 | 5/5 |
| F3 / first_local_range_max_ms | 175.815 | 175.078 | 5/5 | 5/5 |
| F3 / first_mapped_max_ms | 85.9141 | 86.2529 | 5/5 | 5/5 |
| F3 / first_mapped_min_ms | 83.1545 | 83.0119 | 5/5 | 5/5 |
| F3 / first_mapped_p50_ms | 83.6464 | 85.3702 | 5/5 | 5/5 |
| F3 / first_mapped_p95_ms | 85.9141 | 86.2529 | 5/5 | 5/5 |
| F3 / first_mapped_range_max_ms | 85.9141 | 86.2529 | 5/5 | 5/5 |
| F4 / failsafe_local_max_ms | 100.931 | 100.556 | 7/14 | 5/5 |
| F4 / failsafe_local_min_ms | 100.405 | 100.412 | 7/14 | 5/5 |
| F4 / failsafe_local_p50_ms | 100.556 | 100.426 | 7/14 | 5/5 |
| F4 / failsafe_local_p95_ms | 100.931 | 100.556 | 7/14 | 5/5 |
| F4 / failsafe_local_range_max_ms | 100.931 | 100.556 | 7/14 | 5/5 |
| F4 / failsafe_mapped_max_ms | 97.3436 | 87.4776 | 7/14 | 5/5 |
| F4 / failsafe_mapped_min_ms | 84.8386 | 86.0612 | 7/14 | 5/5 |
| F4 / failsafe_mapped_p50_ms | 87.2773 | 87.2318 | 7/14 | 5/5 |
| F4 / failsafe_mapped_p95_ms | 97.3436 | 87.4776 | 7/14 | 5/5 |
| F4 / failsafe_mapped_range_max_ms | 97.3436 | 87.4776 | 7/14 | 5/5 |
| F4 / first_local_max_ms | 175.229 | 100.556 | 7/14 | 5/5 |
| F4 / first_local_min_ms | 100.525 | 100.412 | 7/14 | 5/5 |
| F4 / first_local_p50_ms | 100.639 | 100.426 | 7/14 | 5/5 |
| F4 / first_local_p95_ms | 175.229 | 100.556 | 7/14 | 5/5 |
| F4 / first_local_range_max_ms | 175.229 | 100.556 | 7/14 | 5/5 |
| F4 / first_mapped_max_ms | 87.8713 | 87.4776 | 7/14 | 5/5 |
| F4 / first_mapped_min_ms | 56.3441 | 86.0612 | 7/14 | 5/5 |
| F4 / first_mapped_p50_ms | 85.6253 | 87.2318 | 7/14 | 5/5 |
| F4 / first_mapped_p95_ms | 87.8713 | 87.4776 | 7/14 | 5/5 |
| F4 / first_mapped_range_max_ms | 87.8713 | 87.4776 | 7/14 | 5/5 |
| F5 / failsafe_local_max_ms | 475.917 | 474.908 | 5/5 | 5/5 |
| F5 / failsafe_local_min_ms | 474.95 | 474.231 | 5/5 | 5/5 |
| F5 / failsafe_local_p50_ms | 475.596 | 474.459 | 5/5 | 5/5 |
| F5 / failsafe_local_p95_ms | 475.917 | 474.908 | 5/5 | 5/5 |
| F5 / failsafe_local_range_max_ms | 475.917 | 474.908 | 5/5 | 5/5 |
| F5 / failsafe_mapped_max_ms | 385.558 | 384.822 | 5/5 | 5/5 |
| F5 / failsafe_mapped_min_ms | 382.819 | 382.647 | 5/5 | 5/5 |
| F5 / failsafe_mapped_p50_ms | 383.603 | 384.179 | 5/5 | 5/5 |
| F5 / failsafe_mapped_p95_ms | 385.558 | 384.822 | 5/5 | 5/5 |
| F5 / failsafe_mapped_range_max_ms | 385.558 | 384.822 | 5/5 | 5/5 |
| F5 / first_local_max_ms | 175.917 | 174.908 | 5/5 | 5/5 |
| F5 / first_local_min_ms | 174.95 | 174.231 | 5/5 | 5/5 |
| F5 / first_local_p50_ms | 175.596 | 174.459 | 5/5 | 5/5 |
| F5 / first_local_p95_ms | 175.917 | 174.908 | 5/5 | 5/5 |
| F5 / first_local_range_max_ms | 175.917 | 174.908 | 5/5 | 5/5 |
| F5 / first_mapped_max_ms | 85.5629 | 84.8477 | 5/5 | 5/5 |
| F5 / first_mapped_min_ms | 82.8249 | 82.6729 | 5/5 | 5/5 |
| F5 / first_mapped_p50_ms | 83.6084 | 84.205 | 5/5 | 5/5 |
| F5 / first_mapped_p95_ms | 85.5629 | 84.8477 | 5/5 | 5/5 |
| F5 / first_mapped_range_max_ms | 85.5629 | 84.8477 | 5/5 | 5/5 |

Trạng thái: ok.

## LA

| Phép đo / điều kiện | Gốc (2026-10-12) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| F1 / marker_safe_max_ms | 95.541 | 90.6836 | 15/15 | 15/15 |
| F1 / marker_safe_min_ms | 86.9382 | 82.6529 | 15/15 | 15/15 |
| F2 / marker_safe_max_ms | 98.6757 | 93.7774 | 15/15 | 15/15 |
| F2 / marker_safe_min_ms | 86.947 | 83.1966 | 15/15 | 15/15 |
| F4 / marker_safe_max_ms | 91.302 | 99.0391 | 15/15 | 15/15 |
| F4 / marker_safe_min_ms | 82.8516 | 89.9435 | 15/15 | 15/15 |
| final HEARTBEAT / captures | 10 | 15 | 15/15 | 15/15 |
| marker_safe_us / max | 98675.7 | 99039.1 | 15/15 | 15/15 |
| marker_safe_us / min | 82851.6 | 82652.9 | 15/15 | 15/15 |
| matched_delta_us / max | 67.6493 | 102.649 | 15/15 | 15/15 |
| matched_delta_us / min | 47.5243 | 58.6493 | 15/15 | 15/15 |

Trạng thái: ok.

## PS1

| Phép đo / điều kiện | Gốc (not acquired) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| bridge_sent | not run: unmatched condition | 602 | 0/0 | 1/1 |
| done_to_send_us / max | not run: unmatched condition | 595.723 | 0/0 | 1/1 |
| done_to_send_us / p50 | not run: unmatched condition | 21.833 | 0/0 | 1/1 |
| done_to_send_us / p99 | not run: unmatched condition | 42.278 | 0/0 | 1/1 |
| echo_accepted | not run: unmatched condition | 62 | 0/0 | 1/1 |
| echo_received | not run: unmatched condition | 62 | 0/0 | 1/1 |
| mcu_status | not run: unmatched condition | 616 | 0/0 | 1/1 |

Trạng thái: ok.

## Standalone inference

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| cpu stress c2,3 / 1 / max_ms | 65.5 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 1 / p50_ms | 45.1 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 1 / p99_ms | 53.7 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 2 / max_ms | 105.5 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 2 / p50_ms | 33.2 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 2 / p99_ms | 46.1 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 3 / max_ms | 91.1 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 3 / p50_ms | 45.5 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 3 / p99_ms | 77.6 | not run: not repeated by this layout | 3/3 | 0/0 |
| cpu stress c2,3 / 4 / max_ms | 150.3 | not run: not repeated by this layout | 2/3 | 0/0 |
| cpu stress c2,3 / 4 / p50_ms | 60.3 | not run: not repeated by this layout | 2/3 | 0/0 |
| cpu stress c2,3 / 4 / p99_ms | 100.5 | not run: not repeated by this layout | 2/3 | 0/0 |
| idle / 1 / max_ms | 57 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 1 / p50_ms | 44 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 1 / p99_ms | 48 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 2 / max_ms | 51.8 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 2 / p50_ms | 31.1 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 2 / p99_ms | 42.9 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 3 / max_ms | 52.8 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 3 / p50_ms | 29.4 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 3 / p99_ms | 38.5 | not run: not repeated by this layout | 3/3 | 0/0 |
| idle / 4 / max_ms | 94.1 | not run: not repeated by this layout | 1/3 | 0/0 |
| idle / 4 / p50_ms | 31.4 | not run: not repeated by this layout | 1/3 | 0/0 |
| idle / 4 / p99_ms | 70.7 | not run: not repeated by this layout | 1/3 | 0/0 |

Trạng thái: not run: not repeated by this layout.

## Physical E3

| Phép đo / điều kiện | Gốc (2026-10-12) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| Accepted runs | 0 | not run: not repeated by this layout | 0/18 | 0/0 |

Trạng thái: not run: not repeated by this layout.

