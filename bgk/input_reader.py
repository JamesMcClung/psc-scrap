__all__ = ["Input", "InputColumnName"]

import os
from typing import Literal

import numpy as np


def _line_to_list(row: str) -> list[float]:
    return [float(val) for val in row.split()]


def get_B0(path_input: str) -> float:
    for item in os.path.basename(path_input).split("-"):
        if item.startswith("B="):
            return float(item.removeprefix("B="))


InputColumnName = Literal["rho", "ne", "v_phi", "Te", "E_rho", "Psi"]


class Input:
    def __init__(self, path_input: str) -> None:
        if not os.path.exists(path_input):
            # Input files were removed from the psc repo and added to this (psc-scrap) repo.
            # For convenience, this guesses the new location. The psc and psc-scrap repos must be in the same directory,
            #   and psc-scrap must actually have the inputs.
            moved_path_input = path_input.replace("psc/inputs/bgk/", "psc-scrap/inputs/")
            if not os.path.exists(moved_path_input):
                raise FileNotFoundError(f"Can't find input file! Checked '{path_input}' and '{moved_path_input}', but it wasn't at either location.")
            path_input = moved_path_input
        self.path_input = path_input
        with open(path_input) as input:
            labels = input.readline().split()
            data = np.array([_line_to_list(line) for line in input.readlines()])
        for i, label in enumerate(labels):
            self.__dict__[label] = data[:, i]

    def __getitem__(self, key: InputColumnName) -> np.ndarray:
        return self.__dict__[key]

    def __setitem__(self, key: InputColumnName, val: np.ndarray) -> None:
        self.__dict__[key] = val

    def rescale(self, factors: dict[InputColumnName, float]) -> None:
        for k, v in factors.items():
            self[k] *= v

    def truncate(self, slice: slice) -> None:
        for k, v in self.__dict__.items():
            self[k] = v[slice]

    def convert_to_cs_units(self) -> None:
        cs_Te0 = 1
        beta = (self.Te[0] / cs_Te0) ** 0.5
        self.rescale(
            {
                "rho": beta**-1,
                "ne": beta**3,
                "v_phi": beta**-1,
                "Te": beta**-2,
                "E_rho": beta**-1,
                "Psi": beta**-2,
            }
        )

    def interpolate_value(self, rho: float, val: InputColumnName) -> float:
        idx = int(rho / (self.rho[1] - self.rho[0]))
        while self.rho[idx] < rho:
            idx += 1
        while rho < self.rho[idx]:
            idx -= 1
        # now self.rho[idx] <= rho < self.rho[idx + 1]

        w0 = self.rho[idx + 1] - rho
        w1 = rho - self.rho[idx]

        return (self[val][idx] * w0 + self[val][idx + 1] * w1) / (self.rho[idx + 1] - self.rho[idx])

    def get_radius_of_structure(self) -> float:
        if self.rho[0] < 1:
            return self.rho[np.argmax(self.ne)] * 1.5
        elif self.rho[0] > 1:
            return self.rho[np.argmin(self.ne)] * 1.5
        else:
            raise Exception("unrecognized structure")
