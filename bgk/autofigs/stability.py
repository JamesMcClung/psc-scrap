import scipy.signal as sig

from . import util
from bgk.output_reader import VideoMaker

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


__all__ = ["plot_stability"]


def plot_stability(videoMaker: VideoMaker, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    ax.set_xlabel("Time")
    ax.set_ylabel("2-Norm of Difference")
    ax.set_title(f"Deviation from ICs of {videoMaker.view_bounds.adjective}{videoMaker.variable.title} ($B_0={videoMaker.params_record.B0}$, {videoMaker.case_name})")

    ax.plot(videoMaker.axis_t, videoMaker.get_norms_of_diffs())
    return fig, ax
