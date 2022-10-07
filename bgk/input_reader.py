import numpy as np

__all__ = ["Input"]


def _line_to_list(row: str) -> list[float]:
    return [float(val) for val in row.split()]


class Input:
    def __init__(self, file: str) -> None:
        with open(file) as io:
            labels = io.readline().split()
            data = np.array([_line_to_list(line) for line in io.readlines()])
        for i, label in enumerate(labels):
            self.__dict__[label] = data[:, i]

    def rescale(self, factors: dict[str, float]) -> None:
        for k, v in factors.items():
            self.__dict__[k] *= v

    def truncate(self, slice: slice) -> None:
        for k, v in self.__dict__.items():
            self.__dict__[k] = v[slice]

    def convert_to_cs_units(self) -> None:
        beta = self.Te[0] ** 0.5
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
