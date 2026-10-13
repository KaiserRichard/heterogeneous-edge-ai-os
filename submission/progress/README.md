# Owner progress deck

Open `main.pdf` (29 pages). `PAGE_INDEX.md` lists its pages; `TOOL_CATALOG.md` supplies copyable commands and the test-script inventory. All files for this repair are in this folder; source code and retained results were not changed.

## Rebuild and inspect on macOS

Requires Python 3, XeLaTeX/latexmk, the moloch Beamer theme, Avenir Next and Menlo. The reference preamble and study-page snapshot are retained locally, so generation does not require the separate long-deck folder.

```sh
cd submission/progress
python3 build_deck.py
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
CLANG_MODULE_CACHE_PATH=/tmp/progress-clang-cache swift -module-cache-path /tmp/progress-swift-cache /Users/quockaiser/Desktop/OS/OS-project/heterogeneous-edge-ai-os/slides/render.swift main.pdf preview
rg 'Overfull|Underfull|Missing character|undefined|^!' main.log
```

The final `rg` command prints nothing and exits 1 when no warnings match. `preview/page-01.png` through `page-29.png` are full-size 1280 × 720 renders. The same PDFKit renderer is available locally as `render.m` if Swift's cache is unavailable:

```sh
clang -fno-modules -framework Cocoa -framework PDFKit render.m -o /tmp/progress-render
/tmp/progress-render main.pdf preview
```

`REVIEW_LOG.md` records the author repair and visual inspection, not a new independent review. `REVIEW_1.md` remains intact.

## Offline deployment commands (planned; run in the named environment)

On the connected Mac, from the repository root:

```sh
git bundle create /tmp/os-final.bundle release/os-final
bash linux/inference/fetch_offline_deps.sh /tmp/os-offline-bundle
scp /tmp/os-final.bundle richard@192.168.50.2:/tmp/
scp -r /tmp/os-offline-bundle richard@192.168.50.2:/tmp/
```

On the dedicated OS Pi, in its repository checkout:

```sh
git bundle verify /tmp/os-final.bundle
git fetch /tmp/os-final.bundle release/os-final
(cd /tmp/os-offline-bundle && sha256sum -c SHA256SUMS)
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --no-index --find-links /tmp/os-offline-bundle/wheels onnxruntime==1.20.1 numpy==2.1.3
export MODEL=/tmp/os-offline-bundle/mobilenetv2-12.onnx
```

Verify the fetched revision before selecting it for deployment. Bundle defaults are the dependency script's current pins, not the historical measured ONNX Runtime version; record any overrides and exact model/runtime hashes for matched comparisons. No offline deployment or physical experiment was performed during this repair.

## Host/cross-build commands (planned)

From the repository root:

```sh
make -C protocol test
make -C stm32 test
make -C stm32 firmware FREERTOS_REF="$FREERTOS_REF" CLOCK_SOURCE=HSE RX_MODE=DMA UART_BAUD=921600 DEBUG_VCP=0 BRINGUP_BLINK=0
shasum -a 256 stm32/firmware/build/firmware.bin
```

Set `FREERTOS_REF` to the existing reference checkout containing `ThirdParty/FreeRTOS` and `004LEDsNotifyISR`. Cross-compilation is a Mac operation; the full `make test` includes Linux programs and belongs on the Pi/Linux. Flashing the binary remains a separate rig gate.

The deployment-specific `/home/richard/osbuild/rearm_via_mac.sh` helper must exist and actually reset the connected Nucleo before the physical campaign commands are usable. Do not replace it with `true` to bypass startup verification.

## Evidence and known limits

Counts and qualifications follow `results/README.md`, dated summaries, `docs/STAGE_REPORT.md`, and the additional real-UART rerun's retained `per_run.csv`. Historical v1 acceptance stays distinct from read-only v2 replay. Existing rig observations do not verify review-fix firmware. PR state is the supplied 13 October brief snapshot, not a live remote query.

Exact external Obsidian M-lesson filenames are not retained inside this workspace. Page 28 gives verified long-deck page pointers and learning-plan module numbers/titles; the external paths are explicitly UNKNOWN. No new bitmap illustration or data chart was needed; `image-prompts/NEEDS.md` remains `NONE`. Figure 1 is a code-native architecture map, not measured data.

## Provisioning and pending owner lookups

`sudo bash scripts/pi/bootstrap.sh` is initial provisioning requiring reachable apt sources: it unconditionally updates apt and installs packages. Bundles and wheels do not supply system dependencies. On an already provisioned isolated Pi, audit without installing:

```sh
dpkg-query -W -f='${Package} ${Status} ${Version}\n' build-essential cmake git python3 python3-venv python3-pip stress-ng rt-tests htop tmux picocom socat jq rsync avahi-daemon openocd stlink-tools gcc-arm-none-eabi linux-tools-common linux-tools-raspi cpufrequtils
ls -l /dev/ttyAMA0
id
```

Gate: required packages show installed status; UART enabled, console disabled per `scripts/pi/UART.md`, user serial access confirmed after login/reboot. Missing packages require reachable apt sources or a separately prepared complete offline apt dependency set; none is supplied here.

Restore the physical helper using [REARM_SETUP.md](REARM_SETUP.md). Mac destination/tool paths are UNKNOWN until confirmed. Reset success and post-reset FRESH are separate checks.

Pending owner Obsidian lookup: supply or authorize M-lessons. Gate: record exact note title/path for processes, scheduling/contention, queues/freshness, RTOS priorities, supervision and clocks, mapped to page 28's checked long-deck/module pointers. M-identifiers remain UNKNOWN until supplied; no personal vault was searched.
