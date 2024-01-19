from dataclasses import dataclass as _dataclass

from .typing import PrefixBP as _PrefixBP


@_dataclass
class FieldVariable:
    name: str
    latex: str
    vmin: float | None
    vmax: float | None
    colors: str
    prefix_bp: _PrefixBP
    varName: str
    coef: float = 1.0
    skipFirst: bool = False
    recenter: bool = False
    combine: str = "magnitude"


# pfd
e_x = FieldVariable("e_x", "$E_x$", None, None, "RdBu_r", "pfd", "ex_ec", skipFirst=True)
e_y = FieldVariable("e_y", "$E_y$", None, None, "RdBu_r", "pfd", "ey_ec", skipFirst=True)
e_z = FieldVariable("e_z", "$E_z$", None, None, "RdBu_r", "pfd", "ez_ec", skipFirst=True)
e_rho = FieldVariable("e_rho", "$E_\\rho$", None, None, "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="radial", skipFirst=True)
e_phi = FieldVariable("e_phi", "$E_\\phi$", None, None, "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="azimuthal", skipFirst=True, recenter=True)
e = FieldVariable("e", "$|E|$", 0, None, "inferno", "pfd", ["ey_ec", "ez_ec"], combine="magnitude", skipFirst=True)
b_x = FieldVariable("b_x", "$B_x$", None, None, "RdBu_r", "pfd", "hx_fc", skipFirst=True)
b_y = FieldVariable("b_y", "$B_y$", None, None, "RdBu_r", "pfd", "hy_fc", skipFirst=True)
b_z = FieldVariable("b_z", "$B_z$", None, None, "RdBu_r", "pfd", "hz_fc", skipFirst=True)
b_rho = FieldVariable("b_rho", "$B_\\rho$", None, None, "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="radial", skipFirst=True)
b_phi = FieldVariable("b_phi", "$B_\\phi$", None, None, "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="azimuthal", skipFirst=True)
b = FieldVariable("b", "$|B|$", 0, None, "inferno", "pfd", ["hy_fc", "hz_fc"], combine="magnitude", skipFirst=True)
j_x = FieldVariable("j_x", "$J_x$", None, None, "RdBu_r", "pfd", "jx_ec", skipFirst=True)
j_y = FieldVariable("j_y", "$J_y$", None, None, "RdBu_r", "pfd", "jy_ec", skipFirst=True)
j_z = FieldVariable("j_z", "$J_z$", None, None, "RdBu_r", "pfd", "jz_ec", skipFirst=True)
j_rho = FieldVariable("j_rho", "$J_\\rho$", None, None, "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="radial", skipFirst=True)
j_phi = FieldVariable("j_phi", "$J_\\phi$", None, None, "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="azimuthal", skipFirst=True)
j = FieldVariable("j", "$|J|$", 0, None, "inferno", "pfd", ["jy_ec", "jz_ec"], combine="magnitude", skipFirst=True)

# pfd_moments
ne = FieldVariable("ne", "$n_e$", 0, None, "inferno", "pfd_moments", "rho_e", coef=-1)
ni = FieldVariable("ni", "$n_i$", 0, None, "inferno", "pfd_moments", "rho_i")
te = FieldVariable("te", "$T_e$", 0, None, "inferno", "pfd_moments", ["tyy_e", "tzz_e"], combine="sum")
te_x = FieldVariable("te_x", "$T_{e,x}$", 0, None, "inferno", "pfd_moments", "txx_e")
ti = FieldVariable("ti", "$T_i$", 0, None, "inferno", "pfd_moments", ["tyy_i", "tzz_i"], combine="sum")
ti_x = FieldVariable("ti_x", "$T_{i,x}$", 0, None, "inferno", "pfd_moments", "txx_i")
ve_x = FieldVariable("ve_x", "$v_{e,x}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jx_e", coef=-1)
ve_y = FieldVariable("ve_y", "$v_{e,y}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jy_e", coef=-1)
ve_z = FieldVariable("ve_z", "$v_{e,z}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jz_e", coef=-1)
ve_rho = FieldVariable("ve_rho", "$v_{e,\\rho}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], combine="radial", coef=-1)
ve_phi = FieldVariable("ve_phi", "$v_{e,\\phi}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], combine="azimuthal", coef=-1)
vi_x = FieldVariable("vi_x", "$v_{i,x}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jx_i")
vi_y = FieldVariable("vi_y", "$v_{i,y}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jy_i")
vi_z = FieldVariable("vi_z", "$v_{i,z}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jz_i")
vi_rho = FieldVariable("vi_rho", "$v_{i,\\rho}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="radial")
vi_phi = FieldVariable("vi_phi", "$v_{i,\\phi}$", None, None, "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="azimuthal")

# gauss
gauss_dive = FieldVariable("gauss_dive", "Div E", -1.5, 1.5, "RdBu_r", "gauss", "dive")
gauss_rho = FieldVariable("gauss_rho", "Charge Density", -1.5, 1.5, "RdBu_r", "gauss", "rho")
gauss_error = FieldVariable("gauss_error", "Gauss Error", -0.005, 0.005, "RdBu_r", "gauss", ["dive", "rho"], combine="difference")
