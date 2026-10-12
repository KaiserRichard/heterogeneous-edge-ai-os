#!/usr/bin/env python3
"""Summarize single-thread cyclictest -h -q campaigns using only the stdlib.

Percentiles use nearest ranks over ALL samples. Overflow latencies are unknown:
an affected percentile is blank, except rank N whose value is the reported max.
With overflow the mean comes from cyclictest's truncated integer Avg footer.
"""

import argparse
import csv
import json
import math
from pathlib import Path
import re
import statistics
import sys


RUN_FIELDS = [
    "condition", "run", "status", "reason", "samples", "overflows",
    "min_us", "avg_us", "avg_source", "p50_us", "p95_us", "p99_us",
    "p99_9_us", "max_us", "kernel", "governor", "max_temp_c", "throttled",
]
CONDITION_FIELDS = [
    "condition", "runs", "invalid_runs", "p50_us", "p95_us", "p99_us",
    "p99_9_us", "max_us", "kernel", "governor", "max_temp_c", "throttled",
]
RUN_NAME = re.compile(r"(.+)_r([1-9][0-9]*)$")
FOOTER = re.compile(r"^#\s*(Total|Min Latencies|Avg Latencies|Max Latencies|Histogram Overflows):\s*(.*)$")


def parse_histogram(path):
    """Parse one measured thread; reject incomplete or inconsistent captures."""
    bins = {}
    footers = {}
    in_histogram = False
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line == "# Histogram":
            if in_histogram or bins:
                raise ValueError("multiple histograms in one file")
            in_histogram = True
            continue
        match = FOOTER.match(line)
        if match:
            in_histogram = False
            key, raw = match.groups()
            if key in footers or not re.fullmatch(r"[0-9]+", raw):
                raise ValueError("expected one single-thread integer footer: " + key)
            footers[key] = int(raw)
        elif in_histogram and line and not line.startswith("#"):
            if not re.fullmatch(r"[0-9]+\s+[0-9]+", line):
                raise ValueError("expected latency and one thread count")
            latency, count = map(int, line.split())
            if latency in bins:
                raise ValueError("duplicate histogram bucket")
            bins[latency] = count
    if not bins or any(key not in footers for key in
                       ("Total", "Min Latencies", "Max Latencies", "Histogram Overflows")):
        raise ValueError("missing histogram or required footer")
    in_range = sum(bins.values())
    overflow = footers["Histogram Overflows"]
    samples = in_range + overflow
    if footers["Total"] != in_range or not samples:
        raise ValueError("inconsistent Total or empty sample set")
    occupied = sorted((latency, count) for latency, count in bins.items() if count)
    minimum = footers["Min Latencies"]
    maximum = footers["Max Latencies"]
    if minimum > maximum:
        raise ValueError("min exceeds max")
    if occupied and (occupied[0][0] != minimum or occupied[-1][0] > maximum):
        raise ValueError("histogram disagrees with min/max footer")
    if overflow:
        if maximum <= max(bins):
            raise ValueError("overflow without a max beyond the histogram")
        if not occupied and minimum <= max(bins):
            raise ValueError("overflow-only min inside the histogram")
        if "Avg Latencies" not in footers:
            raise ValueError("missing Avg Latencies for overflow mean")
        average = footers["Avg Latencies"]
        if not minimum <= average <= maximum:
            raise ValueError("average outside min/max")
        avg_source = "cyclictest_footer_truncated"
    else:
        if occupied[-1][0] != maximum:
            raise ValueError("histogram disagrees with max footer")
        average = sum(latency * count for latency, count in occupied) / samples
        avg_source = "histogram"

    def percentile(numerator, denominator):
        rank = (samples * numerator + denominator - 1) // denominator
        cumulative = 0
        for latency, count in occupied:
            cumulative += count
            if cumulative >= rank:
                return latency
        return maximum if rank == samples else None

    return dict(samples=samples, overflows=overflow, min_us=minimum,
                avg_us=average, avg_source=avg_source, max_us=maximum,
                p50_us=percentile(50, 100), p95_us=percentile(95, 100),
                p99_us=percentile(99, 100), p99_9_us=percentile(999, 1000))


