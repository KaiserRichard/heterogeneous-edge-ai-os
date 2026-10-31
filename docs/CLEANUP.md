# Final submission cleanup

Changes are left in the working tree on `release/os-final`; no commits were made.
Result folders were moved without changing file contents. SHA-256 verification confirmed all 6,370 retained files unchanged after the moves.
The `.gitignore` result exception keeps moved raw logs/captures addable with ordinary `git add`.

## Deleted files

| File | Reason |
|---|---|
| `tools/timing/p0_cyclictest.sh` | Only forwards to cyclictest_campaign.sh P0; documentation now uses that entry point. |
| `scripts/stm32/build.sh` | Only forwards to make -C stm32 firmware; top-level make firmware replaces it. |
| `analysis/__pycache__/cyclictest_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/__pycache__/e3_real_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/__pycache__/e4_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/__pycache__/e_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/__pycache__/pipeline_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/tests/__pycache__/test_campaign.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/tests/__pycache__/test_cyclictest_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/tests/__pycache__/test_e3_real_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/tests/__pycache__/test_e4_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `analysis/tests/__pycache__/test_e_summary.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/__pycache__/bench_common.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/__pycache__/infer_bench.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/__pycache__/infer_server.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/__pycache__/model_runtime.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_c_abi.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_common.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_model_runtime.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_numpy_runtime.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_pipeline.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `linux/inference/tests/__pycache__/test_scripts.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `tools/experiments/__pycache__/e3_real.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `tools/experiments/__pycache__/e3_startup.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `tools/experiments/__pycache__/e4_campaign.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |
| `tools/experiments/__pycache__/e_campaign.cpython-311.pyc` | Generated Python bytecode cache; not source or measured evidence. |

No raw results were deleted. No editor junk was found outside the protected trees. Experiment shell entry points remain because campaign reproduction commands use them. Completed checklist entries remain as historical records; unresolved hardware checks remain open.
