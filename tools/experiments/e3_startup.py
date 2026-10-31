"""Wait for explicit post-reset FRESH evidence before opening an E3 window."""
import csv
import json
import os
from pathlib import Path
import sys
import time


def wait_fresh(directory, timeout, pids=()):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for pid in pids:
            os.kill(pid, 0)
        path = directory / 'state_events.csv'
        if path.exists():
            lines = path.read_text().splitlines(keepends=True)
            if lines and not lines[-1].endswith('\n'):
                lines.pop()
            records = list(csv.DictReader(lines))
            if records and int(records[-1]['new']) == 1:
                if any(int(r['lost_count']) for r in records):
                    raise ValueError('STATE_EVENT loss during startup')
                event = records[-1]
                (directory / 'fresh_start.json').write_text(json.dumps(event))
                return event
        time.sleep(.05)
    raise TimeoutError('no FRESH STATE_EVENT before startup deadline')


if __name__ == '__main__':
    wait_fresh(Path(sys.argv[1]), float(sys.argv[2]), tuple(map(int, sys.argv[3:])))
