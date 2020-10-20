#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
zoom.py

@author : Louis RICHARD
"""

from matplotlib.transforms import Bbox, TransformedBbox, blended_transform_factory
from mpl_toolkits.axes_grid1.inset_locator import BboxPatch, BboxConnector, BboxConnectorPatch

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def connect_bbox(bbox1, bbox2, loc1a, loc2a, loc1b, loc2b, prop_lines, prop_patches=None):
	if prop_patches is None:
		prop_patches = {**prop_lines, "alpha": prop_lines.get("alpha", 1) * 0}

	c1 = BboxConnector(bbox1, bbox2, loc1=loc1a, loc2=loc2a, **prop_lines)
	c1.set_clip_on(False)
	c2 = BboxConnector(bbox1, bbox2, loc1=loc1b, loc2=loc2b, **prop_lines)
	c2.set_clip_on(False)

	bbox_patch1 = BboxPatch(bbox1, **prop_patches)
	bbox_patch2 = BboxPatch(bbox2, **prop_patches)

	p = BboxConnectorPatch(bbox1, bbox2, loc1a=loc1a, loc2a=loc2a, loc1b=loc1b, loc2b=loc2b, **prop_patches)

	p.set_clip_on(False)

	return c1, c2, bbox_patch1, bbox_patch2, p


def zoom(ax1, ax2, **kwargs):
	"""Similar to zoom_effect01.  The xmin & xmax will be taken from the ax1.viewLim.

	Parameters
	----------
	ax1 : axs
		The main axes.

	ax2 : axs
		The zoomed axes.

	"""

	tt = ax1.transScale + (ax1.transLimits + ax2.transAxes)
	trans = blended_transform_factory(ax2.transData, tt)

	mybbox1 = ax1.bbox
	mybbox2 = TransformedBbox(ax1.viewLim, trans)

	prop_patches = {**kwargs, "ec": "none", "alpha": 0.2}

	c1, c2, bbox_patch1, bbox_patch2, p = connect_bbox(mybbox1, mybbox2, loc1a=2, loc2a=3, loc1b=1, loc2b=4,
													   prop_lines=kwargs)

	ax1.add_patch(bbox_patch1)
	ax2.add_patch(bbox_patch2)
	ax2.add_patch(c1)
	ax2.add_patch(c2)
	ax2.add_patch(p)

	return
