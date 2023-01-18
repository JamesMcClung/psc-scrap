#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import os
import yaml
import dotenv

sys.path.append(dotenv.dotenv_values()["PYTHONPATH"])

import bgk
import matplotlib.pyplot as plt
import numpy as np

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

    nframes = 100
    videoMaker = bgk.VideoMaker(nframes, loader)

    ##########################

    for param_str in set(item["sequences"] + item["profiles"] + item["videos"] + item["stabilities"]):
        if param_str in item["profiles"]:
            pass
        if param_str in item["videos"]:
            pass
        if param_str in item["sequences"]:

            # Move this section out once profiles/videos are implemented:
            param = bgk.run_params.__dict__[param_str]
            videoMaker.loadData(param)
            videoMaker.setSlice(centerSlice)

            ##########################

            minima = videoMaker.getLocalExtremaIndices(np.less)

            startFrame = 0
            endFrame = minima[0]
            titleText = "over First Oscillation"

            ##########################

            plt.close("all")
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

            fig_name = f"sequence_{param_str}_B{B}_n{res}_v{'-' if ve_coef<0 else '+'}.png"
            fig.savefig(os.path.join(outdir, fig_name), bbox_inches="tight", pad_inches=0.01, dpi=300)