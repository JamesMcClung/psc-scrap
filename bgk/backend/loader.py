import typing
import xarray as xr
import os
from math import prod
import itertools

# enables xarray to load bp files
import psc

__all__ = ["readParam", "Loader"]


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


T = typing.TypeVar("T")


def readParam(path: str, paramName: str, paramType: typing.Callable[[str], T], default: T = None) -> T:
    with open(os.path.join(path, "params_record.txt")) as records:
        for line in records:
            if line.startswith(paramName):
                return paramType(line.split()[1])
    if default is None:
        raise Exception(f"Cannot find param '{paramName}' in file '{path}'")
    return default


class Loader:
    def __init__(self, path: str, engine: str, species_names: list[str], max_step: int = 0) -> None:
        self.path = path
        self.engine = engine
        self.species_names = species_names

        self.B = readParam(path, "H_x", float)

        self.fields_every = readParam(path, "fields_every", int, 200)
        self.moments_every = readParam(path, "moments_every", int, 200)
        self.gauss_every = readParam(path, "gauss_every", int)
        self.nmax = readParam(path, "nmax", int)

        self.maxwellian = readParam(path, "maxwellian", lambda s: s.lower() == "true")
        self.ve_coef = readParam(path, "v_e_coef", int)
        self.case_name = ("Maxwellian" if self.maxwellian else "Exact") + (", Reversed" if self.ve_coef < 0 else "")

        # init max written step for each type of output
        bpfiles = [fname for fname in os.listdir(self.path) if fname[-2:] == "bp"]

        self.fields_max = max_step or _get_out_max(bpfiles, "pfd")
        self.moments_max = max_step or _get_out_max(bpfiles, "pfd_moments")
        self.gauss_max = max_step or _get_out_max(bpfiles, "gauss")

    def _get_xr_dataset(self, outputBaseName: typing.Literal["pfd", "pfd_moments", "gauss"], step: int) -> xr.Dataset:
        return xr.open_dataset(
            os.path.join(self.path, f"{outputBaseName}.{step:09d}.bp"),
            engine=self.engine,
            species_names=self.species_names,
        )

    def get_all_suggested_nframes(self, min_nframes: int) -> tuple[int, int, int]:
        """Return tuple of suggested nframes for fields, moments, and gauss outputs"""
        fields_nframes = self._get_suggested_nframes(min_nframes, self.fields_max, self.fields_every)
        moments_nframes = self._get_suggested_nframes(min_nframes, self.moments_max, self.moments_every)
        gauss_nframes = self._get_suggested_nframes(min_nframes, self.gauss_max, self.gauss_every)

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
