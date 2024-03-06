__all__ = ["PrefixBp", "PrefixH5", "Centering", "Dim", "BpVariableName", "H5PrtVariableName", "H5WrapperVariableName"]

from typing import Literal


PrefixBp = Literal["pfd", "pfd_moments", "gauss"]
BpPfdVariableName = Literal["ex_ec", "ey_ec", "ez_ec", "hx_fc", "hy_fc", "hz_fc", "jx_ec", "jy_ec", "jz_ec"]
BpPfdMomentsVariableName = Literal["rho_e", "jx_e", "jy_e", "jz_e", "px_e", "py_e", "pz_e", "txx_e", "tyy_e", "tzz_e", "txy_e", "tyz_e", "tzx_e", "rho_i", "jx_i", "jy_i", "jz_i", "px_i", "py_i", "pz_i", "txx_i", "tyy_i", "tzz_i", "txy_i", "tyz_i", "tzx_i"]
BpGaussVariableName = Literal["dive", "rho"]
BpVariableName = BpPfdVariableName | BpPfdMomentsVariableName | BpGaussVariableName

PrefixH5 = Literal["prt"]
H5PrtVariableName = Literal["x", "y", "z", "px", "py", "pz", "q", "m", "w", "tag", "id"]
H5WrapperVariableName = H5PrtVariableName | Literal["rho", "phi", "prho", "pphi", "vx", "vy", "vz", "vrho", "vphi"]

Species = Literal["e", "i"]
Centering = Literal["cc", "nc"]
Dim = Literal["x", "y", "z"]
