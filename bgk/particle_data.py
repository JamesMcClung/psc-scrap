from functools import cached_property

from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import matplotlib.collections as mplc
import numpy as np

from .backend import load_bp, load_h5
from .input_reader import Input
from .params_record import ParamsRecord
from .particle_variables import ParticleVariable, v_phi
from .run_manager import RunManager

__all__ = ["ParticleData"]


##########################


class ParticleData:
    def __init__(self, run_manager: RunManager, initial_variable: ParticleVariable = v_phi) -> None:
        self.run_manager = run_manager
        self.set_variable(initial_variable)

    @property
    def params_record(self) -> ParamsRecord:
        return self.run_manager.params_record

    def read_step(self, step: int) -> None:
        self.time = load_bp(self.run_manager.path_run, "pfd", step).time
        self.data = load_h5(self.run_manager.path_run, "prt", step).drop_columns(["id", "tag"]).drop_species("i").drop_corners()

    @cached_property
    def input(self) -> Input:
        return Input(self.params_record.path_input)

    def set_variable(self, variable: ParticleVariable):
        self.variable = variable
