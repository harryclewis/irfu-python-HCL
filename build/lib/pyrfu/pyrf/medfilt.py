#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
medfilt.py

@author : Louis RICHARD
"""

import xarray as xr
import numpy as np
from scipy import signal


def medfilt(inp=None, n_pts=11):
	"""Applies a median filter over npts points to inp.

	Parameters
	----------
	inp : xarray.DataArray
		Time series of the input variable.

	n_pts : float or int
		Number of points of median filter.

	Returns
	-------
	out : xarray.DataArry
		Time series of the median filtered input variable.

	Examples
	--------
	>>> import numpy
	>>> from pyrfu import mms, pyrf
	>>> # Time interval
	>>> tint = ["2019-09-14T07:54:00.000", "2019-09-14T08:11:00.000"]
	>>> # Spacecraft indices
	>>> mms_list = numpy.arange(1,5)
	>>> # Load magnetic field and electric field
	>>> r_mms, b_mms = [[] * 4 for _ in range(2)]
	>>> for mms_id in range(1, 5):
	>>> 	r_mms.append(mms.get_data("R_gse", tint, mms_id))
	>>> 	b_mms.append(mms.get_data("B_gse_fgm_srvy_l2", tint, mms_id))
	>>>
	>>> # Compute current density, etc
	>>> j_xyz, div_b, b_xyz, jxb, div_t_shear, div_pb = pyrf.c_4_j(r_mms, b_mms)
	>>> # Get J sampling frequency
	>>> fs = pyrf.calc_fs(j_xyz)
	>>> # Median filter over 1s
	>>> j_xyz = pyrf.medfilt(j_xyz,fs)

	"""

	if inp is None:
		raise ValueError("medfilt requires at least 1 argument")
	
	if not isinstance(inp, xr.DataArray):
		raise TypeError("inp must be a DataArray")
	
	if not isinstance(n_pts, (float, int)):
		raise TypeError("n_pts must be a float or int")

	if isinstance(n_pts, float):
		n_pts = np.floor(n_pts).astype(int)

	if n_pts % 2 == 0:
		n_pts += 1

	nt = len(inp)  

	if inp.ndim == 3:
		inp_data = np.reshape(inp.data, [nt, 9])
	else:
		inp_data = inp.data

	try:
		n_comp = inp_data.shape[1]
	except IndexError:
		n_comp = 1

		inp_data = inp_data[..., None]

	out_data = np.zeros(inp_data.shape)

	if not n_pts % 2:
		n_pts += 1

	for i in range(n_comp):
		out_data[:, i] = signal.medfilt(inp_data[:, i], n_pts)

	if n_comp == 9:
		out_data = np.reshape(out_data, [nt, 3, 3])

	if out_data.shape[1] == 1:
		out_data = out_data[:, 0]

	out = xr.DataArray(out_data, coords=inp.coords, dims=inp.dims)
	out.attrs = inp.attrs
	
	return out
