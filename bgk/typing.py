__all__ = ["PrefixBP", "PrefixH5", "Centering", "Dim"]

from typing import Literal


PrefixBP = Literal["pfd", "pfd_moments", "gauss"]
PrefixH5 = Literal["prt"]

Centering = Literal["cc", "nc"]
Dim = Literal["x", "y", "z"]
