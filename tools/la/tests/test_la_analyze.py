import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('la', Path(__file__).parents[1]/'la_analyze.py')
la = importlib.util.module_from_spec(spec); spec.loader.exec_module(la)

class AnalyzeTests(unittest.TestCase):
    def trace(self):
        # One 0xff UART byte: start low, eight high bits, high stop bit.
        bit = 1/921600
        return [(0,(1,1,1,0)), (.001,(1,1,0,0)),
                (.001+bit,(1,1,1,0)), (.002,(1,1,1,1)),
                (.003,(0,1,1,1)), (.005,(0,0,1,1)), (.006,(0,0,1,0))]

    def test_byte_end_and_latency(self):
        r = la.analyze(self.trace())
        self.assertAlmostEqual(r['marker_safe_us'],3000)
        self.assertAlmostEqual(r['uart_safe_us'],4000-10/921600*1e6)
        self.assertAlmostEqual(r['uart_hold_us'],2000-10/921600*1e6)
        self.assertAlmostEqual(r['t_last_uart_activity_s'],.001+1/921600)

    def test_no_hold_direct_safe(self):
        rows = [r for r in self.trace() if r[0] != .003]
        self.assertIsNone(la.analyze(rows)['uart_hold_us'])

    def test_censored(self):
        self.assertIsNone(la.analyze(self.trace()[:4])['marker_safe_us'])

    def test_missing_marker(self):
        with self.assertRaises(ValueError): la.analyze(self.trace()[:3])

    def test_csv_and_vcd(self):
        with tempfile.TemporaryDirectory() as tmp:
            csvpath=Path(tmp)/'a.csv'; vcdpath=Path(tmp)/'a.vcd'
            with csvpath.open('w') as f:
                w=csv.writer(f); w.writerow(['time','D0','D1','D2','D3'])
                w.writerows((t,*p) for t,p in self.trace())
            lines=['$timescale\n1 ns\n$end']
            for i,code in enumerate('abcd'):
                lines.append(f'$var wire 1 {code} D{i} $end')
            lines.append('$enddefinitions $end')
            for t,p in self.trace():
                lines.append(f'#{round(t*1e9)}')
                lines.extend(f'{v}{code}' for v,code in zip(p,'abcd'))
            vcdpath.write_text('\n'.join(lines))
            for path in (csvpath,vcdpath):
                self.assertAlmostEqual(la.analyze(la.read_trace(path))['marker_safe_us'],3000)

    def test_mcu_comparison_and_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp); (run/'pipeline').mkdir()
            (run/'run.json').write_text(json.dumps({'marker_edges':[{'value':1,'software_bracket_ns':500}]}))
            path=run/'pipeline/state_events.csv'
            def write(loss):
                with path.open('w') as f:
                    w=csv.writer(f); w.writerow(['mcu_us','new','last_hb_mcu_us','lost_count'])
                    w.writerows([[100,'FRESH',90,0],[3000,'HOLD',1000,loss],[5000,'FAILSAFE',1000,loss]])
            write(0); r=la.analyze(self.trace(),run)
            self.assertEqual(r['mcu_safe_us'],4000)
            self.assertAlmostEqual(r['delta_safe_us'],-10/921600*1e6)
            write(1); self.assertIsNone(la.analyze(self.trace(),run)['mcu_safe_us'])

if __name__ == '__main__': unittest.main()
