from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
import matplotlib.pyplot as plt

from ..snapshot_generator import SnapshotParams, snapshot_generator
from .. import util


__all__ = ["draw_map"]


@snapshot_generator("map")
def draw_map(params: SnapshotParams, fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    im = ax.imshow(
        params.data.datas.isel(t=params.frame).sel(x=params.x_pos).transpose(),
        cmap=params.data.variable.cmap_name,
        vmin=params.data._val_bounds[0],
        vmax=params.data._val_bounds[1],
        origin="lower",
        extent=params.data.view_bounds.get_extent(),
    )

    if params.draw_labels:
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        ax.set_title(f"{params.data.view_bounds.adjective}${params.data.variable.latex}$, t={params.data.axis_t[params.frame]:.3f} ($B_0={params.data.params_record.B0}$, {params.data.case_name})")
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")

    if params.draw_colorbar:
        fig.colorbar(im, ax=ax)

    return fig, ax
