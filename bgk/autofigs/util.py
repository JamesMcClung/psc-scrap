import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# imports used for linting
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
from xarray import DataArray


def binned_mean(data: DataArray, coord: str, nbins: int, lower: float | None = None, upper: float | None = None) -> DataArray:
    if lower is None:
        lower = float(data.coords[coord].min())
    if upper is None:
        upper = float(data.coords[coord].max())

    return data.groupby_bins(coord, np.linspace(lower, upper, nbins + 1, endpoint=True), right=False).mean()


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
