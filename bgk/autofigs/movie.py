import matplotlib.pyplot as plt

from . import util
from bgk.output_reader import VideoMaker

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.image import AxesImage
from matplotlib.animation import FuncAnimation

__all__ = ["make_movie", "view_frame"]


def make_movie(videoMaker: VideoMaker, fig: Figure = None, ax: Axes = None) -> tuple[Figure, FuncAnimation]:
    fig, ax, im = view_frame(videoMaker, 0, fig, ax)
    fig.tight_layout(pad=0)
    return fig, view_movie(videoMaker, fig, ax, im)


def _set_title(videoMaker: VideoMaker, ax: Axes, viewAdj: str, paramName: str, time: float) -> None:
    ax.set_title(f"{viewAdj}{paramName}, t={time:.3f} ($B_0={videoMaker.params_record.B0}$, {videoMaker._case_name})")


def view_frame(videoMaker: VideoMaker, frame: int, fig: Figure = None, ax: Axes = None, minimal: bool = False) -> tuple[Figure, Axes, AxesImage]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    im = ax.imshow(
        videoMaker.datas[frame],
        cmap=videoMaker.param.colors,
        vmin=videoMaker._val_bounds[0],
        vmax=videoMaker._val_bounds[1],
        origin="lower",
        extent=videoMaker.view_bounds.get_extent(),
    )

    if not minimal:
        ax.set_xlabel("y")
        ax.set_ylabel("z")
        _set_title(videoMaker, ax, videoMaker.view_bounds.adjective, videoMaker.param.title, videoMaker.axis_t[frame])
        plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
        fig.colorbar(im, ax=ax)

    return fig, ax, im


def view_movie(videoMaker: VideoMaker, fig: Figure, ax: Axes, im: AxesImage) -> FuncAnimation:
    def updateIm(frame: int):
        im.set_array(videoMaker.datas[frame])
        _set_title(videoMaker, ax, videoMaker.view_bounds.adjective, videoMaker.param.title, videoMaker.axis_t[frame])
        return [im]

    return FuncAnimation(fig, updateIm, interval=30, frames=videoMaker.nframes, repeat=False, blit=True)
