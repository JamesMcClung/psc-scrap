from . import util
from .image import ImageParams, image_generator

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_origin_means"]


@image_generator("origin_means")
def plot_origin_means(image_params: ImageParams, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    ax.set_xlabel("Time")
    ax.set_ylabel(f"Mean ${image_params.fields.variable.latex}$")
    ax.set_title(f"Mean ${image_params.fields.variable.latex}$ Near Origin for $B_0={image_params.fields.params_record.B0}$")

    ax.plot(image_params.fields.axis_t, image_params.fields.get_means_at_origin())
    return fig, ax
