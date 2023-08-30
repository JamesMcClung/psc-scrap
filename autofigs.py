#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import os
import yaml
import bgk
import matplotlib.pyplot as plt
import matplotlib.figure as mplf
import matplotlib as mpl
import numpy as np
import xarray as xr
from sequence import Sequence
from autofigs_history import History
import bgk.autofigs as autofigs
from bgk.autofigs.options import FIGURE_TYPES, TRIVIAL_FIGURE_TYPES


########################################################

_VALID_FLAGS = {"save", "only", "warn"}


def _extract_flag_and_val(arg: str) -> tuple[str, str | None]:
    arg = arg.lstrip("-")
    if "=" in arg:
        return tuple(arg.split("="))
    return arg, None


flags = dict(_extract_flag_and_val(arg) for arg in sys.argv if arg.startswith("-"))
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

if invalid_flags := set(flags) - _VALID_FLAGS:
    print(f"Invalid flags: {invalid_flags}")
    print(f"Valid flags: {_VALID_FLAGS}")
    exit(1)
if "only" in flags and flags["only"] not in FIGURE_TYPES:
    print(f"Invalid --only value: {flags['only']}")
    print(f"Valid --only values: {FIGURE_TYPES}")
    exit(1)
for flag in ["save", "warn"]:
    if flag in flags and flags[flag] is not None:
        print(f"Invalid --{flag} value: {flags[flag]}")
        print(f"Flag --{flag} does not take values.")
        exit(1)


if "save" not in flags:
    print("WARNING: NOT SAVING TO HISTORY. ADD --save TO RECORD.")

########################################################


def get_autofigs_config() -> str:
    file = "autofigs.yml" if not args else args[0]
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


config = get_autofigs_config()

########################################################

empty_suite = {figure_option: [] for figure_option in FIGURE_TYPES}


def apply_suite(instruction_item: dict) -> dict:
    filled_instruction_item = empty_suite.copy()
    if "suite" in instruction_item:
        filled_instruction_item.update(config["suites"][instruction_item["suite"]])
    filled_instruction_item.update(instruction_item)
    return filled_instruction_item


def maybe_apply_only_flag(instruction_item: dict) -> dict:
    if "only" not in flags:
        return instruction_item
    chosen_figure = flags["only"]
    filtered_item = instruction_item.copy()
    for opt in instruction_item:
        if opt in FIGURE_TYPES and opt != chosen_figure:
            filtered_item[opt] = []
    return filtered_item


########################################################


def get_params_in_order(item: dict[str, list[str]]) -> list[str]:
    params = set(sum((item[option] for option in TRIVIAL_FIGURE_TYPES), start=[]))
    if "ne" in params:
        params.remove("ne")
        return ["ne"] + list(params)
    return list(params)


########################################################

history = History("autofigs.history.yml")

