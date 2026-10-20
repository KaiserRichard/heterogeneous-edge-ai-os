# Command companion

All commands start at the repository root. Target labels are binding; Pi commands are not macOS programs. New output directories must not exist. Set MODEL to the transferred ONNX file and BRIDGE_PID to the recorded owned bridge PID. These are documented commands, not commands executed during deck repair.

## Tools | Pi provisioning and individual runs

**Provision Pi (Linux; changes system)**

```sh
sudo bash scripts/pi/bootstrap.sh
```

Installs packages/configures UART; record applied system state.

**Metadata snapshot (Pi)**

```sh
bash scripts/pi/collect_metadata.sh > meta.json
```

Writes platform, power and revision metadata to meta.json.

**Detached command wrapper (Pi)**

```sh
bash scripts/pi/run_experiment.sh check -- /usr/bin/true
```

experiments/runs/<UTC>_check/: metadata, logs, exit_code, validity, DONE.

## Tools | pipeline and controlled faults

**Single PTY pipeline (Pi)**

```sh
bash scripts/pi/run_pipeline.sh --duration 60 --run-dir /tmp/pipe
```

/tmp/pipe/: config, CSV timestamps, counters and logs; stub by default.

**Stop bridge briefly (Pi; substitute its recorded PID)**

```sh
bash scripts/pi/fault_inject.sh stop "$BRIDGE_PID" 1000 2 /tmp/fault.csv
```

/tmp/fault.csv onset; stop/continue target process only.

**GPIO sync helper (Pi)**

```sh
python3 scripts/pi/uart_tools.py gpio 17 /tmp/sync.csv
```

/tmp/sync.csv RAW markers; Ctrl-C ends. fault mode is used by wrapper.

## Tools | software and timing campaigns

**E1/E2/E3/E3B (Pi)**

```sh
bash tools/experiments/e_campaign.sh ALL /tmp/e 3 60 --stage onnx --model "$MODEL"
```

/tmp/e/: per-run pipeline/monitor/settings, validity; summary/. ALL follows runner cells.

**Timing profile (Pi)**

```sh
bash tools/timing/cyclictest_campaign.sh P0 /tmp/cyc 3 120
```

/tmp/cyc/: histogram, thread policy, power/liveness and summary; repeat with P1/new directory.

**Python entry point behind shell wrapper**

```sh
python3 tools/experiments/e_campaign.py E3B /tmp/e3b 3 60 --stage onnx --model "$MODEL"
```

/tmp/e3b/: input-policy campaign. MODEL is an existing offline ONNX model.

## Tools | physical campaigns and startup

Prerequisite: complete [REARM_SETUP.md](REARM_SETUP.md), including SSH, reset and post-reset FRESH verification.

**Real-UART E3 (Pi; Mac reset helper required)**

```sh
bash tools/experiments/e3_real.sh /tmp/e3real 3 60 --model "$MODEL" --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"
```

/tmp/e3real/: per-cell pipeline + validity + summary. Wrapper invokes e3_real.py with same arguments.

**E4 single stale-data trial (Pi)**

```sh
bash tools/experiments/e4_campaign.sh /tmp/f5 1 --single F5 --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"
```

/tmp/f5/F5-r01/: power, fault/run JSON and pipeline; e4_campaign.py accepts identical arguments.

**Startup helper (Pi; usually called by pipeline)**

```sh
python3 tools/experiments/e3_startup.py /tmp/e3real/run/pipeline 30
```

Waits for post-reset FRESH event; writes fresh_start.json, errors on timeout/loss.

## Tools | Mac flashing and analyzer

**Flash/reset ST-LINK (Mac with tools installed)**

```sh
bash scripts/stm32/flash.sh openocd
```

Verifies stm32/firmware/build/firmware.elf and resets. reset.sh: bash scripts/stm32/reset.sh; no output file.

**Capture fault with FX2 (Mac)**

```sh
bash tools/la/la_e4.sh /tmp/la 5 F2
```

