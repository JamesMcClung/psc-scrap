import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.figure as mplf
import numpy as np
import scipy.signal as sig
from scipy.optimize import fmin
from functools import cached_property

from .run_params import ParamMetadata, ne
from .bounds import Bounds3D
from .backend import RunManager, load_bp, FrameManagerLinear, FrameManager
from .util.safe_cache_invalidation import safe_cached_property_invalidation
from .util.stream import Stream


__all__ = ["VideoMaker"]


@safe_cached_property_invalidation
class VideoMaker:
    _raw_datas: xr.DataArray

    def __init__(self, nframes: int, run_manager: RunManager, initial_param: ParamMetadata = ne) -> None:
        self.run_manager = run_manager
        self.params_record = run_manager.params_record
        self.nframes = nframes
        self.set_param(initial_param)
        self._last_lmin = 0, 0
        self._case_name = ("Moment" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

    def _get_data(self, frame: int) -> xr.DataArray:
        param = self.param
        dataset = load_bp(self.run_manager.path_run, param.prefix_bp, self.frame_manager.steps[frame])
        c = self._centering

        if isinstance(param.varName, list):
            if param.combine == "magnitude":
                raw_data = (sum(dataset.get(var, c) ** 2 for var in param.varName)) ** 0.5
            elif param.combine == "sum":
                raw_data = sum(dataset.get(var, c) for var in param.varName)
            elif param.combine == "difference":
                raw_data = dataset.get(param.varName[0], c) - dataset.get(param.varName[1], c)
            else:
                raw_data_y = dataset.get(param.varName[0], c)
                raw_data_z = dataset.get(param.varName[1], c)

                # recenter structure
                def sumsq(p: tuple[float, float], ret_rawdata=False) -> float:
                    adjusted_axis_y = dataset.axis_y - p[0]
                    adjusted_axis_z = dataset.axis_z - p[1]
                    adjusted_grid_rho = (adjusted_axis_y**2 + adjusted_axis_z**2) ** 0.5

                    if param.combine == "radial":
                        raw_data = (raw_data_y * adjusted_axis_y + raw_data_z * adjusted_axis_z) / adjusted_grid_rho
                    elif param.combine == "azimuthal":
                        raw_data = (-raw_data_y * adjusted_axis_z + raw_data_z * adjusted_axis_y) / adjusted_grid_rho
                    else:
                        raise Exception(f"Invalid combine method: {param.combine}")
                    raw_data = raw_data.fillna(0)

                    if ret_rawdata:
                        return raw_data

                    return np.sum(raw_data**2)

                if param.recenter:
                    self._last_lmin = fmin(sumsq, self._last_lmin, disp=False)

                raw_data = sumsq(self._last_lmin, True)
        else:
            raw_data = dataset.get(param.varName, c)

        raw_data = raw_data.expand_dims({"t": [dataset.time]})
        self.lengths = dataset.lengths
        return param.coef * raw_data

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
        if hasattr(self, "param") and param == self.param:
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
        raw_datas = Stream(range(self.nframes)).map(self._get_data).collect(lambda raw_datas: xr.concat(raw_datas, "t"))
        raw_datas.coords["rho"] = (raw_datas.coords["y"] ** 2 + raw_datas.coords["z"] ** 2) ** 0.5
        return raw_datas

    @cached_property
    def frame_manager(self) -> FrameManager:
        return self.run_manager.get_frame_manager(FrameManagerLinear, self.nframes, [self.param])

    @cached_property
    def _val_bounds(self) -> tuple[float, float]:
        vmax = self.param.vmax if self.param.vmax is not None else self.datas.quantile(1, ["y", "z"]).max("t")
        vmin = self.param.vmin if self.param.vmin is not None else self.datas.quantile(0, ["y", "z"]).min("t")
        if self.param.vmax is self.param.vmin is None:
            vmax = max(vmax, -vmin)
            vmin = -vmax
        return vmin, vmax

    @cached_property
    def datas(self) -> xr.DataArray:
        return self._raw_datas.sel(y=self.view_bounds.yslice, z=self.view_bounds.zslice)

    # Methods that use the data

    def get_norms_of_diffs(self) -> xr.DataArray:
        diffs = self.datas - self.datas.isel(t=0)
        return xr.apply_ufunc(np.linalg.norm, diffs, input_core_dims=[["y", "z"]], vectorize=True)

    def get_means_at_origin(self, sample_size: int = 2) -> xr.DataArray:
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

        ax.plot(self.axis_t, self.get_means_at_origin())
        return fig, ax

    def getIdxPeriod(self) -> int:
        data = self.get_means_at_origin()
        idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
        return round(1 / idx_freq[sig.find_peaks(power, prominence=power.max() / 10)[0][0]])

    def getLocalExtremaIndices(self, comparator=np.greater_equal) -> list[int]:
        expected_idx_period = self.getIdxPeriod()
        return list(sig.argrelextrema(self.get_means_at_origin().values, comparator, order=expected_idx_period // 2)[0])
