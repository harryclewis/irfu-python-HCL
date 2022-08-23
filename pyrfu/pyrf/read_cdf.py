#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 3rd party imports
import numpy as np
import xarray as xr

from cdflib import cdfread

__author__ = "Louis Richard"
__email__ = "louisr@irfu.se"
__copyright__ = "Copyright 2020-2022"
__license__ = "MIT"
__version__ = "2.3.22"
__status__ = "Prototype"


def read_cdf(path, tint):
    r"""Reads CDF files.

    Parameters
    ----------
    path : str
        String of the filename in .cdf containing the L2 data
    tint : list
        Time interval

    Returns
    -------
    out_dict : dict
        Hash table with fields contained in the .cdf file.

    """
    out_dict = {}

    with cdfread.CDF(path) as file:
        keys_ = file.cdf_info()["zVariables"]
        for k_ in keys_:
            temp_ = file.varget(k_, starttime=tint[0], endtime=tint[1])
            shape_ = temp_.shape
            coords = [np.arange(lim_) for lim_ in shape_]

            out_dict[k_.lower()] = xr.DataArray(temp_, coords=coords)

    return out_dict