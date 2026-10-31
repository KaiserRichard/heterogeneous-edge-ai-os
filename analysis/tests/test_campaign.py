"""Exercise campaign shell orchestration with fake Pi tools, never real sudo/load."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MOCK_TOOL = '''#!/usr/bin/env python3
import os
from pathlib import Path
import subprocess
import sys
import time
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if tool == 'uname':
    print('Linux' if args == ['-s'] else 'synthetic_kernel')
elif tool == 'hostname':
    print('synthetic_pi')
elif tool == 'vcgencmd':
    print('throttled=0x0')
elif tool == 'git':
    if args == ['rev-parse', 'HEAD']:
        print('synthetic_commit')
elif tool == 'cat':
    values = {'scaling_governor': 'performance', 'temp': '42000', 'scaling_cur_freq': '2400000'}
    value = values.get(Path(args[0]).name) if args else None
    if value is None:
        sys.exit(subprocess.call(['/bin/cat'] + args))
    print(value)
elif tool == 'cut':
    if '/proc/loadavg' in args:
        print('0.00 0.00 0.00')
    else:
        sys.exit(subprocess.call(['/usr/bin/cut'] + args))
elif tool == 'sleep':
    time.sleep(0.02)
elif tool == 'lscpu':
    print('synthetic_platform')
elif tool == 'sudo':
    with open(os.environ['MOCK_SUDO_LOG'], 'a') as handle:
        handle.write(' '.join(args) + '\\n')
    if args == ['-v']:
        sys.exit(0)
    if args[0] != '-n':
        sys.exit(2)
    os.execvp(args[1], args[1:])
elif tool == 'taskset':
    os.execvp(args[2], args[2:])
elif tool == 'stress-ng':
    if args == ['--version']:
        print('synthetic stress-ng')
    else:
        time.sleep(float(os.environ.get("MOCK_STRESS_SECONDS", "2")))
        sys.exit(int(os.environ.get('MOCK_STRESS_RC', '0')))
elif tool == 'cyclictest':
    if args == ['--version']:
        print('synthetic cyclictest')
    else:
        time.sleep(0.5)
        print(Path(os.environ['MOCK_HISTOGRAM']).read_text(), end='')
        print('synthetic stderr retained', file=sys.stderr)
        sys.exit(int(os.environ.get('MOCK_CYCLIC_RC', '0')))
else:
    sys.exit(2)
'''


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                 "campaign requires an unprivileged user")
class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for tool in ("uname", "hostname", "vcgencmd", "git", "cat", "cut", "sleep",
                     "lscpu", "sudo", "taskset", "stress-ng", "cyclictest"):
            path = self.bin / tool
            path.write_text(MOCK_TOOL, encoding="utf-8")
            path.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        MOCK_HISTOGRAM=str(Path(__file__).parent / "fixtures" / "cyclictest_hist.txt"),
                        MOCK_SUDO_LOG=str(self.root / "sudo.log"), COOLER="synthetic cooler")

    def campaign(self, profile="P0", **env):
        out = self.root / profile
        result = subprocess.run(["bash", str(ROOT / "tools/timing/cyclictest_campaign.sh"),
                                 profile, str(out), "1", "1"], cwd=ROOT,
                                env=dict(self.env, **env), capture_output=True, text=True, timeout=120)
        return out, result

    def test_both_profiles_capture_raw_and_select_policy(self):
        for profile in ("P0", "P1"):
            with self.subTest(profile=profile):
                out, result = self.campaign(profile)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((out / "DONE").exists())
                runs = sorted(out.glob("*_r1"))
                self.assertEqual(len(runs), 5)
                for run in runs:
                    before = json.loads((run / "meta_before.json").read_text())
                    self.assertEqual(before["profile"], profile)
                    self.assertEqual(before["cooler"], "synthetic cooler")
                    self.assertEqual(before["git_commit"], "synthetic_commit")
                    command = (run / "cyclictest_cmd.txt").read_text()
                    self.assertIn("sudo -n cyclictest --policy=other -m" if profile == "P0" else "sudo -n cyclictest --policy=fifo -p 50", command)
                    self.assertIn("-m -t1 -a 0", command)
                    self.assertIn("-D 1s", command)
                    self.assertIn("SYNTHETIC TEST DATA", (run / "cyclictest_hist.txt").read_text())
                    self.assertIn("synthetic stderr", (run / "cyclictest.err").read_text())
                    self.assertTrue((run / "meta_after.json").exists())
                    self.assertIn("0x0", (run / "thermal.csv").read_text())
                self.assertTrue((self.root / "sudo.log").exists())

    def test_failed_cyclictest_keeps_evidence_without_done_marker(self):
        out, result = self.campaign(MOCK_CYCLIC_RC="1")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((out / "DONE").exists())
        self.assertEqual((out / "B0_idle_r1/exit_code").read_text().strip(), "1")
        self.assertTrue((out / "B0_idle_r1/meta_after.json").exists())

    def test_failed_stressor_is_recorded(self):
        out, result = self.campaign(MOCK_STRESS_RC="1")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((out / "DONE").exists())
        self.assertEqual((out / "CPU_c23_r1/stress_exit_code").read_text().strip(), "1")

    def test_zero_exit_early_stressor_invalidates(self):
        out, result = self.campaign(MOCK_STRESS_SECONDS="0.15")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse((out / "DONE").exists())
        self.assertEqual((out / "CPU_c23_r1/stress_exit_code").read_text().strip(), "0")
        self.assertEqual((out / "CPU_c23_r1/stressor_alive").read_text().strip(), "0")

    def test_existing_campaign_refused(self):
        out = self.root / "P0"
        out.mkdir()
        (out / "sentinel").write_text("keep", encoding="utf-8")
        _, result = self.campaign()
        self.assertEqual(result.returncode, 2)
        self.assertEqual((out / "sentinel").read_text(), "keep")

    def test_invalid_arguments_fail_before_execution(self):
        script = str(ROOT / "tools/timing/cyclictest_campaign.sh")
        for arguments in (["P2", "unused"], ["P0", "unused", "0"],
                          ["P0", "unused", "1", "-1"]):
            result = subprocess.run(["bash", script] + arguments, cwd=ROOT,
                                    env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
