"""Integration replay; temporary symlinks only, no acquisition or raw writes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_rerun as b


def hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for base in paths for p in base.rglob('*') if p.is_file()}


class ReplayTest(unittest.TestCase):
    def test_original_symlinks_and_missing(self):
        with tempfile.TemporaryDirectory(prefix='rerun-test-') as temp:
            base = Path(temp)
            root = base / 'raw'
            links = {
                'P1/cyclictest_p0': b.ORIGINAL['P0'],
                'P1/cyclictest_p1': b.ORIGINAL['P1'],
                'E123/e-onnx': b.ORIGINAL['E123'],
                'E4/e4-real': b.ORIGINAL['E4'],
                'LA/F1': b.ORIGINAL['LA'] / 'run_F1',
                'LA/F2': b.ORIGINAL['LA'] / 'run_F2',
                'LA/F4': b.ORIGINAL['LA'] / 'run_F4',
                # No original PS1 exists in the map. This is an explicitly
                # diagnostic physical-UART pipeline fixture, not an E3 replay.
                'PS1/link60_fixed': next((b.RES / '2026-10-12_e3_real_uart').glob('*/E3_REAL*/pipeline')),
            }
            before = hashes(set(links.values()) | {b.ORIGINAL['LA'] / 'check_F2'})
            for name, target in links.items():
                link = root / name
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(target, target_is_directory=True)
            result = b.build(root, base / 'full')
            self.assertEqual(result['parts']['P0']['valid'], 3)
            self.assertEqual(result['parts']['P1']['valid'], 3)
            self.assertEqual(result['parts']['E123']['total'], 45)
            self.assertEqual(result['parts']['E123']['valid'], 0)
            self.assertEqual(result['parts']['E4']['total'], 25)
            self.assertEqual(result['parts']['LA']['total'], 14)
            self.assertEqual(result['experiments']['LA']['original']['final HEARTBEAT / captures']['value'], 10)
            self.assertEqual(result['experiments']['E4']['original']['F1 / first_local_p50_ms']['value'], 175.317)
            # Re-run == original under the same *current* analyzer, rather
            # than comparing incompatible v1 and v2 acceptance populations.
            for k in ('P0', 'P1'):
                direct = [b.cyclic.summarize_run(p) for p in b.ORIGINAL[k].iterdir()
                          if p.is_dir() and b.cyclic.RUN_NAME.fullmatch(p.name)]
                self.assertEqual(result['experiments']['cyclic-' + k]['rerun'],
                                 b.timer_metrics(b.cyclic.aggregate_runs(direct)))
            direct = [b.pipeline.summarize_run(p.parent) for p in b.ORIGINAL['E123'].glob('E*/condition.json')]
            for exp in ('E1', 'E2', 'E3'):
                self.assertEqual(result['experiments'][exp]['rerun'],
                                 b.software_metrics(b.pipeline.aggregate(direct), exp))
            for r in json.loads((base / 'full/la/records.json').read_text()):
                supplied = next(row for row in b.rows(links['LA/' + r['batch']] / 'la_e4.csv')
                                if row['capture'] == Path(r['capture']).name)
                self.assertAlmostEqual(r['delta_safe_us'], float(supplied['delta_safe_us']), places=6)
            self.assertEqual(before, hashes(set(links.values()) | {b.ORIGINAL['LA'] / 'check_F2'}))
            self.assertEqual(result['plots']['status'], 'ok')
            self.assertTrue((base / 'full/images/E4.pdf').exists())
            for filename in ('rerun_summary.json', 'rerun_compare.tex', 'rerun_compare_vi.md'):
                self.assertTrue((base / 'full' / filename).stat().st_size)
            missing = base / 'partial'
            bad = missing / 'E4/e4-real/F1-r01'
            bad.mkdir(parents=True)
            (bad / 'run.json').write_text('{broken')
            # An intact sibling still gets analyzed after a corrupt run.
            (bad.parent / 'F2-r01').symlink_to(b.ORIGINAL['E4'] / 'F2-r01', target_is_directory=True)
            (missing / 'PS1/link60_fixed').mkdir(parents=True)
            (missing / 'PS1/link60_fixed/summary.json').write_text('{bad')
            with patch.object(b, 'plot_outputs', return_value='not run: test without matplotlib'):
                partial = b.build(missing, base / 'partial-out')
            self.assertEqual(partial['parts']['P0']['status'], 'not run')
            self.assertEqual(partial['parts']['E4']['total'], 2)
            self.assertTrue(partial['parts']['PS1']['status'].startswith('failed:'))
            self.assertIn('not run', (base / 'partial-out/rerun_compare_vi.md').read_text())
            self.assertEqual(before, hashes(set(links.values()) | {b.ORIGINAL['LA'] / 'check_F2'}))

    def test_output_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(ValueError):
                b.build(root, root / 'output')
            target = root / 'elsewhere'
            (root / 'P1').mkdir()
            target.mkdir()
            (root / 'P1/cyclictest_p0').symlink_to(target)
            with self.assertRaises(ValueError):
                b.build(root, target)


if __name__ == '__main__':
    unittest.main()
