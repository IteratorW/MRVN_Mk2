import datetime

import discord
from tortoise import Tortoise

COLORS_REGULAR = ["00F7FF", "3772FF", "F038FF", "EF709D", "E2EF70"]
COLORS_ALTERNATE = ["EFC69B", "9F84BD", "8FB7AA", "F88677", "5878DA"]


class NotEnoughInformationError(BaseException):
    pass


def make_line_glow(line, ax, n_glow_lines=10, diff_linewidth=1.05, alpha_line=0.7):
    """Add a glow effect to the lines in an axis object.

    Each existing line is redrawn several times with increasing width and low alpha to create the glow effect.
    """
    alpha_value = alpha_line / n_glow_lines

    data = line.get_data()
    linewidth = line.get_linewidth()

    try:
        step_type = line.get_drawstyle().split("-")[1]
    except:
        step_type = None

    for n in range(1, n_glow_lines + 1):
        if step_type:
            glow_line, = ax.step(*data)
        else:
            glow_line, = ax.plot(*data)
        glow_line.update_from(
            line)
        glow_line.set_label(None)  # Remove the label from glow lines, so that there won"t be duplicates in the legend.

        glow_line.set_alpha(alpha_value)
        glow_line.set_linewidth(linewidth + (diff_linewidth * n))
        glow_line.is_glow_line = True  # mark the glow lines, to disregard them in the underglow function.
