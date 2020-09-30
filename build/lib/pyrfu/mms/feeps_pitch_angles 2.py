#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
feeps_pitch_angles.py

@author : Louis RICHARD
"""

import math
import numpy as np
import xarray as xr

from astropy.time import Time

from .get_feeps_active_eyes import get_feeps_active_eyes


def feeps_pitch_angles(inp_dset=None, b_bcs=None):
	"""
	Computes the FEEPS pitch angles for each telescope from magnetic field data.
	"""
	var = inp_dset.attrs
	mms_id = var["mmsId"]
	times = inp_dset.time
	btimes = b_bcs.time

	trange = Time(np.hstack([times.data.min(), times.data.max()]), format="datetime64").isot

	eyes = get_feeps_active_eyes(var, trange, var["mmsId"])

	idx_maps = None
	nbins = 13  # number of pitch angle bins; 10 deg = 17 bins, 15 deg = 13 bins
	dpa = 180.0 / nbins  # delta-pitch angle for each bin

	# Rotation matrices for FEEPS coord system (FCS) into body coordinate system (BCS):
	t_top = [[1./np.sqrt(2.), -1./np.sqrt(2.), 0], [1./np.sqrt(2.), 1./np.sqrt(2.), 0], [0, 0, 1]]
	t_bot = [[-1./np.sqrt(2.), -1./np.sqrt(2.), 0], [-1./np.sqrt(2.), 1./np.sqrt(2.), 0], [0, 0, -1]]

	# Telescope vectors in FCS:
	v_fcs = {"1": [0.347, -0.837, 0.423], "2": [0.347, -0.837, -0.423], "3": [0.837, -0.347, 0.423],
			 "4": [0.837, -0.347, -0.423], "5": [-0.087, 0.000, 0.996], "6": [0.104, 0.180, 0.978],
			 "7": [0.654, -0.377, 0.656], "8": [0.654, -0.377, -0.656], "9": [0.837, 0.347, 0.423],
			 "10": [0.837, 0.347, -0.423], "11": [0.347, 0.837, 0.423], "12": [0.347, 0.837, -0.423]}

	telescope_map = {"bottom-electron": [1, 2, 3, 4, 5, 9, 10, 11, 12], "bottom-ion": [6, 7, 8],
					 "top-electron": [1, 2, 3, 4, 5, 9, 10, 11, 12], "top-ion": [6, 7, 8]}

	top_tele_idx_map, bot_tele_idx_map = [{}, {}]

	pas = np.empty([len(btimes), 18])  # pitch angles for each eye at each time

	# Telescope vectors in Body Coordinate System:
	#   Factors of -1 account for 180 deg shift between particle velocity and telescope normal direction:
	# Top:
	vt_bcs, vb_bcs = [{}, {}]

	for s in telescope_map["top-{}".format(var["dtype"])]:
		s = str(s)

		vt_bcs[s] = [-1. * (t_top[0][0] * v_fcs[s][0] + t_top[0][1] * v_fcs[s][1] + t_top[0][2] * v_fcs[s][2]),
					 -1. * (t_top[1][0] * v_fcs[s][0] + t_top[1][1] * v_fcs[s][1] + t_top[1][2] * v_fcs[s][2]),
					 -1. * (t_top[2][0] * v_fcs[s][0] + t_top[2][1] * v_fcs[s][1] + t_top[2][2] * v_fcs[s][2])]

	for s in telescope_map["bottom-{}".format(var["dtype"])]:
		s = str(s)

		vb_bcs[s] = [-1. * (t_bot[0][0] * v_fcs[s][0] + t_bot[0][1] * v_fcs[s][1] + t_bot[0][2] * v_fcs[s][2]),
					 -1. * (t_bot[1][0] * v_fcs[s][0] + t_bot[1][1] * v_fcs[s][1] + t_bot[1][2] * v_fcs[s][2]),
					 -1. * (t_bot[2][0] * v_fcs[s][0] + t_bot[2][1] * v_fcs[s][1] + t_bot[2][2] * v_fcs[s][2])]

	for i, k in zip(np.arange(18),
					np.hstack([telescope_map["bottom-{}".format(var["dtype"])], telescope_map["top-{}".format(var["dtype"])]])):
		if i < 8:
			v_bcs = vt_bcs[str(k)]
		else:
			v_bcs = vb_bcs[str(k)]
		"""
		pas[:, i] = 180. / math.pi * np.arccos(
			(v_bcs[0] * b_bcs[:, 0] + v_bcs[1] * b_bcs[:, 1] + v_bcs[2] * b_bcs[:, 2]) / (
						np.sqrt(v_bcs[0] ** 2 + v_bcs[1] ** 2 + v_bcs[2] ** 2) * np.sqrt(
					b_bcs[:, 0] ** 2 + b_bcs[:, 1] ** 2 + b_bcs[:, 2] ** 2)))
		"""

		if var["tmmode"] == "srvy":
			if i < 8:
				top_tele_idx_map[k] = i
			else:
				bot_tele_idx_map[k] = i

			top_idxs, bot_idxs = [[], []]

			# PAs for only active eyes
			new_pas = np.empty(
				[len(btimes), len(eyes["top"]) + len(eyes["bottom"])])  # pitch angles for each eye at eaceh time

			for top_idx, top_eye in enumerate(eyes["top"]):
				new_pas[:, top_idx] = pas[:, top_tele_idx_map[top_eye]]
				top_idxs.append(top_idx)

			for bot_idx, bot_eye in enumerate(eyes["bottom"]):
				new_pas[:, bot_idx + len(eyes["top"])] = pas[:, bot_tele_idx_map[bot_eye]]
				bot_idxs.append(bot_idx + len(eyes["top"]))

			idx_maps = {"electron-top": top_idxs, "electron-bottom": bot_idxs}

		else:
			new_pas = pas

	outdata = xr.DataArray(new_pas, coords=[btimes, np.arange(18)], dims=["time", "idx"])

	# interpolate to the PA time stamps
	out = outdata.interp({'time': times})

	return out