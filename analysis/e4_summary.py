#!/usr/bin/env python3
"""E4 STATE_EVENT analysis, standard library only. All latencies are microseconds."""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import sys

EVIDENCE = "MEASURED (MCU timestamps + Pi timestamps, no logic analyzer)"
EVENT_COLUMNS = "seq,t_rx_pi_ns,mcu_us,old,new,reason,last_hb_mcu_us,last_inf_mcu_us,lost_count,t_mcu_pi_est_ns".split(",")
METRICS = ("detection_us", "detection_mcu_us", "failsafe_us", "failsafe_mcu_us", "recovery_us")
THRESHOLDS = ("heartbeat_timeout_us", "result_hold_us", "result_failsafe_us", "rearm_healthy_us", "transit_bound_us")


def timeout_kind(reason):
    """Compare a transition with the timer that caused it, not the injected fault."""
    return {"3": "heartbeat", "HEARTBEAT_TIMEOUT": "heartbeat",
            "2": "result_hold", "RESULT_SILENCE": "result_hold",
            "4": "result_failsafe", "RESULT_TIMEOUT": "result_failsafe",
            "9": "source_hold", "SOURCE_AGE_HOLD": "source_hold",
            "10": "source_failsafe", "SOURCE_AGE_TIMEOUT": "source_failsafe"}.get(
                str(reason).removeprefix("SUPERVISOR_REASON_"))


def read_csv(path, columns=()):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(columns) <= set(reader.fieldnames or []):
            raise ValueError(f"{path}: missing columns {set(columns) - set(reader.fieldnames or [])}")
        return list(reader)


def state(value):
    names = {"0": "INIT", "1": "FRESH", "2": "HOLD", "3": "FAILSAFE"}
    value = names.get(value, value.removeprefix("SUPERVISOR_STATE_"))
    if value not in names.values():
        raise ValueError(f"unknown supervisor state {value!r}")
    return value


