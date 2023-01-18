#!/mnt/lustre/IAM851/jm1667/psc-scrap/env/bin/python3
import sys
import yaml


def get_autofigs_config() -> str:
    file = "autofigs.yml" if len(sys.argv) == 1 else sys.argv[1]
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


config = get_autofigs_config()
print(config)
