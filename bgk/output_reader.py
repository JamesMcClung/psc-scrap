import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.animation as animation
import matplotlib.image as mpli
import matplotlib.figure as mplf
import numpy as np
import numpy.typing as npt
import scipy.signal as sig
from scipy.optimize import fmin

from .run_params import ParamMetadata
from .backend import Loader


__all__ = ["ParamMetadata", "DataSlice", "VideoMaker"]


class DataSlice:
    def __init__(self, slice: slice, viewAdjective: str) -> None:
        self.slice = slice
        self.viewAdjective = viewAdjective


def _prepData(data: xr.DataArray, recenter_x=False, recenter_y=False, recenter_z=False) -> xr.DataArray:
    if recenter_x:
        rolled = data.rolling(x=2).mean()
        rolled[0, :, :] = (data[0, :, :] + data[-1, :, :]) / 2
        data = rolled
    if recenter_y:
        rolled = data.rolling(y=2).mean()
        rolled[:, 0, :] = (data[:, 0, :] + data[:, -1, :]) / 2
        data = rolled
    if recenter_z:
        rolled = data.rolling(z=2).mean()
        rolled[:, :, 0] = (data[:, :, 0] + data[:, :, -1]) / 2
        data = rolled
    return data[0, :, :].transpose()  # This is correct - y and z may be initially mislabeled


def _recenter(name: str, dim: str) -> bool:
    # ec => recenter same dim; fc => recenter other dims
    return (name[1] == dim) == name.endswith("ec")


