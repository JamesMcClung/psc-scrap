from __future__ import annotations

from typing import Callable

from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

from ..field_data import FieldData
from . import util

__all__ = ["ImageParams", "image_generator"]

IMAGE_GENERATOR_REGISTRY: dict[str, ImageGenerator] = {}


class ImageParams:
    duration_in_title: str
    time_cutoff_idx: int
    fields: FieldData


class ImageGenerator:
    def __init__(
        self,
        generator: Callable[[ImageParams, Figure | None, Axes | None], tuple[Figure, Axes]],
    ) -> None:
        super().__init__()
        self.generate_image = generator

    def generate_image(params: ImageParams, fig: Figure | None = None, ax: Axes | None = None) -> tuple[Figure, Axes]:
        pass


def image_generator(image_file_name: str):
    def image_generator_inner(func: Callable[[ImageParams, Figure, Axes], tuple[Figure, Axes]]):
        def wrapper(params: ImageParams, fig: Figure | None = None, ax: Axes | None = None):
            fig, ax = util.ensure_fig_ax(fig, ax)
            return func(params, fig, ax)

        IMAGE_GENERATOR_REGISTRY[image_file_name] = ImageGenerator(wrapper)

        return func  # returning func instead of wrapper, so actual function isn't modified

    return image_generator_inner
