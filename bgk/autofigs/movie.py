import matplotlib.pyplot as plt

from . import util
from bgk.output_reader import VideoMaker

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.animation import FuncAnimation
import xarray as xr

__all__ = ["make_movie", "view_frame"]


def _update_title(ax: Axes, videoMaker: VideoMaker, frame: int) -> None:
    ax.set_title(f"{videoMaker.view_bounds.adjective}${videoMaker.variable.latex}$, t={videoMaker.axis_t[frame]:.3f} ($B_0={videoMaker.params_record.B0}$, {videoMaker.case_name})")


def _get_image_data(videoMaker: VideoMaker, frame: int, x_pos: float) -> xr.DataArray:
    return videoMaker.datas.isel(t=frame).sel(x=x_pos).transpose()


def view_frame(videoMaker: VideoMaker, frame: int, fig: Figure = None, ax: Axes = None, minimal: bool = False, x_pos: float = 0) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    im = ax.imshow(
        _get_image_data(videoMaker, frame, x_pos),
        cmap=videoMaker.variable.cmap_name,
        vmin=videoMaker._val_bounds[0],
        vmax=videoMaker._val_bounds[1],
        origin="lower",
        extent=videoMaker.view_bounds.get_extent(),
    )

    if not minimal:
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        _update_title(ax, videoMaker, frame)
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
        fig.colorbar(im, ax=ax)

    return fig, ax


def make_movie(videoMaker: VideoMaker, fig: Figure = None, ax: Axes = None, x_pos: float = 0) -> tuple[Figure, FuncAnimation]:
    fig, ax = view_frame(videoMaker, 0, fig, ax, x_pos)
    fig.tight_layout(pad=0)
    im = ax.get_images()[0]

    def update_im(frame: int):
        im.set_array(_get_image_data(videoMaker, frame, x_pos))
        _update_title(ax, videoMaker, frame)
        return [im]

    return fig, FuncAnimation(fig, update_im, interval=30, frames=videoMaker.nframes, repeat=False, blit=True)
