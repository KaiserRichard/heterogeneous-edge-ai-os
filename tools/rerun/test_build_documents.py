"""Regression checks for available, unmatched, and missing pipeline evidence."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import build_documents


class DocumentTests(unittest.TestCase):
    def render(self, missing=False):
        source = build_documents.ROOT
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                'results/2026-10-20_rerun/S1/firmware.sha256',
                'results/2026-10-20_rerun/S1/firmware.bin',
                'results/2026-10-20_rerun/S1/flash.log',
                'results/2026-10-20_rerun/PS1/link60_fixed/summary.json',
                'results/2026-10-20_rerun/PS1/link60_fixed/config.json',
                'results/2026-10-20_rerun/LA/F1/la_host.json',
            ):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, target)
            compare = root / 'compare'
            shutil.copytree(source / 'results/2026-10-20_rerun/compare', compare)
            if missing:
                table = compare / 'rerun_compare_vi.md'
                text = table.read_text()
                begin, end = text.index('## E3\n'), text.index('## E3B\n')
                table.write_text(text[:begin] + text[end:])
                path = compare / 'rerun_summary.json'
                summary = json.loads(path.read_text())
                summary['experiments']['E3']['status'] = 'not run: missing part'
                path.write_text(json.dumps(summary))
            (root / 'submission/defense/qa').mkdir(parents=True)
            (root / 'report_vi').mkdir()
            (root / 'report_vi/content.md').write_text('<!-- RERUN START --><!-- RERUN END -->')
            with patch.object(build_documents, 'ROOT', root):
                build_documents.refresh(compare)
            return ((root / 'submission/defense/rerun_2026-10-20.tex').read_text(),
                    (root / 'report_vi/content.md').read_text())

    def test_complete_campaign_and_changed_ranking(self):
        tex, report = self.render()
        self.assertNotIn('pending', tex + report)
        self.assertIn('E2 P1 memrate P99: 12890.2 $\\to$ 8357.15 ms [3/3]', tex)
        self.assertIn('E2 P1 stream P99: 83.2902 ms [3/3]', tex)
        self.assertIn('cache was not run in E2', tex)
        self.assertIn('| E2 P1 stream P99 | — | 83.2902 | 0/0 | 3/3 |', report)
        self.assertIn('4698.46 > 225', tex)

    def test_missing_part_does_not_hide_available_parts(self):
        tex, report = self.render(missing=True)
        self.assertIn('Missing parts: E3.', tex)
        self.assertIn('E3: interpretation unavailable', tex)
        self.assertIn('E3 memrate latest AoI: pending [0/0]', tex)
        self.assertIn('E2 P1 stream P99: 83.2902 ms [3/3]', tex)
        self.assertNotIn('remain pending until available', tex)
        self.assertIn('Phần còn thiếu: E3.', report)


if __name__ == '__main__':
    unittest.main()
