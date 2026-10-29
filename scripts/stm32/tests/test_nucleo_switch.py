import contextlib
import hashlib
import io
import os
from pathlib import Path
import pty
import select
import sys
import tempfile
import threading
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import nucleo_switch


class FakeROM:
    """Minimal AN3155 responder attached to a real pseudo-terminal."""
    def __init__(self, pid=0x421, fail_sync=False, fail_read=False,
                 corrupt_verify=False):
        self.master, self.slave = pty.openpty()
        self.port = os.ttyname(self.slave)
        self.memory = bytearray(b"\xA5" * nucleo_switch.FLASH_SIZE)
        self.pid = pid
        self.fail_sync = fail_sync
        self.fail_read = fail_read
        self.corrupt_verify = corrupt_verify
        self.erase_count = 0
        self.write_count = 0
        self.stop = threading.Event()
        self.pending = bytearray()
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def close(self):
        self.stop.set()
        self.thread.join(timeout=1)
        os.close(self.master)
        os.close(self.slave)

    def _exact(self, count):
        while len(self.pending) < count and not self.stop.is_set():
            ready, _, _ = select.select([self.master], [], [], 0.1)
            if not ready:
                continue
            try:
                chunk = os.read(self.master, 4096)
            except OSError:
                return b""
            self.pending.extend(chunk)
        data = bytes(self.pending[:count])
        del self.pending[:count]
        return data

    def _send(self, data):
        os.write(self.master, data)

    def _serve(self):
        while not self.stop.is_set():
            first = self._exact(1)
            if not first:
                continue
            if first == b"\x7f":
                if not self.fail_sync:
                    self._send(b"\x79")
                continue
            tail = self._exact(1)
            if not tail:
                return
            cmd = first[0]
            self._send(b"\x79")
            if cmd == 0x02:
                self._send(bytes((1,)) + self.pid.to_bytes(2, "big") + b"\x79")
            elif cmd in (0x11, 0x31, 0x21):
                raw = self._exact(5)
                if len(raw) != 5:
                    return
                address = int.from_bytes(raw[:4], "big")
                self._send(b"\x79")
                if cmd == 0x11:
                    size = self._exact(2)
                    if len(size) != 2:
                        return
                    count = size[0] + 1
                    self._send(b"\x79")
                    if self.fail_read:
                        continue
                    data = bytes(self.memory[address - nucleo_switch.FLASH_BASE:
                                             address - nucleo_switch.FLASH_BASE + count])
                    if self.corrupt_verify and self.write_count and address == nucleo_switch.FLASH_BASE:
                        data = bytes((data[0] ^ 1,)) + data[1:]
                    self._send(data)
                elif cmd == 0x31:
                    size = self._exact(1)
                    if not size:
                        return
                    count = size[0] + 1
                    data = self._exact(count + 1)
                    if len(data) != count + 1:
                        return
                    start = address - nucleo_switch.FLASH_BASE
                    self.memory[start:start + count] = data[:-1]
                    self.write_count += 1
                    self._send(b"\x79")
            elif cmd == 0x44:
                header = self._exact(2)
                if len(header) != 2:
                    return
                count = int.from_bytes(header, "big") + 1
                rest = self._exact(count + 1)
                if len(rest) != count + 1:
                    return
                self.erase_count += 1
                offset = 0
                sizes = nucleo_switch.SECTORS
                for sector in rest[:-1]:
                    start = sum(sizes[:sector])
                    self.memory[start:start + sizes[sector]] = b"\xff" * sizes[sector]
                self._send(b"\x79")


class SwitchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.image = self.root / "image.bin"
        self.image.write_bytes(bytes(range(256)) * 4)
        self.archive = self.root / "archive"

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, rom, expected=None, dry=False):
        digest = expected or hashlib.sha256(self.image.read_bytes()).hexdigest()
        args = nucleo_switch.parse_args([
            "--port", rom.port, "--image", str(self.image),
            "--expect-sha256", digest, "--archive", str(self.archive),
            "--sync-seconds", "0.2"] + (["--dry-run"] if dry else []))
        return nucleo_switch.run(args, input_fn=lambda _prompt: "", out=io.StringIO())

    def test_sync_failure(self):
        rom = FakeROM(fail_sync=True)
        try:
            with self.assertRaisesRegex(OSError, "sync"):
                self.execute(rom)
            self.assertEqual((rom.erase_count, rom.write_count), (0, 0))
        finally:
            rom.close()

    def test_wrong_product_id(self):
        rom = FakeROM(pid=0x444)
        try:
            with self.assertRaisesRegex(OSError, "wrong product"):
                self.execute(rom)
            self.assertEqual((rom.erase_count, rom.write_count), (0, 0))
        finally:
            rom.close()

    def test_read_failure_does_not_write(self):
        rom = FakeROM(fail_read=True)
        try:
            with self.assertRaisesRegex(OSError, "short read"):
                self.execute(rom)
            self.assertEqual((rom.erase_count, rom.write_count), (0, 0))
        finally:
            rom.close()

    def test_hash_mismatch_does_not_erase(self):
        rom = FakeROM()
        try:
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                self.execute(rom, expected="0" * 64)
            self.assertEqual((rom.erase_count, rom.write_count), (0, 0))
            self.assertEqual(len(next(self.archive.glob("*-backup.bin")).read_bytes()),
                             nucleo_switch.FLASH_SIZE)
        finally:
            rom.close()

    def test_write_and_verify_success(self):
        rom = FakeROM()
        try:
            result = self.execute(rom)
            self.assertEqual(result["status"], "verified")
            self.assertEqual((rom.erase_count, rom.write_count), (1, 4))
            self.assertEqual(rom.memory[:len(self.image.read_bytes())], self.image.read_bytes())
            self.assertEqual(result["sectors_erased"], [0])
        finally:
            rom.close()

    def test_verify_mismatch(self):
        rom = FakeROM(corrupt_verify=True)
        try:
            with self.assertRaisesRegex(OSError, "verify mismatch"):
                self.execute(rom)
            self.assertEqual((rom.erase_count, rom.write_count), (1, 4))
        finally:
            rom.close()


if __name__ == "__main__":
    unittest.main()
