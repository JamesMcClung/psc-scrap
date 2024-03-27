import bgk
import numpy as np
from . import util

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes


def _plot_lines(
    ax: Axes,
    cmap,
    plot_indices: list[int],
    label_indices: list[int],
    xdata: list[float],
    ydatas: list[list[float]],
    tdata: list[float],
):
    for i in plot_indices:
        label = f"$t={tdata[i]:.2f}$" if i in label_indices else "_nolegend_"
        ax.plot(xdata, ydatas[i], color=cmap(i / max(plot_indices) if len(plot_indices) > 1 else 0.5), label=label)


def plot_profiles(
    videoMaker: bgk.field_data.FieldData,
    time_cutoff_idx: int,
    duration_in_title: str,
    fig: Figure = None,
    ax: Axes = None,
):
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = videoMaker.view_bounds.bounds[1].upper
    rStep = videoMaker.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)
    meanss = util.binned_mean(videoMaker.datas, "rho", nbins=len(rs), lower=0, upper=maxR).mean(dim=["x"])

    n_plots = min(13, time_cutoff_idx + 1)
    n_labels = min(5, time_cutoff_idx + 1)

    indices = sorted(list({round(i) for i in np.linspace(0, time_cutoff_idx, n_plots)}))
    label_indices = [indices[round(i * (len(indices) - 1) / (n_labels - 1))] for i in range(n_labels)]

    cmap = util.get_cmap("Reds", min=0.3)

    _plot_lines(ax, cmap, indices, label_indices, xdata=rs, ydatas=meanss, tdata=videoMaker.axis_t)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(f"${videoMaker.variable.latex}$")
    ax.set_title(f"Changing Profile of ${videoMaker.variable.latex}$ for $B_0={videoMaker.params_record.B0}$ {duration_in_title}")
    ax.legend()
    fig.tight_layout()

    return fig, ax


def plot_extrema(
    videoMaker: bgk.field_data.FieldData,
    fig: Figure = None,
    ax: Axes = None,
) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = videoMaker.view_bounds.bounds[1].upper
    rStep = videoMaker.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)
    meanss = util.binned_mean(videoMaker.datas, "rho", nbins=len(rs), lower=0, upper=maxR).mean(dim=["x"])

    indices_maxs = videoMaker.get_local_extrema_idxs(np.greater_equal) or [videoMaker.nframes - 1]
    indices_mins = videoMaker.get_local_extrema_idxs(np.less_equal) or [0]

    cmap_mins = util.get_cmap("Blues", min=0.3, max=0.9)
    cmap_maxs = util.get_cmap("Reds", min=0.3, max=0.9)

    _plot_lines(ax, cmap_mins, indices_mins, [indices_mins[0], indices_mins[-1]], xdata=rs, ydatas=meanss, tdata=videoMaker.axis_t)
    _plot_lines(ax, cmap_maxs, indices_maxs, [indices_maxs[0], indices_maxs[-1]], xdata=rs, ydatas=meanss, tdata=videoMaker.axis_t)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(f"${videoMaker.variable.latex}$")
    ax.set_title(f"Extremal Profiles of ${videoMaker.variable.latex}$ for $B_0={videoMaker.params_record.B0}$")
    ax.legend()
    fig.tight_layout()

    return fig, ax
