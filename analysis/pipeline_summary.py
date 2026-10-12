#!/usr/bin/env python3
"""Summarize one pipeline run. Standard library only; times are in microseconds."""
import argparse
import csv
import json
import math
from pathlib import Path
import sys


def rows(path, required=True):
    if not path.exists() and not required:
        return None
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def indexed(records, label):
    result = {}
    for record in records:
        frame_id = int(record["frame_id"])
        if frame_id in result:
            raise ValueError(f"duplicate frame_id {frame_id} in {label}; use one run per directory")
        result[frame_id] = record
    return result


def distribution(values):
    ordered = sorted(values)
    if not ordered:
        return {"n": 0, "p50": None, "p95": None, "p99": None, "max": None}
    def percentile(p):
        return ordered[max(0, math.ceil(p * len(ordered)) - 1)]
    return {"n": len(ordered), "p50": percentile(.50), "p95": percentile(.95),
            "p99": percentile(.99), "max": ordered[-1]}


def stats(path):
    if not path.exists():
        return {}
    for line in reversed(path.read_text().splitlines()):
        if line.startswith("{"):
            return json.loads(line)
    return {}


def validity(run):
    snapshots = []
    for name in ("meta_before.json", "meta_after.json"):
        path = run / name
        if not path.exists():
            snapshots.append(None)
            continue
        value = json.loads(path.read_text()).get("throttled", "unavailable")
        if value in (None, "unavailable", "unknown"):
            snapshots.append(None)
        else:
            snapshots.append(int(str(value), 0))
    if any(value for value in snapshots):
        return "INVALID: throttling flagged in before/after metadata"
    if any(value is None for value in snapshots):
        return "UNKNOWN: throttling metadata unavailable"
    return "OK"


def summarize(run, state=None):
    state = validity(run) if state is None else state
    if state.startswith("INVALID"):
        return {"validity": state, "excluded": True}
    bridge = indexed(rows(run / "bridge.csv"), "bridge CSV")
    config_path = run / "config.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    if config.get("serial"):
        echoes = rows(run / "echo.csv", required=False) or []
        statuses = rows(run / "mcu_status.csv", required=False) or []
        return {"evidence": "real UART; UNVERIFIED ON HARDWARE", "validity": state,
                "excluded": False, "counts": {"bridge_sent": len(bridge),
                "mcu_status": len(statuses), "echo_received": len(echoes),
                "echo_accepted": sum(r["accepted"] == "1" for r in echoes)},
                "latency_us": {"done_to_send_us": distribution([
                    (int(r["t_send_ns"]) - int(r["t_done_ns"])) / 1000
                    for r in bridge.values()])},
                "aoi_scope": "MCU_STATUS does not identify inference reception; no cross-domain AoI inferred"}
    rx_records = rows(run / "rx.csv")
    rx = indexed([r for r in rx_records if r["type"] == "INFERENCE" and r["crc_ok"] == "1"], "rx CSV")
    source_records = rows(run / "source.csv", required=False)
    infer_records = rows(run / "infer.csv", required=False)
    source = indexed(source_records, "source CSV") if source_records is not None else None
    infer = indexed(infer_records, "inference CSV") if infer_records is not None else None
    # A skipped input has no completion; retain it for counts/identity only.
    completed = {k: r for k, r in infer.items() if r['status'] != 'skipped_stale'} if infer is not None else None
    metrics = {key: [] for key in ("input_to_done_us", "done_to_send_us", "send_to_rx_us", "aoi_at_reception_us")}
    inference_samples = completed if completed is not None else bridge
    for frame_id, record in inference_samples.items():
        ti, td = (int(record[k]) for k in ("t_input_ns", "t_done_ns"))
        if not 0 <= ti <= td:
            raise ValueError(f"clock regression in inference frame {frame_id}")
        metrics["input_to_done_us"].append((td - ti) / 1000)
    for frame_id, b in bridge.items():
        ti, td, ts = (int(b[k]) for k in ("t_input_ns", "t_done_ns", "t_send_ns"))
        if not 0 <= ti <= td <= ts:
            raise ValueError(f"clock regression in bridge frame {frame_id}")
        metrics["done_to_send_us"].append((ts - td) / 1000)
        if frame_id not in rx:
            continue
        r = rx[frame_id]
        if int(r["seq"]) != int(b["seq"]) or int(r["t_input_ns"]) != ti:
            raise ValueError(f"bridge/rx identity mismatch for frame {frame_id}")
        tr = int(r["t_rx_ns"])
        if tr < ts:
            raise ValueError(f"receiver clock regression for frame {frame_id}")
        age = min(0xFFFFFFFF, (ts - ti + 999) // 1000)
        if r["age_at_send_us"] and int(r["age_at_send_us"]) != age:
            raise ValueError(f"bridge/rx age mismatch for frame {frame_id}")
        # The rx t_send_ns field is rounded/reconstructed. Always use bridge ts.
        metrics["send_to_rx_us"].append((tr - ts) / 1000)
        metrics["aoi_at_reception_us"].append((tr - ti) / 1000)
    bridge_stats = stats(run / "bridge.stderr.log")
    counts = {
        "source_generated": len(source) if source is not None else None,
        "source_ipc_dropped": sum(r["status"] == "dropped" for r in source.values()) if source is not None else None,
        "infer_completed": len(completed) if completed is not None else None,
        "infer_skipped_stale": sum(r["status"] == "skipped_stale" for r in infer.values()) if infer is not None else None,
        "infer_ipc_dropped": sum(r["status"] == "dropped" for r in infer.values()) if infer is not None else None,
        "bridge_sent": len(bridge), "rx_received": len(rx),
        "joined": len(bridge.keys() & rx.keys()),
        "bridge_to_rx_missing": len(bridge.keys() - rx.keys()),
        "rx_without_bridge_log": len(rx.keys() - bridge.keys()),
        "end_to_end_missing": len(source.keys() - rx.keys()) if source is not None else None,
        "bridge_overwritten": bridge_stats.get("overwritten"),
        "bridge_queue_dropped": bridge_stats.get("dropped"),
        "bridge_discarded_on_stop": bridge_stats.get("discarded_on_stop"),
        "bridge_malformed": bridge_stats.get("malformed"),
        "rx_crc_errors": sum(r["crc_ok"] == "0" for r in rx_records),
    }
    return {"evidence": "MEASURED from software timestamps; no physical UART or MCU timing",
            "validity": state, "excluded": False, "counts": counts,
            "latency_us": {key: distribution(values) for key, values in metrics.items()},
            "percentiles": "nearest rank; inference uses all infer completions (bridge sends if infer CSV absent); dispatch uses bridge sends; transit/AoI use joined frames",
            "aoi_scope": "age at reception of each delivered frame; not time-average/peak held-value AoI"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        report = summarize(args.run_directory)
    except (OSError, ValueError, KeyError) as error:
        print(f"pipeline_summary: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
