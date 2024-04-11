from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.animation import FuncAnimation

from .snapshot_generator import SnapshotGenerator, SnapshotParams, DATA


__all__ = ["make_movie"]


def make_movie(
    params: SnapshotParams[DATA],
    snapshot_generator: SnapshotGenerator[DATA],
    fig: Figure = None,
    ax: Axes = None,
) -> tuple[Figure, FuncAnimation]:
    params.frame = 0
    params.draw_colorbar = True
    params.draw_labels = True
    fig, ax = snapshot_generator.draw_snapshot(params, fig, ax)
    fig.tight_layout(pad=0)
    im = ax.get_images()[0]

    params.draw_colorbar = False
    params.set_image_only = True

    def update_im(frame: int):
        params.frame = frame
        snapshot_generator.draw_snapshot(params, fig, ax)
        return [im]

    return fig, FuncAnimation(fig, update_im, interval=30, frames=params.frame_manager.nframes, repeat=False, blit=True)
