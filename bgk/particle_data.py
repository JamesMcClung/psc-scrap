from matplotlib import pyplot as plt
import matplotlib.figure as mplf
import matplotlib.collections as mplc
import numpy as np

from .backend import load_bp, load_h5
from .params_record import ParamsRecord
from .input_reader import Input
from .particle_variables import ParticleVariable, v_phi

__all__ = ["ParticleData"]


##########################


class ParticleData:
    def __init__(self, path: str, initial_variable: ParticleVariable = v_phi) -> None:
        self.path = path
        params_record = ParamsRecord(path)

        self.inputFile = params_record.path_input
        self.B = params_record.B0
        self.maxStep = params_record.nmax
        self.reversed = params_record.reversed

        self.set_variable(initial_variable)

    def read_step(self, step: int) -> None:
        self.t: float = load_bp(self.path, "pfd", step).time

        self._data = load_h5(self.path, "prt", step).drop_columns(["id", "tag"]).drop_species("i").drop_corners()
        self.input = Input(self.inputFile)

    def set_variable(self, variable: ParticleVariable):
        self.variable = variable

    def plot_distribution(
        self,
        var: ParticleVariable,
        fig: mplf.Figure = None,
        ax: plt.Axes = None,
        minimal: bool = False,
        show_mean: bool = True,
        show_theoretical_mean: bool = False,
    ) -> tuple[mplf.Figure, plt.Axes, mplc.QuadMesh]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        binned_data, rho_edges, val_edges = np.histogram2d(
            self._data.col("rho"),
            self._data.col(var.h5_variable_name),
            bins=[60, 80],
            weights=self._data.col("w"),
        )
        # n_particles in binned_data[rho, v_phi] = f(rho, v_phi) * 2*pi*rho * drho * dv_phi,
        #   where the factor of 2*pi*rho comes from the implicit integration over phi.
        # Want something proportional to f(rho, v_phi), so divide out rho.
        #   Could also divide out drho and dv_phi (e.g. by setting density=True in histogram2d),
        #   but they are just constants so it doesn't matter.
        rhos_cc = (rho_edges[1:] + rho_edges[:-1]) / 2
        # transpose to a) make rho along rows (2nd dim), which pcolormesh takes to be the x-axis, and b) make broadcasting work
        fs2d = binned_data.T / rhos_cc
        # now: fs2d[v_phi, rho] = f(rho, v_phi) * consts

        mesh = ax.pcolormesh(rho_edges, val_edges, fs2d, cmap=var.cmap_name)

        if not minimal:
            ax.set_xlabel("$\\rho$")
            ax.set_ylabel(f"${var.latex}$")
            ax.set_title(f"$f(\\rho, {var.latex})$ at t={self.t:.3f} for $B={self.B}$")
            fig.colorbar(mesh)

        ax.set_ylim(*var.val_bounds)

        if show_mean or show_theoretical_mean:
            vals_cc = (val_edges[1:] + val_edges[:-1]) / 2

            if show_mean:
                mean_vals = fs2d.T.dot(vals_cc) / fs2d.sum(axis=0)
                ax.plot(rhos_cc, mean_vals, "k", label="mean")

            if show_theoretical_mean:
                mean_vals_input = np.array([self.input.interpolate_value(rho, "v_phi") for rho in rhos_cc])
                ax.plot(rhos_cc, mean_vals_input, "b", label="theoretical mean")

            ax.legend(loc="right", fontsize="small")

        return fig, ax, mesh
