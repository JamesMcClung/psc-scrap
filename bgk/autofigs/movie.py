import matplotlib.pyplot as plt

from . import util
from bgk.field_data import FieldData

from .snapshot_generator import SnapshotGenerator, SnapshotParams

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.animation import FuncAnimation
import xarray as xr


__all__ = ["make_movie"]


def make_movie(
    field_data: FieldData,
    snapshot_generator: SnapshotGenerator,
    fig: Figure = None,
    ax: Axes = None,
    x_pos: float = 0,
) -> tuple[Figure, FuncAnimation]:
    params = SnapshotParams(field_data, 0, x_pos, True, True)
    fig, ax = snapshot_generator.draw_snapshot(params, fig, ax)
    fig.tight_layout(pad=0)
    im = ax.get_images()[0]

    params.draw_colorbar = False

    def update_im(frame: int):
        params.frame = frame
        snapshot_generator.draw_snapshot(params, fig, ax)
        return [im]

    return fig, FuncAnimation(fig, update_im, interval=30, frames=field_data.nframes, repeat=False, blit=True)
