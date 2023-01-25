#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import os
import yaml
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
    print(f"Entering {path}")

    B = bgk.readParam(path, "H_x", float)
    res = bgk.readParam(path, "n_grid", int)
    size = bgk.readParam(path, "box_size", float)
    ve_coef = bgk.readParam(path, "v_e_coef", float)
    input_path = bgk.readParam(path, "path_to_data", str)

    struct_radius = bgk.Input(input_path).get_radius_of_structure()

    centerSlice = bgk.DataSlice(slice(-struct_radius, struct_radius), "Central ")

    loader = bgk.Loader(path, engine="pscadios2", species_names=["e", "i"])

    ##########################

    def get_fig_name(fig_type: str, param_str: str, case: str) -> str:
        ext = "mp4" if fig_type == "movie" else "png"
        param_str = param_str.replace("_", "")
        maybe_rev = "-rev" if ve_coef < 0 else ""
        return f"{fig_type}-{param_str}-{case}{maybe_rev}-B{B}-n{res}.{ext}"

    def save_fig(fig: mplf.Figure, fig_name: str) -> None:
        fig.savefig(os.path.join(outdir, fig_name), bbox_inches="tight", pad_inches=0.01, dpi=300)
        plt.close("all")

    ##########################

    nframes = 100
    videoMaker = bgk.VideoMaker(nframes, loader)

    ##########################
    FIGURE_OPTIONS = ["sequences", "profiles", "videos", "stabilities", "origin_means", "periodograms"]
    for param_str in set(sum((item.get(option, []) for option in FIGURE_OPTIONS), start=[])):
        print(f"  Loading {param_str}...")

        param: bgk.ParamMetadata = bgk.run_params.__dict__[param_str]
        videoMaker.loadData(param)
        videoMaker.setSlice(centerSlice)

        if param_str in item.get("profiles", []):
            print(f"    Generating profile...")
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

            if item["periodic"]:
                time_cutoff_idx = videoMaker.getIdxPeriod()
                titleText = "Over First Oscillation"
            else:
                time_cutoff_idx = len(videoMaker.times) - 1
                titleText = "Over Run"

            ##########################

            nsamples = 13

            indices = sorted(list({round(i) for i in np.linspace(0, time_cutoff_idx, nsamples)}))

            cmap = mplcm.get_cmap("rainbow")
            n_label_indices = min(5, time_cutoff_idx + 1)
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

            save_fig(fig, get_fig_name("profile", param_str, item["case"]))

        if param_str in item.get("videos", []):
            print(f"    Generating movie...")

            fig, ax, im = videoMaker.viewFrame(0)
            fig.tight_layout(pad=0)
            anim = videoMaker.viewMovie(fig, ax, im)

            anim.save(os.path.join(outdir, get_fig_name("movie", param_str, item["case"])), dpi=450)

        if param_str in item.get("stabilities", []):
            print(f"    Generating stability plot...")

            fig, _ = videoMaker.viewStability()

            save_fig(fig, get_fig_name("stability", param_str, item["case"]))

        if param_str in item.get("origin_means", []):
            print(f"    Generating origin mean plot...")

            fig, _ = videoMaker.viewMeansAtOrigin()

            save_fig(fig, get_fig_name("originmean", param_str, item["case"]))

        if param_str in item.get("periodograms", []):
            print(f"    Generating periodogram...")

            fig, _ = videoMaker.viewPeriodogram()

            save_fig(fig, get_fig_name("periodogram", param_str, item["case"]))

        if param_str in item.get("sequences", []):
            include_distr = param_str in item["distr_in_sequence"]
            print(f"    Generating sequence{' with distribution' * include_distr}...")

            if item["periodic"]:
                time_cutoff_idx = videoMaker.getIdxPeriod()
                titleText = "Over First Oscillation"
            else:
                time_cutoff_idx = len(videoMaker.times) - 1
                titleText = "Over Run"

            ##########################

            if include_distr:
                particles = bgk.ParticleReader(path)

            ##########################

            nStillFrames = min(5, time_cutoff_idx + 1)

            fig, axs = plt.subplots(1 + include_distr, nStillFrames + 1)
            stillFrames = [round(i * time_cutoff_idx / (nStillFrames - 1)) for i in range(nStillFrames)]

            img_ax_row = axs[0] if include_distr else axs
            img_cax = img_ax_row[-1]
            for frame, img_ax in zip(stillFrames, img_ax_row):
                _, _, im = videoMaker.viewFrame(frame, fig, img_ax, minimal=True)
                img_ax.set_title(f"$t={videoMaker.times[frame]:.2f}$")
                img_ax.tick_params("both", which="both", labelbottom=False, labelleft=frame == stillFrames[0])
                img_ax.set_aspect(1)
            img_cax.set_aspect(20)
            fig.colorbar(im, cax=img_cax)

            if include_distr:
                distr_ax_row = axs[1]
                distr_cax = distr_ax_row[-1]
                for frame, distr_ax in zip(stillFrames, distr_ax_row):
                    particles.read_step(frame * videoMaker._which_stepsPerFrame(param.outputBaseName))
                    _, _, mesh = particles.plot_distribution(fig, distr_ax, minimal=True, means=False)
                    distr_ax.set_title("")
                    distr_ax.tick_params("both", which="both", labelbottom=True, labelleft=frame == stillFrames[0])
                    distr_ax.set_aspect("auto")
                distr_cax.set_aspect(20)
                fig.colorbar(mesh, cax=distr_cax)

            fig.set_size_inches(9, 2.5 * (1 + include_distr))
            fig.suptitle(f"Snapshots of {param.title} for $B_0={B}$ {titleText}")
            fig.tight_layout(pad=0)

            ##########################

            save_fig(fig, get_fig_name("sequence", param_str, item["case"]))
