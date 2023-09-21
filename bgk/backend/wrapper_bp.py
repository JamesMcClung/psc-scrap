__all__ = ["WrapperBP", "load_bp"]

import os
from functools import cached_property
import xarray as xr

from ..typing import PrefixBP, Centering, Dim

# enables xarray to load bp files
import psc


_SPECIES_NAMES = ["e", "i"]
_ENGINE = "pscadios2"


def _get_recenter_dims(prefix_bp: PrefixBP, var_name: str, centering: Centering) -> list[str]:
    if prefix_bp in ["pfd_moments", "gauss"]:
        return [] if centering == "cc" else ["x", "y", "z"]

    recenter_dims = []
    if centering == "cc":
        if var_name in ["jy_ec", "jz_ec", "ey_ec", "ez_ec", "hx_fc"]:
            recenter_dims.append("x")
        if var_name in ["jz_ec", "jx_ec", "ez_ec", "ex_ec", "hy_fc"]:
            recenter_dims.append("y")
        if var_name in ["jx_ec", "jy_ec", "ex_ec", "ey_ec", "hz_fc"]:
            recenter_dims.append("z")
    elif centering == "nc":
        if var_name in ["jx_ec", "ex_ec", "hy_fc", "hz_fc"]:
            recenter_dims.append("x")
        if var_name in ["jy_ec", "ey_ec", "hz_fc", "hx_fc"]:
            recenter_dims.append("y")
        if var_name in ["jz_ec", "ez_ec", "hx_fc", "hy_fc"]:
            recenter_dims.append("z")
    return recenter_dims


def _recenter(data: xr.DataArray, dim: Dim, to_centering: Centering) -> xr.DataArray:
    roll_dir = {"cc": -1, "nc": 1}[to_centering]
    shifted = data.roll(shifts={dim: roll_dir}, roll_coords=False)
    return 0.5 * (data + shifted)


class WrapperBP:
    _prefix_bp: PrefixBP

    lengths: tuple[float, float, float]
    time: float
    step: int

    axis_x: xr.DataArray
    axis_y: xr.DataArray
    axis_z: xr.DataArray

    def __init__(self, ds_raw: xr.Dataset, prefix_bp: PrefixBP) -> None:
        self._ds_raw = ds_raw
        self._prefix_bp = prefix_bp

        self.lengths = tuple(ds_raw.attrs["length"])
        self.time = ds_raw.attrs["time"]
        self.step = ds_raw.attrs["step"]

        self.axis_x = ds_raw.coords["x"]
        self.axis_y = ds_raw.coords["y"]
        self.axis_z = ds_raw.coords["z"]

    @cached_property
    def grid_rho(self) -> xr.DataArray:
        return (self.axis_y**2 + self.axis_z**2) ** 0.5

    def get(self, var_name: str, to_centering: Centering) -> xr.DataArray:
        data = self._ds_raw[var_name]
        for dim in _get_recenter_dims(self._prefix_bp, var_name, to_centering):
            data = _recenter(data, dim, to_centering)
        if len(self.axis_x) == 1:
            # TODO use data.squeeze("x")
            data = data[0, :, :].transpose()  # still not happy about this, but also not sure what it does exactly
            # data = data.squeeze("x")
        return data


def load_bp(path_run: str, prefix_bp: PrefixBP, step: int) -> WrapperBP:
    path = os.path.join(path_run, f"{prefix_bp}.{step:09d}.bp")
    ds_raw = xr.open_dataset(path, engine=_ENGINE, species_names=_SPECIES_NAMES)
    return WrapperBP(ds_raw, prefix_bp)
