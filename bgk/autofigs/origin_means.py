from . import util
from bgk.field_data import FieldData

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_origin_means"]


def plot_origin_means(videoMaker: FieldData, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    ax.set_xlabel("Time")
    ax.set_ylabel(f"Mean ${videoMaker.variable.latex}$")
    ax.set_title(f"Mean ${videoMaker.variable.latex}$ Near Origin for $B_0={videoMaker.params_record.B0}$")

    ax.plot(videoMaker.axis_t, videoMaker.get_means_at_origin())
    return fig, ax