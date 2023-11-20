import matplotlib as mpl
import matplotlib.pyplot as plt

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from xarray import DataArray
from ..output_reader import VideoMaker


def get_mean(data: DataArray, r: float, dr: float, videoMaker: VideoMaker) -> float:
    rslice = data.where((r <= videoMaker.grid_rho) & (videoMaker.grid_rho < r + dr))
    return rslice.mean().item()


def save_fig(fig: Figure, path: str, close: bool = False):
    fig.savefig(path, bbox_inches="tight", pad_inches=0.01, dpi=300)
    if close:
        plt.close(fig)


def get_cmap(name: str, min: float = 0.0, max: float = 1.0, reverse: bool = False):
    return lambda x: mpl.colormaps[name](min + (1 - x if reverse else x) * (max - min))


def ensure_fig_ax(fig: Figure | None, ax: Axes | None) -> tuple[Figure, Axes]:
    if (fig or ax) is None:
        fig, ax = plt.subplots()
    return fig, ax
