from matplotlib.artist import Artist
from matplotlib.collections import QuadMesh
from matplotlib.figure import Figure
from matplotlib.pyplot import Axes
import numpy as np

from ...particle_data import ParticleData
from ..snapshot_generator import SnapshotParams, snapshot_generator
from .. import util


__all__ = ["draw_histogram"]


@snapshot_generator("histogram")
def draw_histogram(params: SnapshotParams[ParticleData], fig: Figure = None, ax: Axes = None) -> tuple[Figure, Axes, list[Artist]]:
    fig, ax = util.ensure_fig_ax(fig, ax)
    params.data.set_step(params.step)

    if params.set_data_only:
        # retrieve coordinates from previous mesh and use them for binning
        mesh: QuadMesh = ax.collections[0]
        coords = mesh.get_coordinates()  # array of dimension (nrows, ncols, 2), where nrows/ncols refers to mesh vertices and 2 is x/y
        bins = [coords[0, :, 0], coords[:, 0, 1]]
    else:
        bins = [60, 80]

    val_edges = np.linspace(-3e-3, 3e-3, 60)
    binned_data, rho_edges, val_edges = np.histogram2d(
        params.data.col("rho"),
        params.data.col(params.data.variable.h5_variable_name),
        bins=bins,
        weights=params.data.col("w"),
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

    if params.set_data_only:
        mesh.set_array(fs2d)
    else:
        mesh = ax.pcolormesh(rho_edges, val_edges, fs2d, cmap=params.data.variable.cmap_name)
    artists = [mesh]

    if params.draw_labels:
        ax.set_xlabel("$\\rho$")
        ax.set_ylabel(f"${params.data.variable.latex}$")
        ax.set_title(f"$f(\\rho, {params.data.variable.latex})$ at t={params.data.time:.3f} for $B={params.data.params_record.B0}$")

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
            if params.set_data_only:
                ax.get_lines()[0].set_data(rhos_cc, mean_vals)
            else:
                ax.plot(rhos_cc, mean_vals, "k", label="mean")

        if show_theoretical_mean:
            mean_vals_input = np.array([params.data.input.interpolate_value(rho, "v_phi") for rho in rhos_cc])
            if params.set_data_only:
                ax.get_lines()[-1].set_data(rhos_cc, mean_vals_input)
            else:
                ax.plot(rhos_cc, mean_vals_input, "b", label="theoretical mean")

        artists += ax.get_lines()

        if not params.set_data_only:
            ax.legend(loc="right", fontsize="small")

    return fig, ax, artists
