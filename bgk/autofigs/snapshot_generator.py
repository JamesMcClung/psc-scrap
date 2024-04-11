from __future__ import annotations

from typing import Callable, TypeVar, Generic

from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

from ..field_data import FieldData
from ..particle_data import ParticleData
from ..run_manager import FrameManager
from . import util

__all__ = ["SNAPSHOT_GENERATOR_REGISTRY", "SnapshotParams"]


SNAPSHOT_GENERATOR_REGISTRY: dict[str, SnapshotGenerator] = {}

DATA = TypeVar("DATA", FieldData, ParticleData)


class SnapshotParams(Generic[DATA]):
    frame_manager: FrameManager

    def __init__(
        self,
        data: DATA,
        x_pos: float,
        *,
        step: int = None,
        draw_colorbar: bool = None,
        draw_labels: bool = None,
        set_image_only: bool = False,
    ) -> None:
        self.data = data
        self.x_pos = x_pos
        if isinstance(data, FieldData):
            self.frame_manager = data.frame_manager
        elif isinstance(data, ParticleData):
            raise NotImplementedError()
        else:
            raise TypeError()

        self.step = step
        self.draw_colorbar = draw_colorbar
        self.draw_labels = draw_labels
        self.set_image_only = set_image_only


class SnapshotGenerator(Generic[DATA]):
    def __init__(self, generator: Callable[[SnapshotParams[DATA], Figure | None, Axes | None], tuple[Figure, Axes]]) -> None:
        self._generator = generator

    def draw_snapshot(self, params: SnapshotParams[DATA], fig: Figure | None = None, ax: Axes | None = None):
        return self._generator(params, fig, ax)


def snapshot_generator(snapshot_name: str):
    def figure_generator_inner(func: Callable[[SnapshotParams[DATA], Figure, Axes], tuple[Figure, Axes]]):
        def wrapper(params: SnapshotParams[DATA], fig: Figure | None = None, ax: Axes | None = None):
            fig, ax = util.ensure_fig_ax(fig, ax)
            return func(params, fig, ax)

        SNAPSHOT_GENERATOR_REGISTRY[snapshot_name] = SnapshotGenerator(wrapper)

        return func  # returning func instead of wrapper, so actual function isn't modified

    return figure_generator_inner
