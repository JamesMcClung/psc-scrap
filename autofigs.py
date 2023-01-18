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
    print(item)
