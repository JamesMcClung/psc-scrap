from dataclasses import dataclass as _dataclass

from .typing import PrefixBp as _PrefixBp


@_dataclass
class FieldVariable:
    name: str
    latex: str
    colors: str
    prefix_bp: _PrefixBp
    varName: str
    val_bounds: tuple[float | None, float | None] = (None, None)
    coef: float = 1.0
    skipFirst: bool = False
    recenter: bool = False
    combine: str = "magnitude"


# pfd
e_x = FieldVariable("e_x", "$E_x$", "RdBu_r", "pfd", "ex_ec", skipFirst=True)
e_y = FieldVariable("e_y", "$E_y$", "RdBu_r", "pfd", "ey_ec", skipFirst=True)
e_z = FieldVariable("e_z", "$E_z$", "RdBu_r", "pfd", "ez_ec", skipFirst=True)
e_rho = FieldVariable("e_rho", "$E_\\rho$", "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="radial", skipFirst=True)
e_phi = FieldVariable("e_phi", "$E_\\phi$", "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="azimuthal", skipFirst=True, recenter=True)
e = FieldVariable("e", "$|E|$", "inferno", "pfd", ["ey_ec", "ez_ec"], val_bounds=(0, None), combine="magnitude", skipFirst=True)
b_x = FieldVariable("b_x", "$B_x$", "RdBu_r", "pfd", "hx_fc", skipFirst=True)
b_y = FieldVariable("b_y", "$B_y$", "RdBu_r", "pfd", "hy_fc", skipFirst=True)
b_z = FieldVariable("b_z", "$B_z$", "RdBu_r", "pfd", "hz_fc", skipFirst=True)
b_rho = FieldVariable("b_rho", "$B_\\rho$", "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="radial", skipFirst=True)
b_phi = FieldVariable("b_phi", "$B_\\phi$", "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="azimuthal", skipFirst=True)
b = FieldVariable("b", "$|B|$", "inferno", "pfd", ["hy_fc", "hz_fc"], val_bounds=(0, None), combine="magnitude", skipFirst=True)
j_x = FieldVariable("j_x", "$J_x$", "RdBu_r", "pfd", "jx_ec", skipFirst=True)
j_y = FieldVariable("j_y", "$J_y$", "RdBu_r", "pfd", "jy_ec", skipFirst=True)
j_z = FieldVariable("j_z", "$J_z$", "RdBu_r", "pfd", "jz_ec", skipFirst=True)
j_rho = FieldVariable("j_rho", "$J_\\rho$", "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="radial", skipFirst=True)
j_phi = FieldVariable("j_phi", "$J_\\phi$", "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="azimuthal", skipFirst=True)
j = FieldVariable("j", "$|J|$", "inferno", "pfd", ["jy_ec", "jz_ec"], val_bounds=(0, None), combine="magnitude", skipFirst=True)

# pfd_moments
ne = FieldVariable("ne", "$n_e$", "inferno", "pfd_moments", "rho_e", val_bounds=(0, None), coef=-1)
ni = FieldVariable("ni", "$n_i$", "inferno", "pfd_moments", "rho_i", val_bounds=(0, None))
te = FieldVariable("te", "$T_e$", "inferno", "pfd_moments", ["tyy_e", "tzz_e"], val_bounds=(0, None), combine="sum")
te_x = FieldVariable("te_x", "$T_{e,x}$", "inferno", "pfd_moments", "txx_e", val_bounds=(0, None))
ti = FieldVariable("ti", "$T_i$", "inferno", "pfd_moments", ["tyy_i", "tzz_i"], val_bounds=(0, None), combine="sum")
ti_x = FieldVariable("ti_x", "$T_{i,x}$", "inferno", "pfd_moments", "txx_i", val_bounds=(0, None))
ve_x = FieldVariable("ve_x", "$v_{e,x}$", "RdBu_r", "pfd_moments", "jx_e", val_bounds=(-0.0005, 0.0005), coef=-1)
ve_y = FieldVariable("ve_y", "$v_{e,y}$", "RdBu_r", "pfd_moments", "jy_e", val_bounds=(-0.0005, 0.0005), coef=-1)
ve_z = FieldVariable("ve_z", "$v_{e,z}$", "RdBu_r", "pfd_moments", "jz_e", val_bounds=(-0.0005, 0.0005), coef=-1)
ve_rho = FieldVariable("ve_rho", "$v_{e,\\rho}$", "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], val_bounds=(-0.0005, 0.0005), combine="radial", coef=-1)
ve_phi = FieldVariable("ve_phi", "$v_{e,\\phi}$", "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], val_bounds=(-0.0005, 0.0005), combine="azimuthal", coef=-1)
vi_x = FieldVariable("vi_x", "$v_{i,x}$", "RdBu_r", "pfd_moments", "jx_i", val_bounds=(-0.0005, 0.0005))
vi_y = FieldVariable("vi_y", "$v_{i,y}$", "RdBu_r", "pfd_moments", "jy_i", val_bounds=(-0.0005, 0.0005))
vi_z = FieldVariable("vi_z", "$v_{i,z}$", "RdBu_r", "pfd_moments", "jz_i", val_bounds=(-0.0005, 0.0005))
vi_rho = FieldVariable("vi_rho", "$v_{i,\\rho}$", "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="radial", val_bounds=(-0.0005, 0.0005))
vi_phi = FieldVariable("vi_phi", "$v_{i,\\phi}$", "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="azimuthal", val_bounds=(-0.0005, 0.0005))

# gauss
gauss_dive = FieldVariable("gauss_dive", "Div E", "RdBu_r", "gauss", "dive", val_bounds=(-1.5, 1.5))
gauss_rho = FieldVariable("gauss_rho", "Charge Density", "RdBu_r", "gauss", "rho", val_bounds=(-1.5, 1.5))
gauss_error = FieldVariable("gauss_error", "Gauss Error", "RdBu_r", "gauss", ["dive", "rho"], val_bounds=(-0.0005, 0.0005), combine="difference")
