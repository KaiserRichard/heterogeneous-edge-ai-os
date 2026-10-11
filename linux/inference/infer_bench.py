#!/usr/bin/env python3
"""Offline CPU inference benchmark; no network access or model auto-download."""
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from bench_common import clock, parse_cpu, pin_cpu, sha256, summarize, write_csv
from model_runtime import Model, add_runtime_args, load_image, preprocess


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_runtime_args(parser)
    parser.add_argument('--warmup', type=int, default=50)
    parser.add_argument('--runs', type=int, default=1000)
    parser.add_argument('--output', type=Path, required=True, help='new run directory')
    args = parser.parse_args(argv)
    if args.warmup < 0 or args.runs < 1 or args.seed < 0:
        parser.error('warmup/seed must be nonnegative and runs must be positive')
    affinity = pin_cpu(parse_cpu(args.cpu) if args.cpu else None)
    import numpy as np
    import onnxruntime as ort

    model_hash = sha256(args.model)
    image = load_image(np, args.seed, args.image)
    tensor = preprocess(np, image)
    now, clock_name = clock()
    args.output.mkdir(parents=True, exist_ok=False)
    start = now()
    model = Model(ort, args.model, args.threads)
    model.run(tensor)
    cold_ns = now() - start
    for _ in range(args.warmup):
        model.run(preprocess(np, image))
    samples = []
    for run_idx in range(args.runs):
        start = now()
        tensor = preprocess(np, image)
        prepared = now()
        model.run(tensor)
        done = now()
        samples.append((run_idx, prepared - start, done - prepared))
    write_csv(args.output / 'samples.csv', samples)
    report = {
        'config': {'model': str(Path(args.model).resolve()), 'model_sha256': model_hash,
                   'ort_version': ort.__version__, 'numpy_version': np.__version__,
                   'python_version': platform.python_version(), 'threads': args.threads,
                   'inter_op_num_threads': 1, 'execution_mode': 'ORT_SEQUENTIAL',
                   'providers': model.session.get_providers(), 'affinity': affinity,
                   'clock': clock_name, 'seed': args.seed, 'image': args.image,
                   'image_sha256': sha256(args.image) if args.image else None,
                   'input_shape': [1, 3, 224, 224], 'input_dtype': 'float32',
                   'preprocessing': 'nearest resize 256->224; RGB/255; ImageNet mean/std; NCHW',
                   'warmup': args.warmup, 'runs': args.runs, 'argv': sys.argv,
                   'utc': datetime.now(timezone.utc).isoformat()},
        'cold_start_ns': cold_ns,
        'summary': {'cold_start': summarize([cold_ns]),
                    'preprocessing': summarize([row[1] for row in samples]),
                    'inference': summarize([row[2] for row in samples])}}
    (args.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
