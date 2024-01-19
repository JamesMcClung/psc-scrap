__all__ = ["PrefixBP", "PrefixH5", "Centering", "Dim", "H5PrtVariableName", "H5WrapperVariableName"]

from typing import Literal


PrefixBP = Literal["pfd", "pfd_moments", "gauss"]

PrefixH5 = Literal["prt"]
H5PrtVariableName = Literal["x", "y", "z", "px", "py", "pz", "q", "m", "w", "tag", "id"]
H5WrapperVariableName = H5PrtVariableName | Literal["rho", "phi", "prho", "pphi", "vx", "vy", "vz", "vrho", "vphi"]

Species = Literal["e", "i"]
Centering = Literal["cc", "nc"]
Dim = Literal["x", "y", "z"]