class VideoMaker:
    def __init__(self, nframes: int, loader: Loader) -> None:
        self.loader = loader
        self.nframes = nframes
        self.rGrid = None
        self._currentParam = None
        self._lengths = None
        self._last_lmin = 0, 0

        # init stepsPerFrame for each type of output
        self.gauss_stepsPerFrame = self.loader.gauss_max // self.nframes
        self.gauss_stepsPerFrame -= self.gauss_stepsPerFrame % self.loader.gauss_every

        self.fields_stepsPerFrame = self.loader.fields_max // self.nframes
        self.fields_stepsPerFrame -= self.fields_stepsPerFrame % self.loader.fields_every

        self.moments_stepsPerFrame = self.loader.moments_max // self.nframes
        self.moments_stepsPerFrame -= self.moments_stepsPerFrame % self.loader.moments_every

    def _setTitle(self, ax: plt.Axes, viewAdj: str, paramName: str, time: float) -> None:
        ax.set_title(f"{viewAdj} {paramName}, t={time:.3f} ($B_0={self.loader.B}$, {self.loader.case_name})")

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
                rawData = _prepData(sum(dataset[var] ** 2 for var in param.varName)) ** 0.5
            elif param.combine == "sum":
                rawData = _prepData(sum(dataset[var] for var in param.varName))
            elif param.combine == "difference":
                rawData = _prepData(dataset[param.varName[0]] - dataset[param.varName[1]])
            else:
                rawData_x = _prepData(dataset[param.varName[0]], recenter_y=_recenter(param.varName[0], "y"), recenter_z=_recenter(param.varName[0], "z"))
                rawData_y = _prepData(dataset[param.varName[1]], recenter_y=_recenter(param.varName[1], "y"), recenter_z=_recenter(param.varName[1], "z"))

                # recenter structure
                def sumsq(p: tuple[float, float], ret_rawdata=False) -> float:
                    adjusted_xgrid = self.xGrid - p[0]
                    adjusted_ygrid = self.yGrid - p[1]
                    adjusted_rgrid = (adjusted_xgrid**2 + adjusted_ygrid**2) ** 0.5

                    if param.combine == "radial":
                        rawData = (rawData_x * adjusted_xgrid + rawData_y * adjusted_ygrid) / adjusted_rgrid
                    elif param.combine == "azimuthal":
                        rawData = (-rawData_x * adjusted_ygrid + rawData_y * adjusted_xgrid) / adjusted_rgrid
                    else:
                        raise Exception(f"Invalid combine method: {param.combine}")
                    rawData = rawData.fillna(0)

                    if ret_rawdata:
                        return rawData

                    return np.sum(rawData**2)

                self._last_lmin = fmin(sumsq, self._last_lmin, disp=False)

                rawData = sumsq(self._last_lmin, True)
        else:
            rawData = _prepData(dataset[param.varName])
        self._lengths = tuple(dataset.length)
        return param.coef * rawData, dataset.time

    @property
    def lengths(self) -> tuple[float, float, float]:
        if self._lengths is None:
            self._lengths = tuple(self.loader._get_xr_dataset("pfd", 0))
        return self._lengths

    def loadData(self, param: ParamMetadata) -> None:
        if param == self._currentParam:
            return
        self._currentParam = param
        self.datas, self.times = [list(x) for x in zip(*[self._getDataAndTime(param, idx) for idx in range(self.nframes)])]
        self.times = np.array(self.times)

    def setSlice(self, _slice: DataSlice) -> None:
        if _slice.slice.start is None:
            _slice.slice = slice(-self.lengths[1] / 2, _slice.slice.stop)
        if _slice.slice.stop is None:
            _slice.slice = slice(_slice.slice.start, self.lengths[1] / 2)
        self._currentSlice = _slice
        self.slicedDatas = [data.sel(y=self._currentSlice.slice, z=self._currentSlice.slice) for data in self.datas]

        # update min and max values to show on color scale
        self._vmax = self._currentParam.vmax if not self._currentParam.vmax is None else max(np.nanquantile(data.values, 1) for data in self.slicedDatas)
        self._vmin = self._currentParam.vmin if not self._currentParam.vmin is None else min(np.nanquantile(data.values, 0) for data in self.slicedDatas)
        if self._currentParam.vmax is self._currentParam.vmin is None:
            self._vmax = max(self._vmax, -self._vmin)
            self._vmin = -self._vmax

    # Methods that use the data

    def viewFrame(self, frameIdx: int, fig: mplf.Figure = None, ax: plt.Axes = None, minimal: bool = False) -> tuple[mplf.Figure, plt.Axes, mpli.AxesImage]:
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
            self._setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frameIdx])
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
            fig.colorbar(im, ax=ax)

        return fig, ax, im

    def viewMovie(self, fig: mplf.Figure, ax: plt.Axes, im: mpli.AxesImage) -> animation.FuncAnimation:
        def updateIm(frameIdx: int):
            im.set_array(self.slicedDatas[frameIdx])
            self._setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frameIdx])
            return [im]

        return animation.FuncAnimation(fig, updateIm, interval=30, frames=self.nframes, repeat=False, blit=True)

    def _getNormsOfDiffs(self) -> npt.NDArray[np.float64]:
        def norm(x: xr.DataArray) -> float:
            return xr.apply_ufunc(np.linalg.norm, x, input_core_dims=[["y", "z"]])

        return np.array([norm(data - self.slicedDatas[0]) for data in self.slicedDatas])

    def viewStability(self, fig: mplf.Figure = None, ax: plt.Axes = None) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        ax.set_xlabel("Time")
        ax.set_ylabel("2-Norm of Difference")
        ax.set_title(f"Deviation from ICs of {self._currentSlice.viewAdjective}{self._currentParam.title} ($B_0={self.loader.B}$, {self.loader.case_name})")

        ax.plot(self.times, self._getNormsOfDiffs())
        return fig, ax

    def _getMeansAtOrigin(self, sample_size: int = 2) -> npt.NDArray[np.float64]:
        orig_idx = len(self.datas[0]) // 2
        orig_slice = slice(orig_idx - sample_size // 2, orig_idx + sample_size // 2)
        return np.array([data.isel(y=orig_slice, z=orig_slice).values.mean() for data in self.datas])

    def viewMeansAtOrigin(self, fig: mplf.Figure = None, ax: plt.Axes = None) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        ax.set_xlabel("Time")
        ax.set_ylabel(f"Mean {self._currentParam.title}")
        ax.set_title(f"Mean {self._currentParam.title} Near Origin for $B_0={self.loader.B}$")

        ax.plot(self.times, self._getMeansAtOrigin())
        return fig, ax

    def getIdxPeriod(self) -> int:
        data = self._getMeansAtOrigin()
        idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
        return round(1 / idx_freq[sig.find_peaks(power, prominence=power.max() / 10)[0][0]])

    def viewPeriodogram(self, fig: mplf.Figure = None, ax: plt.Axes = None, annotate: bool = True) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        data = self._getMeansAtOrigin()
        idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
        freq = idx_freq * len(self.times) / self.times[-1]

        if annotate:
            for peak_idx in sig.find_peaks(power, prominence=power.max() / 10)[0]:
                peak_freq = freq[peak_idx]
                peak_power = power[peak_idx]
                ax.annotate(f"{peak_freq:.3f}", xy=(peak_freq, peak_power))

        ax.set_xlabel("Frequency")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Periodogram of $n_e(0,0)$ ($B_0={self.loader.B}$, {self.loader.case_name})")

        ax.plot(freq, power)
        return fig, ax

    def getLocalExtremaIndices(self, comparator=np.greater_equal) -> list[int]:
        expected_idx_period = self.getIdxPeriod()
        return list(sig.argrelextrema(self._getMeansAtOrigin(), comparator, order=expected_idx_period // 2)[0])
