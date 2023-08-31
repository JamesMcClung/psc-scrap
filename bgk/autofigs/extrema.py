import bgk
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.figure as mplf
from . import util


def _plot_lines(
    ax: plt.Axes,
    cmap,
    plot_indices: list[int],
    label_indices: list[int],
    xdata: list[float],
    ydatas: list[list[float]],
    tdata: list[float],
):
    for i in plot_indices:
        label = f"$t={tdata[i]:.2f}$" if i in label_indices else "_nolegend_"
        ax.plot(xdata, ydatas[i], color=cmap(i / max(plot_indices) if len(plot_indices) > 1 else 0.5), label=label)


def plot_extrema(
    videoMaker: bgk.output_reader.VideoMaker,
    fig: mplf.Figure = None,
    ax: plt.Axes = None,
) -> tuple[mplf.Figure, plt.Axes]:
    fig, ax = util.ensure_fig_ax(fig, ax)

    maxR = videoMaker._currentSlice.slice.stop
    rStep = videoMaker.lengths[1] / 100

    rs = np.arange(0, maxR, rStep)

    allMeans = np.array([[util.get_mean(videoMaker.slicedDatas[idx], r, rStep, videoMaker) for r in rs] for idx in range(videoMaker.nframes)])

    indices_maxs = videoMaker.getLocalExtremaIndices(np.greater_equal) or [videoMaker.nframes - 1]
    indices_mins = videoMaker.getLocalExtremaIndices(np.less_equal) or [0]

    cmap_mins = util.get_cmap("Blues", min=0.3, max=0.9)
    cmap_maxs = util.get_cmap("Reds", min=0.3, max=0.9)

    _plot_lines(ax, cmap_mins, indices_mins, [indices_mins[0], indices_mins[-1]], xdata=rs, ydatas=allMeans, tdata=videoMaker.times)
    _plot_lines(ax, cmap_maxs, indices_maxs, [indices_maxs[0], indices_maxs[-1]], xdata=rs, ydatas=allMeans, tdata=videoMaker.times)

    ax.set_xlabel("$\\rho$")
    ax.set_ylabel(videoMaker._currentParam.title)
    ax.set_title(f"Extremal Profiles of {videoMaker._currentParam.title} for $B_0={videoMaker.loader.B}$")
    ax.legend()
    fig.tight_layout()

    return fig, ax


if __name__ == "__main__":
    path = f"/mnt/lustre/IAM851/jm1667/psc-runs/case1/trials/max/B02.00-n256/"

    B = bgk.readParam(path, "H_x", float)
    res = bgk.readParam(path, "n_grid", int)
    ve_coef = bgk.readParam(path, "v_e_coef", float)
    input_path = bgk.readParam(path, "path_to_data", str)

    struct_radius = bgk.Input(input_path).get_radius_of_structure()

    wholeSlice = bgk.DataSlice(slice(None, None), "")
    centerSlice = bgk.DataSlice(slice(-struct_radius, struct_radius), "Central ")

    loader = bgk.Loader(path, engine="pscadios2", species_names=["e", "i"])
    size = loader._get_xr_dataset("pfd", 0).length[1]  # get the y-length (= z-length)

    print(f"B={B}")
    print(f"res={res}")
    print(f"size={size}")
    print(f"struct size={2*struct_radius:.3f}")
    print(f"ve_coef={ve_coef}")
    print(f"input_path={input_path}")

    # fiddle with this until as many steps as possible are used (usually, they can all be used)
    nframes = 100

    videoMaker = bgk.VideoMaker(nframes, loader)

    completion_percent = 100 * loader.fields_max / loader.nmax
    video_coverage_percent = 100 * nframes * videoMaker.fields_stepsPerFrame / loader.fields_max
    steps_used_percent = 100 * nframes / (loader.fields_max / loader.fields_every)
    print(f"steps simulated:      {loader.fields_max} ({completion_percent:.1f}% complete)")
    print(f"nframes in animation: {nframes}")
    print(f"steps per frame:      {videoMaker.fields_stepsPerFrame}")
    print(f"max step in video:    {nframes * videoMaker.fields_stepsPerFrame} ({video_coverage_percent:.1f}% coverage, {steps_used_percent:.1f}% step used)")
    if video_coverage_percent != 100:
        print(f"suggested nframes:    {loader.get_all_suggested_nframes(nframes)[0]}")

    import bgk.run_params as rp

    # select parameter
    param = rp.ne
    print(f"parameter: {param.title}")

    videoMaker.loadData(param)

    sliceId = 0
    whichSlice = [wholeSlice, centerSlice][sliceId]
    videoMaker.setSlice(whichSlice)

    print(f"view: {whichSlice.viewAdjective}= {whichSlice.slice}")

    fig, ax = plot_extrema(videoMaker)
    util.save_fig(fig, "figs-test/extrema.png")
