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

    filtered_matches = [m for m in d.matches if keep_fn(m)]
    max_p1 = d.book_left.nb_images
    max_p2 = d.book_right.nb_images
    max_p = max(max_p1, max_p2)
    if not scaling:
        max_p1 = 1.0
        max_p2 = 1.0

    for match in filtered_matches:
        passage1, passage2 = match.left, match.right
        p1, p2 = passage1.image_number, passage2.image_number
        l1, l2 = str(p1), str(p2)
        y1 = p1/max_p1
        y2 = p2/max_p2

        verts = [
            (0., y1),   # P0
            (L/2, y1),  # P1
            (L/2, y2),  # P2
            (L, y2),  # P3
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
            plt.text(0., y1, l1, horizontalalignment='right',
                     verticalalignment='center', fontsize=7
                     )
            plt.text(L, y2, l2, horizontalalignment='left',
                     verticalalignment='center', fontsize=7
                     )
        else:
            patch = patches.PathPatch(path, facecolor='none', lw=2, ec=color1, ls='--')

        ax.add_patch(patch)

    ax.set_xlim(-1, L+ 1)
    if scaling:
        ax.set_ylim(1.0, 0.0)
    else:
        ax.set_ylim(max_p+5, -1)
    ax.set_ylabel('Image number')
    ax.set_xticks([0, L])
    ax.set_xticklabels([d.book_left.short_descriptor(), d.book_right.short_descriptor()])
    fig.tight_layout()

    return fig
