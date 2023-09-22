from __future__ import annotations

__all__ = ["RunManager", "FrameManagerLinear"]

import os
from typing import Callable, Type
from itertools import combinations
from functools import cached_property
from math import prod, lcm
from abc import ABCMeta, abstractmethod

from .params_record import ParamsRecord
from ..util.stream import Stream
from ..typing import PrefixBP, PrefixH5
from .wrapper_bp import load_bp
from ..input_reader import Input, get_B0
from ..run_params import ParamMetadata


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
    max_step = steps.fold(-1, max)
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


class RunManager:
    def __init__(self, path_run: str, max_step_override: int | None = None) -> None:
        self.path_run = path_run
        self.params_record = ParamsRecord(path_run)
        self.run_diagnostics = RunDiagnostics(self)

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

    @cached_property
    def run_input(self) -> Input:
        return Input(self.params_record.path_input)

    def get_max_step(self, prefix: PrefixBP | PrefixH5 | None = None) -> int | None:
        if prefix is None:
            return max([step for step in [self.max_pfd, self.max_pfd_moments, self.max_gauss, self.max_prt] if step is not None] or [None])
        return {
            "pfd": self.max_pfd,
            "pfd_moments": self.max_pfd_moments,
            "gauss": self.max_gauss,
            "prt": self.max_prt,
        }[prefix]

    def get_interval(self, prefix: PrefixBP | PrefixH5) -> int | None:
        return {
            "pfd": self.interval_pfd,
            "pfd_moments": self.interval_pfd_moments,
            "gauss": self.interval_gauss,
            "prt": self.interval_prt,
        }[prefix]

    def get_suggested_nframes(self, nframes_min: int, prefix: PrefixBP | PrefixH5) -> int | None:
        return FrameManagerLinear.get_suggested_nframes(nframes_min, self.get_max_step(prefix), self.get_interval(prefix))

    def get_frame_manager(
        self,
        frame_manager_type: Type[FrameManager],
        nframes: int,
        params: list[ParamMetadata],
    ) -> FrameManager:
        return frame_manager_type(self, nframes, params)

    def get_steps_per_frame(self, nframes: int, prefix: PrefixBP | PrefixH5) -> int | None:
        return FrameManagerLinear.get_steps_per_frame(nframes, self.get_max_step(prefix), self.get_interval(prefix))


class RunDiagnostics:
    def __init__(self, run_manager: RunManager) -> None:
        self._run_manager = run_manager

    def get_completion_percent(self) -> float:
        return 100.0 * self._run_manager.get_max_step() / self._run_manager.params_record.nmax

    def get_time_coverage_percent(self, nframes: int, prefix: PrefixBP | PrefixH5) -> float:
        return 100.0 * nframes * self._run_manager.get_steps_per_frame(nframes, prefix) / self._run_manager.params_record.nmax

    def get_steps_coverage_percent(self, nframes: int, prefix: PrefixBP | PrefixH5) -> float:
        return 100.0 * nframes / (self._run_manager.get_max_step(prefix) / self._run_manager.get_interval(prefix))

    def print_coverage(self, nframes: int, prefix: PrefixBP | PrefixH5 = "pfd") -> None:
        time_coverage_percent = self.get_time_coverage_percent(nframes, prefix)
        steps_per_frame = self._run_manager.get_steps_per_frame(nframes, prefix)
        print(f"Steps in run:      {self._run_manager.get_max_step()} ({self.get_completion_percent():.1f}% complete)")
        print(f"nframes:           {nframes}")
        print(f"Steps per frame:   {steps_per_frame}")
        print(f"Last step used:    {nframes * steps_per_frame} ({time_coverage_percent:.1f}% coverage, {self.get_steps_coverage_percent(nframes, prefix):.1f}% step used)")
        if time_coverage_percent != 100:
            print(f"Suggested nframes: {self._run_manager.get_suggested_nframes(nframes, prefix)}")

    @cached_property
    def domain_size(self) -> float:
        return load_bp(self._run_manager.path_run, "pfd", 0).lengths[1]

    @cached_property
    def hole_radius(self) -> float:
        return self._run_manager.run_input.get_radius_of_structure()

    def check_params(self) -> None:
        param_B0 = self._run_manager.params_record.B0
        input_B0 = get_B0(self._run_manager.params_record.path_input)
        if param_B0 != input_B0:
            print("PROBLEM: MISMATCH IN B0")
            print(f"Params record: B0={param_B0}")
            print(f"Input:         B0={input_B0}")
        else:
            print("Check passed: param B0 = input B0")

        if self.hole_radius * 2 >= self.domain_size:
            print("PROBLEM: DOMAIN SIZE TOO SMALL")
            print(f"Hole diameter: {self.hole_radius * 2}")
            print(f"Domain size:   {self.domain_size}")
        else:
            print("Check passed: hole diameter < domain size")

    def print_params(self) -> None:
        print(f"B0:            {self._run_manager.params_record.B0}")
        print(f"Resolution:    {self._run_manager.params_record.res}^2")
        print(f"Domain size:   {self.domain_size}")
        print(f"Hole diameter: {2 * self.hole_radius:.3f} ({100.0 * 2 * self.hole_radius / self.domain_size:.1f}% of domain)")
        print(f"Reversed:      {self._run_manager.params_record.reversed}")
        print(f"Input path:    {self._run_manager.params_record.path_input}")


