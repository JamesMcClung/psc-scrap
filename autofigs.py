#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import yaml
import dotenv

sys.path.append(dotenv.dotenv_values()["PYTHONPATH"])

import bgk

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
