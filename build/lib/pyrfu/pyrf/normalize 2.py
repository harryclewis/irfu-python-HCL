#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
import numpy as np


def normalize(inp=None):
    """Normalizes the input field.

    Parameters
    ----------
    inp : xarray.DataArray
        Time series of the input field.

    Returns
    -------
    out : xarray.DataArray
        Time series of the normalized input field.

    Examples
    --------
    >>> from pyrfu import mms, pyrf
    >>> # Time interval
    >>> tint = ["2019-09-14T07:54:00.000", "2019-09-14T08:11:00.000"]
    >>> # Spacecraft index
    >>> mms_id = 1
    >>> # Load magnetic field
    >>> b_xyz = mms.get_data("B_gse_fgm_srvy_l2", tint, mms_id)
    >>> # Compute the normalized magnetic field
    >>> b = pyrf.normalize(b_xyz)

    """

    assert inp is not None and isinstance(inp, xr.DataArray)

    out = inp / np.linalg.norm(inp, axis=1, keepdims=True)

    return out