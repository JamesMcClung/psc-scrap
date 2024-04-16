from typing import Callable as _Callable, ParamSpec as _ParamSpec

from xarray import DataArray as _DataArray

from .typing import PrefixBp as _PrefixBp, BpVariableName as _BpVariableName
from .variable import Variable as _Variable

# stuff for data mappers

_P = _ParamSpec("_P")

_MultiVarMapper = _Callable[[list[_DataArray]], _DataArray]
_HoleCenter = tuple[float, float]
_ShiftedMultiVarMapper = _Callable[[list[_DataArray], _HoleCenter], _DataArray]


def _negated(data_mapper: _Callable[_P, _DataArray]) -> _Callable[_P, _DataArray]:
    def map_data(*args: _P.args, **kwargs: _P.kwargs) -> _DataArray:
        return -data_mapper(*args, **kwargs)

    return map_data


def _get_shifted_coords(original_coords: dict[str, _DataArray], hole_center: _HoleCenter) -> tuple[_DataArray, _DataArray, _DataArray]:
    """Returns `(shifted_axis_y, shifted_axis_z, shifted_grid_rho)`"""
    shifted_axis_y = original_coords["y"] - hole_center[0]
    shifted_axis_z = original_coords["z"] - hole_center[1]
    shifted_grid_rho = (shifted_axis_y**2 + shifted_axis_z**2) ** 0.5
    return shifted_axis_y, shifted_axis_z, shifted_grid_rho


# data mappers


def _identity(datas: list[_DataArray]) -> _DataArray:
    return datas[0]


def _magnitude(datas: list[_DataArray]) -> _DataArray:
    return sum(data**2 for data in datas) ** 0.5


def _sum(datas: list[_DataArray]) -> _DataArray:
    return sum(datas)


def _difference(datas: list[_DataArray]) -> _DataArray:
    return datas[0] - datas[1]


def _radial_component(datas: list[_DataArray], hole_center: _HoleCenter = (0, 0)) -> _DataArray:
    shifted_axis_y, shifted_axis_z, shifted_grid_rho = _get_shifted_coords(datas[0].coords, hole_center)
    raw_data = (datas[0] * shifted_axis_y + datas[1] * shifted_axis_z) / shifted_grid_rho
    return raw_data.fillna(0)


def _azimuthal_component(datas: list[_DataArray], hole_center: _HoleCenter = (0, 0)) -> _DataArray:
    shifted_axis_y, shifted_axis_z, shifted_grid_rho = _get_shifted_coords(datas[0].coords, hole_center)
    raw_data = (-datas[0] * shifted_axis_z + datas[1] * shifted_axis_y) / shifted_grid_rho
    return raw_data.fillna(0)


class FieldVariable(_Variable):
    def __init__(
        self,
        name: str,
        latex: str,
        prefix: _PrefixBp,
        bp_variable_names: list[_BpVariableName],
        val_bounds: tuple[float | None, float | None] = (None, None),
        data_mapper: _MultiVarMapper | _ShiftedMultiVarMapper = _identity,
        shift_hole_center: bool = False,
    ) -> None:
        # "pfd.*.bp" files are written at t=0, but the j components are all 0s because PSC doesn't calculate them until it does a time step
        skip_first_step = prefix == "pfd" and any(var_name.startswith("j") for var_name in bp_variable_names)
        cmap_name = "inferno" if 0 in val_bounds else "RdBu_r"
        super().__init__(name, latex, prefix, skip_first_step, cmap_name)

        self.bp_variable_names = bp_variable_names
        self.val_bounds = val_bounds
        self.data_mapper = data_mapper
        self.shift_hole_center = shift_hole_center


