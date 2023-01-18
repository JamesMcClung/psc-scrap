import sys


def get_output_dir() -> str:
    return "/mnt/lustre/IAM851/jm1667/psc-scrap/figs/"


def get_paths_to_data() -> list[str]:
    paths_in_args = sys.argv[1:]
    paths_in_stdin = [] if sys.stdin.isatty() else list(filter(None, sys.stdin.read().splitlines()))
    return paths_in_args + paths_in_stdin


paths_to_data = get_paths_to_data()
output_dir = get_output_dir()

print(f"Making figs for {paths_to_data} at {output_dir}")
