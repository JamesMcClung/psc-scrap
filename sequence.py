from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import bgk


class Sequence:
    def __init__(self, n_rows: int, step_idxs: list[int], times: list[float]) -> None:
        self.step_idxs = step_idxs
        self.times = times

        self.fig, self.axs = plt.subplots(
            n_rows,
            len(times) + 1,  # +1 col for the cmap
            squeeze=False,
            width_ratios=[8] * len(times) + [1],
        )

    def plot_row_pfd(self, row_idx: int, videoMaker: bgk.VideoMaker) -> None:
        axs_row = self.axs[row_idx]
        cmap_ax = axs_row[-1]

        for step_idx, ax, time in zip(self.step_idxs, axs_row, self.times):
            frame = step_idx // videoMaker._which_stepsPerFrame(videoMaker._currentParam.outputBaseName)
            _, _, im = videoMaker.viewFrame(frame, self.fig, ax, minimal=True)
            ax.set_title(f"$t={time:.2f}$" if row_idx == 0 else "")
            ax.tick_params("both", which="both", labelbottom=row_idx == len(self.axs) - 1, labelleft=step_idx == self.step_idxs[0])
            ax.set_aspect("auto")
        cmap_ax.set_aspect("auto")
        self.fig.colorbar(im, cax=cmap_ax)

    def plot_row_prt(self, row_idx: int, particles: bgk.ParticleReader, param: str) -> None:
        axs_row = self.axs[row_idx]
        cmap_ax = axs_row[-1]
        for step_idx, ax, time in zip(self.step_idxs, axs_row, self.times):
            particles.read_step(step_idx)
            _, _, mesh = particles.plot_distribution(param, self.fig, ax, minimal=True, show_mean=True)
            ax.set_title(f"$t={time}$" if row_idx == 0 else "")
            ax.tick_params("both", which="both", labelbottom=row_idx == len(self.axs) - 1, labelleft=step_idx == self.step_idxs[0])
            ax.set_aspect("auto")
        cmap_ax.set_aspect("auto")
        self.fig.colorbar(mesh, cax=cmap_ax)

    def get_fig(self, title: str) -> mplf.Figure:
        self.fig.suptitle(title)
        self.fig.set_size_inches(2 * len(self.axs[0]), 2 * len(self.axs))
        return self.fig
