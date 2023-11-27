import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.animation as animation
import matplotlib.image as mpli
import matplotlib.figure as mplf
import numpy as np
import numpy.typing as npt
import scipy.signal as sig
from scipy.optimize import fmin
from functools import cached_property

from .run_params import ParamMetadata, ne
from .backend import RunManager, load_bp, FrameManagerLinear
from .util.safe_cache_invalidation import safe_cached_property_invalidation


__all__ = ["ParamMetadata", "DataSlice", "VideoMaker"]


class DataSlice:
    def __init__(self, slice: slice, viewAdjective: str) -> None:
        self.slice = slice
        self.viewAdjective = viewAdjective


@safe_cached_property_invalidation
class VideoMaker:
    _raw_datas: list[xr.DataArray]

    def __init__(self, nframes: int, run_manager: RunManager) -> None:
        self.run_manager = run_manager
        self.params_record = run_manager.params_record
        self.frame_manager = run_manager.get_frame_manager(FrameManagerLinear, nframes, [ne])  # never used except for diagnostics
        self.nframes = nframes
        self.grid_rho = None
        self._currentParam = None
        self._last_lmin = 0, 0
        self._case_name = ("Moment" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

    def _setTitle(self, ax: plt.Axes, viewAdj: str, paramName: str, time: float) -> None:
        ax.set_title(f"{viewAdj} {paramName}, t={time:.3f} ($B_0={self.params_record.B0}$, {self._case_name})")

    def _getDataAndTime(self, param: ParamMetadata, frame: int) -> tuple[xr.DataArray, float]:
        dataset = load_bp(self.run_manager.path_run, param.prefix_bp, self.frame_manager.steps[frame])

        if self.grid_rho is None:
            self.axis_y = dataset.axis_y
            self.axis_z = dataset.axis_z
            self.grid_rho = dataset.grid_rho

        c = self._centering

        if isinstance(param.varName, list):
            if param.combine == "magnitude":
                rawData = (sum(dataset.get(var, c) ** 2 for var in param.varName)) ** 0.5
            elif param.combine == "sum":
                rawData = sum(dataset.get(var, c) for var in param.varName)
            elif param.combine == "difference":
                rawData = dataset.get(param.varName[0], c) - dataset.get(param.varName[1], c)
            else:
                rawData_x = dataset.get(param.varName[0], c)
                rawData_y = dataset.get(param.varName[1], c)

                # recenter structure
                def sumsq(p: tuple[float, float], ret_rawdata=False) -> float:
                    adjusted_axis_y = self.axis_y - p[0]
                    adjusted_axis_z = self.axis_z - p[1]
                    adjusted_grid_rho = (adjusted_axis_y**2 + adjusted_axis_z**2) ** 0.5

                    if param.combine == "radial":
                        rawData = (rawData_x * adjusted_axis_y + rawData_y * adjusted_axis_z) / adjusted_grid_rho
                    elif param.combine == "azimuthal":
                        rawData = (-rawData_x * adjusted_axis_z + rawData_y * adjusted_axis_y) / adjusted_grid_rho
                    else:
                        raise Exception(f"Invalid combine method: {param.combine}")
                    rawData = rawData.fillna(0)

                    if ret_rawdata:
                        return rawData

                    return np.sum(rawData**2)

                if param.recenter:
                    self._last_lmin = fmin(sumsq, self._last_lmin, disp=False)

                rawData = sumsq(self._last_lmin, True)
        else:
            rawData = dataset.get(param.varName, c)
        self.lengths = dataset.lengths
        return param.coef * rawData, dataset.time

    @cached_property
    def lengths(self) -> tuple[float, float, float]:
        return load_bp(self.run_manager.path_run, "pfd", 0).lengths

    def loadData(self, param: ParamMetadata) -> None:
        if param == self._currentParam:
            return
        self.frame_manager = self.run_manager.get_frame_manager(FrameManagerLinear, self.nframes, [param])
        self._currentParam = param
        self._centering = "nc" if param.prefix_bp == "pfd" else "cc"
        self._raw_datas, self.times = [list(x) for x in zip(*[self._getDataAndTime(param, frame) for frame in range(self.nframes)])]
        self.times = np.array(self.times)

    def setSlice(self, _slice: DataSlice) -> None:
        if _slice.slice.start is None:
            _slice.slice = slice(-self.lengths[1] / 2, _slice.slice.stop)
        if _slice.slice.stop is None:
            _slice.slice = slice(_slice.slice.start, self.lengths[1] / 2)
        self._currentSlice = _slice
        self.slicedDatas = [raw_data.sel(y=self._currentSlice.slice, z=self._currentSlice.slice) for raw_data in self._raw_datas]

        del self._val_bounds

    @cached_property
    def _val_bounds(self) -> tuple[float, float]:
        vmax = self._currentParam.vmax if self._currentParam.vmax is not None else max(np.nanquantile(data.values, 1) for data in self.slicedDatas)
        vmin = self._currentParam.vmin if self._currentParam.vmin is not None else min(np.nanquantile(data.values, 0) for data in self.slicedDatas)
        if self._currentParam.vmax is self._currentParam.vmin is None:
            vmax = max(vmax, -vmin)
            vmin = -vmax
        return vmin, vmax

    # Methods that use the data

    def viewFrame(self, frame: int, fig: mplf.Figure = None, ax: plt.Axes = None, minimal: bool = False) -> tuple[mplf.Figure, plt.Axes, mpli.AxesImage]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        im = ax.imshow(
            self.slicedDatas[frame],
            cmap=self._currentParam.colors,
            vmin=self._val_bounds[0],
            vmax=self._val_bounds[1],
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
            self._setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frame])
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
            fig.colorbar(im, ax=ax)

        return fig, ax, im

    def viewMovie(self, fig: mplf.Figure, ax: plt.Axes, im: mpli.AxesImage) -> animation.FuncAnimation:
        def updateIm(frame: int):
            im.set_array(self.slicedDatas[frame])
            self._setTitle(ax, self._currentSlice.viewAdjective, self._currentParam.title, self.times[frame])
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
        ax.set_title(f"Deviation from ICs of {self._currentSlice.viewAdjective}{self._currentParam.title} ($B_0={self.params_record.B0}$, {self._case_name})")

        ax.plot(self.times, self._getNormsOfDiffs())
        return fig, ax

    def _getMeansAtOrigin(self, sample_size: int = 2) -> npt.NDArray[np.float64]:
        orig_idx = len(self._raw_datas[0]) // 2
        if self._centering == "nc":
            sample_size -= (sample_size + 1) % 2
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + 1 + sample_size // 2)
        elif self._centering == "cc":
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + sample_size // 2)
        return np.array([raw_data.isel(y=orig_slice, z=orig_slice).values.mean() for raw_data in self._raw_datas])

    def viewMeansAtOrigin(self, fig: mplf.Figure = None, ax: plt.Axes = None) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        ax.set_xlabel("Time")
        ax.set_ylabel(f"Mean {self._currentParam.title}")
        ax.set_title(f"Mean {self._currentParam.title} Near Origin for $B_0={self.params_record.B0}$")

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
        ax.set_title(f"Periodogram of $n_e(0,0)$ ($B_0={self.params_record.B0}$, {self._case_name})")

        ax.plot(freq, power)
        return fig, ax

    def getLocalExtremaIndices(self, comparator=np.greater_equal) -> list[int]:
        expected_idx_period = self.getIdxPeriod()
        return list(sig.argrelextrema(self._getMeansAtOrigin(), comparator, order=expected_idx_period // 2)[0])
