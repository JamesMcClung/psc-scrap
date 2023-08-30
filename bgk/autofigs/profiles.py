import bgk
import numpy as np
from . import util
from . import extrema

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


def plot_profiles(
    videoMaker: bgk.output_reader.VideoMaker,
    time_cutoff_idx: int,
    duration_in_title: str,
    fig: Figure = None,
    ax: Axes = None,
):
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = videoMaker._currentSlice.slice.stop
    rStep = videoMaker.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)

    allMeans = np.array([[util.get_mean(videoMaker.slicedDatas[idx], r, rStep, videoMaker) for r in rs] for idx in range(videoMaker.nframes)])

    n_plots = 13
    n_labels = min(5, time_cutoff_idx + 1)

    indices = sorted(list({round(i) for i in np.linspace(0, time_cutoff_idx, n_plots)}))
    label_indices = [indices[round(i * (len(indices) - 1) / (n_labels - 1))] for i in range(n_labels)]

    cmap = util.get_cmap("Reds", min=0.3)

    extrema._plot_lines(ax, cmap, indices, label_indices, xdata=rs, ydatas=allMeans, tdata=videoMaker.times)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(videoMaker._currentParam.title)
    ax.set_title(f"Changing Profile of {videoMaker._currentParam.title} for $B_0={videoMaker.loader.B}$ {duration_in_title}")
    ax.legend()
    fig.tight_layout()

    return fig, ax
