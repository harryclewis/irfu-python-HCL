import warnings
import numpy as np
import xarray as xr

from .get_feeps_active_eyes import get_feeps_active_eyes
from .get_feeps_oneeye import get_feeps_oneeye


# noinspection PyUnboundLocalVariable
def get_feeps_omni(tar_var="flux_ion_brst_l2", mms_id=1, tint=None):

    data_units = tar_var.split("_")[0]

    var = {"dtype": tar_var.split("_")[1], "tmmode": tar_var.split("_")[2], "lev": tar_var.split("_")[3]}

    specie = var["dtype"][0]

    if var["dtype"] == "electron":
        energies = np.array([33.2, 51.90, 70.6, 89.4, 107.1, 125.2, 146.5, 171.3,
                    200.2, 234.0, 273.4, 319.4, 373.2, 436.0, 509.2, 575.8])
    else:
        energies = np.array([57.9, 76.8, 95.4, 114.1, 133.0, 153.7, 177.6,
                    205.1, 236.7, 273.2, 315.4, 363.8, 419.7, 484.2,  558.6, 609.9])

    # set unique energy bins per spacecraft; from DLT on 31 Jan 2017
    e_corr = {"e": [14.0, -1.0, -3.0, -3.0], "i": [0.0, 0.0, 0.0, 0.0]}

    g_fact = {"e": [1.0, 1.0, 1.0, 1.0], "i": [0.84, 1.0, 1.0, 1.0]}

    energies += e_corr[specie][mms_id - 1]

    active_eyes = get_feeps_active_eyes(var, tint, mms_id)

    # percent error around energy bin center to accept data for averaging; 
    # anything outside of energies[i] +/- en_chk*energies[i] will be changed 
    # to NAN and not averaged   
    # en_chk = 0.1

    top_sensors = active_eyes["top"]
    bot_sensors = active_eyes["bottom"]

    top_it, bot_it = [{}, {}]

    for tsen in top_sensors:
        top = get_feeps_oneeye(f"{data_units}{var['dtype'][0]}_{var['tmmode']}_{var['lev']}", mms_id, f"top-{tsen:d}",
                               tint)

        mask = get_feeps_oneeye(f"mask{var['dtype'][0]}_{var['tmmode']}_{var['lev']}", mms_id, f"top-{tsen:d}", tint)

        mask.data = np.tile(mask.data[:, 0], (mask.shape[1], 1)).T

        top.data[mask.data == 1] = np.nan

        top_it[tsen] = top

    for bsen in bot_sensors:
        bot = get_feeps_oneeye(f"{data_units}{var['dtype'][0]}_{var['tmmode']}_{var['lev']}", mms_id,
                               f"bottom-{bsen:d}", tint)

        mask = get_feeps_oneeye(f"mask{var['dtype'][0]}_{var['tmmode']}_{var['lev']}", mms_id, f"bottom-{bsen:d}", tint)

        mask.data = np.tile(mask.data[:, 0], (mask.shape[1], 1)).T

        bot.data[mask.data == 1] = np.nan

        bot_it[bsen] = bot

    dalleyes = np.empty((top.shape[0], top.shape[1], len(top_sensors) + len(bot_sensors)))

    for i, tsen in enumerate(top_sensors):
        dalleyes[..., i] = top_it[tsen]

    for i, bsen in enumerate(bot_sensors):
        dalleyes[..., len(top_sensors) + i] = bot_it[tsen]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        flux_omni = np.nanmean(dalleyes, axis=2)

    flux_omni *= g_fact[specie][mms_id - 1]

    time = top_it[top_sensors[0]]

    out = xr.DataArray(flux_omni[:], coords=[time, energies], dims=["time", "energy"])

    return out
