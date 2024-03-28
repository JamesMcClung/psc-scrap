from typing import Callable

from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

from ..field_data import FieldData


class SnapshotParams:
    fields: FieldData
    frame: int
    x_pos: float
    draw_colorbar: bool
    draw_labels: bool


class SnapshotGenerator:
    def __init__(self, generator: Callable[[SnapshotParams, Figure | None, Axes | None], tuple[Figure, Axes]]) -> None:
        self._generator = generator

    def draw_snapshot(self, params: SnapshotParams, fig: Figure | None = None, ax: Axes | None = None):
        return self._generator(params, fig, ax)
