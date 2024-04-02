from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import matplotlib.ticker as ticker

from ..field_data import FieldData
from ..particle_variables import ParticleVariable
from ..particle_data import ParticleData
from .snapshot_generator import SnapshotGenerator, SnapshotParams

__all__ = ["Sequence"]


class Sequence:
    fig: mplf.Figure
    ax_rows: list[list[plt.Axes]]  # technically it's a numpy ndarray

    def __init__(self, n_rows: int, steps: list[int], times: list[float]) -> None:
        self.steps = steps
        self.times = times

        self.fig, self.ax_rows = plt.subplots(
            n_rows,
            len(times) + 1,  # +1 col for the cmap
            squeeze=False,
            width_ratios=[8] * len(times) + [1],
        )

    def plot_row_pfd(self, row_idx: int, fields: FieldData, snapshot_generator: SnapshotGenerator) -> None:
        ax_row = self.ax_rows[row_idx]
        cmap_ax = ax_row[-1]

        params = SnapshotParams(fields, 0, 0, False, False)
        for ax, step, time in zip(ax_row, self.steps, self.times):
            params.frame = 0 if step == 0 else fields.frame_manager.steps.index(step)  # sometimes step 0 is skipped
            snapshot_generator.draw_snapshot(params, self.fig, ax)
            ax.set_title(f"$t={time:.2f}$" if row_idx == 0 else "")
            ax.tick_params("both", which="both", labelbottom=row_idx == len(self.ax_rows) - 1, labelleft=step == self.steps[0])
            ax.set_aspect("auto")
        cmap_ax.set_aspect("auto")
        self.fig.colorbar(ax.get_images()[0], cax=cmap_ax)

    def plot_row_prt(self, row_idx: int, particles: ParticleData, var: ParticleVariable) -> None:
        ax_row = self.ax_rows[row_idx]
        cmap_ax = ax_row[-1]
        for step, ax, time in zip(self.steps, ax_row, self.times):
            particles.read_step(step)
            _, _, mesh = particles.plot_distribution(var, self.fig, ax, minimal=True, show_mean=True)
            ax.set_title(f"$t={time}$" if row_idx == 0 else "")
            ax.tick_params("both", which="both", labelbottom=row_idx == len(self.ax_rows) - 1, labelleft=step == self.steps[0])
            ax.set_aspect("auto")

        cmap_ax.set_aspect("auto")
        cbar_formatter = ticker.ScalarFormatter()
        cbar_formatter.set_powerlimits((-1, 3))
        self.fig.colorbar(mesh, cax=cmap_ax, format=cbar_formatter)

    def get_fig(self, title: str) -> mplf.Figure:
        self.fig.suptitle(title)
        self.fig.set_size_inches(2 * len(self.ax_rows[0]), 2 * len(self.ax_rows))
        return self.fig
