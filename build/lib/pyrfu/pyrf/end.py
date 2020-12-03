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

import xarray as xr
from astropy.time import Time


def end(inp=None):
    """Gives the last time of the time series in unix format.

    Parameters
    ----------
    inp : xarray.DataArray
        Time series of the input variable.

    Returns
    -------
    out : float or str
        Value of the last time in the desired format.

    """

    assert inp is not None and isinstance(inp, xr.DataArray)

    out = Time(inp.time.data[-1], format="datetime64").unix

    return out
