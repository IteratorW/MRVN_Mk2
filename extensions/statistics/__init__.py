import os

import matplotlib
from matplotlib import pyplot as plt

from . import commands
from . import listener
from . import autopost

plt.style.use(f"{os.path.dirname(__file__)}/assets/mrvn.mplstyle")
matplotlib.use('agg')  # No GUI backend
