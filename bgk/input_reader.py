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