class FrameManager(metaclass=ABCMeta):
    def __init__(self, run_manager: RunManager, nframes: int, params: list[ParamMetadata]) -> None:
        self._run_manager = run_manager
        self._prefixes = {param.prefix_bp for param in params}
        self._interval_all = Stream(self._prefixes).map(run_manager.get_interval).reduce(lcm)
        self._last_step = Stream(self._prefixes).map(run_manager.get_max_step).reduce(min)

        self.nframes = nframes
        self.steps = self._get_steps()
        assert nframes == len(self.steps)

        if Stream(params).map(lambda param: param.skipFirst).any():
            self.steps[0] = self._interval_all

    @abstractmethod
    def _get_steps(self) -> list[int]:
        raise NotImplementedError()

    def get_time_coverage_percent(self) -> float:
        return 100.0 * self.steps[-1] / self._run_manager.params_record.nmax

    def get_steps_coverage_percent(self) -> float:
        return 100.0 * self.nframes / (self._run_manager.params_record.nmax / self._interval_all + 1)  # +1 because of t=0

    def print_coverage(self) -> None:
        print(f"Steps in run:      {self._run_manager.get_max_step()} ({self._run_manager.run_diagnostics.get_completion_percent():.1f}% complete)")
        print(f"nframes:           {self.nframes}")
        print(f"Steps per frame:   {self.steps[-1] / (self.nframes - 1)}")
        print(f"Last step used:    {self.steps[-1]} ({self.get_time_coverage_percent():.1f}% coverage, {self.get_steps_coverage_percent():.1f}% step used)")


class FrameManagerLinear(FrameManager):
    def __init__(self, run_manager: RunManager, nframes: int, params: list[ParamMetadata]) -> None:
        super().__init__(run_manager, nframes, params)

    def _get_steps(self) -> list[int]:
        steps_per_frame = FrameManagerLinear.get_steps_per_frame(self.nframes, self._last_step, self._interval_all)
        return list(range(0, self._last_step, steps_per_frame))

    def print_coverage(self) -> None:
        super().print_coverage()
        if self.get_time_coverage_percent() != 100:
            print(f"Suggested nframes: {FrameManagerLinear.get_suggested_nframes(self.nframes, self._last_step, self._interval_all)}")

    @staticmethod
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

    @staticmethod
    def get_steps_per_frame(nframes: int, out_max: int | None, out_interval: int) -> int | None:
        if out_max is None:
            return None

        steps_per_frame = out_max // nframes
        steps_per_frame -= steps_per_frame % out_interval
        return steps_per_frame


def _remove_duplicates(steps: list[int]) -> list[int]:
    return list(dict.fromkeys(steps))  # order is maintained since 3.7


class FrameManagerNearest(FrameManager):
    def __init__(self, run_manager: RunManager, nframes: int, params: list[ParamMetadata]) -> None:
        super().__init__(run_manager, nframes, params)

    def _get_steps(self) -> list[int]:
        steps = [FrameManagerNearest.get_step(frame, self.nframes, self._last_step, self._interval_all) for frame in range(self.nframes)]
        return _remove_duplicates(steps)

    @staticmethod
    def get_step(frame: int, nframes: int, last_step: int, interval: int) -> int:
        step_float = last_step * frame / min(1, nframes - 1)  # include first and last steps
        step_nearest = interval * round(step_float / interval)
        return step_nearest
