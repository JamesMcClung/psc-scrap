import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.animation as animation
import matplotlib.image as mpli
import matplotlib.figure as mplf
import pandas as pd
import numpy as np
import scipy.signal as sig
from scipy.optimize import fmin
from functools import cached_property

from .run_params import ParamMetadata, ne
from .bounds import Bounds3D
from .backend import RunManager, load_bp, FrameManagerLinear, FrameManager
from .util.safe_cache_invalidation import safe_cached_property_invalidation


__all__ = ["VideoMaker"]


@safe_cached_property_invalidation
class VideoMaker:
    _raw_datas: xr.DataArray

    def __init__(self, nframes: int, run_manager: RunManager, initial_param: ParamMetadata = ne) -> None:
        self.run_manager = run_manager
        self.params_record = run_manager.params_record
        self.nframes = nframes
        self.param = initial_param
        self._last_lmin = 0, 0
        self._case_name = ("Moment" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

    def _setTitle(self, ax: plt.Axes, viewAdj: str, paramName: str, time: float) -> None:
        ax.set_title(f"{viewAdj} {paramName}, t={time:.3f} ($B_0={self.params_record.B0}$, {self._case_name})")

    def _getDataAndTime(self, param: ParamMetadata, frame: int) -> tuple[xr.DataArray, float]:
        dataset = load_bp(self.run_manager.path_run, param.prefix_bp, self.frame_manager.steps[frame])

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
                    adjusted_axis_y = dataset.axis_y - p[0]
                    adjusted_axis_z = dataset.axis_z - p[1]
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

    @property
    def axis_y(self) -> xr.DataArray:
        return self.datas.y

    @property
    def axis_z(self) -> xr.DataArray:
        return self.datas.z

    @property
    def axis_t(self) -> xr.DataArray:
        return self.datas.t

    @property
    def grid_rho(self) -> xr.DataArray:
        return self.datas.rho

    def set_param(self, param: ParamMetadata) -> None:
        if param == self.param and hasattr(self, "_raw_datas"):
            return
        self.param = param
        self._centering = "nc" if param.prefix_bp == "pfd" else "cc"
        del self.frame_manager
        del self._raw_datas

    def set_view_bounds(self, bounds: Bounds3D):
        self.view_bounds = bounds.concretize(self.lengths)
        del self._val_bounds
        del self.datas

    @cached_property
    def _raw_datas(self) -> xr.DataArray:
        raw_datas, times = [list(x) for x in zip(*[self._getDataAndTime(self.param, frame) for frame in range(self.nframes)])]
        raw_datas: xr.DataArray = xr.concat(raw_datas, pd.Index(times, name="t"))
        raw_datas.coords["rho"] = (raw_datas.coords["y"] ** 2 + raw_datas.coords["z"] ** 2) ** 0.5
        return raw_datas

    @cached_property
    def frame_manager(self) -> FrameManager:
        return self.run_manager.get_frame_manager(FrameManagerLinear, self.nframes, [self.param])

    @cached_property
    def _val_bounds(self) -> tuple[float, float]:
        vmax = self.param.vmax if self.param.vmax is not None else max(np.nanquantile(data.values, 1) for data in self.datas)
        vmin = self.param.vmin if self.param.vmin is not None else min(np.nanquantile(data.values, 0) for data in self.datas)
        if self.param.vmax is self.param.vmin is None:
            vmax = max(vmax, -vmin)
            vmin = -vmax
        return vmin, vmax

    @cached_property
    def datas(self) -> xr.DataArray:
        return self._raw_datas.sel(y=self.view_bounds.yslice, z=self.view_bounds.zslice)

    # Methods that use the data

    def viewFrame(self, frame: int, fig: mplf.Figure = None, ax: plt.Axes = None, minimal: bool = False) -> tuple[mplf.Figure, plt.Axes, mpli.AxesImage]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        im = ax.imshow(
            self.datas[frame],
            cmap=self.param.colors,
            vmin=self._val_bounds[0],
            vmax=self._val_bounds[1],
            origin="lower",
            extent=self.view_bounds.get_extent(),
        )

        if not minimal:
            ax.set_xlabel("y")
            ax.set_ylabel("z")
            self._setTitle(ax, self.view_bounds.adjective, self.param.title, self.axis_t[frame])
            plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment="right")
            fig.colorbar(im, ax=ax)

        return fig, ax, im

    def viewMovie(self, fig: mplf.Figure, ax: plt.Axes, im: mpli.AxesImage) -> animation.FuncAnimation:
        def updateIm(frame: int):
            im.set_array(self.datas[frame])
            self._setTitle(ax, self.view_bounds.adjective, self.param.title, self.axis_t[frame])
            return [im]

        return animation.FuncAnimation(fig, updateIm, interval=30, frames=self.nframes, repeat=False, blit=True)

    def _getNormsOfDiffs(self) -> xr.DataArray:
        diffs = self.datas - self.datas.isel(t=0)
        return xr.apply_ufunc(np.linalg.norm, diffs, input_core_dims=[["y", "z"]], vectorize=True)

    def viewStability(self, fig: mplf.Figure = None, ax: plt.Axes = None) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        ax.set_xlabel("Time")
        ax.set_ylabel("2-Norm of Difference")
        ax.set_title(f"Deviation from ICs of {self.view_bounds.adjective}{self.param.title} ($B_0={self.params_record.B0}$, {self._case_name})")

        ax.plot(self.axis_t, self._getNormsOfDiffs())
        return fig, ax

    def _getMeansAtOrigin(self, sample_size: int = 2) -> xr.DataArray:
        orig_idx = len(self._raw_datas.y) // 2
        if self._centering == "nc":
            sample_size -= (sample_size + 1) % 2
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + 1 + sample_size // 2)
        elif self._centering == "cc":
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + sample_size // 2)
        return self._raw_datas.isel(y=orig_slice, z=orig_slice).mean(["y", "z"])

    def viewMeansAtOrigin(self, fig: mplf.Figure = None, ax: plt.Axes = None) -> tuple[mplf.Figure, plt.Axes]:
        if not (fig or ax):
            fig, ax = plt.subplots()

        ax.set_xlabel("Time")
        ax.set_ylabel(f"Mean {self.param.title}")
        ax.set_title(f"Mean {self.param.title} Near Origin for $B_0={self.params_record.B0}$")

        ax.plot(self.axis_t, self._getMeansAtOrigin())
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
        freq = idx_freq * len(self.axis_t) / self.axis_t.values[-1]

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
        return list(sig.argrelextrema(self._getMeansAtOrigin().values, comparator, order=expected_idx_period // 2)[0])
