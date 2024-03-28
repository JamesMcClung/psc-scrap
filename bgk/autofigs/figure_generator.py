from __future__ import annotations

from typing import Callable

from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

from ..field_data import FieldData
from . import util

__all__ = ["FigureParams", "figure_generator"]

FIGURE_GENERATOR_REGISTRY: dict[str, FigureGenerator] = {}


class FigureParams:
    duration_in_title: str
    time_cutoff_idx: int
    fields: FieldData


class FigureGenerator:
    def __init__(
        self,
        generator: Callable[[FigureParams, Figure | None, Axes | None], tuple[Figure, Axes]],
    ) -> None:
        super().__init__()
        self.generate_figure = generator

    def generate_figure(params: FigureParams, fig: Figure | None = None, ax: Axes | None = None) -> tuple[Figure, Axes]:
        pass


def figure_generator(figure_name: str):
    def figure_generator_inner(func: Callable[[FigureParams, Figure, Axes], tuple[Figure, Axes]]):
        def wrapper(params: FigureParams, fig: Figure | None = None, ax: Axes | None = None):
            fig, ax = util.ensure_fig_ax(fig, ax)
            return func(params, fig, ax)

        FIGURE_GENERATOR_REGISTRY[figure_name] = FigureGenerator(wrapper)

        return func  # returning func instead of wrapper, so actual function isn't modified

    return figure_generator_inner
