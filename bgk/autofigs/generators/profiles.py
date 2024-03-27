import numpy as np
from .. import util
from ..figure_generator import figure_generator, FigureParams

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes

__all__ = ["plot_profiles", "plot_extrema"]


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


@figure_generator("profiles")
def plot_profiles(image_params: FigureParams, fig: Figure = None, ax: Axes = None):
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = image_params.fields.view_bounds.bounds[1].upper
    rStep = image_params.fields.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)
    meanss = util.binned_mean(image_params.fields.datas, "rho", nbins=len(rs), lower=0, upper=maxR).mean(dim=["x"])

    n_plots = min(13, image_params.time_cutoff_idx + 1)
    n_labels = min(5, image_params.time_cutoff_idx + 1)

    indices = sorted(list({round(i) for i in np.linspace(0, image_params.time_cutoff_idx, n_plots)}))
    label_indices = [indices[round(i * (len(indices) - 1) / (n_labels - 1))] for i in range(n_labels)]

    cmap = util.get_cmap("Reds", min=0.3)

    _plot_lines(ax, cmap, indices, label_indices, xdata=rs, ydatas=meanss, tdata=image_params.fields.axis_t)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(f"${image_params.fields.variable.latex}$")
    ax.set_title(f"Changing Profile of ${image_params.fields.variable.latex}$ for $B_0={image_params.fields.params_record.B0}$ {image_params.duration_in_title}")
    ax.legend()
    fig.tight_layout()

    return fig, ax


@figure_generator("extrema")
def plot_extrema(image_params: FigureParams, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = image_params.fields.view_bounds.bounds[1].upper
    rStep = image_params.fields.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)
    meanss = util.binned_mean(image_params.fields.datas, "rho", nbins=len(rs), lower=0, upper=maxR).mean(dim=["x"])

    indices_maxs = image_params.fields.get_local_extrema_idxs(np.greater_equal) or [image_params.fields.nframes - 1]
    indices_mins = image_params.fields.get_local_extrema_idxs(np.less_equal) or [0]

    cmap_mins = util.get_cmap("Blues", min=0.3, max=0.9)
    cmap_maxs = util.get_cmap("Reds", min=0.3, max=0.9)

    _plot_lines(ax, cmap_mins, indices_mins, [indices_mins[0], indices_mins[-1]], xdata=rs, ydatas=meanss, tdata=image_params.fields.axis_t)
    _plot_lines(ax, cmap_maxs, indices_maxs, [indices_maxs[0], indices_maxs[-1]], xdata=rs, ydatas=meanss, tdata=image_params.fields.axis_t)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(f"${image_params.fields.variable.latex}$")
    ax.set_title(f"Extremal Profiles of ${image_params.fields.variable.latex}$ for $B_0={image_params.fields.params_record.B0}$")
    ax.legend()
    fig.tight_layout()

    return fig, ax
