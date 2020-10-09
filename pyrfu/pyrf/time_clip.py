#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
time_clip.py

@author : Louis RICHARD
"""

import xarray as xr
import numpy as np
import datetime
from dateutil import parser
from astropy.time import Time
import bisect


def time_clip(inp=None, tint=None):
	"""
	Time clip the input (if time interval is TSeries clip between start and stop)

	Parameters
	----------
	inp : xarray.DataArray
		Time series of the quantity to clip

	tint : xarray.DataArray or numpy.ndarray or list
		Time interval can be a time series, a array of datetime64 or a list

	Returns
	-------
	out : xarray.DataArray
		Time series of the time clipped input

	"""

	if type(inp) != xr.DataArray:
		raise TypeError('Input must be a TSeries')
	
	if type(tint) == xr.DataArray:
		t_start, t_stop = [tint.time.data[0], tint.time.data[-1]]

	elif type(tint) == np.ndarray:
		if type(tint[0]) == datetime.datetime and type(tint[-1]) == datetime.datetime:
			t_start, t_stop = [tint.time[0], tint.time[-1]]

		else:
			raise TypeError('Values must be in Datetime64')

	elif type(tint) == list:
		t_start, t_stop = [parser.parse(tint[0]), parser.parse(tint[-1])]

	else:
		raise TypeError("Invalid type of time interval")

	idx_min = bisect.bisect_left(inp.time.data, Time(t_start, format="datetime").datetime64)
	idx_max = bisect.bisect_right(inp.time.data, Time(t_stop, format="datetime").datetime64)

	coord = [inp.time.data[idx_min:idx_max]]

	if len(inp.coords) > 1:
		for k in inp.dims[1:]:
			coord.append(inp.coords[k].data)

	out = xr.DataArray(inp.data[idx_min:idx_max, ...], coords=coord, dims=inp.dims, attrs=inp.attrs)
	out.time.attrs = inp.time.attrs

	return out
