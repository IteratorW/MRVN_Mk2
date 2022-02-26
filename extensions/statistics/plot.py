import io

import mplcyberpunk
import numpy as np
from matplotlib import pyplot as plt, patches

plt.style.use("cyberpunk")


def get_plot(messages: dict[str, int], legend_text: str):
    fig, ax = plt.subplots(figsize=(12, 6))

    x = list(messages.keys())
    y = list(messages.values())

    ax.plot(x, y, marker="o")

    mplcyberpunk.add_glow_effects()

    # Trend Line ================

    np_array = np.array(y)
    x_numbers = list(range(len(x)))

    z = np.polyfit(x_numbers, np_array, 1)
    p = np.poly1d(z)

    line = ax.plot(x, p(x_numbers), "--", color="#00ff41")[0]
    make_line_glow(line, ax)

    # Legend ====================

    plt.legend([legend_text])

    # Plot Config ===============

    max_y = max(y)

    ax.set_ylim([0, max_y + 1])

    plt.xticks(rotation=45)
    plt.yticks(np.arange(min(y), max_y + 1, 5))

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return buf


def make_line_glow(line, ax, n_glow_lines=10, diff_linewidth=1.05, alpha_line=0.3):
    """Add a glow effect to the lines in an axis object.

    Each existing line is redrawn several times with increasing width and low alpha to create the glow effect.
    """
    alpha_value = alpha_line / n_glow_lines

    data = line.get_data()
    linewidth = line.get_linewidth()

    try:
        step_type = line.get_drawstyle().split('-')[1]
    except:
        step_type = None

    for n in range(1, n_glow_lines + 1):
        if step_type:
            glow_line, = ax.step(*data)
        else:
            glow_line, = ax.plot(*data)
        glow_line.update_from(
            line)

        glow_line.set_alpha(alpha_value)
        glow_line.set_linewidth(linewidth + (diff_linewidth * n))
        glow_line.is_glow_line = True  # mark the glow lines, to disregard them in the underglow function.
