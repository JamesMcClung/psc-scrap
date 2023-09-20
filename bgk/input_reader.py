__all__ = ["Input"]

import numpy as np
import os


def _line_to_list(row: str) -> list[float]:
    return [float(val) for val in row.split()]


def get_B0(path_input: str) -> float:
    for item in os.path.basename(path_input).split("-"):
        if item.startswith("B="):
            return float(item.removeprefix("B="))


class Input:
    def __init__(self, path_input: str) -> None:
        self.path_input = path_input
        with open(path_input) as input:
            labels = input.readline().split()
            data = np.array([_line_to_list(line) for line in input.readlines()])
        for i, label in enumerate(labels):
            self.__dict__[label] = data[:, i]

    def __getitem__(self, key: str) -> np.ndarray:
        return self.__dict__[key]

    def __setitem__(self, key: str, val: np.ndarray) -> None:
        self.__dict__[key] = val

    def rescale(self, factors: dict[str, float]) -> None:
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

    def interpolate_value(self, rho: float, val: str) -> float:
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
        return self.rho[np.argmax(self.ne)] * 1.5
