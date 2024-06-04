from functools import cached_property
import pandas as pd

from .backend import load_bp, load_h5, WrapperH5
from .input_reader import Input
from .params_record import ParamsRecord
from .particle_variables import ParticleVariable, v_phi
from .run_manager import RunManager
from .typing import H5WrapperVariableName
from .util.safe_cache_invalidation import safe_cached_property_invalidation

__all__ = ["ParticleData"]


##########################


@safe_cached_property_invalidation
class ParticleData:
    def __init__(self, run_manager: RunManager, initial_variable: ParticleVariable = v_phi) -> None:
        self.run_manager = run_manager
        self.set_variable(initial_variable)

    @property
    def params_record(self) -> ParamsRecord:
        return self.run_manager.params_record

    def set_step(self, step: int):
        if hasattr(self, "step") and step == self.step:
            return
        self.step = step
        del self.time
        del self.data

    @cached_property
    def time(self) -> float:
        return load_bp(self.run_manager.path_run, "pfd", self.step).time

    @cached_property
    def data(self) -> WrapperH5:
        return load_h5(self.run_manager.path_run, "prt", self.step).drop_variables(["id", "tag"]).drop_species("i").drop_corners()

    @cached_property
    def input(self) -> Input:
        return Input(self.params_record.path_input)

    def set_variable(self, variable: ParticleVariable):
        self.variable = variable

    def col(self, column_name: H5WrapperVariableName) -> pd.Series:
        return self.data.col(column_name)
