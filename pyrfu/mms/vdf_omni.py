#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
vdf_omni.py

@author : Louis RICHARD
"""

import numpy as np
import xarray as xr


def vdf_omni(vdf):
    """Computes omnidirectional distribution, conserving unit.

    Parameters
    ----------
    vdf : xarray.Dataset
        Time series of the 3D velocity distribution with :
            * time : Time samples.
            * data : 3D velocity distribution.
            * energy : Energy levels.
            * phi : Azimuthal angles.
            * theta : Elevation angle.

    Returns
    -------
    out : xarray.Dataset
        Time series of the omnidirectional velocity distribution function with :
            * time : Time samples.
            * data : 3D velocity distribution.
            * energy : Energy levels.

    """

    assert vdf is not None and isinstance(vdf, xr.Dataset)

    time = vdf.time.data

    energy = vdf.energy.data
    thetas = vdf.theta.data
    dangle = np.pi / 16
    np_phi = 32

    z2 = np.ones((np_phi, 1)) * np.sin(thetas * np.pi / 180)
    solid_angles = dangle * dangle * z2
    all_solid_angles = np.tile(solid_angles, (len(time), energy.shape[1], 1, 1))

    dist = vdf.data.data * all_solid_angles
    omni = np.squeeze(np.nanmean(np.nanmean(dist, axis=3), axis=2)) / (np.mean(np.mean(solid_angles)))

    energy = np.mean(energy[:2, :], axis=0)

    out = xr.DataArray(omni, coords=[time, energy], dims=["time", "energy"], attrs=vdf.attrs)

    return out