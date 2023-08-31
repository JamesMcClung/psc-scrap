import yaml
from functools import cache

__all__ = ["OriginMeans"]


@cache
def _get_yml(yml_path: str) -> dict[str, dict]:
    with open(yml_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)


class OriginMeans:
    times: list[float]
    means: list[float]

    def __init__(self, case: str, param: str, yml_path: str = "figdata.yml") -> None:
        """`case`: e.g. `"B00.10-n1024"`.\n\n `param`: e.g. `"ne"`"""
        self.case = case
        self.param = param

        data = _get_yml(yml_path)[case]
        self.times = data["times"]
        self.means = data["origin_means"][param]