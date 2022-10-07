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
