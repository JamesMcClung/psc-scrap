from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
import numpy as np

from ...particle_data import ParticleData
from ..snapshot_generator import SnapshotParams, snapshot_generator
from .. import util


__all__ = ["draw_histogram"]


@snapshot_generator("histogram")
def draw_histogram(params: SnapshotParams[ParticleData], fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)
    params.data.read_step(params.step)

    binned_data, rho_edges, val_edges = np.histogram2d(
        params.data._data.col("rho"),
        params.data._data.col(params.data.variable.h5_variable_name),
        bins=[60, 80],
        weights=params.data._data.col("w"),
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

    mesh = ax.pcolormesh(rho_edges, val_edges, fs2d, cmap=params.data.variable.cmap_name)

    if params.draw_labels:
        ax.set_xlabel("$\\rho$")
        ax.set_ylabel(f"${params.data.variable.latex}$")
        ax.set_title(f"$f(\\rho, {params.data.variable.latex})$ at t={params.data.t:.3f} for $B={params.data.params_record.B0}$")

    if params.draw_colorbar:
        fig.colorbar(mesh)

    ax.set_ylim(*params.data.variable.val_bounds)

    # TODO add these as global params or something
    show_mean = True
    show_theoretical_mean = False

    if show_mean or show_theoretical_mean:
        vals_cc = (val_edges[1:] + val_edges[:-1]) / 2

        if show_mean:
            mean_vals = fs2d.T.dot(vals_cc) / fs2d.sum(axis=0)
            ax.plot(rhos_cc, mean_vals, "k", label="mean")

        if show_theoretical_mean:
            mean_vals_input = np.array([params.data.input.interpolate_value(rho, "v_phi") for rho in rhos_cc])
            ax.plot(rhos_cc, mean_vals_input, "b", label="theoretical mean")

        ax.legend(loc="right", fontsize="small")

    return fig, ax, mesh
