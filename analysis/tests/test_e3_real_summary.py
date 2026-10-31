import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis'))
sys.path.insert(0, str(ROOT / 'tools/experiments'))
import e3_real_summary as summary
import e3_real
import e3_startup
from unittest.mock import patch


def csv_write(path, records):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def fixture(root):
    run = root / 'E3_REAL_P1_B0_idle_input_fifo_bridge_fifo_r1'
    p = run / 'pipeline'
    p.mkdir(parents=True)
    def js(path, value):
        path.write_text(json.dumps(value))
    js(run / 'condition.json', dict(experiment='E3_REAL', profile='P1', stressor='B0_idle',
                                   input_policy='fifo', policy='fifo', repetition=1, exact_load='idle'))
    for phase in ('before', 'after'):
        js(run / f'meta_{phase}.json', dict(throttled='0x10000'))  # Existing sticky bit allowed.
    js(run / 'execution.json', dict(stressor_ok=True, monitor_ok=True, settings_ok=True))
    (run / 'exit_code').write_text('0\n')
    csv_write(run / 'thermal.csv', [dict(t_pi_ns=t, timestamp=t/1e9, throttled='0x10000',
        ext5v_v='5.1', temp_millic='40000', cpu0_khz='2400000')
        for t in (9900000000, 10400000000, 10900000000, 11400000000)])
    js(p / 'config.json', dict(serial='/dev/ttyAMA0', baud=921600, stage='onnx'))
    (p / 'window_start_ns').write_text('10000000000')
    (p / 'window_end_ns').write_text('11000000000')
    base = 3 * 2**32
    offset = base - 10000000
    csv_write(p / 'echo.csv', [dict(accepted=1, rms_residual_us=10, sample_count=3,
        t4_pi_ns=t, reference_pi_us=10000000, mapping_offset_us=offset, mapping_drift=0)
        for t in (10000000000, 10500000000, 11000000000)])
    csv_write(p / 'mcu_status.csv', [dict(state_event_lost=0)])
    times = (10000000000, 10050000000, 10149999000)
    receipts = (10100000000, 10200000000, 10300000000)
    csv_write(p / 'bridge.csv', [dict(seq=65534+i if i < 2 else 0, frame_id=i, t_input_ns=t)
                               for i, t in enumerate(times)])
    csv_write(p / 'inf_rx.csv', [dict(seq=65534+i if i < 2 else 0, frame_id=i, t_input_ns=t,
        mcu_rx_us=base+(rx-10000000000)//1000, t_mcu_pi_est_ns='', age_mcu_us=age,
        state=1, lost_count=0, aoi_mapped_us='', t_rx_pi_ns=rx+1000000)
        for i, (t, rx, age) in enumerate(zip(times, receipts, (100000,150000,150001)))])
    csv_write(p / 'state_events.csv', [dict(t_rx_pi_ns=stamp+1000000,
        mcu_us=base+(stamp-10000000000)//1000, old=old, new=new, lost_count=0)
        for stamp, old, new in ((10100000000,0,1),(10400000000,1,2),(10800000000,2,3))])
    csv_write(p / 'infer.csv', [dict(status=s) for s in ('sent','sent','sent','skipped_stale')])
    csv_write(p / 'source.csv', [dict(frame_id=i) for i in range(6)])
    (p / 'bridge.stderr.log').write_text(json.dumps(dict(overwritten=2, dropped=0)))
    return run


class RealSummaryTests(unittest.TestCase):
    def test_metrics_and_state_window(self):
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            r = summary.summarize_run(run)
            self.assertTrue(r['valid'], r['validity'])
            for prefix in ('mapped', 'mcu'):
                self.assertEqual(r[prefix+'_p50_us'], 150000)
                self.assertEqual(r[prefix+'_p99_us'], 150001)
                self.assertEqual(r[prefix+'_max_us'], 150001)
                self.assertEqual(r[prefix+'_misses_100'], 2)
                self.assertEqual(r[prefix+'_misses_150'], 1)
            self.assertEqual((r['delivered'],r['skipped'],r['overwritten']), (3,1,2))
            self.assertAlmostEqual(r['hold_seconds'], .4)
            self.assertAlmostEqual(r['failsafe_seconds'], .199)
            runs, conditions = summary.write_summary(Path(temp))
            self.assertEqual(conditions[0]['delivered'], 3)
            self.assertIn(summary.EVIDENCE, (Path(temp)/'summary/per_run.tex').read_text())

    def test_local_age_is_independent_of_clock_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            path = run / 'pipeline/inf_rx.csv'
            rows = summary.pipeline.rows(path)
            rows[-1]['age_mcu_us'] = 170001
            csv_write(path, rows)
            r = summary.summarize_run(run)
            self.assertTrue(r['valid'], r['validity'])
            self.assertEqual(r['mapped_max_us'], 150001)
            self.assertEqual(r['mcu_max_us'], 170001)

    def test_monitor_gap_and_uncovered_window(self):
        for timestamps in ((9900000000, 11000000000), (10100000000, 10600000000)):
            with self.subTest(timestamps=timestamps), tempfile.TemporaryDirectory() as temp:
                run = fixture(Path(temp))
                path = run / 'thermal.csv'
                rows = summary.pipeline.rows(path)[:2]
                for r, t in zip(rows, timestamps):
                    r['t_pi_ns'] = t
                csv_write(path, rows)
                self.assertFalse(summary.summarize_run(run)['valid'])

    def test_exclusions(self):
        cases = [('inf_rx.csv','lost_count',1), ('inf_rx.csv','frame_id',''),
                 ('inf_rx.csv','age_mcu_us','nan'), ('echo.csv','rms_residual_us',201),
                 ('state_events.csv','lost_count',1), ('state_events.csv','old',3),
                 ('echo.csv','accepted',0)]
        for filename, key, value in cases:
            with self.subTest(filename=filename,key=key), tempfile.TemporaryDirectory() as temp:
                run = fixture(Path(temp))
                path = run/'pipeline'/filename
                rows = summary.pipeline.rows(path)
                for r in rows:
                    r[key] = value
                csv_write(path, rows)
                self.assertFalse(summary.summarize_run(run)['valid'])

    def test_power_and_settings_exclusions(self):
        for key, value in [('throttled','0x10001'),('throttled','0x30000'),('ext5v_v','')]:
            with self.subTest(key=key,value=value), tempfile.TemporaryDirectory() as temp:
                run = fixture(Path(temp))
                path = run/'thermal.csv'
                rows = summary.pipeline.rows(path)
                rows[1][key] = value
                csv_write(path, rows)
                self.assertFalse(summary.summarize_run(run)['valid'])
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            (run/'execution.json').write_text('{"stressor_ok":true,"monitor_ok":true,"settings_ok":false}')
            self.assertFalse(summary.summarize_run(run)['valid'])

    def test_pooled_conditions_and_excluded_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = fixture(root)
            r = summary.summarize_run(run)
            invalid = dict(r, valid=False, mcu_valid=False, run='missing', validity='INVALID')
            group = summary.aggregate([r, r, invalid], root)[0]
            self.assertEqual((group['valid_reps'],group['total_reps']), (2,3))
            self.assertEqual((group['delivered'],group['mapped_misses_150']), (6,2))
            self.assertAlmostEqual(group['hold_seconds'], .8)

    def test_fresh_gate_and_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            (p / 'state_events.csv').write_text('t_rx_pi_ns,mcu_us,old,new,lost_count\n1,1,0,3,0\n')
            with self.assertRaises(TimeoutError):
                e3_startup.wait_fresh(p, .01)
            def publish(_):
                (p / 'state_events.csv').write_text('t_rx_pi_ns,mcu_us,old,new,lost_count\n2,2,0,1,0\n')
            with patch.object(e3_startup.time, 'sleep', side_effect=publish):
                event = e3_startup.wait_fresh(p, 1)
            self.assertEqual(event['new'], '1')
            self.assertTrue((p / 'fresh_start.json').is_file())

    def test_transition_free_fresh_window(self):
        with tempfile.TemporaryDirectory() as temp:
            run = fixture(Path(temp))
            p = run / 'pipeline'
            (p / 'fresh_start.json').write_text(json.dumps(dict(new=1, old=0,
                lost_count=0, t_rx_pi_ns=9900000000, mcu_us=9900000)))
            (p / 'state_events.csv').write_text('t_rx_pi_ns,mcu_us,old,new,lost_count\n')
            r = summary.summarize_run(run)
            self.assertTrue(r['mcu_valid'], r['mcu_validity'])
            self.assertEqual(r['fresh_seconds'], 1)
            self.assertEqual(r['failsafe_seconds'], 0)
            (p / 'fresh_start.json').unlink()
            self.assertFalse(summary.summarize_run(run)['mcu_valid'])

    def test_bad_or_missing_sync_preserves_local_metrics(self):
        for missing in (False, True):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                run = fixture(root)
                path = run / 'pipeline/echo.csv'
                rows = summary.pipeline.rows(path)
                for row in rows:
                    row['accepted'] = 0 if missing else 1
                    row['rms_residual_us'] = 201
                csv_write(path, rows)
                r = summary.summarize_run(run)
                self.assertTrue(r['mcu_valid'], r['mcu_validity'])
                self.assertFalse(r['mapped_valid'])
                self.assertEqual(r['mcu_max_us'], 150001)
                self.assertNotIn('mapped_max_us', r)
                self.assertAlmostEqual(r['hold_seconds'], .4)
                pooled = summary.aggregate([r], root)[0]
                self.assertEqual(pooled['mcu_valid_reps'], 1)
                self.assertEqual(pooled['mapped_valid_reps'], 0)
                self.assertEqual(pooled['mcu_max_us'], 150001)

    def test_model_ready_reset_bridge_source_gate_order(self):
        script = (ROOT / 'scripts/pi/run_pipeline.sh').read_text()
        stages = ['wait_ready "$ipc_dir/source.sock"', 'subprocess.run(command, check=True, timeout=15)',
                  'launch hea_bridge --serial', 'launch hea_source --output',
                  '"$repo/tools/experiments/e3_startup.py"', '> "$run/window_start_ns"']
        positions = [script.index(stage) for stage in stages]
        self.assertEqual(positions, sorted(positions))

    def test_plan(self):
        order = e3_real.plan(3)
        self.assertEqual(len(order),18)
        self.assertEqual(len(set(order)),18)
        self.assertEqual(order,e3_real.plan(3))
        self.assertEqual({(r[2],r[3]) for r in order}, {('fifo','fifo'),('fifo','latest'),('latest','latest')})


if __name__ == '__main__':
    unittest.main()
