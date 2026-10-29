"""Small POSIX UART client for the STM32 system bootloader (AN3155)."""
from __future__ import annotations

import os
import select
import termios
import time

ACK, NACK = 0x79, 0x1F
FLASH_BASE = 0x08000000


class BootloaderError(IOError):
    pass


class STM32Boot:
    def __init__(self, port: str, baud: int = 57600):
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        self._configure(baud)

    def close(self) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def _configure(self, baud: int) -> None:
        speed = getattr(termios, f"B{baud}", None)
        if speed is None:
            raise ValueError(f"unsupported baud rate: {baud}")
        attrs = termios.tcgetattr(self.fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL | termios.PARENB
        attrs[2] &= ~termios.PARODD
        attrs[3] = 0
        attrs[4] = speed
        attrs[5] = speed
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        termios.tcflush(self.fd, termios.TCIOFLUSH)

    def _write(self, data: bytes, timeout: float = 2.0) -> None:
        view = memoryview(data)
        end = time.monotonic() + timeout
        while view:
            left = end - time.monotonic()
            if left <= 0:
                raise BootloaderError("UART write timed out")
            _, ready, _ = select.select([], [self.fd], [], left)
            if not ready:
                raise BootloaderError("UART write timed out")
            count = os.write(self.fd, view)
            view = view[count:]

    def _read(self, count: int, timeout: float = 2.0) -> bytes:
        result = bytearray()
        end = time.monotonic() + timeout
        while len(result) < count:
            left = end - time.monotonic()
            if left <= 0:
                break
            ready, _, _ = select.select([self.fd], [], [], left)
            if not ready:
                break
            chunk = os.read(self.fd, count - len(result))
            if not chunk:
                continue
            result.extend(chunk)
        return bytes(result)

    def _ack(self, timeout: float = 2.0) -> None:
        reply = self._read(1, timeout)
        if reply != bytes([ACK]):
            label = "nothing" if not reply else f"0x{reply[0]:02x}"
            raise BootloaderError(f"expected ACK, got {label}")

    def _command(self, command: int, timeout: float = 2.0) -> None:
        self._write(bytes((command, command ^ 0xFF)))
        self._ack(timeout)

    def _address(self, address: int) -> None:
        raw = address.to_bytes(4, "big")
        check = raw[0] ^ raw[1] ^ raw[2] ^ raw[3]
        self._write(raw + bytes((check,)))
        self._ack()

    def sync(self, timeout: float = 10.0) -> None:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            termios.tcflush(self.fd, termios.TCIFLUSH)
            self._write(b"\x7f")
            reply = self._read(1, min(0.3, max(0.01, end - time.monotonic())))
            if reply == bytes([ACK]):
                return
            if reply == bytes([NACK]):
                continue
        raise BootloaderError("no bootloader ACK during sync")

    def get_id(self) -> int:
        self._command(0x02)
        raw = self._read(1)
        if len(raw) != 1:
            raise BootloaderError("short GET_ID response")
        body = self._read(raw[0] + 1)
        if len(body) != raw[0] + 1:
            raise BootloaderError("short GET_ID product id")
        self._ack()
        if len(body) < 2:
            raise BootloaderError("invalid GET_ID product id")
        return int.from_bytes(body[-2:], "big")

    def read_memory(self, address: int, count: int) -> bytes:
        if not 1 <= count <= 256:
            raise ValueError("READ_MEMORY count must be 1..256")
        self._command(0x11)
        self._address(address)
        n = count - 1
        self._write(bytes((n, n ^ 0xFF)))
        self._ack()
        data = self._read(count, timeout=5.0)
        if len(data) != count:
            raise BootloaderError(f"short read at {address:#x}: {len(data)} of {count}")
        return data

    def dump(self, address: int, count: int) -> bytes:
        out = bytearray()
        for offset in range(0, count, 256):
            size = min(256, count - offset)
            out.extend(self.read_memory(address + offset, size))
        return bytes(out)

    def erase_sectors(self, sectors: list[int]) -> None:
        if not sectors or any(not 0 <= n <= 11 for n in sectors):
            raise ValueError("invalid F446 sector list")
        self._command(0x44)
        payload = (len(sectors) - 1).to_bytes(2, "big") + bytes(sectors)
        check = 0
        for byte in payload:
            check ^= byte
        self._write(payload + bytes((check,)))
        self._ack(timeout=60.0)

    def write_memory(self, address: int, data: bytes) -> None:
        if not 1 <= len(data) <= 256:
            raise ValueError("WRITE_MEMORY count must be 1..256")
        self._command(0x31)
        self._address(address)
        checksum = len(data) - 1
        for byte in data:
            checksum ^= byte
        self._write(bytes((len(data) - 1,)) + data + bytes((checksum,)))
        self._ack(timeout=10.0)

    def go(self, address: int) -> None:
        self._command(0x21)
        self._address(address)