# pfd
e_x = FieldVariable("e_x", "E_x", "pfd", ["ex_ec"])
e_y = FieldVariable("e_y", "E_y", "pfd", ["ey_ec"])
e_z = FieldVariable("e_z", "E_z", "pfd", ["ez_ec"])
e_rho = FieldVariable("e_rho", "E_\\rho", "pfd", ["ey_ec", "ez_ec"], data_mapper=_radial_component)
e_phi = FieldVariable("e_phi", "E_\\phi", "pfd", ["ey_ec", "ez_ec"], data_mapper=_azimuthal_component, shift_hole_center=True)
e = FieldVariable("e", "|E|", "pfd", ["ey_ec", "ez_ec"], val_bounds=(0, None), data_mapper=_magnitude)
b_x = FieldVariable("b_x", "B_x", "pfd", ["hx_fc"])
b_y = FieldVariable("b_y", "B_y", "pfd", ["hy_fc"])
b_z = FieldVariable("b_z", "B_z", "pfd", ["hz_fc"])
b_rho = FieldVariable("b_rho", "B_\\rho", "pfd", ["hy_fc", "hz_fc"], data_mapper=_radial_component)
b_phi = FieldVariable("b_phi", "B_\\phi", "pfd", ["hy_fc", "hz_fc"], data_mapper=_azimuthal_component)
b = FieldVariable("b", "|B|", "pfd", ["hy_fc", "hz_fc"], val_bounds=(0, None), data_mapper=_magnitude)
j_x = FieldVariable("j_x", "J_x", "pfd", ["jx_ec"])
j_y = FieldVariable("j_y", "J_y", "pfd", ["jy_ec"])
j_z = FieldVariable("j_z", "J_z", "pfd", ["jz_ec"])
j_rho = FieldVariable("j_rho", "J_\\rho", "pfd", ["jy_ec", "jz_ec"], data_mapper=_radial_component)
j_phi = FieldVariable("j_phi", "J_\\phi", "pfd", ["jy_ec", "jz_ec"], data_mapper=_azimuthal_component)
j = FieldVariable("j", "|J|", "pfd", ["jy_ec", "jz_ec"], val_bounds=(0, None), data_mapper=_magnitude)

# pfd_moments
ne = FieldVariable("ne", "n_e", "pfd_moments", ["rho_e"], val_bounds=(0, None), data_mapper=_negated(_identity))
ni = FieldVariable("ni", "n_i", "pfd_moments", ["rho_i"], val_bounds=(0, None))
te = FieldVariable("te", "T_e", "pfd_moments", ["tyy_e", "tzz_e"], val_bounds=(0, None), data_mapper=_sum)
te_x = FieldVariable("te_x", "T_{e,x}", "pfd_moments", "txx_e", val_bounds=(0, None))
ti = FieldVariable("ti", "T_i", "pfd_moments", ["tyy_i", "tzz_i"], val_bounds=(0, None), data_mapper=_sum)
ti_x = FieldVariable("ti_x", "T_{i,x}", "pfd_moments", ["txx_i"], val_bounds=(0, None))
ve_x = FieldVariable("ve_x", "v_{e,x}", "pfd_moments", ["jx_e"], data_mapper=_negated(_identity))
ve_y = FieldVariable("ve_y", "v_{e,y}", "pfd_moments", ["jy_e"], data_mapper=_negated(_identity))
ve_z = FieldVariable("ve_z", "v_{e,z}", "pfd_moments", ["jz_e"], data_mapper=_negated(_identity))
ve_rho = FieldVariable("ve_rho", "v_{e,\\rho}", "pfd_moments", ["jy_e", "jz_e"], data_mapper=_negated(_radial_component))
ve_phi = FieldVariable("ve_phi", "v_{e,\\phi}", "pfd_moments", ["jy_e", "jz_e"], data_mapper=_negated(_azimuthal_component))
vi_x = FieldVariable("vi_x", "v_{i,x}", "pfd_moments", ["jx_i"])
vi_y = FieldVariable("vi_y", "v_{i,y}", "pfd_moments", ["jy_i"])
vi_z = FieldVariable("vi_z", "v_{i,z}", "pfd_moments", ["jz_i"])
vi_rho = FieldVariable("vi_rho", "v_{i,\\rho}", "pfd_moments", ["jy_i", "jz_i"], data_mapper=_radial_component)
vi_phi = FieldVariable("vi_phi", "v_{i,\\phi}", "pfd_moments", ["jy_i", "jz_i"], data_mapper=_azimuthal_component)

# gauss
gauss_dive = FieldVariable("gauss_dive", "Div E", "gauss", ["dive"], val_bounds=(-1.5, 1.5))
gauss_rho = FieldVariable("gauss_rho", "Charge Density", "gauss", ["rho"], val_bounds=(-1.5, 1.5))
gauss_error = FieldVariable("gauss_error", "Gauss Error", "gauss", ["dive", "rho"], val_bounds=(-0.0005, 0.0005), data_mapper=_difference)
