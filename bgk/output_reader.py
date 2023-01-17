from math import prod
from typing import Any
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.animation as animation
import numpy as np
import os
import itertools
from scipy.signal import argrelextrema

from .run_params import ParamMetadata

# enables xarray to load bp files
import psc

__all__ = ["readParam", "ParamMetadata", "DataSlice", "Loader", "VideoMaker"]


def readParam(path: str, paramName: str, paramType) -> Any:
    with open(path + "params_record.txt") as records:
        for line in records:
            if line.startswith(paramName):
                return paramType(line.split()[1])
    raise Exception(f"Cannot find param '{paramName}' in file '{path}'")


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


def _setTitle(ax: Any, viewAdj: str, paramName: str, time: float) -> None:
    ax.set_title(viewAdj + paramName + " (t={:.3f})".format(time))


class DataSlice:
    def __init__(self, slice: slice, viewAdjective: str) -> None:
        self.slice = slice
        self.viewAdjective = viewAdjective


def _prepData(data: xr.DataArray) -> xr.DataArray:
    return data[0, :, :].transpose()


def _get_out_max(bpfiles: list[str], outType: str) -> int:
    return max(itertools.chain([0], (int(fname.split(".")[1]) for fname in bpfiles if fname.startswith(f"{outType}."))))


class Loader:
    def __init__(self, path: str, length: tuple[float, float, float], engine: str, species_names: list[str]) -> None:
        self.path = path
        self.length = length
        self.engine = engine
        self.species_names = species_names

        # init out_every for each type of output
        with open(self.path + "params_record.txt") as records:
            self.fields_every = 200  # default value
            self.moments_every = 200  # default value
            self.gauss_every = 200  # default value
            for line in records:
                if line.startswith("fields_every"):
                    self.fields_every = int(line.split()[1])
                elif line.startswith("moments_every"):
                    self.moments_every = int(line.split()[1])
                elif line.startswith("gauss_every"):
                    self.gauss_every = int(line.split()[1])
                elif line.startswith("nmax"):
                    self.nmax = int(line.split()[1])

        # init max written step for each type of output
        bpfiles = [fname for fname in os.listdir(self.path) if fname[-2:] == "bp"]

        self.fields_max = _get_out_max(bpfiles, "pfd")
        self.moments_max = _get_out_max(bpfiles, "pfd_moments")
        self.gauss_max = _get_out_max(bpfiles, "gauss")

    def _get_xr_dataset(self, outputBaseName: str, step: int) -> xr.Dataset:
        return xr.open_dataset(
            self.path + f"{outputBaseName}.{str(step).rjust(9,'0')}.bp",
            length=self.length,
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


class VideoMaker:
    def __init__(self, nframes: int, loader: Loader) -> None:
        self.loader = loader
        self.nframes = nframes
        self.rGrid = None

        # init stepsPerFrame for each type of output
        self.gauss_stepsPerFrame = self.loader.gauss_max // self.nframes
        self.gauss_stepsPerFrame -= self.gauss_stepsPerFrame % self.loader.gauss_every

        self.fields_stepsPerFrame = self.loader.fields_max // self.nframes
        self.fields_stepsPerFrame -= self.fields_stepsPerFrame % self.loader.fields_every

        self.moments_stepsPerFrame = self.loader.moments_max // self.nframes
        self.moments_stepsPerFrame -= self.moments_stepsPerFrame % self.loader.moments_every

    def _which_every(self, outputBaseName: str) -> int:
        return {
            "pfd": self.loader.fields_every,
            "pfd_moments": self.loader.moments_every,
            "gauss": self.loader.gauss_every,
        }[outputBaseName]

    def _which_stepsPerFrame(self, outputBaseName: str) -> int:
        return {
            "pfd": self.fields_stepsPerFrame,
            "pfd_moments": self.moments_stepsPerFrame,
            "gauss": self.gauss_stepsPerFrame,
        }[outputBaseName]

    def _getDataAndTime(self, param: ParamMetadata, frameIdx: int) -> tuple[xr.DataArray, float]:
        if frameIdx == 0 and param.skipFirst:
            dataset = self.loader._get_xr_dataset(param.outputBaseName, self._which_every(param.outputBaseName))
        else:
            dataset = self.loader._get_xr_dataset(param.outputBaseName, frameIdx * self._which_stepsPerFrame(param.outputBaseName))

        if self.rGrid is None:
            self.xGrid = dataset.y
            self.yGrid = dataset.z
            self.rGrid = (self.xGrid**2 + self.yGrid**2) ** 0.5

        if isinstance(param.varName, list):
            if param.combine == "magnitude":
                rawData = _prepData(sum(dataset[var]) ** 2 for var in param.varName) ** 0.5
            elif param.combine == "sum":
                rawData = _prepData(sum(dataset[var]) for var in param.varName)
            elif param.combine == "difference":
                rawData = _prepData(dataset[param.varName[0]] - dataset[param.varName[1]])
            else:
                rawData_x = _prepData(dataset[param.varName[0]])
                rawData_y = _prepData(dataset[param.varName[1]])
                if param.combine == "radial":
                    rawData = (rawData_x * self.xGrid + rawData_y * self.yGrid) / self.rGrid
                elif param.combine == "azimuthal":
                    rawData = (-rawData_x * self.yGrid + rawData_y * self.xGrid) / self.rGrid
                else:
                    raise Exception(f"Invalid combine method: {param.combine}")
                rawData = rawData.fillna(0)
        else:
            rawData = _prepData(dataset[param.varName])
        return param.coef * rawData, dataset.time

    def loadData(self, param: ParamMetadata):
        self._currentParam = param
        self.datas, self.times = [list(x) for x in zip(*[self._getDataAndTime(param, idx) for idx in range(self.nframes)])]
        self.times = np.array(self.times)

    def setSlice(self, slice: DataSlice):
        self._currentSlice = slice
        self.slicedDatas = [data.sel(y=self._currentSlice.slice, z=self._currentSlice.slice) for data in self.datas]

        # update min and max values to show on color scale
        self._vmax = (
            self._currentParam.vmax if not self._currentParam.vmax is None else max(np.nanquantile(data.values, 1) for data in self.slicedDatas)
        )
        self._vmin = (
            self._currentParam.vmin if not self._currentParam.vmin is None else min(np.nanquantile(data.values, 0) for data in self.slicedDatas)
        )
        if self._currentParam.vmax is self._currentParam.vmin is None:
            self._vmax = max(self._vmax, -self._vmin)
            self._vmin = -self._vmax

    # Methods that use the data

    def viewFrame(self, frameIdx: int, fig: plt.Figure = None, ax: plt.Axes = None, minimal: bool = False) -> Any:
        if not (fig or ax):
            fig, ax = plt.subplots()

        im = ax.imshow(
            self.slicedDatas[frameIdx],
            cmap=self._currentParam.colors,
            vmin=self._vmin,
            vmax=self._vmax,
            origin="lower",
            extent=(
                self._currentSlice.slice.start,
                self._currentSlice.slice.stop,
                self._currentSlice.slice.start,
                self._currentSlice.slice.stop,
            ),
        )

        if not minimal:
            ax.set_xlabel("y")
            ax.set_ylabel("z")
            _setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frameIdx])
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
            fig.colorbar(im, ax=ax)

        return fig, ax, im

    def viewMovie(self, fig, ax, im) -> Any:
        def updateIm(frameIdx):
            im.set_array(self.slicedDatas[frameIdx])
            _setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frameIdx])
            return [im]

        return animation.FuncAnimation(fig, updateIm, interval=30, frames=self.nframes, repeat=False, blit=True)

    def _getNormsOfDiffs(self) -> np.array:
        def norm(x):
            return xr.apply_ufunc(np.linalg.norm, x, input_core_dims=[["y", "z"]])

        return np.array([norm(data - self.slicedDatas[0]) for data in self.slicedDatas])

    def viewStability(self):
        plt.xlabel("Time")
        plt.ylabel("2-Norm of Difference")
        plt.title("Deviation from ICs of " + self._currentSlice.viewAdjective + self._currentParam.title)

        plt.plot(self.times, self._getNormsOfDiffs())
        plt.show()

    def getLocalExtremaIndices(self, comparator) -> np.array:
        return argrelextrema(self._getNormsOfDiffs(), comparator, order=5)[0]
