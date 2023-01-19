#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import os
import yaml
import dotenv

sys.path.append(dotenv.dotenv_values()["PYTHONPATH"])

import bgk
import matplotlib.pyplot as plt
import matplotlib.figure as mplf
import matplotlib.cm as mplcm
import numpy as np
import xarray as xr

########################################################


def get_autofigs_config() -> str:
    file = "autofigs.yml" if len(sys.argv) == 1 else sys.argv[1]
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


config = get_autofigs_config()

########################################################

outdir = config["output_directory"]

print(f"Generating figures in {outdir}")

for item in config["instructions"]:
    path = item["path"]

    B = bgk.readParam(path, "H_x", float)
    res = bgk.readParam(path, "n_grid", int)
    size = bgk.readParam(path, "box_size", float)
    ve_coef = bgk.readParam(path, "v_e_coef", float)
    input_path = bgk.readParam(path, "path_to_data", str)

    struct_radius = bgk.Input(input_path).get_radius_of_structure()

    centerSlice = bgk.DataSlice(slice(-struct_radius, struct_radius), "Central ")

    loader = bgk.Loader(path, engine="pscadios2", species_names=["e", "i"])

    ##########################

    def get_fig_name(fig_type: str, param_str: str) -> str:
        ext = "mp4" if fig_type == "movie" else "png"
        return f"{fig_type}_{param_str}_B{B}_n{res}_v{'-' if ve_coef<0 else '+'}.{ext}"

    def save_fig(fig: mplf.Figure, fig_name: str) -> None:
        fig.savefig(os.path.join(outdir, fig_name), bbox_inches="tight", pad_inches=0.01, dpi=300)
        plt.close("all")

    ##########################

    nframes = 100
    videoMaker = bgk.VideoMaker(nframes, loader)

    ##########################

    for param_str in set(item["sequences"] + item["profiles"] + item["videos"] + item["stabilities"]):
        param: bgk.ParamMetadata = bgk.run_params.__dict__[param_str]
        videoMaker.loadData(param)
        videoMaker.setSlice(centerSlice)

        if param_str in item["profiles"]:
            maxR = videoMaker._currentSlice.slice.stop
            rStep = size / 100

            def getMeanAndStd(data: xr.DataArray, r: float) -> tuple[float, float]:
                rslice = data.where((r <= videoMaker.rGrid) & (videoMaker.rGrid < r + rStep))
                return rslice.mean().item(), rslice.std().item()

            rs = np.arange(0, maxR, rStep)

            def getMeansAndStds(data):
                return tuple(zip(*[getMeanAndStd(data, r) for r in rs]))

            ##########################

            allMeans = np.array([getMeansAndStds(videoMaker.slicedDatas[idx])[0] for idx in range(nframes)])

            ##########################

            time_cutoff_idx = videoMaker.getLocalExtremaIndices(np.less)[0]
            titleText = "over First Oscillation"

            ##########################

            nsamples = 13

            indices = sorted(list({round(i) for i in np.linspace(0, time_cutoff_idx, nsamples)}))

            cmap = mplcm.get_cmap("rainbow")
            n_label_indices = 5
            label_indices = [indices[round(i * (len(indices) - 1) / (n_label_indices - 1))] for i in range(n_label_indices)]

            fig, ax = plt.subplots()

            for i in indices:
                label = f"$t={videoMaker.times[i]:.2f}$" if i in label_indices else "_nolegend_"
                ax.plot(rs, allMeans[i], color=cmap(i / max(indices)), label=label)

            ax.set_xlabel("$\\rho$")
            ax.set_ylabel(param.title)
            ax.set_title(f"Changing Radial Profile of {param.title} for $B={B}$ {titleText}")
            ax.legend()
            fig.tight_layout()

            ##########################

            save_fig(fig, get_fig_name("profile", param_str))

        if param_str in item["videos"]:
            fig, ax, im = videoMaker.viewFrame(0)
            fig.tight_layout(pad=0)
            anim = videoMaker.viewMovie(fig, ax, im)

            anim.save(os.path.join(outdir, get_fig_name("movie", param_str)), dpi=450)

        if param_str in item["stabilities"]:
            fig, _ = videoMaker.viewStability()

            save_fig(fig, get_fig_name("stability", param_str))

        if param_str in item["sequences"]:
            minima = videoMaker.getLocalExtremaIndices(np.less)

            startFrame = 0
            endFrame = minima[0]
            titleText = "over First Oscillation"

            ##########################

            nStillFrames = 5

            fig, axs = plt.subplots(1, nStillFrames)
            stillFrames = [startFrame + round(i * (endFrame - startFrame) / (nStillFrames - 1)) for i in range(nStillFrames)]

            for frame, ax in zip(stillFrames, axs):
                videoMaker.viewFrame(frame, fig, ax, minimal=True)
                ax.set_title(f"$t={videoMaker.times[frame]:.2f}$")
                ax.tick_params("both", which="both", labelbottom=False, labelleft=frame == stillFrames[0])
            fig.suptitle(f"Snapshots of {param.title} for $B_0={B}$ {titleText}")
            fig.tight_layout(pad=0)
            fig.set_size_inches(9, 2.5)

            fig.subplots_adjust(right=0.9)
            cbar_ax = fig.add_axes([0.91, 0.2, 0.01, 0.56])
            fig.colorbar(axs[0].images[0], cax=cbar_ax)

            ##########################

            save_fig(fig, get_fig_name("sequence", param_str))
