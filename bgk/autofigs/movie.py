from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from matplotlib.animation import FuncAnimation

from ..field_data import FieldData
from ..particle_data import ParticleData
from ..run_manager import FrameManagerLinear
from .snapshot_generator import SnapshotGenerator, SnapshotParams, DATA


__all__ = ["make_movie"]


def make_movie(
    nframes: int,
    params: SnapshotParams[DATA],
    snapshot_generator: SnapshotGenerator[DATA],
    fig: Figure = None,
    ax: Axes = None,
) -> tuple[Figure, FuncAnimation]:
    if isinstance(params.data, FieldData):
        if nframes != params.data.nframes:
            raise ValueError(f"nframes of {FieldData.__name__} = {params.data.nframes} must match passed nframes = {nframes}")
        frame_manager = params.data.frame_manager
    elif isinstance(params.data, ParticleData):
        frame_manager = params.data.run_manager.get_frame_manager(FrameManagerLinear, nframes, [params.data.variable])
    else:
        raise TypeError(f"invalid data type: {params.data.__class__}")

    params.step = frame_manager.steps[0]
    params.draw_colorbar = True
    params.draw_labels = True
    fig, ax, artist = snapshot_generator.draw_snapshot(params, fig, ax)
    fig.tight_layout(pad=0)

    params.draw_colorbar = False
    params.set_data_only = True

    def update_im(frame: int):
        params.step = frame_manager.steps[frame]
        snapshot_generator.draw_snapshot(params, fig, ax)
        return [artist]

    return fig, FuncAnimation(fig, update_im, interval=30, frames=frame_manager.nframes, repeat=False, blit=True)
