#!/usr/bin/env python3
"""Back up, program, and verify an STM32F446RE over its ROM UART bootloader."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

from stm32boot import BootloaderError, FLASH_BASE, STM32Boot

FLASH_SIZE = 512 * 1024
PRODUCT_ID = 0x421
SECTORS = (16 * 1024, 16 * 1024, 16 * 1024, 16 * 1024,
           64 * 1024, 128 * 1024, 128 * 1024, 128 * 1024)


def sectors_for_size(size: int) -> list[int]:
    if not 0 < size <= FLASH_SIZE:
        raise ValueError(f"image must be between 1 and {FLASH_SIZE} bytes")
    end = size
    result, boundary = [], 0
    for sector, sector_size in enumerate(SECTORS):
        boundary += sector_size
        if end <= boundary:
            result.append(sector)
            return result
        result.append(sector)
    raise ValueError("image exceeds STM32F446RE flash")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyAMA0")
    parser.add_argument("--baud", type=int, default=57600)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true",
                        help="back up and validate the image without erasing or writing")
    parser.add_argument("--sync-seconds", type=float, default=180)
    return parser.parse_args(argv)


def run(args, boot_factory=STM32Boot, input_fn=input, out=sys.stdout):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", args.expect_sha256):
        raise ValueError("--expect-sha256 must be 64 hexadecimal characters")
    image = args.image.read_bytes()
    sectors = sectors_for_size(len(image))
    padded = image + b"\xff" * ((-len(image)) % 4)
    args.archive.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = args.archive / f"{stamp}-backup.bin"
    sums_path = args.archive / "SHA256SUMS"
    if backup_path.exists():
        raise FileExistsError(f"refusing to overwrite existing backup: {backup_path}")
    print("Hold BOOT0 high, press RESET, then release RESET.", file=out, flush=True)
    input_fn("Press Enter when ready to sync: ")
    with boot_factory(args.port, args.baud) as boot:
        boot.sync(args.sync_seconds)
        product_id = boot.get_id()
        if product_id != PRODUCT_ID:
            raise BootloaderError(f"wrong product id: 0x{product_id:03x}, expected 0x421")
        backup = boot.dump(FLASH_BASE, FLASH_SIZE)
        if len(backup) != FLASH_SIZE:
            raise BootloaderError(f"incomplete flash backup: {len(backup)} bytes")
        # Exclusive creation preserves every earlier backup even if timestamps collide.
        with backup_path.open("xb") as stream:
            stream.write(backup)
        backup_sha = hashlib.sha256(backup).hexdigest()
        with sums_path.open("a", encoding="ascii") as stream:
            stream.write(f"{backup_sha}  {backup_path.name}\n")
        image_sha = hashlib.sha256(image).hexdigest()
        expected = args.expect_sha256.lower()
        if image_sha != expected:
            raise ValueError(f"image SHA256 mismatch: got {image_sha}, expected {expected}")
        if args.dry_run:
            result = {"status": "dry-run", "product_id": f"0x{product_id:03x}",
                      "backup": str(backup_path), "backup_sha256": backup_sha,
                      "image_sha256": image_sha}
        else:
            boot.erase_sectors(sectors)
            for offset in range(0, len(padded), 256):
                boot.write_memory(FLASH_BASE + offset, padded[offset:offset + 256])
            readback = boot.dump(FLASH_BASE, len(padded))
            if readback != padded:
                raise BootloaderError("verify mismatch: read-back differs from image")
            print("Set BOOT0 low and press RESET to start the new image.", file=out, flush=True)
            result = {"status": "verified", "product_id": f"0x{product_id:03x}",
                      "backup": str(backup_path), "backup_sha256": backup_sha,
                      "image_sha256": image_sha, "bytes_written": len(image),
                      "sectors_erased": sectors}
    print(json.dumps(result, sort_keys=True), file=out, flush=True)
    return result


def main(argv=None):
    try:
        run(parse_args(argv))
        return 0
    except (OSError, ValueError, BootloaderError) as exc:
        print(f"nucleo_switch: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
