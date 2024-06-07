#!env/bin/python3

import sys
import os
import yaml
import matplotlib.pyplot as plt

import bgk
import bgk.autofigs as autofigs
import bgk.autofigs.util as util
from bgk.autofigs.history import History
from bgk.autofigs.options import FIGURE_TYPES, TRIVIAL_FIGURE_TYPES
from bgk.autofigs.config import AutofigsConfig, AutofigsSuite

from bgk.autofigs.figure_generator import FIGURE_GENERATOR_REGISTRY

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

config = AutofigsConfig.from_file("autofigs.yml" if not args else args[0])
if "only" in flags:
    config.instructions.remove_figures_except(flags["only"])

########################################################

history = History("autofigs.history.yml")

for item in config.instructions:
    path = item.path
    print(f"Entering {path}")

    variables_to_load_names_standard = item.get_variable_names_in_order()
    variables_to_load_names_special = list({var_name for var_names in item["sequences"] for var_name in var_names} | set(item["videos"]))
    if not variables_to_load_names_standard and not variables_to_load_names_special:
        print(f"No figures requested. Skipping.")
        continue

    outdir = item["output_directory"]
    os.makedirs(outdir, exist_ok=True)
    print(f"Saving to {outdir}")

    history.log_item(item, warn="warn" in flags)

    prefix: str = item._instruction_item.get("prefix", "")
    if "/" in prefix:
        os.makedirs(os.path.join(outdir, prefix[: prefix.rindex("/")]), exist_ok=True)

    run_manager = bgk.RunManager(path)
    params_record = run_manager.params_record

    case = item._instruction_item.get("case", "auto")
    if case == "auto":
        case = params_record.init_strategy

    print(f"  (slice={item['slice']})")
    if item["slice"] == "whole":
        view_bounds = bgk.Bounds3D.whole()
    elif item["slice"] == "center":
        struct_radius = run_manager.run_diagnostics.hole_radius
        view_bounds = bgk.Bounds3D.center_yz(struct_radius)
    else:
        print(f"Invalid slice: '{item['slice']}'. Valid slices are 'whole' and 'center'.", file=sys.stderr)
        sys.exit(1)

    size = run_manager.run_diagnostics.domain_size

    ##########################

    def get_fig_path(fig_type: str, variable_name: str, case: str) -> str:
        ext = "mp4" if fig_type == "movie" else "png"
        variable_name = variable_name.replace("_", "")
        maybe_rev = "-rev" if params_record.reversed else ""
        fig_name = f"{prefix}{fig_type}-{variable_name}-{case}{maybe_rev}-B{params_record.B0:05.2f}-n{params_record.res}.{ext}"
        return os.path.join(outdir, fig_name)

    ##########################

    nframes = item._instruction_item.get("nframes", 100)
    fields = bgk.FieldData(nframes, run_manager)
    particles = bgk.ParticleData(run_manager)

    figure_params = autofigs.FigureParams()
    figure_params.fields = fields

    if item["periodic"]:
        print(f"  Loading ne for determining period...")
        fields.set_variable(bgk.field_variables.ne)
        fields.set_view_bounds(view_bounds)
        figure_params.time_cutoff_idx = fields.get_idx_period()
        figure_params.duration_in_title = "Over First Oscillation"
    else:
        first_variable_name = (variables_to_load_names_standard or ["ne"])[0]
        print(f"  Loading {first_variable_name} for determining run duration...")
        fields.set_variable(bgk.field_variables.__dict__[first_variable_name])
        fields.set_view_bounds(view_bounds)
        figure_params.time_cutoff_idx = nframes - 1
        figure_params.duration_in_title = "Over Run"

    ##########################
    for variable_name in variables_to_load_names_standard:
        print(f"  Loading {variable_name}...")

        variable: bgk.FieldVariable = bgk.field_variables.__dict__[variable_name]
        fields.set_variable(variable)
        fields.set_view_bounds(view_bounds)

        ##########################

        for figure_name in FIGURE_GENERATOR_REGISTRY:
            if variable_name in item[figure_name]:
                print(f"    Generating {figure_name}...")
                fig, _ = FIGURE_GENERATOR_REGISTRY[figure_name].generate_figure(figure_params)
                util.save_fig(fig, get_fig_path(figure_name, variable_name, case), close=True)

        ##########################

        if variable_name in item["videos"]:
            print(f"    Generating movie...")

            params = bgk.autofigs.SnapshotParams(fields, 0.0)
            fig, movie = autofigs.make_movie(nframes, params, bgk.autofigs.SNAPSHOT_GENERATOR_REGISTRY["image"])
            movie.save(get_fig_path("movie", variable_name, case), dpi=450)
            plt.close(fig)

    for variable_name in item["videos"]:
        variable_name = str(variable_name)  # for linting
        if variable_name.startswith("prt:"):
            print(f"  Loading {variable_name}...")
            print(f"    Generating movie...")
            variable: bgk.ParticleVariable = bgk.particle_variables.__dict__[variable_name.removeprefix("prt:")]
            particles.set_variable(variable)
            params = bgk.autofigs.SnapshotParams(particles, 0.0)
            fig, movie = autofigs.make_movie(nframes, params, bgk.autofigs.SNAPSHOT_GENERATOR_REGISTRY["histogram"])
            movie.save(get_fig_path("movie", variable_name.replace(":", ""), case), dpi=450)
            plt.close(fig)

    ##########################

    if item["sequences"]:
        # get times and step indices
        print(f"  Loading ne for sequences...")
        fields.set_variable(bgk.field_variables.ne)
        fields.set_view_bounds(view_bounds)

        n_frames = min(5, figure_params.time_cutoff_idx + 1)
        frames = [round(i * figure_params.time_cutoff_idx / (n_frames - 1)) for i in range(n_frames)]

        times = fields.axis_t[frames]
        steps = [fields.frame_manager.steps[frame] for frame in frames]

        for var_names in item["sequences"]:
            print(f"    Generating sequence [{', '.join(var_names)}]...")

            vars: list[bgk.FieldVariable | bgk.ParticleVariable] = [bgk.particle_variables.__dict__[var_name.removeprefix("prt:")] if var_name.startswith("prt:") else bgk.field_variables.__dict__[var_name] for var_name in map(str, var_names)]

            seq = autofigs.Sequence(len(var_names), steps, times)
            for i, var in enumerate(vars):
                print(f"      Loading {var.name}...")
                if isinstance(var, bgk.ParticleVariable):
                    particles.set_variable(var)
                    params = autofigs.SnapshotParams(particles, 0.0)
                    seq.plot_row(i, params, bgk.autofigs.SNAPSHOT_GENERATOR_REGISTRY["histogram"])
                else:
                    fields.set_variable(var)
                    fields.set_view_bounds(view_bounds)
                    params = autofigs.SnapshotParams(fields, 0.0)
                    seq.plot_row(i, params, bgk.autofigs.SNAPSHOT_GENERATOR_REGISTRY["image"])

            names_latex = ", ".join(f"f({bgk.particle_variables.rho.latex}, {var.latex})" if isinstance(var, bgk.ParticleVariable) else f"{var.latex}(y, z)" for var in vars)
            util.save_fig(seq.get_fig(f"Snapshots of ${names_latex}$ for $B_0={params_record.B0}$ {figure_params.duration_in_title}"), get_fig_path("sequence", ",".join(var_names).replace(":", ""), case), close=True)

    if "save" in flags:
        history.save()
