from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import matplotlib.collections as mplc
import numpy as np
import pandas as pd
import os

from .output_reader import readParam, Loader
from .input_reader import Input

__all__ = ["ParticleReader"]

##########################


def _read_step(path: str, step: int, electronsOnly: bool = True) -> pd.DataFrame:
    rank = 0
    df = pd.read_hdf(os.path.join(path, f"prt.{step:06d}_p{rank:06d}.h5"), "particles/p0/1d")
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

        self.inputFile = readParam(path, "path_to_data", str)
        self.B = readParam(path, "H_x", float)
        self.maxStep = readParam(path, "nmax", int)
        self.ve_coef = readParam(path, "v_e_coef", float)
        self.size = readParam(path, "box_size", float)

    def read_step(self, step: int) -> None:
        self.t: float = Loader(self.path, engine="pscadios2", species_names=["e", "i"])._get_xr_dataset("pfd", step).time

        self.df = _read_step(self.path, step)
        self.input = Input(self.inputFile)

        df = self.df
        df["r"] = (df.y**2 + df.z**2) ** 0.5
        df["v_phi"] = (df.pz * df.y - df.py * df.z) / df.r
        df["v_rho"] = (df.py * df.y + df.pz * df.z) / df.r
        df.v_rho.fillna(0, inplace=True)
        df.v_phi.fillna(0, inplace=True)
        self.df = df[df.r < self.size / 2]

    def plot_distribution(
        self, fig: mplf.Figure = None, ax: plt.Axes = None, minimal: bool = False, means: bool = True
    ) -> tuple[mplf.Figure, plt.Axes, mplc.QuadMesh]:

        if not (fig or ax):
            fig, ax = plt.subplots()

        hist, rhos, v_phis = np.histogram2d(self.df.r, self.df.v_phi, bins=[60, 80])
        rhos_cc = (rhos[1:] + rhos[:-1]) / 2
        fs2d = hist.T / rhos_cc

        mesh = ax.pcolormesh(rhos, v_phis, fs2d, cmap="Reds")

        if not minimal:
            ax.set_xlabel("$\\rho$")
            ax.set_ylabel("$v_\\phi$")
            ax.set_title(f"f($\\rho$, $v_\\phi$) at t={self.t:.3f} for $B={self.B}$")
            fig.colorbar(mesh)

        ax.set_ylim(-0.003, 0.003)
        if means:
            v_phis_cc = (v_phis[1:] + v_phis[:-1]) / 2

            mean_v_phis = fs2d.T.dot(v_phis_cc) / fs2d.sum(axis=0)
            mean_v_phis_input = np.array([self.input.interpolate_value(rho, "v_phi") for rho in rhos_cc])

            ax.plot(rhos_cc, mean_v_phis, "k", label="actual mean")
            ax.plot(rhos_cc, mean_v_phis_input, "b", label="target mean")
            ax.legend()

        return fig, ax, mesh
