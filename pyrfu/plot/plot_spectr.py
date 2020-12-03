# MIT License
#
# Copyright (c) 2020 Louis Richard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib import colors
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# plt.style.use("seaborn-whitegrid")
locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
# sns.set_context("paper")
# plt.rc('lines', linewidth=1)


def plot_spectr(ax=None, inp=None, yscale="", cscale="", clim=None, cmap="", cbar=True, **kwargs):
    """Plot a spectrogram using pcolormesh.

    Parameters
    ----------
    ax : axes
        Target axis to plot. If None create a new figure.

    inp : DataArray
        Input 2D data to plot.

    yscale : str
        Y-axis flag. Default is "" (linear).

    cscale : str
        C-axis flag. Default is "" (linear).

    clim : list
        C-axis bounds. Default is None (autolim).

    cmap : str
        Colormap. Default is jet.

    cbar : bool
        Flag for colorbar. Set to False to hide.

    Returns
    -------
    fig : figure
        to fill.

    axs : axes
        to fill.

    caxs : caxes
        Only if cbar is True.

    """

    if ax is None:
        fig, ax = plt.subplots(1)
    else:
        fig = plt.gcf()

    if not cmap:
        cmap = "jet"

    if cscale == "log":
        if clim is not None and isinstance(clim, list):
            options = dict(norm=colors.LogNorm(vmin=clim[0], vmax=clim[1]), cmap=cmap, shading='auto')
        else:
            options = dict(norm=colors.LogNorm(), cmap=cmap, shading='auto')
    else:
        if clim is not None and isinstance(clim, list):
            options = dict(cmap=cmap, vmin=clim[0], vmax=clim[1], shading='auto')
        else:
            options = dict(cmap=cmap, vmin=None, vmax=None, shading='auto')

    t, y = [inp.coords[inp.dims[0]], inp.coords[inp.dims[1]]]

    im = ax.pcolormesh(t, y, inp.data.T, rasterized=True, **options)

    if yscale == "log":
        ax.set_yscale("log")

    if cbar:
        if "pad" in kwargs:
            pad = kwargs["pad"]
        else:
            pad = 0.01

        pos = ax.get_position()
        cax = fig.add_axes([pos.x0+pos.width+pad, pos.y0, 0.01, pos.height])
        fig.colorbar(mappable=im, cax=cax, ax=ax)

        return ax, cax
    else:
        return ax
