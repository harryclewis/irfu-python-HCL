#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
calculate_epsilon.py

@author : Louis RICHARD
"""

import numpy as np

from astropy import constants

from ..pyrf import resample, ts_scalar


def calculate_epsilon(vdf=None, model_vdf=None, n=None, sc_pot=None, **kwargs):
    """
    Calculate epsilon parameter using model distribution

    Parameters :
        vdf : Dataset
            Observed particle distribution (skymap).

        model_vdf : Dataset
            Model particle distribution (skymap).

        n : DataArray
            Time series of the number density

        sc_pot : DataArray
            Time series of the spacecraft potential

    Options :
        en_channels : list/array
            Set energy channels to integrate over [min max]; min and max between must be between 1 and 32.


    Returns :
        epsilon : DataArray
            Time series of the epsilon parameter.

    See also :
        mms.make_model_vdf

    Example :
        >>> from pyrfu import mms
        >>> eps = mms.calculate_epsilon(vdf, model_vdf, n, sc_pot, en_channel=[4, 32])

    """

    if np.abs(np.median(np.diff(vdf.time-n.time))).astype(float) > 0:
        raise RuntimeError("vdf and moments have different times.")

    # Default energy channels used to compute epsilon, lowest energy channel should not be used.
    int_energies = np.arange(2, 33)

    if "en_channels" in kwargs and isinstance(kwargs["en_channels"], (list, np.ndarray)):
        int_energies = np.arange(kwargs["en_channels"][0], kwargs["en_channels"][1] + 1)

    # Resample sc_pot
    sc_pot = resample(sc_pot, n)

    # Remove zero count points from final calculation
    # model_vdf.data.data[vdf.data.data <= 0] = 0

    model_vdf /= 1e18
    vdf /= 1e18

    vdf_diff = np.abs(vdf.data.data - model_vdf.data.data)

    # Define constants
    qe = constants.e.value

    # Check whether particles are electrons or ions
    if vdf.attrs["specie"] == "e":
        mp = constants.m_e.value
        print("notice : Particles are electrons")
    elif vdf.attrs["specie"] == "i":
        sc_pot.data = -sc_pot.data
        mp = constants.m_p.value
        print("notice : Particles are electrons")
    else:
        raise ValueError("Invalid specie")

    # Define lengths of variables
    n_ph = len(vdf.phi.data[0, :])

    # Define corrected energy levels using spacecraft potential
    energy_arr = vdf.energy.data
    v, delta_v = [np.zeros(energy_arr.shape) for _ in range(2)]

    for it in range(len(vdf.time)):
        energy_vec, energy_log = [energy_arr[it, :], np.log10(energy_arr[it, :])]

        v[it, :] = np.real(np.sqrt(2 * (energy_vec - sc_pot.data[it]) * qe / mp))

        temp0, temp33 = [2 * energy_log[0] - energy_log[1], 2 * energy_log[-1] - energy_log[-2]]

        energy_all = np.hstack([temp0, energy_log, temp33])

        diff_en_all = np.diff(energy_all)

        energy_upper = 10 ** (energy_log + diff_en_all[1:34] / 2)
        energy_lower = 10 ** (energy_log - diff_en_all[0:33] / 2)

        v_upper = np.sqrt(2 * qe * energy_upper / mp)
        v_lower = np.sqrt(2 * qe * energy_lower / mp)

        v_lower[np.isnan(v_lower)] = 0
        v_upper[np.isnan(v_upper)] = 0

        delta_v[it, :] = (v_upper - v_lower)

    v[v < 0] = 0

    # Calculate density of vdf_diff
    delta_ang = (11.25 * np.pi / 180) ** 2
    theta_k = vdf.theta.data

    epsilon, m_psd2_n = [np.zeros(len(vdf.time)), np.ones(n_ph) * np.sin(theta_k * np.pi / 180)]

    for it in range(len(vdf.time)):
        for ii in int_energies:
            tmp = np.squeeze(vdf_diff[it, ii, ...])

            epsilon[it] += np.nansum(np.nansum(tmp * m_psd2_n, axis=0), axis=0) * v[it, ii] ** 2 * delta_v[
                it, ii] * delta_ang

    epsilon /= 1e6 * n.data * 2
    epsilon = ts_scalar(vdf.time.data, epsilon)

    return epsilon