from math import pi as _pi

from .typing import H5WrapperVariableName as _H5WrapperVariableName
from .variable import Variable as _Variable


class ParticleVariable(_Variable):
    def __init__(
        self,
        name: str,
        latex: str,
        h5_variable_name: _H5WrapperVariableName,
        val_bounds: tuple[float | None, float | None] = (None, None),
    ) -> None:
        super().__init__(name, latex, "prt", False, "Reds")
        self.h5_variable_name = h5_variable_name
        self.val_bounds = val_bounds


x = ParticleVariable("x", "x", "x")
y = ParticleVariable("y", "y", "y")
z = ParticleVariable("z", "z", "z")
rho = ParticleVariable("rho", "\\rho", "rho", val_bounds=(0, None))
phi = ParticleVariable("phi", "\\phi", "phi", val_bounds=(-_pi, _pi))

p_x = ParticleVariable("p_x", "p_x", "px", val_bounds=(-0.003, 0.003))
p_y = ParticleVariable("p_y", "p_y", "py", val_bounds=(-0.003, 0.003))
p_z = ParticleVariable("p_z", "p_z", "pz", val_bounds=(-0.003, 0.003))
p_rho = ParticleVariable("p_rho", "p_\\rho", "prho", val_bounds=(-0.003, 0.003))
p_phi = ParticleVariable("p_phi", "p_\\phi", "pphi", val_bounds=(-0.003, 0.003))

v_x = ParticleVariable("v_x", "v_x", "vx", val_bounds=(-0.003, 0.003))
v_y = ParticleVariable("v_y", "v_y", "vy", val_bounds=(-0.003, 0.003))
v_z = ParticleVariable("v_z", "v_z", "vz", val_bounds=(-0.003, 0.003))
v_rho = ParticleVariable("v_rho", "v_\\rho", "vrho", val_bounds=(-0.003, 0.003))
v_phi = ParticleVariable("v_phi", "v_\\phi", "vphi", val_bounds=(-0.003, 0.003))

m = ParticleVariable("m", "m", "m")
q = ParticleVariable("q", "q", "q")
