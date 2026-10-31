"""Synthetic campaign data only; these values are not Pi measurements."""
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import shutil
from types import SimpleNamespace
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'analysis'))
import e_summary
spec = importlib.util.spec_from_file_location('e_campaign', ROOT / 'tools/experiments/e_campaign.py')
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


def write_json(path, value):
    path.write_text(json.dumps(value))


def write_csv(path, fields, rows):
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(fields.split(','))
        writer.writerows(rows)


def fixture(root, experiment='E1', stressor='B0_idle', rep=1, ages=(100, 101, 150, 151), input_policy='fifo'):
    profile = 'P1' if experiment == 'E3B' else 'P0'
    run = root / f'{experiment}_{profile}_{stressor}_latest_{input_policy}_r{rep}'
    run.mkdir()
    p = run / 'pipeline'
    p.mkdir()
    write_json(run / 'condition.json', dict(experiment=experiment, profile=profile, stressor=stressor,
               policy='latest', input_policy=input_policy, repetition=rep, exact_load='synthetic_test_load'))
    for name in ('meta_before.json', 'meta_after.json'):
        write_json(run / name, {'throttled': '0x0'})
    write_json(run / 'execution.json', {'stressor_ok': True, 'settings_ok': True, 'monitor_ok': True})
    (run / 'exit_code').write_text('0')
    write_csv(run / 'thermal.csv', 't_pi_ns,timestamp,temp_millic,cpu0_khz,throttled,ext5v_v',
              [[1000000000, 1, 42000, 2400000, '0x0', 5.1], [2000000000, 1.5, 43000, 2400000, '0x0', 5.1]])
    write_csv(run / 'resources.csv', 'timestamp,cpu_percent,rss_mib', [[1, 20, 10], [2, 40, 12]])
    write_json(p / 'config.json', {'serial': None, 'period_ms': 100})
    source, infer, bridge, rx = [], [], [], []
    for i, age in enumerate(ages):
        ti = 1_000_000_000 + i * 200_000_000
        source.append([i, ti, 'sent'])
        infer.append([i, ti, ti + 10_000_000, 'sent'])
        bridge.append([i, i, ti, ti + 10_000_000, ti + 20_000_000])
        rx.append(['INFERENCE', i, i, ti, ti + 20_000_000, ti + age * 1_000_000, 20000, 1])
    write_csv(p / 'source.csv', 'frame_id,t_input_ns,status', source)
    write_csv(p / 'infer.csv', 'frame_id,t_input_ns,t_done_ns,status', infer)
    write_csv(p / 'bridge.csv', 'seq,frame_id,t_input_ns,t_done_ns,t_send_ns', bridge)
    write_csv(p / 'rx.csv', 'type,seq,frame_id,t_input_ns,t_send_ns,t_rx_ns,age_at_send_us,crc_ok', rx)
    (p / 'bridge.stderr.log').write_text(json.dumps({'overwritten': 2, 'dropped': 1, 'discarded_on_stop': 3}) + '\n')
    (p / 'window_start_ns').write_text('1000000000')
    (p / 'window_end_ns').write_text('2000000000')
    return run


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_strict_reception_deadlines_and_counts(self):
        result = e_summary.summarize_run(fixture(self.root))
        self.assertTrue(result['valid'], result['validity'])
        self.assertEqual((result['misses_100'], result['misses_150'], result['deadline_denominator']), (3, 1, 4))
        self.assertEqual(result['miss_rate_100'], .75)
        self.assertEqual(result['bridge_discarded_on_stop'], 3)
        self.assertEqual(result['drops'], 1)
        self.assertEqual(result['delivery_p99_ms'], 151)
        self.assertEqual(result['cpu_percent'], 30)
        self.assertEqual(result['rss_mib'], 12)
        self.assertAlmostEqual(result['uninitialized_seconds'], .1)

    def test_e3b_skips_are_separate_from_completions_and_input_policies_group_separately(self):
        fifo = fixture(self.root, experiment='E3B')
        latest = fixture(self.root, experiment='E3B', input_policy='latest')
        # Synthetic skips have no t_done_ns. They must not enter service samples.
        for run in (fifo, latest):
            with (run / 'pipeline/source.csv').open('a') as stream:
                stream.write('10,900000000,sent\n11,950000000,sent\n')
        with (latest / 'pipeline/infer.csv').open('a') as stream:
            stream.write('10,900000000,,skipped_stale\n11,950000000,,skipped_stale\n')
        result = e_summary.summarize_run(latest)
        self.assertTrue(result['valid'], result['validity'])
        self.assertEqual(result['infer_completed'], 4)
        self.assertEqual(result['infer_skipped_stale'], 2)
        self.assertEqual(result['service_p99_ms'], 10)
        self.assertEqual(result['infer_ipc_dropped'], 0)
        self.assertEqual(result['rx_received'], 4)
        self.assertEqual(result['end_to_end_missing'], 2)
        self.assertEqual((result['delivery_p50_ms'], result['delivery_p99_ms']), (101, 151))
        self.assertEqual((result['misses_100'], result['misses_150']), (3, 1))
        # Analytic held AoI: 100->301, 101->350, 150->351, 151->400 ms.
        self.assertAlmostEqual(result['aoi_time_average_ms'], 239.33333333333333)
        self.assertEqual(result['aoi_peak_ms'], 400)
        _, conditions = e_summary.write_summary(self.root)
        self.assertEqual(len(conditions), 2)
        self.assertEqual({r['input_policy'] for r in conditions}, {'fifo', 'latest'})
        with (self.root / 'summary/E3B_table.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        row = next(r for r in rows if r['Input policy'] == 'latest')
        self.assertEqual(row['Bridge policy'], 'latest')
        self.assertEqual(row['Reception AoI P50'], '101 ms')
        self.assertEqual(row['Reception AoI P99'], '151 ms')
        self.assertEqual(row['Skipped count'], '2')
        self.assertEqual(row['Deadline misses'], '3/1 of 4')
        self.assertEqual(row['Delivered count'], '4')
        (latest / 'exit_code').write_text('1')
        _, conditions = e_summary.write_summary(self.root)
        self.assertEqual(next(r for r in conditions if r['input_policy'] == 'latest')['valid_reps'], 0)
        self.assertIn(latest.name, (self.root / 'summary/excluded.csv').read_text())

    def test_historical_campaign_defaults_to_fifo_input(self):
        run = fixture(self.root)
        config = e_summary.read_json(run / 'condition.json')
        del config['input_policy']
        write_json(run / 'condition.json', config)
        result = e_summary.summarize_run(run)
        self.assertTrue(result['valid'])
        self.assertEqual(result['input_policy'], 'fifo')
        self.assertEqual(result['infer_skipped_stale'], 0)

    def test_transient_live_bits_excluded_even_with_clean_endpoints(self):
        run = fixture(self.root)
        text = (run / 'thermal.csv').read_text().replace('0x0', '0x1', 1)
        (run / 'thermal.csv').write_text(text)
        result = e_summary.summarize_run(run)
        self.assertFalse(result['valid'])
        self.assertIn('live', result['validity'])

    def test_old_sticky_allowed_new_sticky_rejected(self):
        run = fixture(self.root)
        for name in ('meta_before.json', 'meta_after.json'):
            write_json(run / name, {'throttled': '0x10000'})
        self.assertTrue(e_summary.summarize_run(run)['valid'])
        write_json(run / 'meta_after.json', {'throttled': '0x30000'})
        self.assertFalse(e_summary.summarize_run(run)['valid'])

    def test_incomplete_or_failed_evidence_excluded(self):
        for failure in ('telemetry', 'exit', 'settings', 'stress', 'data'):
            with self.subTest(failure=failure):
                run = fixture(self.root, rep=len(list(self.root.iterdir())) + 1)
                if failure == 'telemetry':
                    (run / 'thermal.csv').unlink()
                elif failure == 'exit':
                    (run / 'exit_code').write_text('1')
                elif failure == 'data':
                    (run / 'pipeline/infer.csv').unlink()
                else:
                    write_json(run / 'execution.json', {'stressor_ok': failure != 'stress', 'settings_ok': failure != 'settings', 'monitor_ok': True})
                self.assertFalse(e_summary.summarize_run(run)['valid'])

    def test_group_median_of_run_percentiles_and_exclusion_manifest(self):
        fixture(self.root, rep=1, ages=(30, 40))
        fixture(self.root, rep=2, ages=(50, 90))
        invalid = fixture(self.root, rep=3, ages=(1000,))
        (invalid / 'exit_code').write_text('1')
        runs, conditions = e_summary.write_summary(self.root)
        self.assertEqual(len(runs), 3)
        self.assertEqual(conditions[0]['valid_reps'], 2)
        self.assertEqual(conditions[0]['delivery_p50_ms'], 40)
        self.assertEqual(conditions[0]['delivery_p99_ms'], 65)
        self.assertEqual(conditions[0]['delivery_max_ms'], 90)
        self.assertIn(invalid.name, (self.root / 'summary/excluded.csv').read_text())
        self.assertTrue(invalid.exists())
        deck_columns = {
            'E1': ['Condition', 'Service latency', 'Delivery latency', 'CPU', 'RAM', 'Drops', 'Overflows', 'Exact load'],
            'E2': ['Profile', 'Service latency', 'Delivery latency', 'CPU', 'RAM', 'Drops', 'Overflows', 'Exact load'],
            'E3': ['Policy', 'Time-average AoI', 'Peak AoI', 'Age-violation time', 'Deadline misses',
                   'Generated count', 'Delivered count', 'Replaced count'],
        }
        for e, columns in deck_columns.items():
            with (self.root / f'summary/{e}_table.csv').open() as stream:
                self.assertEqual(next(csv.reader(stream)), columns)
            self.assertIn('\\toprule', (self.root / f'summary/{e}.tex').read_text())
            self.assertIn('MEASURED; software timestamps; pty link; no physical UART, no MCU',
                          (self.root / f'summary/{e}.tex').read_text())
            self.assertTrue((self.root / f'summary/{e}_per_run.tex').exists())
            self.assertTrue((self.root / f'summary/{e}_per_condition.tex').exists())

    def test_stressor_ranking_ignores_invalid_outliers(self):
        fixture(self.root, stressor='CPU_c23', ages=(20,))
        fixture(self.root, stressor='B1_stream_c2', ages=(40,))
        fixture(self.root, stressor='C1_cache2M_c2', ages=(60,))
        invalid = fixture(self.root, stressor='B2_memrate_c23', ages=(9000,))
        (invalid / 'exit_code').write_text('1')
        self.assertEqual(e_summary.worst_stressors(self.root), ['C1_cache2M_c2', 'B1_stream_c2'])

    def test_e2_e3_tables_contain_matched_conditions_and_denominators(self):
        fixture(self.root, experiment='E2', stressor='CPU_c23')
        fixture(self.root, experiment='E3', stressor='CPU_c23')
        e_summary.write_summary(self.root)
        with (self.root / 'summary/E3_table.csv').open() as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row['Deadline misses'], '3/1 of 4')
        self.assertEqual(row['Generated count'], '4')
        self.assertEqual(row['Delivered count'], '4')
        self.assertEqual(row['Replaced count'], '2')
        self.assertIn('initialized', row['Time-average AoI'])
        for experiment in ('E2', 'E3'):
            text = (self.root / f'summary/{experiment}.tex').read_text()
            self.assertIn(r'CPU\_c23', text)
            self.assertIn('valid reps 1/1', text)

    def test_held_aoi_stalls_final_tail_and_out_of_order_delivery(self):
        # Ages 20->40 ms then fresh reset to 10->70 ms, last interval ends at 100 ms.
        value = e_summary.held_age([(20_000_000, 0), (40_000_000, 30_000_000),
                                   (60_000_000, 10_000_000)], 0, 100_000_000)
        self.assertAlmostEqual(value['aoi_time_average_ms'], 37.5)
        self.assertEqual(value['aoi_peak_ms'], 70)
        self.assertEqual(value['uninitialized_seconds'], .02)
        stalled = e_summary.held_age([(20_000_000, 0)], 0, 200_000_000)
        self.assertAlmostEqual(stalled['violation_100_seconds'], .1)
        self.assertAlmostEqual(stalled['violation_150_seconds'], .05)
        empty = e_summary.held_age([], 0, 100_000_000)
        self.assertIsNone(empty['aoi_time_average_ms'])
        self.assertEqual(empty['uninitialized_seconds'], .1)


