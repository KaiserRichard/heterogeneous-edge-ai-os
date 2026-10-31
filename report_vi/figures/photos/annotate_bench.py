#!/usr/bin/env python3
"""Annotate the owner's unchanged bench photo; run with Python + Pillow/matplotlib.

Coordinates are source-photo pixels (960 × 1280), checked against full photo
and component crops. No hardware state or cable connectivity is inferred.
"""
from pathlib import Path
import os
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'os-photo-mpl'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir()) / 'os-photo-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})


def main():
    photo = Image.open(ROOT / 'bench_full_raw.jpg')
    assert photo.size == (960, 1280), 'Recheck annotations if source photo changes'
    # At 16 cm print width: 8 pt labels, full portrait photo between side margins.
    fig, ax = plt.subplots(figsize=(16 / 2.54, 11.3 / 2.54))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 1900), ylim=(1340, 0))
    ax.axis('off')
    x0, y0 = 470, 30
    ax.imshow(photo, extent=(x0, x0 + 960, y0 + 1280, y0))

    def xy(x, y):
        return x0 + x, y0 + y

    # Thin outlines only. The LED count is obscured by wiring in this photo.
    components = [
        (555, 1000, 650, 490),  # Pi case and fan
        (700, 455, 430, 465),  # Nucleo board, including ST-LINK section
        (260, 420, 520, 340),  # breadboard
        (108, 359, 130, 160),  # visible status LEDs
        (351, 474, 132, 115),  # GY-521
        (207, 625, 245, 195),  # camera PCB and lens
        (126, 956, 230, 590),  # orange ribbon; excludes unrelated jumper wires
    ]
    for x, y, width, height in components:
        ax.add_patch(Ellipse(xy(x, y), width, height, fill=False,
                             edgecolor='black', lw=.7))

    # Paths terminate on ellipse boundaries. The MPU6050 leader passes below
    # the Nucleo and to the right of the camera, avoiding other leader paths.
    labels = [
        ((10, 180, 430, 85), 'Breadboard',
         [(440, 222.5), (450, 222.5), xy(60, 312)]),
        ((10, 350, 430, 85), 'LED trạng thái',
         [(440, 392.5), xy(43, 359)]),
        ((10, 635, 430, 110), 'Pi Camera Module v2\n(IMX219)',
         [(440, 690), (450, 690), xy(88, 648)]),
        ((10, 980, 430, 110), 'Cáp ribbon 22-to-15 pin\n→ CAM/DISP 0',
         [(440, 1035), xy(12.4, 1000)]),
        ((1460, 395, 430, 110), 'STM32\nNucleo-F446RE',
         [(1460, 450), (1450, 450), xy(914.8, 445)]),
        ((1460, 725, 430, 130), 'MPU6050 (GY-521)\nIMU 6 trục',
         [(1460, 790), xy(950, 760), xy(440, 760), xy(389, 521)]),
        ((1460, 1080, 430, 130), 'Raspberry Pi 5 (4 GB)\n+ vỏ có quạt tản nhiệt',
         [(1460, 1145), (1450, 1145), xy(870, 1060)]),
    ]
    for (x, y, width, height), label, points in labels:
        ax.plot([p[0] for p in points], [p[1] for p in points], color='black', lw=.7)
        ax.add_patch(Rectangle((x, y), width, height, facecolor='white',
                               edgecolor='black', lw=.7))
        ax.text(x + width / 2, y + height / 2, label, ha='center', va='center',
                linespacing=1.2)
    for extension in ('png', 'pdf'):
        fig.savefig(ROOT.parent / f'os_bench_photo_annotated.{extension}',
                    dpi=300, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    main()
