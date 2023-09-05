class ParamMetadata:
    def __init__(
        self,
        name: str,
        title: str,
        vmin: float | None,
        vmax: float | None,
        colors: str,
        outputBaseName: str,
        varName: str,
        coef: float = 1.0,
        skipFirst: bool = False,
        combine: str = "magnitude",
    ):
        self.name = name
        self.title = title
        self.vmin = vmin
        self.vmax = vmax
        self.colors = colors
        self.outputBaseName = outputBaseName
        self.varName = varName
        self.coef = coef
        self.skipFirst = skipFirst
        self.combine = combine


# pfd
e_y = ParamMetadata("e_y", "$E_y$", None, None, "RdBu", "pfd", "ey_ec")
e_z = ParamMetadata("e_z", "$E_z$", None, None, "RdBu", "pfd", "ez_ec")
e_rho = ParamMetadata("e_rho", "$E_\\rho$", None, None, "RdBu", "pfd", ["ey_ec", "ez_ec"], combine="radial")
e_phi = ParamMetadata("e_phi", "$E_\\phi$", None, None, "RdBu", "pfd", ["ey_ec", "ez_ec"], combine="azimuthal")
b_x = ParamMetadata("b_x", "$B_x$", None, None, "RdBu", "pfd", "hx_fc")
b_y = ParamMetadata("b_y", "$B_y$", None, None, "RdBu", "pfd", "hy_fc", skipFirst=True)
b_z = ParamMetadata("b_z", "$B_z$", None, None, "RdBu", "pfd", "hz_fc", skipFirst=True)
b_rho = ParamMetadata("b_rho", "$B_\\rho$", None, None, "RdBu", "pfd", ["hy_fc", "hz_fc"], combine="radial")
b_phi = ParamMetadata("b_phi", "$B_\\phi$", None, None, "RdBu", "pfd", ["hy_fc", "hz_fc"], combine="azimuthal")
j_y = ParamMetadata("j_y", "$J_y$", None, None, "RdBu", "pfd", "jy_ec", skipFirst=True)
j_z = ParamMetadata("j_z", "$J_z$", None, None, "RdBu", "pfd", "jz_ec", skipFirst=True)
j_rho = ParamMetadata("j_rho", "$J_\\rho$", None, None, "RdBu", "pfd", ["jy_ec", "jz_ec"], skipFirst=True, combine="radial")
j_phi = ParamMetadata("j_phi", "$J_\\phi$", None, None, "RdBu", "pfd", ["jy_ec", "jz_ec"], skipFirst=True, combine="azimuthal")

# pfd_moments
ne = ParamMetadata("ne", "$n_e$", 0, None, "inferno", "pfd_moments", "rho_e", coef=-1)
ni = ParamMetadata("ni", "$n_i$", 0, None, "inferno", "pfd_moments", "rho_i")
te = ParamMetadata("te", "$T_e$", 0, None, "inferno", "pfd_moments", ["tyy_e", "tzz_e"], combine="sum")
te_x = ParamMetadata("te_x", "$T_e$", 0, None, "inferno", "pfd_moments", "txx_e")
ti = ParamMetadata("ti", "$T_i$", 0, None, "inferno", "pfd_moments", ["tyy_i", "tzz_i"], combine="sum")
ve_rho = ParamMetadata("ve_rho", "$v_{e,\\rho}$", -0.0005, 0.0005, "RdBu", "pfd_moments", ["jy_e", "jz_e"], combine="radial", coef=-1)
ve_phi = ParamMetadata("ve_phi", "$v_{e,\\phi}$", -0.0005, 0.0005, "RdBu", "pfd_moments", ["jy_e", "jz_e"], combine="azimuthal", coef=-1)
ve_x = ParamMetadata("ve_x", "$v_{e,x}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jx_e", coef=-1)
ve_y = ParamMetadata("ve_y", "$v_{e,y}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jy_e", coef=-1)
ve_z = ParamMetadata("ve_z", "$v_{e,z}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jz_e", coef=-1)
vi_phi = ParamMetadata("vi_phi", "$v_{i,\\phi}$", None, None, "RdBu", "pfd_moments", ["jy_i", "jz_i"], combine="azimuthal")

# gauss
gauss_dive = ParamMetadata("gauss_dive", "Div E", -1.5, 1.5, "RdBu", "gauss", "dive")
gauss_rho = ParamMetadata("gauss_rho", "Charge Density", -1.5, 1.5, "RdBu", "gauss", "rho")
gauss_error = ParamMetadata("gauss_error", "Gauss Error", -0.005, 0.005, "RdBu", "gauss", ["dive", "rho"], combine="difference")
