# Offline re-run comparison

Run from any directory with Python 3 (standard library; plots use matplotlib only
if it is already installed):

```sh
python3 tools/rerun/build_rerun.py /path/to/rerun-root --outdir /tmp/os-rerun-2026-10-20
```

The input layout is:

```text
P1/cyclictest_p0/          cyclictest_campaign.sh campaign
P1/cyclictest_p1/          cyclictest_campaign.sh campaign
PS1/link60_fixed/          run_pipeline.sh real-UART run, summary.json + config.json
E4/e4-real/               e4_campaign.sh campaign
LA/F1/ LA/F2/ LA/F4/      batches: la_e4.csv, Fx-rNN/capture.vcd, pi/F*/run.json
E123/e-onnx/              e_campaign.sh ALL campaign
```

Use a new or empty output directory outside the raw root, linked run directories,
and repository `results/`. The program never runs acquisition, SSH, hardware,
builds of either document, or the fixed-path defense evidence builder. Existing
analyzer functions are imported and their output is explicitly redirected.
Matplotlib caches go to a temporary directory in the CLI. No packages are installed.

Outputs:

- `rerun_summary.json`: dated original/current metric cells with valid/total
  independent-run counts; transition sample counts; part statuses and per-run
  records, including invalid reasons, censoring, recovery and transition reasons.
- `rerun_compare.tex`: one booktabs table per experiment, with dated original and
  re-run columns and both acceptance counts. UTF-8, suitable for XeLaTeX; long
  tables may need splitting/resizing when integrated into slides.
- `rerun_compare_vi.md`: identical cells with Vietnamese comparison headers.
- `cyclic-P{0,1}/`, `pipeline/`, `e4/`: R1/R2/R4 CSV/TeX analyzer outputs;
  `E4_local.tex` and `E4_mapped.tex` give the two deck table views in ms.
- `la/`: R5 raw-VCD reanalysis, classification, per-batch CSVs and capture key.
  `original-la/` holds separate original VCD reanalysis, including `check_F2`.
- `ps1/summary.json`: retained smoke summary, including if subsequently rejected.
- `images/`: R6 deck-style PDFs for cyclic, E1/E2/E3/E3B, E4, LA, and each
  available batch's first waveform. Blank invalid cells remain blank, with no
  valid measurements annotated. Missing experiments have no plot. Without
  matplotlib the reports still work and the plot status explains the omission.

See `RERUN_UPDATE_MAP.md` for the exact original paths, scope and metrics. Original
values come from retained result directories, not numbers copied from the deck.
Condition joins include profile, stressor, input policy and bridge policy; newly
selected loads are shown separately rather than paired by row order. Re-run
status `ok` means analysis completed; acceptance is given separately. Missing
parts are `not run`; analysis errors and zero accepted populations are `failed:
reason`. Errors in one run do not discard intact siblings. Per-run CSVs/JSON keep
the precise rejection reasons.

Historical comparisons deliberately use original v1 acceptance. Current replay
uses v2: the original timer files yield 6/30, and original E1–E3 yield 0/45.
Thus symlinking originals **does not** imply all re-run table cells equal the
published v1 values. No rejected observation is promoted or replaced with zero.
E4's original deck population combines full E4 and short F4/F5 windows (27/34);
new E4 remains a separate full campaign with recovery checks. Reason 3 uses the
last heartbeat; reasons 9/10 use the last inference. Mixed reasons are retained
in the records and analyzer warnings. Threshold provenance is exported; source
fallbacks do not establish what was flashed. LA matching is a reference check,
not a declaration of collection validity or absolute calibration.

PS1 consumes its existing real-UART summary and checks validity, serial config
and exit code when present. It does not supply an E3_REAL policy comparison;
R3 is explicitly not run. Standalone inference is also not repeated (R7); the
original accepted thread sweep stays dated 2026-10-11. Original E3b is compared
only if the new ALL campaign actually contains E3B.

Test with retained originals and a missing/malformed fixture:

```sh
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/tmp/os-rerun-mpl \
  python3 -m unittest discover -s tools/rerun -v
```

The test constructs temporary symlinks to original campaigns, checks current
replay against direct analyzer calls, checks LA values against retained CSVs,
checks historical E4 values, and hashes raw inputs before/after. Three LA batch
links contain 14 captures; the original comparison also includes the separate
`check_F2` capture, giving 15. No original PS1 exists in the map: its fixture
borrows an original physical E3 pipeline purely to test smoke-summary handling.
It is never treated as accepted PS1 or as an E3 policy rerun. The second fixture
omits parts and places a corrupt E4 run beside an intact sibling. No hardware
verification is claimed.
