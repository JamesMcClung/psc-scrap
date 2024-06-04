from __future__ import annotations

import numpy as np
import pandas as pd
import os

from ..typing import PrefixH5, H5WrapperVariableName, Species

__all__ = ["WrapperH5", "load_h5"]

_VARIABLE_NAME = "particles/p0/1d"


class WrapperH5:
    """Wraps a `pandas.DataFrame`, providing convenience methods for accessing and filtering particle data."""

    _path_data: str
    step: int
    _data: pd.DataFrame

    def __init__(self, path_data: str, step: int) -> None:
        self._path_data = path_data
        self.step = step
        # would like to lazily load columns, but loading specific columns doesn't seem to actually work, and it might not be worthwhile even if it did
        self._data = pd.read_hdf(self._path_data, key=_VARIABLE_NAME)

    def _has_variable(self, variable: H5WrapperVariableName) -> bool:
        return variable in self._data.columns

    def _velocity_from_momentum(self, momentum: pd.Series, *, relativistic: bool = False) -> pd.Series:
        if relativistic:
            raise NotImplementedError()
        else:
            return momentum / self._data["m"]

    def drop_variables(self, variables: list[H5WrapperVariableName]) -> WrapperH5:
        """Drop the given variables entirely. Return `self`."""
        self._data.drop(columns=variables, inplace=True)
        return self

    def drop_species(self, species: Species) -> WrapperH5:
        """Drop data for a given species. Species are identified by their charge, `q`. Return `self`."""
        if species == "e":
            self._data.drop(index=self._data[self.get("q") == -1], inplace=True)
        elif species == "i":
            self._data.drop(index=self._data[self.get("q") == 1].index, inplace=True)
        return self

    def drop_corners(self) -> WrapperH5:
        """Drop data outside of the largest inscribed circle in the domain, i.e., where `rho > max(y) == max(z)`. Return `self`."""
        self._data.drop(index=self._data[self.get("rho") > self.get("y").max()].index, inplace=True)
        return self

    def restrict(self, variable: H5WrapperVariableName, lower_bound: float | None = None, upper_bound: float | None = None) -> WrapperH5:
        """Drop data not within the given bounds, inclusive. Return `self`."""
        if lower_bound is not None:
            self._data.drop(index=self._data[self.get(variable) < lower_bound].index, inplace=True)
        if upper_bound is not None:
            self._data.drop(index=self._data[self.get(variable) > upper_bound].index, inplace=True)
        return self

    def get(self, variable: H5WrapperVariableName) -> pd.Series:
        """Return the column containing the given variable, generating it if necessary."""
        match variable:
            case _ if self._has_variable(variable):
                pass
            case "rho":
                self._data["rho"] = (self.get("y") ** 2 + self.get("z") ** 2) ** 0.5
            case "phi":
                self._data["phi"] = np.arctan2(self.get("z"), self.get("y"))
            case "prho":
                self._data["prho"] = (self.get("py") * self.get("y") + self.get("pz") * self.get("z")) / self.get("rho")
                # TODO don't do this unless requested; better thing to request is remove na rows entirely
                self._data["prho"].fillna(0, inplace=True)
            case "pphi":
                self._data["pphi"] = (self.get("pz") * self.get("y") - self.get("py") * self.get("z")) / self.get("rho")
                # TODO don't do this unless requested; better thing to request is remove na rows entirely
                self._data["pphi"].fillna(0, inplace=True)
            case "vx" | "vy" | "vz" | "vrho" | "vphi":
                self._data[variable] = self._velocity_from_momentum(self.get("p" + variable[1:]))

        return self._data[variable]


def load_h5(path_run: str, prefix_h5: PrefixH5, step: int) -> WrapperH5:
    """Return the data at the given step in the given run."""
    rank = 0
    path_data = os.path.join(path_run, f"{prefix_h5}.{step:06d}_p{rank:06d}.h5")
    return WrapperH5(path_data, step)
