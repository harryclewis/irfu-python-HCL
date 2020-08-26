import numpy as np
import xarray as xr

from .resample import resample
from .ts_tensor_xyz import ts_tensor_xyz


def rotate_tensor(*args):
	"""
	Rotates pressure or temperature tensor into another coordinate system
	
	Parameters :
		PeIJ/Peall : DataArray
			Time series of either separated terms of the tensor or the complete tensor. 
			If columns (PeXX,PeXY,PeXZ,PeYY,PeYZ,PeZZ)
		flag : str
			Flag of the target coordinates system : 
				Field-aligned coordinates "fac", requires background magnetic field Bback, optional 
				flag "pp" P_perp1 = P_perp2 or "qq" P_perp1 and P_perp2 are most unequal, sets P23 to zero.

				Arbitrary coordinate system "rot", requires new x-direction xnew, new y and z directions 
				ynew, znew (if not included y and z directions are orthogonal to xnew and closest to the 
				original y and z directions)

				GSE coordinates "gse", requires MMS spacecraft number 1--4 MMSnum

	Returns : 
		Pe : DataArray
			Time series of the pressure or temperature tensor in field-aligned, user-defined, or GSE coordinates.
			For "fac" Pe = [Ppar P12 P13; P12 Pperp1 P23; P13 P23 Pperp2].
			For "rot" and "gse" Pe = [Pxx Pxy Pxz; Pxy Pyy Pyz; Pxz Pyz Pzz]
	Example :
		>>> from pyrfu import mms, pyrf
		>>> # Time interval
		>>> tint = ["2015-10-30T05:15:20.000", "2015-10-30T05:16:20.000"]
		>>> # Spacecraft index
		>>> mms_id = 1
		>>> # Load magnetic field and ion temperature tensor
		>>> b_xyz = mms.get_data("B_gse_fgm_srvy_l2", tint, mms_id)
		>>> t_xyz_i = mms.get_data("Ti_gse_fpi_fast_l2", tint, mms_id)
		>>> # Compute ion temperature in field aligned coordinates
		>>> t_xyzfac_i = pyrf.rotate_tensor(t_xyz_i, "fac", b_xyz, "pp")

	"""

	nargin = len(args)

	# Check input and load pressure/temperature terms
	if isinstance(args[1], str):
		rot_flag = args[1]
		rot_flag_pos = 1
		p_all = args[0]
		p_times = p_all.time.data

		if p_all.data.ndim == 3:
			p_tensor = p_all.data
		else:
			p_tensor = np.reshape(p_all.data, (p_all.shape[0], 3, 3))
			p_tensor = ts_tensor_xyz(p_times, p_tensor)

	elif isinstance(args[6], str):
		rot_flag = args[6]
		rot_flag_pos = 6
		p_times = args[0].time.data
		p_tensor = np.zeros((len(args[0].time.data), 3, 3))
		p_tensor[:, 0, 0] = args[0].data
		p_tensor[:, 1, 0] = args[1].data
		p_tensor[:, 2, 0] = args[2].data
		p_tensor[:, 0, 1] = args[1].data
		p_tensor[:, 1, 1] = args[3].data
		p_tensor[:, 2, 1] = args[4].data
		p_tensor[:, 0, 2] = args[2].data
		p_tensor[:, 1, 2] = args[4].data
		p_tensor[:, 2, 2] = args[5].data

		p_tensor = ts_tensor_xyz(p_times, p_tensor)

	else:
		raise SystemError("critical','Something is wrong with the input.")

	ppeq, qqeq = [0, 0]

	rot_mat = np.zeros((len(p_times), 3, 3))

	if rot_flag[0] == "f":
		print("notice : Transforming tensor into field-aligned coordinates.")

		if nargin == rot_flag_pos:
			raise ValueError("B TSeries is missing.")
		
		b_back = args[rot_flag_pos + 1]
		b_back = resample(b_back, p_tensor)

		if nargin == 4:
			if isinstance(args[3], str) and args[3][0] == "p":
				ppeq = 1
			elif isinstance(args[3], str) and args[3][0] == "q":
				qqeq = 1
			else:
				raise ValueError("Flag not recognized no additional rotations applied.")
		
		if nargin == 9:
			if isinstance(args[8], str) and args[8][0] == "p":
				ppeq = 1
			elif isinstance(args[8], str) and args[8][0] == "q":
				qqeq = 1
			else:
				raise ValueError("Flag not recognized no additional rotations applied.")
		
		b_vec = b_back / np.linalg.norm(b_back, axis=1, keepdims=True)

		r_x = b_vec.data
		r_y = np.array([1, 0, 0])
		r_z = np.cross(r_x, r_y)
		r_z /= np.linalg.norm(r_z, axis=1, keepdims=True)
		r_y = np.cross(r_z, r_x)
		r_y /= np.linalg.norm(r_y, axis=1, keepdims=True)

		rot_mat[:, 0, :], rot_mat[:, 1, :], rot_mat[:, 2, :] = [r_x, r_y, r_z]

	elif rot_flag[0] == "r":
		print("notice : Transforming tensor into user defined coordinate system.")

		if nargin == rot_flag_pos:
			raise ValueError("Vector(s) is(are) missing.")
		
		vectors = list(args[rot_flag_pos + 1:])

		if len(vectors) == 1:
			r_x = vectors[0]

			if len(r_x) != 3:
				raise TypeError("Vector format not recognized.")
			
			r_x /= np.linalg.norm(r_x, keepdims=True)
			r_y = np.array([0, 1, 0])
			r_z = np.cross(r_x, r_y)
			r_z /= np.linalg.norm(r_z, keepdims=True)
			r_y = np.cross(r_z, r_x)
			r_y /= np.linalg.norm(r_y, keepdims=True)

		elif len(vectors) == 3:
			r_x, r_y, r_z = [r / np.linalg.norm(r, keepdims=True) for r in vectors]
			# TODO : add check that vectors are orthogonal
		else:
			raise TypeError("Vector format not recognized.")

		rot_mat[:, 0, :], rot_mat[:, 1, :], rot_mat[:, 2, :] = [np.ones((len(p_times), 1)) * r for r in [r_x, r_y, r_z]]

	else:
		raise ValueError("Flag is not recognized.")

	p_tensor_p = np.zeros((len(p_times), 3, 3))

	for ii in range(len(p_times)):
		rot_temp = np.squeeze(rot_mat[ii, :, :])

		p_tensor_p[ii, :, :] = np.matmul(np.matmul(rot_temp, np.squeeze(p_tensor[ii, :, :])), np.transpose(rot_temp))

	if ppeq:
		print("notice : Rotating tensor so perpendicular diagonal components are equal.")
		thetas = 0.5 * np.arctan((p_tensor_p[:, 2, 2] - p_tensor_p[:, 1, 1]) / (2 * p_tensor_p[:, 1, 2]))
		
		for ii, theta in enumerate(thetas):
			if np.isnan(theta):
				theta = 0

			rot_temp = np.array([[1, 0, 0], [0, np.cos(theta), np.sin(theta)], [0, -np.sin(theta), np.cos(theta)]])

			p_tensor_p[ii, :, :] = np.matmul(np.matmul(rot_temp, np.squeeze(p_tensor_p[ii, :, :])),\
											 np.transpose(rot_temp))

	if qqeq:
		print("notice : Rotating tensor so perpendicular diagonal components are most unequal.")
		thetas = 0.5 * np.arctan((2 * p_tensor_p[:, 1, 2]) / (p_tensor_p[:, 2, 2] - p_tensor_p[:, 1, 1]))

		for ii, theta in enumerate(thetas):
			rot_temp = np.array([[1, 0, 0], [0, np.cos(theta), -np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])

			p_tensor_p[ii, :, :] = np.matmul(np.matmul(rot_temp, np.squeeze(p_tensor_p[ii, :, :])),\
											 np.transpose(rot_temp))

	# Construct output
	p = ts_tensor_xyz(p_times, p_tensor_p)

	try:
		p.attrs["units"] = args[0].attrs["units"]
	except KeyError:
		pass

	return p