/tmp/la/: capture.sr/VCD, Pi logs, la_e4.csv/tex and optional timing PNG. Needs Mac-owned ST-LINK with `st-flash`, FX2/sigrok, Mac-to-Pi SSH and confirmed `LA_PI` / `LA_PI_REPO` deployment values. The runner resets locally with `st-flash reset`, then invokes the Pi campaign with `--rearm-command true`. Pi campaigns on page 19 retain the Pi-to-Mac reset-helper prerequisite.

**Analyze retained/new capture copies (Mac)**

```sh
python3 tools/la/la_analyze.py /tmp/la
```

/tmp/la/: comparisons and optional PNG. Analyze a copied capture tree to preserve originals.

## Tools | analysis entry points

**One pipeline JSON report**

```sh
python3 analysis/pipeline_summary.py /tmp/pipe > /tmp/pipe-summary.json
```

Reception age/latency distributions; not time-average held-value AoI.

**E campaign and cyclictest summaries**

```sh
python3 analysis/e_summary.py /tmp/e --outdir /tmp/e-summary
```

CSV/TeX + README in /tmp/e-summary. Timing: python3 analysis/cyclictest_summary.py /tmp/cyc --outdir /tmp/cyc-summary

**Physical E4 and real-E3 summaries**

```sh
python3 analysis/e4_summary.py /tmp/f5 --outdir /tmp/f5-summary
```

Fault CSV/TeX in /tmp/f5-summary. Real E3: python3 analysis/e3_real_summary.py /tmp/e3real → campaign/summary/.

## Explicit alternate entry points

The shell wrappers use these same Python entry points:

```sh
python3 tools/experiments/e3_real.py /tmp/e3real 3 60 --model "$MODEL" --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"
python3 tools/experiments/e4_campaign.py /tmp/f5 1 --single F5 --rearm-command "bash /home/richard/osbuild/rearm_via_mac.sh"
python3 analysis/cyclictest_summary.py /tmp/cyc --outdir /tmp/cyc-summary
python3 analysis/e3_real_summary.py /tmp/e3real
bash scripts/stm32/reset.sh
```

Real E3 writes campaign/summary; cyclictest writes /tmp/cyc-summary; reset produces console output only. `scripts/pi/uart_tools.py fault stop "$BRIDGE_PID" 1000 2 /tmp/fault.csv` is the Python entry point used by fault_inject.sh; GPIO helper output is /tmp/sync.csv.

## Regression test scripts

These are verification programs, rather than experiment runners. Each command writes test results to the terminal and returns a failure status if a check fails. Linux integration/ABI tests require Linux binaries; use the Pi for the full suite.

| Script | Purpose | Exact command |
|---|---|---|
| `analysis/tests/test_campaign.py` | campaign regression checks | `python3 -m unittest discover -s analysis/tests -p test_campaign.py -v` |
| `analysis/tests/test_cyclictest_summary.py` | cyclictest summary regression checks | `python3 -m unittest discover -s analysis/tests -p test_cyclictest_summary.py -v` |
| `analysis/tests/test_e3_real_summary.py` | e3 real summary regression checks | `python3 -m unittest discover -s analysis/tests -p test_e3_real_summary.py -v` |
| `analysis/tests/test_e4_summary.py` | e4 summary regression checks | `python3 -m unittest discover -s analysis/tests -p test_e4_summary.py -v` |
| `analysis/tests/test_e_summary.py` | e summary regression checks | `python3 -m unittest discover -s analysis/tests -p test_e_summary.py -v` |
| `analysis/tests/test_run_experiment.py` | run experiment regression checks | `python3 -m unittest discover -s analysis/tests -p test_run_experiment.py -v` |
| `tools/la/tests/test_la_analyze.py` | la analyze regression checks | `python3 -m unittest discover -s tools/la/tests -p test_la_analyze.py -v` |
| `tools/la/tests/test_la_runner.py` | la runner regression checks | `python3 -m unittest discover -s tools/la/tests -p test_la_runner.py -v` |

Provisioning prerequisite: `bootstrap.sh` requires reachable apt package sources. Git bundles and wheels alone are insufficient; see README for the isolated-rig dependency audit.
