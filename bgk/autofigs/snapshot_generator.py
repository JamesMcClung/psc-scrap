from __future__ import annotations

from typing import Callable

from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

from ..field_data import FieldData
from . import util

__all__ = ["SNAPSHOT_GENERATOR_REGISTRY", "SnapshotParams"]


SNAPSHOT_GENERATOR_REGISTRY: dict[str, SnapshotGenerator] = {}


class SnapshotParams:
    def __init__(self, data: FieldData, x_pos: float, *, frame: int = None, draw_colorbar: bool = None, draw_labels: bool = None) -> None:
        self.data = data
        self.x_pos = x_pos
        self.frame_manager = data.frame_manager

        self.frame = frame
        self.draw_colorbar = draw_colorbar
        self.draw_labels = draw_labels


class SnapshotGenerator:
    def __init__(self, generator: Callable[[SnapshotParams, Figure | None, Axes | None], tuple[Figure, Axes]]) -> None:
        self._generator = generator

    def draw_snapshot(self, params: SnapshotParams, fig: Figure | None = None, ax: Axes | None = None):
        return self._generator(params, fig, ax)


def snapshot_generator(snapshot_name: str):
    def figure_generator_inner(func: Callable[[SnapshotParams, Figure, Axes], tuple[Figure, Axes]]):
        def wrapper(params: SnapshotParams, fig: Figure | None = None, ax: Axes | None = None):
            fig, ax = util.ensure_fig_ax(fig, ax)
            return func(params, fig, ax)

        SNAPSHOT_GENERATOR_REGISTRY[snapshot_name] = SnapshotGenerator(wrapper)

        return func  # returning func instead of wrapper, so actual function isn't modified

    return figure_generator_inner
