__all__ = ["RunManager", "get_suggested_nframes"]

import os
from typing import Callable, Literal
from itertools import combinations
from math import prod

from .params_record import ParamsRecord
from ..util.stream import Stream

PrefixBP = Literal["pfd", "pfd_moments", "gauss"]
PrefixH5 = Literal["prt"]


def _get_files_by_extension(path: str, extension: str) -> list[str]:
    return [file_name for file_name in os.listdir(path) if file_name.endswith(extension)]


def _get_step_bp(file_bp: str) -> int:
    return int(file_bp.split(".")[1])


def _get_step_h5(file_h5: str) -> int:
    return int(file_h5.split(".")[1].split("_")[0])


def _get_max_step(
    files: list[str],
    prefix: str,
    get_step: Callable[[str], int],
    max_step_override: int | None = None,
) -> int | None:
    steps = Stream(files).filter(lambda file: file.startswith(prefix)).map(get_step)
    if max_step_override is not None:
        steps = steps.filter(lambda step: step <= max_step_override)
    max_step = steps.reduce(max, -1)
    if max_step < 0:
        return None
    return max_step


def _get_factors(n: int) -> list[int]:
    factors = []
    maybe_factor = 2
    product_of_remaining_factors = n
    while maybe_factor**2 <= product_of_remaining_factors:
        if product_of_remaining_factors % maybe_factor == 0:
            factors.append(maybe_factor)
            product_of_remaining_factors //= maybe_factor
        else:
            maybe_factor += 1
    factors.append(product_of_remaining_factors)
    return factors


def get_suggested_nframes(nframes_min: int, out_max: int | None, out_interval: int) -> int | None:
    if out_max is None:
        return None

    nframes_max = out_max // out_interval
    factors = _get_factors(nframes_max)
    nframes_best = nframes_max

    for factors_subset_len in range(0, len(factors) + 1):
        for factors_subset in combinations(factors, factors_subset_len):
            nframes_test = nframes_max // prod(factors_subset)
            if nframes_min <= nframes_test < nframes_best:
                nframes_best = nframes_test

    return nframes_best


class RunManager:
    def __init__(self, path_run: str, max_step_override: int | None = None) -> None:
        self.params_record = ParamsRecord(path_run)

        files_bp = _get_files_by_extension(path_run, ".bp")
        files_h5 = _get_files_by_extension(path_run, ".h5")

        self.max_pfd = _get_max_step(files_bp, "pfd.", _get_step_bp, max_step_override)
        self.max_pfd_moments = _get_max_step(files_bp, "pfd_moments.", _get_step_bp, max_step_override)
        self.max_gauss = _get_max_step(files_bp, "gauss.", _get_step_bp, max_step_override)
        self.max_prt = _get_max_step(files_h5, "prt.", _get_step_h5, max_step_override)

        self.interval_pfd = self.params_record.interval_fields
        self.interval_pfd_moments = self.params_record.interval_moments
        self.interval_gauss = self.params_record.interval_gauss
        self.interval_prt = self.params_record.interval_particles

    def get_max_step(self, prefix: PrefixBP | PrefixH5 | None = None) -> int | None:
        if prefix is None:
            return max([step for step in [self.max_pfd, self.max_pfd_moments, self.max_gauss, self.max_prt] if step is not None] or [None])
        return {
            "pfd": self.max_pfd,
            "pfd_moments": self.max_pfd_moments,
            "gauss": self.max_gauss,
            "prt": self.max_prt,
        }[prefix]

    def get_interval(self, prefix: PrefixBP | PrefixH5) -> int:
        return {
            "pfd": self.interval_pfd,
            "pfd_moments": self.interval_pfd_moments,
            "gauss": self.interval_gauss,
            "prt": self.interval_prt,
        }[prefix]

    def get_suggested_nframes(self, nframes_min: int, prefix: PrefixBP | PrefixH5) -> int | None:
        return get_suggested_nframes(nframes_min, self.get_max_step(prefix), self.get_interval(prefix))
