# -*- coding: utf-8 -*-
"""
norm.py

@author : Louis RICHARD
"""

import xarray as xr
import numpy as np


def norm(inp=None):
	"""
	Computes the magnitude of the input field

	Parameters :
		inp : DataArray
			Time series of the input field

	Returns :
		out : DataArray
			Time series of the magnitude of the input field

	Example : 
		>>> from pyrfu import mms, pyrf
		>>> # Time interval
		>>> tint = ["2019-09-14T07:54:00.000", "2019-09-14T08:11:00.000"]
		>>> # Spacecraft index
		>>> mms_id = 1
		>>> # Load magnetic field
		>>> b_xyz = mms.get_data("B_gse_fgm_srvy_l2", tint, mms_id)
		>>> # Compute magnitude of the magnetic field
		>>> Bmag = pyrf.norm(b_xyz)

	"""

	if inp is None:
		raise ValueError("norm require one argument")

	if type(inp) != xr.DataArray:
		raise TypeError('Input must be a DataArray')

	out = np.sqrt(np.sum(inp ** 2, axis=1))
	
	return out
