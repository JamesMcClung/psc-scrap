import matplotlib.pyplot as plt

from . import util
from bgk.field_data import FieldData

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.animation import FuncAnimation
import xarray as xr

__all__ = ["make_movie", "view_frame"]


def _update_title(ax: Axes, field_data: FieldData, frame: int) -> None:
    ax.set_title(f"{field_data.view_bounds.adjective}${field_data.variable.latex}$, t={field_data.axis_t[frame]:.3f} ($B_0={field_data.params_record.B0}$, {field_data.case_name})")


def _get_image_data(field_data: FieldData, frame: int, x_pos: float) -> xr.DataArray:
    return field_data.datas.isel(t=frame).sel(x=x_pos).transpose()


def view_frame(
    field_data: FieldData,
    frame: int,
    *,
    fig: Figure = None,
    ax: Axes = None,
    x_pos: float = 0,
    draw_labels: bool = True,
    first_view: bool = True,
) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    im = ax.imshow(
        _get_image_data(field_data, frame, x_pos),
        cmap=field_data.variable.cmap_name,
        vmin=field_data._val_bounds[0],
        vmax=field_data._val_bounds[1],
        origin="lower",
        extent=field_data.view_bounds.get_extent(),
    )

    if draw_labels:
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        _update_title(ax, field_data, frame)
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
        if first_view:
            fig.colorbar(im, ax=ax)

    return fig, ax


def make_movie(field_data: FieldData, fig: Figure = None, ax: Axes = None, x_pos: float = 0) -> tuple[Figure, FuncAnimation]:
    fig, ax = view_frame(field_data, 0, fig=fig, ax=ax, x_pos=x_pos)
    fig.tight_layout(pad=0)
    im = ax.get_images()[0]

    def update_im(frame: int):
        view_frame(field_data, frame, fig=fig, ax=ax, x_pos=x_pos, first_view=False)
        return [im]

    return fig, FuncAnimation(fig, update_im, interval=30, frames=field_data.nframes, repeat=False, blit=True)
