from . import util
from .image import image_generator, ImageParams

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_stability"]


@image_generator("stability")
def plot_stability(image_params: ImageParams, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    ax.set_xlabel("Time")
    ax.set_ylabel("2-Norm of Difference")
    ax.set_title(f"Deviation from ICs of {image_params.fields.view_bounds.adjective}${image_params.fields.variable.latex}$ ($B_0={image_params.fields.params_record.B0}$, {image_params.fields.case_name})")

    ax.plot(image_params.fields.axis_t, image_params.fields.get_norms_of_diffs())
    return fig, ax