for item in config["instructions"]:
    item = apply_suite(item)
    item = maybe_apply_only_flag(item)

    path = item["path"]
    outdir = item["output_directory"]
    os.makedirs(outdir, exist_ok=True)

    print(f"Entering {path}")
    print(f"Saving to {outdir}")

    history.log_item(item, warn="warn" in flags)

    prefix = item.get("prefix", "")
    if prefix.endswith("/"):
        os.makedirs(os.path.join(outdir, item["prefix"]), exist_ok=True)

    case = item.get("case", "auto")
    if case == "auto":
        case = "max" if bgk.readParam(path, "maxwellian", str).lower() == "true" else "exact"

    B = bgk.readParam(path, "H_x", float)
    res = bgk.readParam(path, "n_grid", int)
    ve_coef = bgk.readParam(path, "v_e_coef", float)
    input_path = bgk.readParam(path, "path_to_data", str)

    print(f"  (slice={item['slice']})")
    if item["slice"] == "whole":
        which_slice = bgk.DataSlice(slice(None, None), "")
    elif item["slice"] == "center":
        struct_radius = bgk.Input(input_path).get_radius_of_structure()
        which_slice = bgk.DataSlice(slice(-struct_radius, struct_radius), "Central ")

    loader = bgk.Loader(path, engine="pscadios2", species_names=["e", "i"])

    size = loader._get_xr_dataset("pfd", 0).length[1]  # get the y-length (= z-length)

    ##########################

    def get_fig_name(fig_type: str, param_str: str, case: str) -> str:
        ext = "mp4" if fig_type == "movie" else "png"
        param_str = param_str.replace("_", "")
        maybe_rev = "-rev" if ve_coef < 0 else ""
        return f"{fig_type}-{param_str}-{case}{maybe_rev}-B{B:05.2f}-n{res}.{ext}"

    def get_fig_path(fig_name: str) -> str:
        if prefix.endswith("/"):
            return os.path.join(outdir, prefix, fig_name)
        return os.path.join(outdir, prefix + fig_name)

    def save_fig(fig: mplf.Figure, fig_name: str) -> None:
        fig.savefig(get_fig_path(fig_name), bbox_inches="tight", pad_inches=0.01, dpi=300)
        plt.close("all")

    ##########################

    nframes = item.get("nframes", 100)
    videoMaker = bgk.VideoMaker(nframes, loader)

    params_to_load = get_params_in_order(item)

    if item["periodic"]:
        print(f"  Loading ne for determining period...")
        videoMaker.loadData(bgk.run_params.ne)
        videoMaker.setSlice(which_slice)
        time_cutoff_idx = videoMaker.getIdxPeriod()
        duration_in_title = "Over First Oscillation"
    else:
        first_param_str = params_to_load[0]
        print(f"  Loading {first_param_str} for determining run duration...")
        videoMaker.loadData(bgk.run_params.__dict__[first_param_str])
        videoMaker.setSlice(which_slice)
        time_cutoff_idx = len(videoMaker.times) - 1
        duration_in_title = "Over Run"

    ##########################
    for param_str in params_to_load:
        print(f"  Loading {param_str}...")

        param: bgk.ParamMetadata = bgk.run_params.__dict__[param_str]
        videoMaker.loadData(param)
        videoMaker.setSlice(which_slice)

        ##########################

        if param_str in item["extrema"]:
            print(f"    Generating extrema profiles...")
            fig, _ = autofigs.plot_extrema(videoMaker)
            save_fig(fig, get_fig_name("extrema", param_str, case))

        ##########################

        if param_str in item["profiles"]:
            print(f"    Generating profile...")
            fig, _ = autofigs.plot_profiles(videoMaker, time_cutoff_idx, duration_in_title)
            save_fig(fig, get_fig_name("profile", param_str, case))

        ##########################

        if param_str in item["videos"]:
            print(f"    Generating movie...")

            fig, ax, im = videoMaker.viewFrame(0)
            fig.tight_layout(pad=0)
            anim = videoMaker.viewMovie(fig, ax, im)

            anim.save(get_fig_path(get_fig_name("movie", param_str, case)), dpi=450)

        ##########################

        if param_str in item["stabilities"]:
            print(f"    Generating stability plot...")

            fig, _ = videoMaker.viewStability()

            save_fig(fig, get_fig_name("stability", param_str, case))

        ##########################

        if param_str in item["origin_means"]:
            print(f"    Generating origin mean plot...")

            fig, _ = videoMaker.viewMeansAtOrigin()

            save_fig(fig, get_fig_name("originmean", param_str, case))

        ##########################

        if param_str in item["periodograms"]:
            print(f"    Generating periodogram...")

            fig, _ = videoMaker.viewPeriodogram()

            save_fig(fig, get_fig_name("periodogram", param_str, case))

    ##########################

    if item["sequences"]:
        # get times and step indices
        print(f"  Loading ne for sequences...")
        videoMaker.loadData(bgk.run_params.ne)
        videoMaker.setSlice(which_slice)

        n_frames = min(5, time_cutoff_idx + 1)
        frame_idxs = [round(i * time_cutoff_idx / (n_frames - 1)) for i in range(n_frames)]

        times = [videoMaker.times[frame_idx] for frame_idx in frame_idxs]
        step_idxs = [frame_idx * videoMaker._which_stepsPerFrame(videoMaker._currentParam.outputBaseName) for frame_idx in frame_idxs]
        particles = bgk.ParticleReader(path)

        for seq_params in item["sequences"]:
            print(f"    Generating sequence [{', '.join(seq_params)}]...")
            seq = Sequence(len(seq_params), step_idxs, times)
            for i, seq_param in enumerate(seq_params):
                seq_param = str(seq_param)  # just for the linter; doesn't do anything
                print(f"      Loading {seq_param}...")
                if seq_param.startswith("prt:"):
                    seq.plot_row_prt(i, particles, seq_param.removeprefix("prt:"))
                else:
                    videoMaker.loadData(bgk.run_params.__dict__[seq_param])
                    videoMaker.setSlice(which_slice)
                    seq.plot_row_pfd(i, videoMaker)

            def name_to_latex(name: str) -> str:
                name = name.replace("rho", "\\rho").replace("phi", "\\phi")
                if "_" not in name:
                    name = name[0] + "_" + name[1:]
                if name.startswith("prt:"):
                    name = f"f(\\rho, {name.removeprefix('prt:')})"
                else:
                    name += "(y, z)"
                return name

            params_latex = ", ".join([name_to_latex(seq_param) for seq_param in seq_params])
            save_fig(seq.get_fig(f"Snapshots of ${params_latex}$ for $B_0={B}$ {duration_in_title}"), get_fig_name("sequence", ",".join(seq_params).replace(":", ""), case))

    if "save" in flags:
        history.save()
