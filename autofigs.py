#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3

import sys
import os
import yaml
import matplotlib.pyplot as plt

import bgk
import bgk.autofigs as autofigs
import bgk.autofigs.util as util
from bgk.autofigs.history import History
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
        return ["ne"] + sorted(list(params))
    return sorted(list(params))


########################################################

history = History("autofigs.history.yml")

for item in config["instructions"]:
    item = apply_suite(item)
    item = maybe_apply_only_flag(item)

    path = item["path"]
    print(f"Entering {path}")

    params_to_load_standard = get_params_in_order(item)
    params_to_load_special = list({seq_param for seq_params in item["sequences"] for seq_param in seq_params})
    if not params_to_load_standard and not params_to_load_special:
        print(f"No figures requested. Skipping.")
        continue

    outdir = item["output_directory"]
    os.makedirs(outdir, exist_ok=True)
    print(f"Saving to {outdir}")

    history.log_item(item, warn="warn" in flags)

    prefix: str = item.get("prefix", "")
    if prefix.endswith("/"):
        os.makedirs(os.path.join(outdir, item["prefix"]), exist_ok=True)

    run_manager = bgk.RunManager(path)
    params_record = run_manager.params_record

    case = item.get("case", "auto")
    if case == "auto":
        case = params_record.init_strategy

    print(f"  (slice={item['slice']})")
    if item["slice"] == "whole":
        which_slice = bgk.DataSlice(slice(None, None), "")
    elif item["slice"] == "center":
        struct_radius = run_manager.run_diagnostics.hole_radius
        which_slice = bgk.DataSlice(slice(-struct_radius, struct_radius), "Central ")

    size = run_manager.run_diagnostics.domain_size

    ##########################

    def get_fig_path(fig_type: str, param_str: str, case: str) -> str:
        ext = "mp4" if fig_type == "movie" else "png"
        param_str = param_str.replace("_", "")
        maybe_rev = "-rev" if params_record.reversed else ""
        fig_name = f"{prefix}{fig_type}-{param_str}-{case}{maybe_rev}-B{params_record.B0:05.2f}-n{params_record.res}.{ext}"
        return os.path.join(outdir, fig_name)

    ##########################

    nframes = item.get("nframes", 100)
    videoMaker = bgk.VideoMaker(nframes, run_manager)

    if item["periodic"]:
        print(f"  Loading ne for determining period...")
        videoMaker.loadData(bgk.run_params.ne)
        videoMaker.setSlice(which_slice)
        time_cutoff_idx = videoMaker.getIdxPeriod()
        duration_in_title = "Over First Oscillation"
    else:
        first_param_str = (params_to_load_standard or ["ne"])[0]
        print(f"  Loading {first_param_str} for determining run duration...")
        videoMaker.loadData(bgk.run_params.__dict__[first_param_str])
        videoMaker.setSlice(which_slice)
        time_cutoff_idx = len(videoMaker.times) - 1
        duration_in_title = "Over Run"

    ##########################
    for param_str in params_to_load_standard:
        print(f"  Loading {param_str}...")

        param: bgk.ParamMetadata = bgk.run_params.__dict__[param_str]
        videoMaker.loadData(param)
        videoMaker.setSlice(which_slice)

        ##########################

        if param_str in item["extrema"]:
            print(f"    Generating extrema profiles...")
            fig, _ = autofigs.plot_extrema(videoMaker)
            util.save_fig(fig, get_fig_path("extrema", param_str, case), close=True)

        ##########################

        if param_str in item["profiles"]:
            print(f"    Generating profile...")
            fig, _ = autofigs.plot_profiles(videoMaker, time_cutoff_idx, duration_in_title)
            util.save_fig(fig, get_fig_path("profile", param_str, case), close=True)

        ##########################

        if param_str in item["videos"]:
            print(f"    Generating movie...")

            fig, ax, im = videoMaker.viewFrame(0)
            fig.tight_layout(pad=0)
            anim = videoMaker.viewMovie(fig, ax, im)

            anim.save(get_fig_path("movie", param_str, case), dpi=450)
            plt.close(fig)

        ##########################

        if param_str in item["stabilities"]:
            print(f"    Generating stability plot...")
            fig, _ = videoMaker.viewStability()
            util.save_fig(fig, get_fig_path("stability", param_str, case), close=True)

        ##########################

        if param_str in item["origin_means"]:
            print(f"    Generating origin mean plot...")
            fig, _ = videoMaker.viewMeansAtOrigin()
            util.save_fig(fig, get_fig_path("originmean", param_str, case), close=True)

        ##########################

        if param_str in item["periodograms"]:
            print(f"    Generating periodogram...")
            fig, _ = videoMaker.viewPeriodogram()
            util.save_fig(fig, get_fig_path("periodogram", param_str, case), close=True)

    ##########################

    if item["sequences"]:
        # get times and step indices
        print(f"  Loading ne for sequences...")
        videoMaker.loadData(bgk.run_params.ne)
        videoMaker.setSlice(which_slice)

        n_frames = min(5, time_cutoff_idx + 1)
        frames = [round(i * time_cutoff_idx / (n_frames - 1)) for i in range(n_frames)]

        times = [videoMaker.times[frame] for frame in frames]
        steps = [videoMaker.frame_manager.steps[frame] for frame in frames]
        particles = bgk.ParticleReader(path)

        for seq_params in item["sequences"]:
            print(f"    Generating sequence [{', '.join(seq_params)}]...")
            seq = autofigs.Sequence(len(seq_params), steps, times)
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
                if name.startswith(tuple("ebj")):
                    name = name.capitalize()
                name = name.replace("rho", "\\rho").replace("phi", "\\phi")
                if "_" not in name:
                    name = name[0] + "_" + name[1:]
                if name.startswith("prt:"):
                    name = f"f(\\rho, {name.removeprefix('prt:')})"
                else:
                    name += "(y, z)"
                return name

            params_latex = ", ".join([name_to_latex(seq_param) for seq_param in seq_params])
            util.save_fig(seq.get_fig(f"Snapshots of ${params_latex}$ for $B_0={params_record.B0}$ {duration_in_title}"), get_fig_path("sequence", ",".join(seq_params).replace(":", ""), case), close=True)

    if "save" in flags:
        history.save()
