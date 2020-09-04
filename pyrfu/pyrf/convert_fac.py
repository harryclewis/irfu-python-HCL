#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
convert_fac.py

@author : Louis RICHARD
"""

import numpy as np
import xarray as xr

from .resample import resample
from .ts_vec_xyz import ts_vec_xyz
from .calc_fs import calc_fs


def convert_fac(inp=None, b_bgd=None, r=np.array([1, 0, 0])):
	"""
	Transforms to a field-aligned coordinate (FAC) system defined as:
	R_parallel_z aligned with the background magnetic field
	R_perp_y defined by R_parallel cross the position vector of the spacecraft (nominally eastward at the equator)
	R_perp_x defined by R_perp_y cross R_par
	If inp is one vector along r direction, out is inp[perp, para] projection
	
	Parameters :
		inp : DataArray
			Time series of the input field

		b_bgd : DataArray
			Time series of the background magnetic field

		r : DataArray/ndarray/list
			Position vector of spacecraft

	Returns :
		out : DataArray
			Time series of the input field in field aligned coordinates system

	Example :
		>>> from pyrfu import mms, pyrf
		>>> # Time interval
		>>> tint = ["2019-09-14T07:54:00.000","2019-09-14T08:11:00.000"]
		>>> # Spacecraft index
		>>> ic = 1
		>>> # Load magnetic field (FGM) and electric field (EDP)
		>>> b_xyz = mms.get_data("B_gse_fgm_brst_l2",tint,ic)
		>>> e_xyz = mms.get_data("E_gse_edp_brst_l2",tint,ic)
		>>> # Convert to field aligned coordinates
		>>> e_xyzfac = pyrf.convert_fac(e_xyz,b_xyz,[1,0,0])
	
	Note : 
		all input parameters must be in the same coordinate system
	
	"""
	
	if (inp is None) or (b_bgd is None):
		raise ValueError("convert_fac requires at least 2 arguments")

	if not isinstance(inp, xr.DataArray):
		raise TypeError("inp must be a DataArray")

	if not isinstance(b_bgd, xr.DataArray):
		raise TypeError("Bbgd must be a DataArray")

	if len(inp) != len(b_bgd):
		b_bgd = resample(b_bgd, inp, fs=calc_fs(inp))
	
	t, inp_data = [inp.time.data, inp.data]

	# Normalize background magnetic field
	bn = b_bgd/np.linalg.norm(b_bgd, axis=1, keepdims=True)

	if isinstance(r, (list, np.ndarray)) and len(r) == 3:
		r = np.tile(r, (len(b_bgd), 1))
	elif isinstance(r, xr.DataArray):
		r = resample(r, b_bgd)
	else:
		raise TypeError("Invalid type of spacecraft position")

	# Parallel
	r_par = bn

	# Perpandicular
	r_perp_y = np.cross(r_par, r, axis=1)
	r_perp_y /= np.linalg.norm(r_perp_y, axis=1, keepdims=True)
	r_perp_x = np.cross(r_perp_y, b_bgd, axis=1)
	r_perp_x /= np.linalg.norm(r_perp_x, axis=1, keepdims=True)
	
	(ndata, ndim) = inp_data.shape
	
	if ndim == 3:
		outdata = np.zeros(inp.shape)

		outdata[:, 0] = np.sum(r_perp_x * inp_data, axis=1)
		outdata[:, 1] = np.sum(r_perp_y * inp_data, axis=1)
		outdata[:, 2] = np.sum(r_par * inp_data, axis=1)

		# xarray
		out = xr.DataArray(outdata, coords=[t, inp.comp], dims=["time", "comp"])

	elif ndim == 1:
		outdata = np.zeros((3, ndata))

		outdata[:, 0] = inp[:, 0]*(r_perp_x[:, 0] * r[:, 0] + r_perp_x[:, 1] * r[:, 1] + r_perp_x[:, 2] * r[:, 2])
		outdata[:, 1] = inp[:, 0]*(r_par[:, 0] * r[:, 0] + r_par[:, 1] * r[:, 1] + r_par[:, 2] * r[:, 2])

		out = ts_vec_xyz(t, outdata, attrs=inp.attrs)
	else:
		raise TypeError("Invalid dimension of inp")

	return out
