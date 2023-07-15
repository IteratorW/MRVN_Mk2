import hashlib
import io
import os
import random

import numpy as np
from matplotlib import pyplot as plt, patches, cm, cycler

plt.style.use(f"{os.path.dirname(__file__)}/mrvn.mplstyle")


def get_plot(dates_list: list[str], counts: dict[str, list[int]], legend_text: str = None,
             alternate_colors: bool = False):
    """
    Make a message statistics plot for at least one channel

    This function is used for following plots: channels, messages, users

    :param dates_list: Dates list (x-axis)
    :param counts: Message counts (y-axis). Key is the channel name, value is the message count in that channel
    :param legend_text: Guild name (unused if multiple channels are passed, safe to provide None in this case)
    :param alternate_colors: Use alternate colors for lines
    :return: PNG image BytesIO
    """

    fig, ax = plt.subplots(figsize=(12, 6))

    if alternate_colors:
        ax.set_prop_cycle(cycler(color=["BCD2EE", "00FF51", "D90368", "4444FF", "FFFF00"]))

    x = dates_list

    for name, chan_counts in counts.items():
        line = ax.plot(x, chan_counts, marker="o")[0]
        line.set_label(name)

        make_line_glow(line, ax)

    multiple_channels = len(counts.keys()) > 1

    # Trend Line ================

    if not multiple_channels:
        np_array = np.array(next(iter(counts.values())))
        x_numbers = list(range(len(x)))

        z = np.polyfit(x_numbers, np_array, 1)
        p = np.poly1d(z)

        line = ax.plot(x, p(x_numbers), "--", color="#00ff41")[0]
        make_line_glow(line, ax)

    # Legend ====================

    if not multiple_channels:
        plt.legend([legend_text])
    else:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1),
                  ncol=5)

    # Plot Config ===============

    max_y = max([max(x) for x in counts.values()])

    ax.set_ylim([0, max_y + 10])

    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    return buf


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