def finite(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite timing value")
    return result


def clock_fits(directory):
    fits = []
    for row in read_csv(directory / "echo.csv"):
        if row["accepted"] != "1" or not row.get("rms_residual_us"):
            continue
        rms = finite(row["rms_residual_us"])
        if rms < 0:
            raise ValueError("negative clock residual")
        if int(row["sample_count"]) < 2:
            continue
        reference = int(row["reference_pi_us"])
        offset = finite(row["mapping_offset_us"])
        drift = finite(row["mapping_drift"])
        if 1 + drift <= 0:
            raise ValueError("non-positive clock slope")
        fits.append((int(row["t4_pi_ns"]), reference, offset, drift, rms))
    return sorted(fits)


def map_mcu(mcu_us, fit):
    _, reference, offset, drift, _ = fit
    # Same inverse affine estimator as hea_bridge; centre before scaling.
    return (reference + (mcu_us - reference - offset) / (1 + drift)) * 1000


def events(directory, fits, replay=False):
    result = []
    for row in read_csv(directory / "state_events.csv", EVENT_COLUMNS):
        mcu = int(row["mcu_us"])
        received = int(row["t_rx_pi_ns"])
        eligible = fits if replay else [fit for fit in fits if fit[0] <= received]
        fit = eligible[-1] if eligible else None
        mapped = row["t_mcu_pi_est_ns"]
        # A replay decoder's Pi epoch is unrelated to the original receipt.
        pi = finite(mapped) if mapped and finite(mapped) > 0 and not replay else None
        if pi is None and fit:
            pi = map_mcu(mcu, fit)
        result.append(dict(row, mcu_us=mcu, pi_ns=pi, old=state(row["old"]),
                           new=state(row["new"]), lost_count=int(row["lost_count"])))
    return result


def thresholds(path=None, include=None):
    values = {name: None for name in THRESHOLDS}
    if path:
        data = json.loads(Path(path).read_text())
        for name in THRESHOLDS:
            if name in data:
                value = finite(data[name])
                if value < 0:
                    raise ValueError(f"negative threshold {name}")
                values[name] = value
        return values, str(Path(path).resolve())
    # Read literal macros only: no guessed defaults or C expression evaluation.
    sources = []
    for header in sorted(Path(include).glob("*.h")):
        for name, literal in re.findall(r"^\s*#define\s+(?:HEA_|SUPERVISOR_)?([A-Z_]+_US)\s+(\d+)[uUlL]*\s*(?:/\*.*)?$", header.read_text(), re.M):
            key = name.lower()
            if key in values:
                value = int(literal)
                if values[key] is not None and values[key] != value:
                    raise ValueError(f"conflicting {key}; pass --thresholds")
                values[key] = value
                sources.append(str(header))
    return values, ";".join(sorted(set(sources))) or "UNKNOWN: no literal threshold macros in stm32/include; pass --thresholds"


def summarize_run(run, rms_bound=200):
    meta = json.loads((run / "run.json").read_text())
    report = dict(run=run.name, fault=meta["fault"], rep=meta["rep"], evidence=EVIDENCE,
                  validity="INVALID", reasons="", false_transitions=None,
                  clock_rms_max_us=None, detection_status="not_observed", failsafe_status="not_observed",
                  detection_reason="", failsafe_reason="", local_reference=("last_inf_mcu_us" if meta["fault"] in ("F3", "F5") else "last_hb_mcu_us"),
                  detection_reference="", failsafe_reference="",
                  recovery_status="not_observed", **{key: None for key in METRICS})
    if meta["status"] == "NOT_DONE":
        report.update(validity="NOT_DONE", evidence="NOT DONE", reasons=meta["reason"])
        return report
    errors = []
    if meta["status"] != "COMPLETE":
        errors.append(meta.get("reason", "run did not complete"))
    try:
        samples = read_csv(run / "power.csv", ("t_pi_ns", "throttled", "temp_millic"))
        if not samples or any(not r["throttled"] or not r["temp_millic"] for r in samples):
            errors.append("power/thermal monitor unavailable")
        else:
            baseline = int(samples[0]["throttled"], 0)
            if any(not 0 <= int(r["throttled"], 0) <= 0xFFFFFFFF for r in samples):
                errors.append("invalid throttle bitmask")
            for sample in samples:
                int(sample["temp_millic"])
            if any(int(r["throttled"], 0) & 0xF for r in samples):
                errors.append("live throttle bits")
            if any((int(r["throttled"], 0) & 0xF0000) & ~baseline for r in samples):
                errors.append("new sticky throttle bits")
            times = [int(r["t_pi_ns"]) for r in samples]
            if any(b <= a or b - a > 750_000_000 for a, b in zip(times, times[1:])):
                errors.append("power monitor gap exceeds 0.75 s")
            if times[0] > meta["steady_start_pi_ns"] or times[-1] < meta["recovery_observation_end_pi_ns"]:
                errors.append("power monitor does not cover measurement windows")
        fits = clock_fits(run / "pipeline")
        recovery_fits = clock_fits(run / "recovery")
        if not fits or not recovery_fits:
            errors.append("clock-sync fit unavailable")
        residuals = [f[-1] for f in fits + recovery_fits]
        report["clock_rms_max_us"] = max(residuals) if residuals else None
        if any(rms > rms_bound for rms in residuals):
            errors.append("clock-sync residual RMS exceeds bound")
        observed = events(run / "pipeline", fits)
        if (run / "capture/state_events.csv").exists():
            observed += events(run / "capture", fits, replay=True)
        recovered = events(run / "recovery", recovery_fits)
        if any(r["lost_count"] > 0 for r in observed + recovered):
            errors.append("STATE_EVENT lost_count > 0")
        if any(r["lost_count"] < 0 or r["mcu_us"] < 0 or int(r["t_rx_pi_ns"]) < 0 for r in observed + recovered):
            errors.append("negative STATE_EVENT counters/timestamps")
        if any(r["pi_ns"] is None for r in observed + recovered
               if r["mcu_us"] >= 0):
            # Initial startup events may predate the first fit; they are mapped
            # with the first fit below, within the same MCU epoch only.
            for records, mapping in ((observed, fits), (recovered, recovery_fits)):
                for row in records:
                    if row["pi_ns"] is None and mapping:
                        row["pi_ns"] = map_mcu(row["mcu_us"], mapping[0])
            if any(r["pi_ns"] is None for r in observed + recovered):
                errors.append("STATE_EVENT mapping unavailable")
        observed = sorted((r for r in observed if r["pi_ns"] is not None), key=lambda r: r["pi_ns"])
        for records in (observed, sorted(recovered, key=lambda r: r["pi_ns"] or 0)):
            if any(a["new"] != b["old"] or b["mcu_us"] < a["mcu_us"] for a, b in zip(records, records[1:])):
                errors.append("STATE_EVENT state/MCU timestamp discontinuity")
        start, onset = meta["steady_start_pi_ns"], meta["onset_pi_ns"]
        end = meta["observation_end_pi_ns"]
        report["false_transitions"] = sum(start <= r["pi_ns"] < onset and r["old"] != r["new"] for r in observed)
        if onset - start < 20_000_000_000:
            errors.append("steady window shorter than 20 s")
        if end - onset < 10_000_000_000:
            errors.append("observation window shorter than 10 s")
        initial = [r for r in observed if r["pi_ns"] <= start]
        if not initial or initial[-1]["new"] != "FRESH" or report["false_transitions"]:
            errors.append("steady phase was not continuously FRESH")
        affected = [r for r in observed if onset <= r["pi_ns"] <= end]
        detect = next((r for r in affected if r["old"] == "FRESH" and r["new"] != "FRESH"), None)
        failsafe = next((r for r in affected if r["new"] == "FAILSAFE" and r["old"] != "FAILSAFE"), None)
        local_field = "last_inf_mcu_us" if meta["fault"] in ("F3", "F5") else "last_hb_mcu_us"
        for prefix, row in (("detection", detect), ("failsafe", failsafe)):
            if row:
                report[prefix + "_us"] = (row["pi_ns"] - onset) / 1000
                kind = timeout_kind(row["reason"])
                reference = ("last_hb_mcu_us" if kind == "heartbeat" else
                             "last_inf_mcu_us" if kind else local_field)
                report[prefix + "_reference"] = reference
                local = row["mcu_us"] - int(row[reference])
                if local < 0:
                    errors.append("MCU-local clock regression")
                else:
                    report[prefix + "_mcu_us"] = local
                report[prefix + "_status"] = "observed"
                report[prefix + "_reason"] = row["reason"]
            else:
                report[prefix + "_status"] = "censored: no transition in 10 s"
        # STOP/hog may recover inside observation; latched FAILSAFE requires rearm.
        candidates = observed + recovered
        finish = meta["fault_end_pi_ns"]
        recovery = next((r for r in sorted(candidates, key=lambda r: r["pi_ns"] or 0)
                         if r["pi_ns"] is not None and finish <= r["pi_ns"] <= meta["recovery_observation_end_pi_ns"]
                         and r["new"] == "FRESH" and r["old"] != "FRESH"), None)
        if recovery:
            report["recovery_us"] = (recovery["pi_ns"] - finish) / 1000
            report["recovery_status"] = "observed" if detect else "restart FRESH; no fault transition observed"
            if detect is None:
                report["recovery_us"] = None
        else:
            report["recovery_status"] = "censored: no FRESH by recovery deadline"
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    report.update(validity="INVALID" if errors else "VALID", reasons="; ".join(errors))
    return report


def distribution(values):
    values = sorted(values)
    if not values:
        return (None, None, None)
    return values[math.ceil(len(values) * .5) - 1], values[math.ceil(len(values) * .95) - 1], values[-1]


def fault_table(reports, configured, source):
    table = []
    for fault in ("F1", "F2", "F3", "F4", "F5"):
        runs = [r for r in reports if r["fault"] == fault]
        valid = [r for r in runs if r["validity"] == "VALID"]
        for metric in METRICS:
            values = [r[metric] for r in valid if r[metric] is not None]
            p50, p95, maximum = distribution(values)
            key = None
            label = "not directly comparable"
            if metric in ("detection_mcu_us", "failsafe_mcu_us"):
                prefix = metric.split("_")[0]
                kinds = {timeout_kind(r[prefix + "_reason"]) for r in valid if r[metric] is not None}
                if len(kinds) == 1:
                    kind = next(iter(kinds))
                    key = {"heartbeat": "heartbeat_timeout_us", "result_hold": "result_hold_us",
                           "result_failsafe": "result_failsafe_us"}.get(kind)
                    if kind in ("source_hold", "source_failsafe"):
                        label = ("result_hold_us" if kind == "source_hold" else "result_failsafe_us") + " - age_at_send_us - transit_bound_us"
                elif len(kinds) > 1:
                    label = "mixed transition reasons; not directly comparable"
            threshold = configured.get(key) if key else None
            table.append(dict(fault=fault, metric=metric, evidence=EVIDENCE if valid else "NO VALID MEASUREMENTS",
                              n_runs=len(runs), n_valid=len(valid), n_samples=len(values),
                              n_invalid=sum(r["validity"] == "INVALID" for r in runs),
                              n_not_done=sum(r["validity"] == "NOT_DONE" for r in runs),
                              p50_us=p50, p95_us=p95, max_us=maximum,
                              threshold=key or label, threshold_us=threshold,
                              p50_minus_threshold_us=p50 - threshold if p50 is not None and threshold is not None else None,
                              threshold_source=source))
    return table


def write_csv(path, records):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def latex(table):
    def escape(value):
        specials = {"\\": r"\textbackslash{}", "_": r"\_", "%": r"\%", "&": r"\&", "#": r"\#", "{": r"\{", "}": r"\}", "$": r"\$"}
        return "".join(specials.get(character, character) for character in str(value))
    def number(value):
        return "--" if value is None else f"{value:.3f}"
    label = EVIDENCE if any(row["n_valid"] for row in table) else "NO VALID MEASUREMENTS"
    lines = ["% " + EVIDENCE, r"\begin{tabular}{llrrrrrlr}", r"\multicolumn{9}{l}{" + escape(label) + r"} \\", r"Fault & Metric & $n$ valid & $n$ samples & P50 ($\mu$s) & P95 ($\mu$s) & Max ($\mu$s) & Threshold & $\Delta$P50 ($\mu$s) \\", r"\hline"]
    for row in table:
        bound = row["threshold"] + ("=" + number(row["threshold_us"]) if row["threshold_us"] is not None else " (unknown/N.A.)")
        lines.append(" & ".join([row["fault"], escape(row["metric"]), str(row["n_valid"]), str(row["n_samples"]), number(row["p50_us"]), number(row["p95_us"]), number(row["max_us"]), escape(bound), number(row["p50_minus_threshold_us"])]) + r" \\")
    return "\n".join(lines + [r"\end{tabular}", ""])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--thresholds", type=Path, help="JSON with *_us threshold keys")
    parser.add_argument("--rms-bound-us", type=float, help="default: campaign setting, otherwise 200")
    parser.add_argument("--include", type=Path, default=Path(__file__).resolve().parents[1] / "stm32/include")
    args = parser.parse_args()
    try:
        if args.rms_bound_us is None:
            manifest = args.campaign / "campaign.json"
            args.rms_bound_us = finite(json.loads(manifest.read_text()).get("rms_bound_us", 200)) if manifest.exists() else 200
        if args.thresholds is None and (args.campaign / "supervisor_thresholds.json").exists():
            args.thresholds = args.campaign / "supervisor_thresholds.json"
        if not math.isfinite(args.rms_bound_us) or args.rms_bound_us <= 0:
            raise ValueError("RMS bound must be finite and positive")
        configured, source = thresholds(args.thresholds, args.include)
        reports = [summarize_run(p.parent, args.rms_bound_us) for p in sorted(args.campaign.glob("F*/run.json"))]
        if not reports:
            raise ValueError("no F*/run.json directories")
        table = fault_table(reports, configured, source)
        write_csv(args.campaign / "e4_runs.csv", reports)
        write_csv(args.campaign / "e4_faults.csv", table)
        (args.campaign / "e4_faults.tex").write_text(latex(table))
        (args.campaign / "e4_thresholds.json").write_text(json.dumps(dict(values=configured, source=source), indent=2) + "\n")
        print(f"{EVIDENCE}: {sum(r['validity'] == 'VALID' for r in reports)}/{len(reports)} valid runs; {args.campaign}/e4_{{runs,faults}}.csv, e4_faults.tex")
    except (OSError, ValueError, KeyError) as error:
        print(f"e4_summary: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
