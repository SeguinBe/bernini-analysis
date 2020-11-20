import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from model.base import *


def side_matching_plot(d: BooksComparison, scaling=False, highlight_fn=None, keep_fn=None, with_structure=False):
    fig, ax = plt.subplots(figsize=(14, 14), dpi=200)

    L = 3
    if keep_fn is None:
        keep_fn = lambda m: True
    if highlight_fn is None:
        highlight_fn = lambda m: True

    for match in d.matches:
        if not keep_fn(match):
            continue
        passage1, passage2 = match.left, match.right
        p1, p2 = passage1.image_number, passage2.image_number
        l1, l2 = str(p1), str(p2)

        verts = [
            (0., p1),   # P0
            ( L /2, p1),  # P1
            ( L /2, p2),  # P2
            (L, p2),  # P3
        ]

        codes = [
            Path.MOVETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
        ]
        path = Path(verts, codes)
        color1, color2 = (style['color'] for style in plt.rcParams['axes.prop_cycle'][:2])
        if highlight_fn(match):
            patch = patches.PathPatch(path, facecolor='none', lw=2, ec=color2)
            plt.text(0., p1, l1, horizontalalignment='right',
                     verticalalignment='center', fontsize=7
                     )
            plt.text(L, p2, l2, horizontalalignment='left',
                     verticalalignment='center', fontsize=7
                     )
        else:
            patch = patches.PathPatch(path, facecolor='none', lw=2, ec=color1, ls='--')

        ax.add_patch(patch)

    ax.set_xlim(-1, L+ 1)
    ax.set_ylim(205, -1)
    ax.set_ylabel('Image number')
    ax.set_xticks([0, L])
    ax.set_xticklabels([d.book_left.short_descriptor(), d.book_right.short_descriptor()])
    fig.tight_layout()

    return fig
