from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import matplotlib.collections as mplc
import numpy as np
import pandas as pd
import os

from .backend import ParamsRecord, load_bp
from .input_reader import Input

__all__ = ["ParticleReader"]

##########################


def _read_step(path: str, step: int, electronsOnly: bool = True) -> pd.DataFrame:
    rank = 0
    df = pd.read_hdf(os.path.join(path, f"prt.{step:06d}_p{rank:06d}.h5"), "particles/p0/1d")

    df["r"] = (df.y**2 + df.z**2) ** 0.5
    df.drop(df[df.r > df.y.max()].index, inplace=True)

    df["v_phi"] = (df.pz * df.y - df.py * df.z) / df.r
    df["v_rho"] = (df.py * df.y + df.pz * df.z) / df.r
    df.v_rho.fillna(0, inplace=True)
    df.v_phi.fillna(0, inplace=True)

    df.drop(columns=["x", "px", "m", "w", "tag"], inplace=True)

    if electronsOnly:
        df = df[df.q == -1]
        df.drop(columns=["q"], inplace=True)
    df["step"] = step
    return df


##########################


class ParticleReader:
    def __init__(self, path: str) -> None:
        self.path = path
        params_record = ParamsRecord(path)

        self.inputFile = params_record.path_input
        self.B = params_record.B0
        self.maxStep = params_record.nmax
        self.reversed = params_record.reversed

    def read_step(self, step: int) -> None:
        self.t: float = load_bp(self.path, "pfd", step).time

        self.df = _read_step(self.path, step)
        self.input = Input(self.inputFile)

    def plot_distribution(
        self,
        param: str,
        fig: mplf.Figure = None,
        ax: plt.Axes = None,
        minimal: bool = False,
        show_mean: bool = True,
    ) -> tuple[mplf.Figure, plt.Axes, mplc.QuadMesh]:
        """param: "v_phi", "v_rho", "py", "pz" """

        if not (fig or ax):
            fig, ax = plt.subplots()

        hist, rhos, vals = np.histogram2d(self.df.r, self.df[param], bins=[60, 80])
        rhos_cc = (rhos[1:] + rhos[:-1]) / 2
        fs2d = hist.T / rhos_cc

        mesh = ax.pcolormesh(rhos, vals, fs2d, cmap="Reds")

        if not minimal:
            ax.set_xlabel("$\\rho$")
            ax.set_ylabel("$v_\\phi$")
            ax.set_title(f"f($\\rho$, $v_\\phi$) at t={self.t:.3f} for $B={self.B}$")
            fig.colorbar(mesh)

        if param in ["v_phi", "v_rho", "py", "pz"]:
            ax.set_ylim(-0.003, 0.003)

        if show_mean:
            vals_cc = (vals[1:] + vals[:-1]) / 2

            mean_vals = fs2d.T.dot(vals_cc) / fs2d.sum(axis=0)
            # mean_vals_input = np.array([self.input.interpolate_value(rho, "v_phi") for rho in rhos_cc])

            ax.plot(rhos_cc, mean_vals, "k", label="mean")
            # ax.plot(rhos_cc, mean_vals_input, "b", label="target mean")
            ax.legend(loc="right", fontsize="small")

        return fig, ax, mesh
