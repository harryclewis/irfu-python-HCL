#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
#
# Copyright (c) 2020 - 2021 Louis Richard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

"""match_phibe_v.py
@author: Louis Richard
"""

import itertools
import numpy as np


from scipy import constants


def match_phibe_v(b_0, b_z, int_e_dt, n, v):
    r"""Get propagation velocity by matching dBpar and phi. Used together with
    irf_match_phibe_dir.m.Finds best match in amplitude given, B0, dB_par,
    phi, propagation direction implied, for specified n and v given as
    vectors.Returns a matrix of correlations and the two potentials that were
    correlated.

    Parameters
    ----------
    b_0 : ndarray
        Average background magnetic field.
    b_z : ndarray
        Parallel wave magnetic field.
    int_e_dt : ndarray
        Potential.
    n : ndarray
        Vector of densities
    v : ndarray
        Vector of velocities.

    Returns
    -------
    corr_mat : ndarray
        Correlation matrix(nn x nv).
    phi_b : ndarray
        B0 * dB_par / n_e * e * mu0
    phi_e : ndarray
        int(E) dt * v(dl=-vdt = > -dl = vdt)

    """

    # Define constants
    mu0 = constants.mu_0
    q_e = constants.elementary_charge

    # density in #/m^3
    n.data *= 1e6

    # Allocate correlations matrix rows: n, cols: v
    nn_, nv_ = [len(n), len(v)]
    corr_mat = np.zeros((nn_, nv_))

    # Setup potentials
    phi_e = int_e_dt * v  # depends on v
    phi_b = np.transpose(b_z[:, 0] * b_0 * 1e-18 / (mu0 * q_e * n[:, None]))

    # Get correlation
    for k, p in itertools.product(range(nn_), range(nv_)):
        corr_mat[k, p] = np.sum((np.log10(abs(phi_e[:, p]) / phi_b[:, k])))

    return corr_mat, phi_b, phi_e
