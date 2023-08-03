class ParamMetadata:
    def __init__(self, title, vmin, vmax, colors, outputBaseName, varName, coef=1, skipFirst=False, combine="magnitude"):
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
e_y = ParamMetadata("$E_y$", None, None, "RdBu", "pfd", "ey_ec")
e_z = ParamMetadata("$E_z$", None, None, "RdBu", "pfd", "ez_ec")
e_rho = ParamMetadata("$E_\\rho$", None, None, "RdBu", "pfd", ["ey_ec", "ez_ec"], combine="radial")
e_phi = ParamMetadata("$E_\\phi$", None, None, "RdBu", "pfd", ["ey_ec", "ez_ec"], combine="azimuthal")
b_x = ParamMetadata("$B_x$", None, None, "RdBu", "pfd", "hx_fc")
b_y = ParamMetadata("$B_y$", None, None, "RdBu", "pfd", "hy_fc", skipFirst=True)
b_z = ParamMetadata("$B_z$", None, None, "RdBu", "pfd", "hz_fc", skipFirst=True)
b_rho = ParamMetadata("$B_\\rho$", None, None, "RdBu", "pfd", ["hy_fc", "hz_fc"], combine="radial")
b_phi = ParamMetadata("$B_\\phi$", None, None, "RdBu", "pfd", ["hy_fc", "hz_fc"], combine="azimuthal")
j_y = ParamMetadata("$J_y$", None, None, "RdBu", "pfd", "jy_ec", skipFirst=True)
j_z = ParamMetadata("$J_z$", None, None, "RdBu", "pfd", "jz_ec", skipFirst=True)
j_rho = ParamMetadata("$J_\\rho$", None, None, "RdBu", "pfd", ["jy_ec", "jz_ec"], skipFirst=True, combine="radial")
j_phi = ParamMetadata("$J_\\phi$", None, None, "RdBu", "pfd", ["jy_ec", "jz_ec"], skipFirst=True, combine="azimuthal")

# pfd_moments
ne = ParamMetadata("$n_e$", 0, None, "inferno", "pfd_moments", "rho_e", coef=-1)
ni = ParamMetadata("$n_i$", 0, None, "inferno", "pfd_moments", "rho_i")
te = ParamMetadata("$T_e$", 0, None, "inferno", "pfd_moments", ["tyy_e", "tzz_e"], combine="sum")
te_x = ParamMetadata("$T_e$", 0, None, "inferno", "pfd_moments", "txx_e")
ti = ParamMetadata("$T_i$", 0, None, "inferno", "pfd_moments", ["tyy_i", "tzz_i"], combine="sum")
ve_rho = ParamMetadata("$v_{e,\\rho}$", -0.0005, 0.0005, "RdBu", "pfd_moments", ["jy_e", "jz_e"], combine="radial", coef=-1)
ve_phi = ParamMetadata("$v_{e,\\phi}$", -0.0005, 0.0005, "RdBu", "pfd_moments", ["jy_e", "jz_e"], combine="azimuthal", coef=-1)
ve_x = ParamMetadata("$v_{e,x}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jx_e", coef=-1)
ve_y = ParamMetadata("$v_{e,y}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jy_e", coef=-1)
ve_z = ParamMetadata("$v_{e,z}$", -0.0005, 0.0005, "RdBu", "pfd_moments", "jz_e", coef=-1)
vi_phi = ParamMetadata("$v_{i,\\phi}$", None, None, "RdBu", "pfd_moments", ["jy_i", "jz_i"], combine="azimuthal")

# gauss
gauss_dive = ParamMetadata("Div E", -1.5, 1.5, "RdBu", "gauss", "dive")
gauss_rho = ParamMetadata("Charge Density", -1.5, 1.5, "RdBu", "gauss", "rho")
gauss_error = ParamMetadata("Gauss Error", -0.005, 0.005, "RdBu", "gauss", ["dive", "rho"], combine="difference")
