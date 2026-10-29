#!/usr/bin/env python3
"""Offline CPU inference benchmark; no network access or model auto-download."""
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from bench_common import clock, parse_cpu, pin_cpu, sha256, summarize, write_csv
from model_runtime import Model, ShmImage, add_runtime_args, load_image, preprocess


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_runtime_args(parser)
    parser.add_argument('--warmup', type=int, default=50)
    parser.add_argument('--runs', type=int, default=1000)
    parser.add_argument('--output', type=Path, required=True, help='new run directory')
    parser.add_argument('--image-source', default='fixed', metavar='fixed|shm:NAME',
                        help='fixed image (default) or newest camera shared-memory frame')
    args = parser.parse_args(argv)
    if args.warmup < 0 or args.runs < 1 or args.seed < 0:
        parser.error('warmup/seed must be nonnegative and runs must be positive')
    if args.image_source != 'fixed' and not (args.image_source.startswith('shm:') and
                                            args.image_source[4:]):
        parser.error('image-source must be fixed or shm:NAME')
    if args.image_source != 'fixed' and args.image:
        parser.error('--image cannot be combined with a shared-memory image source')
    affinity = pin_cpu(parse_cpu(args.cpu) if args.cpu else None)
    import numpy as np
    import onnxruntime as ort

    model_hash = sha256(args.model)
    image_reader = ShmImage(args.image_source[4:]) if args.image_source != 'fixed' else None
    image = load_image(np, args.seed, args.image) if image_reader is None else None
    initial_image = image if image_reader is None else require_camera_frame(image_reader.read_latest(np))
    tensor = preprocess(np, initial_image)
    now, clock_name = clock()
    args.output.mkdir(parents=True, exist_ok=False)
    start = now()
    model = Model(ort, args.model, args.threads)
    try:
        model.run(tensor)
        cold_ns = now() - start
        for _ in range(args.warmup):
            warm_image = image if image_reader is None else require_camera_frame(image_reader.read_latest(np))
            model.run(preprocess(np, warm_image))
        samples = []
        frame_rows = []
        for run_idx in range(args.runs):
            start = now()
            if image_reader is None:
                frame_image = image
                frame_id = frame_status = None
            else:
                frame_image, frame_id, frame_status = require_camera_frame(
                    image_reader.read_latest(np), with_metadata=True)
            tensor = preprocess(np, frame_image)
            prepared = now()
            model.run(tensor)
            done = now()
            samples.append((run_idx, prepared - start, done - prepared))
            if image_reader is not None:
                frame_rows.append((frame_id, frame_status))
        if image_reader is None:
            write_csv(args.output / 'samples.csv', samples)
        else:
            import csv
            with (args.output / 'samples.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(('run_idx', 'pre_ns', 'infer_ns', 'frame_seq', 'frame_status'))
                writer.writerows((*sample, *frame) for sample, frame in zip(samples, frame_rows))
    finally:
        if image_reader is not None:
            image_reader.close()
    config = {'model': str(Path(args.model).resolve()), 'model_sha256': model_hash,
                   'ort_version': ort.__version__, 'numpy_version': np.__version__,
                   'python_version': platform.python_version(), 'threads': args.threads,
                   'inter_op_num_threads': 1, 'execution_mode': 'ORT_SEQUENTIAL',
                   'providers': model.session.get_providers(), 'affinity': affinity,
                   'clock': clock_name, 'seed': args.seed, 'image': args.image,
                   'image_sha256': sha256(args.image) if args.image else None,
                   'input_shape': [1, 3, 224, 224], 'input_dtype': 'float32',
                   'preprocessing': 'nearest resize 256->224; RGB/255; ImageNet mean/std; NCHW',
                   'warmup': args.warmup, 'runs': args.runs, 'argv': sys.argv,
                   'utc': datetime.now(timezone.utc).isoformat()}
    if image_reader is not None:
        config['image_source'] = args.image_source
    summary = {'cold_start': summarize([cold_ns]),
               'preprocessing': summarize([row[1] for row in samples]),
               'inference': summarize([row[2] for row in samples])}
    if image_reader is not None:
        sequences = [row[0] for row in frame_rows]
        summary['camera_frames'] = {'new': sum(status == 'new' for _, status in frame_rows),
                                    'repeated': sum(status == 'repeated' for _, status in frame_rows),
                                    'first_seq': sequences[0], 'last_seq': sequences[-1],
                                    'sequence_status': [{'seq': seq, 'status': status}
                                                        for seq, status in frame_rows]}
    report = {
        'config': config,
        'cold_start_ns': cold_ns,
        'summary': summary}
    (args.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))


def require_camera_frame(result, with_metadata=False):
    image, sequence, status = result
    if image is None:
        raise RuntimeError(f'could not read a consistent camera frame: {status}')
    return (image, sequence, status) if with_metadata else image


if __name__ == '__main__':
    main()
