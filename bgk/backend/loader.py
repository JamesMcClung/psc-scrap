import os
from math import prod
import itertools
from typing import Literal as _Literal

from .params_record import ParamsRecord

__all__ = ["Loader", "PrefixBP"]


PrefixBP = _Literal["pfd", "pfd_moments", "gauss"]


def _getFactors(n: int) -> list[int]:
    factors = []
    f = 2
    while f**2 <= n:
        if n % f == 0:
            factors.append(f)
            n //= f
        else:
            f += 1
    factors.append(n)
    return factors


def _get_out_max(bpfiles: list[str], outType: str) -> int:
    return max(itertools.chain([0], (int(fname.split(".")[1]) for fname in bpfiles if fname.startswith(f"{outType}."))))


class Loader:
    def __init__(self, path: str, engine: str, species_names: list[str], max_step: int = 0) -> None:
        self.path = path
        self.engine = engine
        self.species_names = species_names

        self.params_record = ParamsRecord(path)

        self.case_name = ("Maxwellian" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

        # init max written step for each type of output
        bpfiles = [fname for fname in os.listdir(self.path) if fname[-2:] == "bp"]

        self.fields_max = max_step or _get_out_max(bpfiles, "pfd")
        self.moments_max = max_step or _get_out_max(bpfiles, "pfd_moments")
        self.gauss_max = max_step or _get_out_max(bpfiles, "gauss")

    def get_all_suggested_nframes(self, min_nframes: int) -> tuple[int, int, int]:
        """Return tuple of suggested nframes for fields, moments, and gauss outputs"""
        fields_nframes = self._get_suggested_nframes(min_nframes, self.fields_max, self.params_record.interval_fields)
        moments_nframes = self._get_suggested_nframes(min_nframes, self.moments_max, self.params_record.interval_moments)
        gauss_nframes = self._get_suggested_nframes(min_nframes, self.gauss_max, self.params_record.interval_gauss)

        return fields_nframes, moments_nframes, gauss_nframes

    def _get_suggested_nframes(self, min_nframes: int, out_max: int, out_every: int) -> int:
        if out_max == 0:
            return 0
        max_nframes = out_max // out_every
        factors = _getFactors(max_nframes)
        smallest_nframes_so_far = max_nframes

        for nfactors in range(0, len(factors) + 1):
            for factors_subset in itertools.combinations(factors, nfactors):
                if min_nframes <= (test_nframes := max_nframes // prod(factors_subset)) < smallest_nframes_so_far:
                    smallest_nframes_so_far = test_nframes

        return smallest_nframes_so_far
