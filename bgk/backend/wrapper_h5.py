from __future__ import annotations

import numpy as np
import pandas as pd
import os

from ..typing import PrefixH5, H5WrapperVariableName, Species

__all__ = ["WrapperH5", "load_h5"]

_VARIABLE_NAME = "particles/p0/1d"


class WrapperH5:
    _path_data: str
    step: int
    _df: pd.DataFrame

    def __init__(self, path_data: str, step: int) -> None:
        self._path_data = path_data
        self.step = step
        # would like to lazily load columns, but loading specific columns doesn't seem to actually work, and it might not be worthwhile even if it did
        self._df = pd.read_hdf(self._path_data, key=_VARIABLE_NAME)

    def _has_col(self, column_name: H5WrapperVariableName) -> bool:
        return column_name in self._df.columns

    def _velocity_from_momentum(self, momentum: pd.Series, *, relativistic: bool = False) -> pd.Series:
        if relativistic:
            raise NotImplementedError()
        else:
            return momentum / self._df["m"]

    def drop_columns(self, column_names: list[H5WrapperVariableName]) -> WrapperH5:
        self._df.drop(columns=column_names, inplace=True)
        return self

    def drop_species(self, species: Species) -> WrapperH5:
        if species == "e":
            self._df.drop(index=self._df[self.col("q") == -1], inplace=True)
        elif species == "i":
            self._df.drop(index=self._df[self.col("q") == 1].index, inplace=True)
        return self

    def drop_corners(self) -> WrapperH5:
        self._df.drop(index=self._df[self.col("rho") > self.col("y").max()].index, inplace=True)
        return self

    def restrict(self, variable: H5WrapperVariableName, lower_bound: float | None = None, upper_bound: float | None = None) -> WrapperH5:
        """Drop data not within the given bounds, inclusive. Return `self`."""
        if lower_bound is not None:
            self._df.drop(index=self._df[self.col(variable) < lower_bound].index, inplace=True)
        if upper_bound is not None:
            self._df.drop(index=self._df[self.col(variable) > upper_bound].index, inplace=True)
        return self

    def col(self, column_name: H5WrapperVariableName) -> pd.Series:
        match column_name:
            case _ if self._has_col(column_name):
                pass
            case "rho":
                self._df["rho"] = (self.col("y") ** 2 + self.col("z") ** 2) ** 0.5
            case "phi":
                self._df["phi"] = np.arctan2(self.col("z"), self.col("y"))
            case "prho":
                self._df["prho"] = (self.col("py") * self.col("y") + self.col("pz") * self.col("z")) / self.col("rho")
                # TODO don't do this unless requested; better thing to request is remove na rows entirely
                self._df["prho"].fillna(0, inplace=True)
            case "pphi":
                self._df["pphi"] = (self.col("pz") * self.col("y") - self.col("py") * self.col("z")) / self.col("rho")
                # TODO don't do this unless requested; better thing to request is remove na rows entirely
                self._df["pphi"].fillna(0, inplace=True)
            case "vx" | "vy" | "vz" | "vrho" | "vphi":
                self._df[column_name] = self._velocity_from_momentum(self.col("p" + column_name[1:]))

        return self._df[column_name]


def load_h5(path_run: str, prefix_h5: PrefixH5, step: int) -> WrapperH5:
    rank = 0
    path_data = os.path.join(path_run, f"{prefix_h5}.{step:06d}_p{rank:06d}.h5")
    return WrapperH5(path_data, step)