class RunnerTests(unittest.TestCase):
    def test_voltage_format_with_adc_channel_annotation(self):
        self.assertEqual(campaign.voltage_value('EXT5V_V volt(24)=5.12340000V'), '5.12340000')
        self.assertEqual(campaign.voltage_value('EXT5V_V=5.1V'), '5.1')
        self.assertEqual(campaign.voltage_value('unavailable'), '')

    def test_run_orchestration_preserves_evidence_and_selects_p1(self):
        # Real output files, fake process launches/metadata/monitor. Never sudo/load.
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            root = Path(temp)
            template = fixture(root)
            out = root / 'campaign'
            out.mkdir()
            commands = []

            class FakeProcess:
                pid = 12345

                def __init__(self, command, **kwargs):
                    commands.append(command)
                    self.returncode = None
                    if '--run-dir' in command:
                        dest = Path(command[command.index('--run-dir') + 1])
                        shutil.copytree(template / 'pipeline', dest)
                        self.returncode = 0

                def poll(self):
                    return self.returncode

                def wait(self, **kwargs):
                    return self.returncode

            def fake_stop(process, *args, **kwargs):
                process.returncode = 0

            def fake_monitor(run, stop, profile, evidence, errors):
                for name in ('thermal.csv', 'resources.csv'):
                    shutil.copyfile(template / name, run / name)
                evidence.append({n: dict(policy=1 if p else 0, priority=p, affinity=[cpu], locked_kib=12)
                                 for n, cpu, p in [('source', 1, 60), ('infer', 0, 0), ('bridge', 1, 70)]})
                stop.wait(2)

            args = SimpleNamespace(out=out, seconds=60, stage='stub', model=None, python='/synthetic/python')
            with patch.object(campaign, 'snapshot', side_effect=lambda p: write_json(p, {'throttled': '0x0'})), \
                    patch.object(campaign, 'monitor', side_effect=fake_monitor), \
                    patch.object(campaign.subprocess, 'Popen', side_effect=FakeProcess), \
                    patch.object(campaign.subprocess, 'run') as sudo, \
                    patch.object(campaign, 'stop_process', side_effect=fake_stop), \
                    patch.object(campaign.time, 'sleep'), \
                    patch.object(campaign.os, 'SCHED_FIFO', 1, create=True), \
                    patch.object(campaign.os, 'SCHED_OTHER', 0, create=True):
                campaign.execute_run(args, 'E2', ('P1', 'CPU_c23', 'latest', 1))
                campaign.execute_run(args, 'E3B', ('P1', 'B2_memrate_c23', 'fifo', 1))
                campaign.execute_run(args, 'E3B', ('P1', 'B2_memrate_c23', 'latest', 1))
            run = next(out.iterdir())
            self.assertEqual((run / 'validity').read_text().strip(), 'OK')
            self.assertEqual(len(commands), 9)
            self.assertEqual([c[2] for c in commands[:2]], ['2', '3'])
            pipeline_command = commands[2]
            self.assertEqual(pipeline_command[:3], ['sudo', '-n', 'env'])
            self.assertEqual(pipeline_command[pipeline_command.index('--source-priority') + 1], '60')
            self.assertEqual(pipeline_command[pipeline_command.index('--bridge-priority') + 1], '70')
            self.assertIn('--mlock', pipeline_command)
            self.assertNotIn('--infer-priority', pipeline_command)
            self.assertEqual(pipeline_command[pipeline_command.index('--input-policy') + 1], 'fifo')
            for index, policy in ((5, 'fifo'), (8, 'latest')):
                cmd = commands[index]
                self.assertEqual(cmd[cmd.index('--policy') + 1], 'latest')
                self.assertEqual(cmd[cmd.index('--input-policy') + 1], policy)
                self.assertEqual(cmd[cmd.index('--source-priority') + 1], '60')
                self.assertEqual(cmd[cmd.index('--bridge-priority') + 1], '70')
            for run in out.glob('E3B*'):
                condition = json.loads((run / 'condition.json').read_text())
                self.assertEqual(condition['policy'], 'latest')
                self.assertIn(condition['input_policy'], ('fifo', 'latest'))
            self.assertEqual(sudo.call_args.args[0][:4], ['sudo', '-n', 'chown', '-R'])

    def test_fixed_seed_matrix_and_independent_stress_cores(self):
        worst = ['B2_memrate_c23', 'CPU_c23']
        for experiment, count in [('E1', 15), ('E2', 18), ('E3', 12), ('E3B', 12)]:
            order = campaign.plan(experiment, 3, worst)
            self.assertEqual(len(order), count)
            self.assertEqual(order, campaign.plan(experiment, 3, worst))
            self.assertEqual(len(set(order)), count)
        self.assertEqual(set(campaign.plan('E3B', 1)), {
            ('P1', s, q, 1) for s in ('B0_idle', 'B2_memrate_c23') for q in ('fifo', 'latest')})
        commands = campaign.stress_commands('B2_memrate_c23')
        self.assertEqual([c[2] for c in commands], ['2', '3'])
        self.assertTrue(all('--memrate' in c and '--memrate-bytes' in c for c in commands))

    def test_actual_settings_verification(self):
        # No scheduler syscalls: synthetic observed /proc evidence.
        with patch.object(campaign.os, 'SCHED_FIFO', 1, create=True), patch.object(campaign.os, 'SCHED_OTHER', 0, create=True):
            evidence = {n: dict(policy=1 if p else 0, priority=p, affinity=[cpu], locked_kib=12)
                        for n, cpu, p in [('source', 1, 60), ('infer', 0, 0), ('bridge', 1, 70)]}
            self.assertTrue(campaign.settings_match(evidence, 'P1'))
            evidence['infer']['policy'] = 1
            self.assertFalse(campaign.settings_match(evidence, 'P1'))
            evidence['infer']['policy'] = 0
            evidence['bridge']['locked_kib'] = 0
            self.assertFalse(campaign.settings_match(evidence, 'P1'))

    def test_passwordless_sudo_failure_before_output_or_load(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            out = Path(temp) / 'new'
            with patch.object(sys, 'argv', ['e_campaign', 'ALL', str(out)]), \
                    patch.object(campaign.platform, 'system', return_value='Linux'), \
                    patch.object(campaign.shutil, 'which', return_value='/synthetic/bin'), \
                    patch.object(campaign.subprocess, 'run', return_value=MagicMock(returncode=1)) as run:
                self.assertEqual(campaign.main(), 2)
                run.assert_called_once_with(['sudo', '-n', 'true'])
                self.assertFalse(out.exists())

    def test_e3b_standalone_does_not_run_or_rank_e1(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            out = Path(temp) / 'new'
            with patch.object(sys, 'argv', ['e_campaign', 'E3B', str(out), '3']), \
                    patch.object(campaign.platform, 'system', return_value='Linux'), \
                    patch.object(campaign.shutil, 'which', return_value='/synthetic/bin'), \
                    patch.object(campaign.subprocess, 'run', return_value=MagicMock(returncode=0)), \
                    patch.object(campaign, 'capture', return_value='synthetic'), \
                    patch.object(campaign, 'execute_run') as execute, \
                    patch.object(e_summary, 'worst_stressors') as rank, \
                    patch.object(e_summary, 'write_summary', return_value=([{'valid': True}], [])), \
                    patch('builtins.print'):
                self.assertEqual(campaign.main(), 0)
                rank.assert_not_called()
                self.assertEqual(execute.call_count, 12)
                self.assertTrue(all(call.args[1] == 'E3B' for call in execute.call_args_list))
                self.assertFalse((out / 'E1_order.json').exists())


if __name__ == '__main__':
    unittest.main()

class MonitorRegressionTests(unittest.TestCase):
    def test_monitor_order_gap_and_full_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = fixture(Path(tmp))
            self.assertEqual(e_summary.validity(run), 'OK')
            fields = 't_pi_ns,timestamp,temp_millic,cpu0_khz,throttled,ext5v_v'
            for times in ([1000000000], [2000000000, 1000000000],
                          [1000000000, 1000000000, 2000000000],
                          [1000000000, 3000000000], [1100000000, 2000000000],
                          [1000000000, 1900000000]):
                write_csv(run / 'thermal.csv', fields,
                          [[t, 1, 42000, 2400000, '0x0', 5.1] for t in times])
                self.assertTrue(e_summary.validity(run).startswith('INVALID'), times)

    def test_cpu_uses_counter_collection_time_after_delayed_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            stop = MagicMock()
            stop.is_set.side_effect = [False, False, True]
            evidence = {name: {'pid': i} for i, name in enumerate(('source', 'infer', 'bridge'))}
            with patch.object(campaign, 'capture', return_value='throttled=0x0'), \
                 patch.object(campaign, 'read_sys', return_value='1'), \
                 patch.object(campaign, 'process_evidence', side_effect=[(evidence, 0, 1), (evidence, 100, 1)]), \
                 patch.object(campaign.os, 'sysconf', return_value=100), \
                 patch.object(campaign.time, 'monotonic', side_effect=[0, .8, .8, .5, 1.8, 1.8]), \
                 patch.object(campaign.time, 'CLOCK_MONOTONIC_RAW', 4, create=True):
                campaign.monitor_samples(Path(tmp), stop, [])
            with (Path(tmp) / 'resources.csv').open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(float(rows[1]['cpu_percent']), 100)
