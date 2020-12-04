import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from typing import Callable, Optional, Union, Tuple
from model.base import *


class Highlighters:
    colors = [style['color'] for style in plt.rcParams['axes.prop_cycle'][:5]]

    @staticmethod
    def default(highlight_fn):
        def _highlight_fn(m):
            if highlight_fn(m):
                return True, dict(lw=2, ec=Highlighters.colors[1])
            else:
                return False, dict(lw=2, ec=Highlighters.colors[0], ls='--')
        return _highlight_fn

    @staticmethod
    def ls(highlight_fn):
        def _highlight_fn(m):
            if highlight_fn(m):
                return True, dict(lw=1.5, ec=Highlighters.colors[1])
            else:
                return False, dict(lw=1.0, ec=Highlighters.colors[0], ls='--', alpha=0.7)
        return _highlight_fn

    @staticmethod
    def alpha(highlight_fn):
        def _highlight_fn(m):
            if highlight_fn(m):
                return True, dict(lw=1.5, ec=Highlighters.colors[1])
            else:
                return False, dict(lw=1.5, ec=Highlighters.colors[1], alpha=0.2)
        return _highlight_fn


def side_matching_plot(d: BooksComparison,
                       scaling=False,
                       highlight_fn: Optional[Callable[[Match], Union[bool, Tuple[bool, Union[Dict, Tuple[Dict, Dict]]]]]] = None,
                       keep_fn: Optional[Callable[[Match], bool]] = None,
                       with_structure=False,
                       title=None):
    """

    :param d: the main data object
    :param scaling: scale the vertical axis so both books occupy all the vertical space even if they have different
                    number of pages
    :param highlight_fn: function that takes a match as input and returns a single bool if it should be highlighted
                    or a tuple (bool, params) with the drawing parameters of the line. The params can be a tuple of dicts
                    if both sides should highlighted differently
    :param keep_fn: functions that takes a match as input and returns if the match should be drawn or not
    :param with_structure:
    :param title:
    :return: the generated figure
    """
    fig, ax = plt.subplots(figsize=(14, 14), dpi=200)

    L = 3
    if keep_fn is None:
        keep_fn = lambda m: True
    if highlight_fn is None:
        highlight_fn = lambda m: True

    filtered_matches = [m for m in d.matches if keep_fn(m)]

    # Check if highlight_fn returns bool or (bool, dict) and adjust it
    if len(filtered_matches) == 0 or isinstance(highlight_fn(filtered_matches[0]), bool):
        _highlight_fn = Highlighters.default(highlight_fn)
    else:
        _highlight_fn = highlight_fn

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

        # Left part of the arc
        verts1 = [
            (0., y1),  # P0
            (L / 4, y1),  # P1
            (L / 2, abs((y2 - y1) / 2 + y1)),  # P3
        ]
        # Right part
        verts2 = [
            (L / 2, abs((y2 - y1) / 2 + y1)),
            (3 * L / 4, y2),
            (L, y2)  # P3
        ]

        codes = [
            Path.MOVETO,
            Path.CURVE3,
            Path.CURVE3,
        ]
        path1 = Path(verts1, codes)
        path2 = Path(verts2, codes)
        do_highlight, drawing_params = _highlight_fn(match)
        if do_highlight:
            plt.text(-0.03, y1, l1, horizontalalignment='right',
                     verticalalignment='center', fontsize=6.5
                     )
            plt.text(L+0.03, y2, l2, horizontalalignment='left',
                     verticalalignment='center', fontsize=6.5
                     )
        if not isinstance(drawing_params, tuple):
            left_params, right_params = drawing_params, drawing_params
        else:
            left_params, right_params = drawing_params
        patch = patches.PathPatch(path1, facecolor='none', **left_params)
        ax.add_patch(patch)
        patch = patches.PathPatch(path2, facecolor='none', **right_params)
        ax.add_patch(patch)

    # TODO this is a quick fix for the moment... should be much better
    if with_structure:
        for chapter in d.book_left.chapter_sections[7:-1]:
            cn = chapter.name_id
            pcb = chapter.image_number_begin / max_p1
            pce = chapter.image_number_end / max_p1

            plt.text(-0.75, (pcb + pce) / 2, cn, horizontalalignment='center',
                     verticalalignment='center', fontsize=8, alpha=0.8)

            plt.axhspan(pcb - 0.5 / max_p1, pce + 0.5 / max_p1, 0, 0.1, fc='whitesmoke', ec='gray', alpha=1)

        for patron in d.book_left.patron_sections:
            cn = patron.name
            pcb = patron.image_number_begin / max_p1
            pce = patron.image_number_end / max_p1

            plt.text(-0.3, (pcb + pce) / 2, cn, horizontalalignment='center',
                     verticalalignment='center', fontsize=8, alpha=0.8)

            plt.axhspan(pcb - 0.5 / max_p1, pce + 0.5 / max_p1, 0.1, 0.18, facecolor='white', ec='gray', alpha=1)

        for patron in d.book_right.patron_sections:
            cn = patron.name
            pcb = patron.image_number_begin / max_p2
            pce = patron.image_number_end / max_p2

            plt.text(L + 0.35, (pcb + pce) / 2, cn, horizontalalignment='center',
                     verticalalignment='center', fontsize=8, alpha=0.8)

            plt.axhspan(pcb - 0.5 / max_p2, pce + 0.5 / max_p2, 0.82, 0.92, fc='white', ec='gray', alpha=1)
    # End Structure plotting

    ax.set_xlim(-1, L + 1)
    if scaling:
        ax.set_ylim(1.0, 0.0)
    else:
        ax.set_ylim(max_p+5, -1)
    ax.set_ylabel('Image number')
    ax.set_xticks([0, L])
    ax.set_xticklabels([d.book_left.short_descriptor(), d.book_right.short_descriptor()])
    fig.tight_layout()

    if title:
        plt.title(title, fontsize=16)
    ax.set_facecolor('whitesmoke')

    return fig