# vcgencmd get_throttled: bits 0-3 are live (under-voltage, freq capped, throttled,
# soft temp limit); bits 16-19 are sticky "has occurred" flags kept until reboot.
# A run is INVALID if a live bit is ever sampled, or a new sticky bit appears between
# meta_before and meta_after (catches events shorter than the sampling interval).
LIVE_MASK = 0xF
STICKY_MASK = 0xF0000


def throttled_value(value):
    raw = str(value).strip().lower()
    if raw.startswith("throttled="):
        raw = raw.split("=", 1)[1]
    if not re.fullmatch(r"0x[0-9a-f]+|[0-9]+", raw):
        raise ValueError("missing or malformed throttled value: " + raw)
    return int(raw, 16 if raw.startswith("0x") else 10)


def summarize_run(directory):
    directory = Path(directory)
    condition, _ = RUN_NAME.fullmatch(directory.name).groups()
    row = dict(condition=condition, run=directory.name, status="VALID", reason="")
    reasons = []
    temperatures = []
    throttles = set()
    metadata = []

    def health(temp, throttle, source):
        try:
            value = throttled_value(throttle)
            throttles.add(value)
            if value & LIVE_MASK:
                reasons.append(source + ": live throttled=" + hex(value))
        except ValueError as error:
            reasons.append(source + ": " + str(error))
        try:
            value = float(temp) / 1000
            if not math.isfinite(value):
                raise ValueError("nonfinite temperature")
            temperatures.append(value)
        except (TypeError, ValueError):
            reasons.append(source + ": missing or malformed temperature")

    for name in ("meta_before.json", "meta_after.json"):
        try:
            data = json.loads((directory / name).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("metadata must be a JSON object")
            metadata.append(data)
            health(data.get("temp_millic"), data.get("throttled"), name)
        except (OSError, ValueError) as error:
            reasons.append(name + ": " + str(error))
    sticky = [throttled_value(d.get("throttled")) & STICKY_MASK for d in metadata
              if isinstance(d.get("throttled"), str) and d.get("throttled").startswith("0x")]
    if len(sticky) == 2 and sticky[1] & ~sticky[0]:
        reasons.append("new sticky throttle/under-voltage bits during run: " + hex(sticky[1] & ~sticky[0]))
    profiles = {data.get("profile") for data in metadata if data.get("profile")}
    if len(profiles) > 1:
        reasons.append("profile changed during run")
    if len(profiles) == 1:
        profile = next(iter(profiles))
        if not condition.startswith(str(profile) + "_"):
            row["condition"] = str(profile) + "_" + condition
    for key in ("kernel", "governor"):
        values = {str(data[key]) for data in metadata if data.get(key)}
        row[key] = ";".join(sorted(values)) or "unknown"
        if len(values) != 1 or len(metadata) != 2 or any(not data.get(key) for data in metadata):
            reasons.append(key + ": missing or changed during run")
    try:
        with (directory / "thermal.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        if rows and rows[0] and rows[0][0].strip() == "timestamp":
            if rows[0] != ["timestamp", "temp_millic", "cpu0_khz", "throttled"]:
                raise ValueError("unexpected thermal header")
            rows = rows[1:]
        if not rows:
            raise ValueError("empty thermal log")
        for number, values in enumerate(rows, 1):
            if len(values) != 4:
                reasons.append("thermal.csv: malformed row " + str(number))
                continue
            health(values[1], values[3], "thermal.csv row " + str(number))
    except (OSError, ValueError, csv.Error) as error:
        reasons.append("thermal.csv: " + str(error))
    for name in ("exit_code", "stress_exit_code"):
        path = directory / name
        if path.exists():
            try:
                if int(path.read_text(encoding="utf-8").strip()) != 0:
                    reasons.append(name + ": command failed")
            except (OSError, ValueError) as error:
                reasons.append(name + ": " + str(error))
    if condition in ('CPU_c23', 'B1_stream_c2', 'C1_cache2M_c2', 'B2_memrate_c23'):
        try:
            if (directory / "stressor_alive").read_text().strip() != "1":
                raise ValueError("stressor ended early during measurement")
            with (directory / "stress_liveness.csv").open(newline="") as stream:
                samples = list(csv.DictReader(stream))
            times = [float(sample["timestamp"]) for sample in samples]
            if (not samples or any(sample["alive"] != "1" for sample in samples)
                    or any(not math.isfinite(t) for t in times)
                    or any(b <= a or b - a > 1.5 for a, b in zip(times, times[1:]))):
                raise ValueError("invalid stressor liveness samples")
        except (OSError, ValueError, KeyError) as error:
            reasons.append("stressor liveness unavailable or failed: " + str(error))
    try:
        row.update(parse_histogram(directory / "cyclictest_hist.txt"))
    except (OSError, ValueError) as error:
        reasons.append("cyclictest_hist.txt: " + str(error))
    row["max_temp_c"] = max(temperatures) if temperatures else None
    row["throttled"] = ";".join(hex(value) for value in sorted(throttles)) or "unknown"
    if reasons:
        row.update(status="INVALID", reason="; ".join(dict.fromkeys(reasons)))
    return row


def aggregate_runs(rows):
    result = []
    for condition in sorted({row["condition"] for row in rows}):
        all_runs = [row for row in rows if row["condition"] == condition]
        valid = [row for row in all_runs if row["status"] == "VALID"]
        summary = dict(condition=condition, runs=len(valid),
                       invalid_runs=len(all_runs) - len(valid))
        for key in ("p50_us", "p95_us", "p99_us", "p99_9_us"):
            values = [row.get(key) for row in valid]
            summary[key] = statistics.median(values) if values and None not in values else None
        for key in ("max_us", "max_temp_c"):
            values = [row[key] for row in valid]
            summary[key] = max(values) if values else None
        for key in ("kernel", "governor", "throttled"):
            summary[key] = ";".join(sorted({row[key] for row in valid})) or "unknown"
        result.append(summary)
    return result


def latex_escape(value):
    escapes = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(escapes.get(char, char) for char in str(value))


def display(value):
    if value is None:
        return "--"
    if isinstance(value, float):
        return format(value, ".6g")
    return latex_escape(value)


def write_outputs(campaign, rows):
    aggregate = aggregate_runs(rows)
    for filename, fields, data in (("summary.csv", RUN_FIELDS, rows),
                                   ("summary_by_condition.csv", CONDITION_FIELDS, aggregate)):
        with (campaign / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    lines = [
        "% Requires \\usepackage{booktabs}. Latencies in microseconds.",
        "% VALID runs only; percentile columns are medians of per-run percentiles.",
        "% -- denotes unknown; overflow percentiles are never substituted with max.",
        r"\begin{tabular}{lrrrrllrl}", r"\toprule",
        r"condition & runs & P50 & P99 & max (us) & kernel & governor & max temp (C) & throttled \\",
        r"\midrule",
    ]
    fields = ("condition", "runs", "p50_us", "p99_us", "max_us", "kernel",
              "governor", "max_temp_c", "throttled")
    lines.extend(" & ".join(display(row[key]) for key in fields) + r" \\" for row in aggregate)
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (campaign / "summary_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path, help="directory containing condition_rN subdirectories")
    parser.add_argument("--outdir", type=Path)
    args = parser.parse_args(argv)
    if not args.campaign.is_dir():
        parser.error("campaign must be a directory")
    directories = sorted(path for path in args.campaign.iterdir()
                         if path.is_dir() and RUN_NAME.fullmatch(path.name))
    if not directories:
        parser.error("no condition_rN run directories found")
    rows = [summarize_run(directory) for directory in directories]
    dest = args.outdir or args.campaign
    dest.mkdir(parents=True, exist_ok=True)
    write_outputs(dest, rows)
    invalid = sum(row["status"] == "INVALID" for row in rows)
    print(f"Wrote summaries for {len(rows)} runs ({invalid} INVALID).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
