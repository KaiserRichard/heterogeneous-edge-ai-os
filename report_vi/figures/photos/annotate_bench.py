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
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle
import matplotlib.patheffects as pe
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

    # Small, isolated outlines. The breadboard mark calls out a patch of holes
    # between the LED and MPU6050 marks.
    cyan = '#00B7FF'
    outline_effect = [pe.Stroke(linewidth=4.1, foreground='black'), pe.Normal()]
    components = [
        ('ellipse', 540, 1015, 580, 460),  # Raspberry Pi case
        ('ellipse', 695, 470, 380, 405),  # Nucleo white board
        ('roundrect', 180, 350, 100, 90),  # breadboard holes, clear of LED outline
        ('ellipse', 115, 365, 105, 125),  # LEDs at the left end
        ('roundrect', 295, 415, 125, 110),  # blue GY-521 module and pin header
        ('ellipse', 210, 630, 215, 190),  # Pi Camera v2 board
        ('ellipse', 105, 855, 55, 125),  # straight ribbon section beside the hand
    ]
    for shape, x, y, width, height in components:
        if shape == 'roundrect':
            patch = FancyBboxPatch(xy(x, y), width, height,
                                   boxstyle='round,pad=0,rounding_size=9',
                                   fill=False, edgecolor=cyan, lw=2.8,
                                   path_effects=outline_effect)
        else:
            patch = Ellipse(xy(x, y), width, height, fill=False,
                            edgecolor=cyan, lw=2.8,
                            path_effects=outline_effect)
        ax.add_patch(patch)

    # Black leader segments stay in the white margins; cyan segments stay on
    # the photo. Routes approach each mark without crossing another mark.
    labels = [
        ((10, 500, 430, 85), 'Breadboard',
         [(440, 542.5), (470, 542.5), xy(0, 542.5), xy(0, 440), xy(180, 440)]),
        ((10, 350, 430, 85), 'LED trạng thái',
         [(440, 392.5), (470, 392.5), xy(62.5, 365)]),
        ((10, 635, 430, 110), 'Pi Camera Module v2\n(IMX219)',
         [(440, 690), (470, 690), xy(102.5, 630)]),
        ((10, 980, 430, 110), 'Cáp ribbon 22-to-15 pin\n→ CAM/DISP 0',
         [(440, 1035), (470, 1035), xy(77.5, 855)]),
        ((1460, 395, 430, 110), 'STM32\nNucleo-F446RE',
         [(1460, 450), (1430, 450), xy(885, 450)]),
        ((1460, 140, 430, 130), 'MPU6050 (GY-521)\nIMU 6 trục',
         [(1460, 205), (1430, 205), xy(460, 205), xy(460, 470), xy(420, 470)]),
        ((1460, 1080, 430, 130), 'Raspberry Pi 5 (4 GB)\n+ vỏ có quạt tản nhiệt',
         [(1460, 1145), (1430, 1145), xy(779, 1145)]),
    ]
    for (x, y, width, height), label, points in labels:
        # Split at the photo boundary so margin segments are black and photo
        # segments are cyan. Every path's first two points are the margin part.
        split = 2
        ax.plot([p[0] for p in points[:split]], [p[1] for p in points[:split]],
                color='black', lw=1.4, zorder=5)
        ax.plot([p[0] for p in points[split - 1:]], [p[1] for p in points[split - 1:]],
                color=cyan, lw=2.0, path_effects=[pe.Stroke(linewidth=3.0, foreground='black'),
                                                    pe.Normal()], zorder=5)
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
