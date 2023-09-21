from dataclasses import dataclass

from .backend import PrefixBP


@dataclass
class ParamMetadata:
    name: str
    title: str
    vmin: float | None
    vmax: float | None
    colors: str
    prefix_bp: PrefixBP
    varName: str
    coef: float = 1.0
    skipFirst: bool = False
    combine: str = "magnitude"


# pfd
e_x = ParamMetadata("e_x", "$E_x$", None, None, "RdBu_r", "pfd", "ex_ec")
e_y = ParamMetadata("e_y", "$E_y$", None, None, "RdBu_r", "pfd", "ey_ec")
e_z = ParamMetadata("e_z", "$E_z$", None, None, "RdBu_r", "pfd", "ez_ec")
e_rho = ParamMetadata("e_rho", "$E_\\rho$", None, None, "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="radial")
e_phi = ParamMetadata("e_phi", "$E_\\phi$", None, None, "RdBu_r", "pfd", ["ey_ec", "ez_ec"], combine="azimuthal")
e = ParamMetadata("e", "$|E|$", 0, None, "inferno", "pfd", ["ey_ec", "ez_ec"], combine="magnitude")
b_x = ParamMetadata("b_x", "$B_x$", None, None, "RdBu_r", "pfd", "hx_fc")
b_y = ParamMetadata("b_y", "$B_y$", None, None, "RdBu_r", "pfd", "hy_fc")
b_z = ParamMetadata("b_z", "$B_z$", None, None, "RdBu_r", "pfd", "hz_fc")
b_rho = ParamMetadata("b_rho", "$B_\\rho$", None, None, "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="radial")
b_phi = ParamMetadata("b_phi", "$B_\\phi$", None, None, "RdBu_r", "pfd", ["hy_fc", "hz_fc"], combine="azimuthal")
b = ParamMetadata("b", "$|B|$", 0, None, "inferno", "pfd", ["hy_fc", "hz_fc"], combine="magnitude")
j_x = ParamMetadata("j_x", "$J_x$", None, None, "RdBu_r", "pfd", "jx_ec", skipFirst=True)
j_y = ParamMetadata("j_y", "$J_y$", None, None, "RdBu_r", "pfd", "jy_ec", skipFirst=True)
j_z = ParamMetadata("j_z", "$J_z$", None, None, "RdBu_r", "pfd", "jz_ec", skipFirst=True)
j_rho = ParamMetadata("j_rho", "$J_\\rho$", None, None, "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="radial", skipFirst=True)
j_phi = ParamMetadata("j_phi", "$J_\\phi$", None, None, "RdBu_r", "pfd", ["jy_ec", "jz_ec"], combine="azimuthal", skipFirst=True)
j = ParamMetadata("j", "$|J|$", 0, None, "inferno", "pfd", ["jy_ec", "jz_ec"], combine="magnitude", skipFirst=True)

# pfd_moments
ne = ParamMetadata("ne", "$n_e$", 0, None, "inferno", "pfd_moments", "rho_e", coef=-1)
ni = ParamMetadata("ni", "$n_i$", 0, None, "inferno", "pfd_moments", "rho_i")
te = ParamMetadata("te", "$T_e$", 0, None, "inferno", "pfd_moments", ["tyy_e", "tzz_e"], combine="sum")
te_x = ParamMetadata("te_x", "$T_{e,x}$", 0, None, "inferno", "pfd_moments", "txx_e")
ti = ParamMetadata("ti", "$T_i$", 0, None, "inferno", "pfd_moments", ["tyy_i", "tzz_i"], combine="sum")
ti_x = ParamMetadata("ti_x", "$T_{i,x}$", 0, None, "inferno", "pfd_moments", "txx_i")
ve_x = ParamMetadata("ve_x", "$v_{e,x}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jx_e", coef=-1)
ve_y = ParamMetadata("ve_y", "$v_{e,y}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jy_e", coef=-1)
ve_z = ParamMetadata("ve_z", "$v_{e,z}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jz_e", coef=-1)
ve_rho = ParamMetadata("ve_rho", "$v_{e,\\rho}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], combine="radial", coef=-1)
ve_phi = ParamMetadata("ve_phi", "$v_{e,\\phi}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_e", "jz_e"], combine="azimuthal", coef=-1)
vi_x = ParamMetadata("vi_x", "$v_{i,x}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jx_i")
vi_y = ParamMetadata("vi_y", "$v_{i,y}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jy_i")
vi_z = ParamMetadata("vi_z", "$v_{i,z}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", "jz_i")
vi_rho = ParamMetadata("vi_rho", "$v_{i,\\rho}$", -0.0005, 0.0005, "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="radial")
vi_phi = ParamMetadata("vi_phi", "$v_{i,\\phi}$", None, None, "RdBu_r", "pfd_moments", ["jy_i", "jz_i"], combine="azimuthal")

# gauss
gauss_dive = ParamMetadata("gauss_dive", "Div E", -1.5, 1.5, "RdBu_r", "gauss", "dive")
gauss_rho = ParamMetadata("gauss_rho", "Charge Density", -1.5, 1.5, "RdBu_r", "gauss", "rho")
gauss_error = ParamMetadata("gauss_error", "Gauss Error", -0.005, 0.005, "RdBu_r", "gauss", ["dive", "rho"], combine="difference")
