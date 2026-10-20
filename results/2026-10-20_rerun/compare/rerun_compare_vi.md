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
| P0 / B0_idle / fifo / latest / aoi_peak_ms | 154.218 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / aoi_time_average_ms | 94.5308 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / cpu_percent | 43.9918 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_max_ms | 56.4706 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_p50_ms | 44.3689 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_p99_ms | 48.4731 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / rss_mib | 93.5 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / rx_received | 602 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / service_p50_ms | 44.2471 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / service_p99_ms | 48.2832 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / source_generated | 602 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / aoi_peak_ms | 250.425 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / aoi_time_average_ms | 128.605 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / cpu_percent | 77.9606 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / delivery_max_ms | 203.404 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p50_ms | 76.9924 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / delivery_p99_ms | 89.0164 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / rss_mib | 93.5078 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / rx_received | 604 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / service_p50_ms | 76.4632 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / service_p99_ms | 88.5039 | not run | 3/3 | 0/0 |
| P0 / B1_stream_c2 / fifo / latest / source_generated | 604 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 14998.6 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6709.7 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9478 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 15120.4 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6626.47 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 13977.2 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / rss_mib | 93.5117 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / rx_received | 475 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6625.8 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / service_p99_ms | 13976.5 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / source_generated | 605 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 207.977 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 118.977 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / cpu_percent | 67.974 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 121.841 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 68.0005 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 98.8279 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rss_mib | 93.4961 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rx_received | 603 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 67.5769 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 97.3025 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / source_generated | 603 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / aoi_peak_ms | 180.983 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / aoi_time_average_ms | 95.4163 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / cpu_percent | 45.9909 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / delivery_max_ms | 80.982 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / delivery_p50_ms | 45.4063 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / delivery_p99_ms | 48.2984 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / rss_mib | 93.5195 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / rx_received | 601 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / service_p50_ms | 45.1985 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / service_p99_ms | 48.1294 | not run | 3/3 | 0/0 |
| P0 / CPU_c23 / fifo / latest / source_generated | 601 | not run | 3/3 | 0/0 |

Trạng thái: not run.

## E2

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P0 / B0_idle / fifo / latest / aoi_peak_ms | 158.513 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / aoi_time_average_ms | 94.2121 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / cpu_percent | 43.9917 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_max_ms | 58.5084 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_p50_ms | 44.0216 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / delivery_p99_ms | 49.2938 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / rss_mib | 93.5195 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / rx_received | 602 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / service_p50_ms | 43.8955 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / service_p99_ms | 49.154 | not run | 3/3 | 0/0 |
| P0 / B0_idle / fifo / latest / source_generated | 602 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 13246.8 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6597.91 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / cpu_percent | 101.615 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 13405.9 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6506.4 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 13260.3 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / rss_mib | 93.5352 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / rx_received | 482 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6506.02 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / service_p99_ms | 13259.7 | not run | 3/3 | 0/0 |
| P0 / B2_memrate_c23 / fifo / latest / source_generated | 605 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 206.22 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 117.144 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / cpu_percent | 67.9545 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 109.609 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 66.8116 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 73.572 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rss_mib | 93.5312 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / rx_received | 604 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 66.355 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 73.1049 | not run | 3/3 | 0/0 |
| P0 / C1_cache2M_c2 / fifo / latest / source_generated | 604 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 154.728 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 94.2617 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / cpu_percent | 43.9918 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 56.4093 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 44.0693 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 48.9765 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rss_mib | 95.6836 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rx_received | 602 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 43.9429 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 48.8099 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / source_generated | 602 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 13899.7 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6275.52 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9497 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 14072.8 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6001.83 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 12890.2 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | 95.6836 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | 484 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | 5999.68 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | 12889.7 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | 604 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / aoi_peak_ms | 216.663 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / aoi_time_average_ms | 120.361 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / cpu_percent | 69.9786 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_max_ms | 136.083 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_p50_ms | 70.1861 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms | 97.1552 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / rss_mib | 95.6758 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / rx_received | 603 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / service_p50_ms | 69.7958 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / service_p99_ms | 96.5842 | not run | 3/3 | 0/0 |
| P1 / C1_cache2M_c2 / fifo / latest / source_generated | 603 | not run | 3/3 | 0/0 |

