import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import e_campaign


class CameraCommandTests(unittest.TestCase):
    def test_camera_command_has_expected_capture_and_placement_args(self):
        command = e_campaign.camera_command(
            '/repo/linux/camera/build/hea_cam', '/tmp/input.sock', '/tmp/frames.csv', 30,
            ['--cpu', '1', '--fifo-priority', '60', '--mlock'])
        self.assertEqual(command, [
            '/repo/linux/camera/build/hea_cam', '--backend', 'libcamera', '--width', '640',
            '--height', '480', '--fps', '30', '--shm', 'hea_cam', '--output',
            '/tmp/input.sock', '--csv', '/tmp/frames.csv', '--cpu', '1',
            '--fifo-priority', '60', '--mlock'])


if __name__ == '__main__':
    unittest.main()
