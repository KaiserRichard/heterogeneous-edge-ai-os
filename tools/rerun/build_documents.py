#!/usr/bin/env python3
"""Refresh additive document sections from retained comparison outputs; offline only."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START, END = '<!-- RERUN START -->', '<!-- RERUN END -->'


def refresh(compare=None):
    compare = Path(compare or os.environ.get('RERUN_COMPARE_DIR') or ROOT / 'results/2026-10-20_rerun/compare')
    summary = json.loads((compare / 'rerun_summary.json').read_text())
    # Preserve absent-condition reasons; an unmatched load is not a pending campaign.
    sections = {}
    name = None
    for line in (compare / 'rerun_compare_vi.md').read_text().splitlines():
        if line.startswith('## '):
            name = line[3:]
            sections[name] = {}
        elif line.startswith('| ') and name:
            cells = [x.strip() for x in line.strip('|').split('|')]
            if len(cells) == 5 and cells[0] != 'Phép đo / điều kiện':
                sections[name][cells[0]] = cells[1:]

    def row(exp, key, label):
        cells = sections.get(exp, {}).get(key)
        if cells is None:
            status = summary['experiments'].get(exp, {}).get('status', 'unavailable')
            return [label, '—', 'pending' if status.startswith('not run') else
                    (status if status.startswith('failed') else 'unavailable'), '0/0', '0/0']
        old, new, ov, nv = cells
        if old.startswith('not run'):
            old = '—'
        return [label, old, new, ov, nv]

    timer = []
    for profile in ('P0', 'P1'):
        for load, label in [('B0_idle', 'idle'), ('CPU_c23', 'CPU'), ('B1_stream_c2', 'stream'),
                            ('C1_cache2M_c2', 'cache'), ('B2_memrate_c23', 'memrate')]:
            timer.append(row('cyclic-' + profile, f'{profile}_{load} / p99_us', f'{profile} {label}'))
    safe = [row('E4', f'{f} / failsafe_local_p50_ms', f'{f} P50') for f in ('F1','F2','F3','F4','F5')]
    maximum = [row('E4', f'{f} / failsafe_local_max_ms', f'{f} max') for f in ('F1','F2','F3','F4','F5')]
    mapped = [row('E4', f'{f} / failsafe_mapped_p50_ms', f'{f} mapped P50') for f in ('F1','F2','F3','F4','F5')]
    analyzer = [row('LA', key, label) for key, label in [
        ('final HEARTBEAT / captures', 'Final HEARTBEAT'),
        ('matched_delta_us / min', 'Delta min (µs)'), ('matched_delta_us / max', 'Delta max (µs)'),
        ('F1 / marker_safe_min_ms', 'F1 marker min (ms)'), ('F1 / marker_safe_max_ms', 'F1 marker max (ms)'),
        ('F2 / marker_safe_min_ms', 'F2 marker min (ms)'), ('F2 / marker_safe_max_ms', 'F2 marker max (ms)'),
        ('F4 / marker_safe_min_ms', 'F4 marker min (ms)'), ('F4 / marker_safe_max_ms', 'F4 marker max (ms)')]]
    smoke = [row('PS1', key, label) for key, label in [
        ('bridge_sent', 'Bridge sent'), ('mcu_status', 'MCU status'), ('echo_accepted', 'Echo accepted'),
        ('done_to_send_us / p50', 'Done-to-send P50 (µs)'), ('done_to_send_us / p99', 'Done-to-send P99 (µs)'),
        ('done_to_send_us / max', 'Done-to-send max (µs)')]]
    pipeline = []
    for exp, load, inp, bridge, metric, label in [
        ('E1','B2_memrate_c23','fifo','latest','delivery_p99_ms','E1 memrate P99'),
        ('E2','B2_memrate_c23','fifo','latest','delivery_p99_ms','E2 P1 memrate P99'),
        ('E2','B1_stream_c2','fifo','latest','delivery_p99_ms','E2 P1 stream P99'),
        ('E3','B2_memrate_c23','fifo','latest','aoi_time_average_ms','E3 memrate latest AoI'),
        ('E3B','B2_memrate_c23','latest','latest','delivery_p99_ms','E3B input latest P99')]:
        profile = 'P0' if exp == 'E1' else 'P1'
        pipeline.append(row(exp, f'{profile} / {load} / {inp} / {bridge} / {metric}', label))

    def value(exp, key):
        cells = sections.get(exp, {}).get(key)
        try:
            return float(cells[1]) if cells else None
        except ValueError:
            return None

    def comparison(exp, a, b, en, vi):
        x, y = value(exp, a), value(exp, b)
        if x is None or y is None:
            return (f'{exp}: interpretation unavailable; paired evidence missing.',
                    f'{exp}: chưa đủ bằng chứng ghép cặp để diễn giải.')
        relation = '>' if x > y else ('<' if x < y else '=')
        return (f'{exp}: {en}: {x:g} {relation} {y:g} ms.',
                f'{exp}: {vi}: {x:g} {relation} {y:g} ms (bằng chứng đo).')

    interpretations = [
        comparison('E1', 'P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms',
                   'P0 / B0_idle / fifo / latest / delivery_p99_ms',
                   'memrate vs idle P99; contention reaches delivery',
                   'P99 tải memrate so với nhàn rỗi; tranh chấp làm chậm chuyển giao'),
        comparison('E2', 'P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms',
                   'P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms',
                   'memrate P0 vs P1 P99; tuning leaves backlog',
                   'P99 memrate P0 so với P1; tinh chỉnh vẫn để lại tồn đọng'),
        comparison('E3', 'P1 / B2_memrate_c23 / fifo / fifo / aoi_time_average_ms',
                   'P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms',
                   'bridge FIFO vs latest AoI; upstream backlog remains',
                   'AoI bridge FIFO so với latest; tồn đọng phía trước vẫn còn'),
        comparison('E3B', 'P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms',
                   'P1 / B2_memrate_c23 / latest / latest / delivery_p99_ms',
                   'input FIFO vs latest P99; freshness via replacement',
                   'P99 input FIFO so với latest; thay mẫu để giữ độ mới')]
    present = [exp for exp in ('E1', 'E2', 'E3', 'E3B')
               if any(value(exp, key) is not None for key in sections.get(exp, {}))]
    missing = [exp for exp in ('E1', 'E2', 'E3', 'E3B') if exp not in present]
    availability_en = ('Retained pipeline evidence: ' + ', '.join(present) + '.' if present
                       else 'No retained pipeline values available.')
    availability_vi = ('Bằng chứng pipeline hiện có: ' + ', '.join(present) + '.' if present
                       else 'Chưa có giá trị pipeline để trình bày.')
    if missing:
        availability_en += ' Missing parts: ' + ', '.join(missing) + '.'
        availability_vi += ' Phần còn thiếu: ' + ', '.join(missing) + '.'
    cache_key = 'P1 / C1_cache2M_c2 / fifo / latest / delivery_p99_ms'
    ranking_changed = (value('E2', 'P1 / B1_stream_c2 / fifo / latest / delivery_p99_ms') is not None
                       and value('E2', cache_key) is None
                       and cache_key in sections.get('E2', {}))
    ranking_en = ('E1 ranking changed: memrate + cache became memrate + stream; cache was not run in E2.'
                  if ranking_changed else 'E2 compares matching loads where available; absent cells retain their status.')
    ranking_vi = ('Xếp hạng E1 thay đổi: memrate + cache thành memrate + stream; cache không được chạy trong E2 lần này. Stream không có đối chứng E2 gốc; memrate được đối chiếu cùng điều kiện.'
                  if ranking_changed else 'E2 đối chiếu cùng điều kiện khi có dữ liệu; ô thiếu giữ trạng thái nguồn.')

    e3b_note = ('E3B mới có đối chứng input FIFO/latest hợp lệ riêng; không suy lợi ích từ các lượt tải gốc không hợp lệ.'
                if value('E3B', 'P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms') is not None
                and value('E3B', 'P1 / B2_memrate_c23 / latest / latest / delivery_p99_ms') is not None
                else 'E3B chưa đủ cặp dữ liệu tải hợp lệ để diễn giải lợi ích input-latest.')

    def md(rows):
        return '\n'.join(['| Phép đo / điều kiện | Gốc | Đo lại | Hợp lệ gốc | Hợp lệ đo lại |',
                          '|---|---|---|---|---|'] + ['| ' + ' | '.join(r) + ' |' for r in rows])

    def esc(s):
        for a, b in [('&', r'\&'), ('_', r'\_'), ('%', r'\%'), ('µ', r'\(\mu\)')]:
            s = s.replace(a, b)
        return s

    def tex(rows):
        return '\n'.join([r'{\small\begin{tabular}{@{}lllll@{}}\toprule',
            r'Metric & Original & Re-run & Old n/N & New n/N \\\midrule'] +
            [' & '.join(esc(c) for c in r) + r' \\' for r in rows] + [r'\bottomrule\end{tabular}}'])

    digest = (ROOT / 'results/2026-10-20_rerun/S1/firmware.sha256').read_text().split()[0]
    assert hashlib.sha256((ROOT / 'results/2026-10-20_rerun/S1/firmware.bin').read_bytes()).hexdigest() == digest
    frames = []
    def frame(title, body, scope, takeaway):
        frames.append(r'\begin{frame}[t]{Re-run 2026-10-20: ' + title + '}\n' + body + '\n' +
                      r'\scope{' + scope + '}\n' + r'\takeaway{' + takeaway + '}\n' + r'\end{frame}')

    frame('setup and evidence', r'''\evidence{MEASURED -- new dated evidence; original snapshot retained}
Pi 5, 4 GB; Ubuntu 24.04; kernel \texttt{6.8.0-1065-raspi}.\par
Nucleo-F446RE; S1: \texttt{st-flash} on Pi, write verified.\par\smallskip
Firmware SHA-256 (S1/firmware.sha256):\par
{\tiny\texttt{''' + digest[:32] + r'''}\par\texttt{''' + digest[32:] + r'''}}\par\medskip
Analyzer (fx2lafw) and ST-LINK now share the Pi's USB.\par
8 MHz capture on the system under test, pinned to CPU 3.\par\medskip
Cyclictest: 3\(\times\)60 s/cell; original: 3\(\times\)120 s/cell.''',
        r'Original dates: timer/PTY 11 Oct; E4/LA/E3B 12 Oct. New acceptance uses v2; original comparisons retain v1. Raw source: results/2026-10-20\_rerun.',
        'Changed kernel, duration and capture host limit direct attribution.')
    frame('cyclictest comparison', r'\evidence{MEASURED -- median per-run P99 (\(\mu\)s)}' + '\n' + tex(timer),
          'Original 2026-10-11 (v1); re-run 2026-10-20 (v2). P0 OTHER, P1 FIFO 50; 3 independent runs/cell. Shorter windows do not establish better worst-case tails.',
          'FIFO tails remain sensitive to shared memory contention.')
    frame('E4 comparison', r'\evidence{MEASURED -- MCU-local FAILSAFE P50 (ms)}' + '\n' + tex(safe) + r'''\par\medskip
Reason 3 (F1/F2/F4): last heartbeat; reason 10 (F3/F5): last inference.\par
Re-run F4 first transition: reason 3; old F4 mixes reasons 3/9.''',
          'Original 2026-10-12 includes short F4/F5 windows; new full campaign: 25/25 accepted. F4 original 7/14 = 2/5 full + 5/9 extra. Mapped onset timing is separate; full values in compare/E4\_mapped.tex and report.',
          'Compare matching reasons and references; these are observed timings.')
    frame('analyzer comparison', r'\evidence{MEASURED -- reference cross-check; no absolute calibration}' + '\n' + tex(analyzer[:3]) + r'''\par\medskip
\(\Delta=(\text{last UART byte end}\to\text{both GPIO low})\)\par
\(\phantom{\Delta={}}-(\text{last accepted HB}\to\text{FAILSAFE event})\).\par\medskip
8 MHz: nominal sample period 125 ns. Capture on Pi adds\par
USB/CPU activity to the system under test.''',
          'Original 2026-10-12: FLAGGED collection, 10/15 matching; re-run 15/15 matching final HEARTBEAT frames. Matching does not establish collection validity. Marker-to-safe ranges are separately tabulated in the report.',
          'The changed acquisition topology prevents attributing the residual shift.')
    frame('PS1 and pipeline', r'\evidence{MEASURED -- PS1 real UART; pipeline PTY evidence}' + '\n' +
          r'\begin{columns}[T]\begin{column}{0.49\textwidth}' + tex(smoke).replace(r'{\small', r'{\scriptsize') +
          r'\end{column}\begin{column}{0.49\textwidth}{\scriptsize ' +
          r'\par '.join(esc(r[0]) + ': ' +
                        (esc(r[1]) + r' $\to$ ' if exp == 'E2' and r[1] != '—' else '') + esc(r[2]) +
                        (' ms' if value(exp, key) is not None else '') + ' [' + r[4] + ']'
                        for r, (exp, key) in zip(pipeline, [
                            ('E1', 'P0 / B2_memrate_c23 / fifo / latest / delivery_p99_ms'),
                            ('E2', 'P1 / B2_memrate_c23 / fifo / latest / delivery_p99_ms'),
                            ('E2', 'P1 / B1_stream_c2 / fifo / latest / delivery_p99_ms'),
                            ('E3', 'P1 / B2_memrate_c23 / fifo / latest / aoi_time_average_ms'),
                            ('E3B', 'P1 / B2_memrate_c23 / latest / latest / delivery_p99_ms')])) +
          r'\par\smallskip ' + esc(ranking_en) + r'}\end{column}\end{columns}\par\smallskip{\scriptsize ' +
          r'\par '.join(esc(en) for en, vi in interpretations) + '}',
          'PS1 corrected STM32 TX to Pi pin 10; no original counterpart or physical E3 AoI. Pipeline values are per-condition medians, not bounds. Original loaded E3B had no valid runs; new evidence is separate.',
          availability_en)
    (ROOT / 'submission/defense/rerun_2026-10-20.tex').write_text('% Generated by tools/rerun/build_documents.py; do not hand-edit.\n' + '\n\n'.join(frames) + '\n')

    e4_records = summary['parts'].get('E4', {}).get('records', [])
    valid_e4 = [r for r in e4_records if r.get('validity') == 'VALID']
    recovery = sum(r.get('recovery_status') == 'observed' for r in valid_e4)
    censored = sum(r.get('failsafe_status') != 'observed' for r in valid_e4)
    false = sum(int(r.get('false_transitions') or 0) for r in valid_e4)
    text = f'''{START}
## 5.5 Đo lại ngày 20/10/2026

Đợt đo bổ sung dùng Raspberry Pi 5 RAM 4 GB, Ubuntu 24.04 với kernel 6.8.0-1065-raspi và Nucleo-F446RE. Firmware được nạp từ Pi bằng st-flash; log S1 xác nhận ghi và kiểm tra lại thành công. Mã SHA-256 của tệp nhị phân là {digest}. Các bảng dưới trình bày kết quả đo với số lượt hợp lệ theo kiểm tra gốc và kiểm tra bổ sung tương ứng. Dữ liệu gốc được giữ riêng. Các quan sát ngày 11/10 và 12/10 tiếp tục được diễn giải theo phạm vi thu thập ban đầu, kể cả những hạn chế về nguồn và theo dõi đã nêu ở các mục trước, thay vì gộp mẫu với đợt mới.

Bảng đo lại A. P99 cyclictest, đơn vị µs; trung vị phân vị giữa các lượt, gốc ngày 11/10/2026.
{md(timer)}

Cyclictest P0 dùng SCHED_OTHER, còn P1 dùng FIFO priority 50 với ba lần lặp cho mỗi điều kiện tải. Mỗi lượt mới kéo dài 60 s, bằng một nửa cửa sổ 120 s của đợt gốc trong mục 5.2. P1 vẫn chịu ảnh hưởng tải nhớ; khác biệt kernel và thời lượng chưa cho phép quy chênh lệch cho riêng scheduler. Kiểm tra gốc dùng quy tắc ban đầu, còn đợt mới yêu cầu độ phủ theo dõi và xác nhận tải. Giá trị quan sát không phải cận trên thời gian đáp ứng.

Bảng đo lại B. FAILSAFE MCU-local, đơn vị ms; gốc ngày 12/10/2026, P50 và cực đại quan sát.
{md(safe + maximum)}

Bảng đo lại C. P50 từ lúc tiêm lỗi tới FAILSAFE qua ánh xạ đồng hồ, đơn vị ms; gốc ngày 12/10/2026.
{md(mapped)}

F1, F2 và F4 đo FAILSAFE từ heartbeat cuối với mã nguyên nhân 3; F3 và F5 lấy inference cuối với mã 10. Đợt E4 mới có 25/25 lượt được chấp nhận trong chiến dịch đầy đủ, còn tập gốc ghép thêm cửa sổ ngắn F4/F5. Riêng F4 gốc gồm 2/5 lượt đầy đủ và 5/9 lượt bổ sung; chuyển đầu tiên trộn mã 3 với mã 9. Đợt mới có chuyển đầu tiên F4 theo mã 3, vì vậy không gộp các mốc tham chiếu để diễn giải. Thời gian ánh xạ từ lúc tiêm lỗi được tách khỏi thời gian MCU-local vì còn phụ thuộc phép khớp đồng hồ, trong khi MCU-local sử dụng mốc nhận heartbeat hoặc inference trên cùng bộ đếm của STM32. Có {recovery}/{len(valid_e4)} lượt hợp lệ quan sát phục hồi, {censored} lượt thiếu mốc FAILSAFE và {false} chuyển sai trong cửa sổ đã đo. Đây chưa phải giới hạn xác suất chuyển sai.

Bảng đo lại D. Đối chiếu logic analyzer, gốc ngày 12/10/2026; số lượt ở đây là capture phân tích được, chưa xác nhận toàn bộ điều kiện thu thập.
{md(analyzer)}

Logic analyzer dùng fx2lafw và ST-LINK cùng nối USB trên Pi; capture chạy ngay trên hệ thống được đo, ghim CPU 3. Tần số lấy mẫu là 8 MHz. Chu kỳ danh định 125 ns chưa được hiệu chuẩn tuyệt đối; delta lấy khoảng từ cuối byte UART tới khi cả hai GPIO xuống thấp trừ khoảng từ heartbeat được nhận tới sự kiện FAILSAFE. Chỉ các capture kết thúc bằng heartbeat phù hợp được dùng cho delta; mốc marker được giữ riêng trong bảng. Hoạt động USB và CPU của bộ thu là khác biệt phương pháp, chưa thể quy độ dịch delta cho firmware.

Bảng đo lại E. PS1 trên UART vật lý sau sửa dây; không có đối chứng PS1 gốc.
{md(smoke)}

Lần PS1 đầu không nhận byte nào từ STM32 vì jumper STM32-TX sang Pi được cắm nhầm chân; sau khi chuyển về chân vật lý 10 của Pi, nhóm chạy lại cửa sổ liên kết và giữ kết quả sau sửa dây. Echo nhận và chấp nhận đều là 62; các phân vị trong bảng đo từ hoàn tất inference tới gửi, không phải AoI xuyên miền. Tóm tắt thô vẫn giữ nhãn chưa kiểm chứng trên phần cứng; chấp nhận phân tích liên kết chưa chứng minh mọi thuộc tính firmware. S1 và PS1 bổ sung bằng chứng nạp và liên lạc, chưa xác nhận biên mất DMA, stack hoặc cận trễ truyền.

Bảng đo lại F. Kết quả đo E1–E3B trên PTY, đơn vị ms; gốc E1–E3 ngày 11/10, E3B ngày 12/10/2026.
{md(pipeline)}

{availability_vi} {ranking_vi} Bảng được tạo từ tệp đối chiếu theo tải, profile, chính sách đầu vào và bridge tương ứng. E3 trình bày AoI trung bình đã khởi tạo; E1, E2 và E3B trình bày P99 chuyển giao, nên các hàng có ý nghĩa khác nhau. Các lượt E3B gốc có tải không hợp lệ không được dùng làm đối chứng sạch cho lợi ích của input-latest. Thí nghiệm inference độc lập và so sánh chính sách E3 trên UART vật lý chưa được lặp lại trong bố cục này.
{chr(10).join(vi for en, vi in interpretations)}

Các diễn giải trên dùng bằng chứng PTY đo lại, không xác nhận AoI trên UART vật lý hoặc cận trễ. {e3b_note}
{END}

'''
    target = ROOT / 'report_vi/content.md'
    content = target.read_text()
    if START in content:
        content = content[:content.index(START)] + text + content[content.index(END) + len(END):].lstrip('\n')
    else:
        content = content.replace('# PHẦN 6.', text + '# PHẦN 6.', 1)
    target.write_text(content)
    sources = [compare / 'rerun_summary.json', compare / 'rerun_compare_vi.md',
               ROOT / 'results/2026-10-20_rerun/S1/firmware.sha256',
               ROOT / 'results/2026-10-20_rerun/S1/flash.log',
               ROOT / 'results/2026-10-20_rerun/PS1/link60_fixed/summary.json',
               ROOT / 'results/2026-10-20_rerun/PS1/link60_fixed/config.json',
               ROOT / 'results/2026-10-20_rerun/LA/F1/la_host.json']
    manifest = {str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p):
                hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (ROOT / 'submission/defense/qa/rerun_2026-10-20_sources.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print('Refreshed five rerun frames and report section 5.5 from', compare)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare', type=Path)
    refresh(parser.parse_args().compare)