Trạng thái: not run.

## E3

| Phép đo / điều kiện | Gốc (2026-10-11) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P1 / B0_idle / fifo / fifo / aoi_peak_ms | 158.011 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / aoi_time_average_ms | 94.688 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / cpu_percent | 43.9918 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / delivery_max_ms | 58.0232 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / delivery_p50_ms | 44.5754 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / delivery_p99_ms | 50.0972 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / rss_mib | 95.6836 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / rx_received | 602 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / service_p50_ms | 44.4549 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / service_p99_ms | 49.8964 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / fifo / source_generated | 602 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 155.995 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 94.5942 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / cpu_percent | 43.9918 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 57.5863 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 44.4957 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 47.2564 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rss_mib | 95.6836 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rx_received | 602 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 44.3739 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 47.0847 | not run | 3/3 | 0/0 |
| P1 / B0_idle / fifo / latest / source_generated | 602 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / aoi_peak_ms | 13659.1 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / aoi_time_average_ms | 6660.08 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / cpu_percent | 99.9468 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_max_ms | 13777.4 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_p50_ms | 6422.85 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / delivery_p99_ms | 13388 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / rss_mib | 95.6797 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / rx_received | 480 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / service_p50_ms | 6421.95 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / service_p99_ms | 13387.4 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / fifo / source_generated | 605 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | 14172.3 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | 6957.88 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | 99.9467 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | 14300.5 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | 6782.73 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | 14133.4 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / drops | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | 0 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | 95.6719 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | 472 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | 6782.09 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | 14132.9 | not run | 3/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | 605 | not run | 3/3 | 0/0 |

Trạng thái: not run.

## E3B

| Phép đo / điều kiện | Gốc (2026-10-12) | Đo lại 2026-10-20 | Lặp hợp lệ gốc | Lặp hợp lệ đo lại |
|---|---|---|---|---|
| P1 / B0_idle / fifo / latest / aoi_peak_ms | 188.532 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / aoi_time_average_ms | 97.6337 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / bridge_overwritten | 0 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / cpu_percent | 47.9909 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_max_ms | 88.5283 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p50_ms | 47.0821 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / delivery_p99_ms | 60.555 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / drops | 0 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / overflows | 0 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rss_mib | 96.582 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / rx_received | 601 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p50_ms | 46.9729 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / service_p99_ms | 60.2678 | not run | 2/3 | 0/0 |
| P1 / B0_idle / fifo / latest / source_generated | 601 | not run | 2/3 | 0/0 |
| P1 / B0_idle / latest / latest / aoi_peak_ms | 188.975 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / aoi_time_average_ms | 98.0681 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / bridge_overwritten | 0 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / cpu_percent | 47.991 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / delivery_max_ms | 88.9646 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / delivery_p50_ms | 47.5318 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / delivery_p99_ms | 61.7457 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / drops | 0 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / overflows | 0 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / rss_mib | 96.5859 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / rx_received | 602 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / service_p50_ms | 47.4159 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / service_p99_ms | 61.5532 | not run | 1/3 | 0/0 |
| P1 / B0_idle / latest / latest / source_generated | 602 | not run | 1/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_peak_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / bridge_overwritten | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / cpu_percent | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_max_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p50_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / drops | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / overflows | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rss_mib | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / rx_received | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p50_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / service_p99_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / fifo / latest / source_generated | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / aoi_peak_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / aoi_time_average_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / bridge_overwritten | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / cpu_percent | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / delivery_max_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / delivery_p50_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / delivery_p99_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / drops | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / overflows | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / rss_mib | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / rx_received | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / service_p50_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / service_p99_ms | failed: no valid runs | not run | 0/3 | 0/0 |
| P1 / B2_memrate_c23 / latest / latest / source_generated | failed: no valid runs | not run | 0/3 | 0/0 |

Trạng thái: not run.

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

