import xarray as xr
import numpy as np
import scipy.signal as sig
from scipy.optimize import fmin
from functools import cached_property

from .field_variables import FieldVariable, ne
from .bounds import Bounds3D
from .backend import load_bp
from .run_manager import RunManager, FrameManagerLinear, FrameManager
from .util.safe_cache_invalidation import safe_cached_property_invalidation
from .util.stream import Stream


__all__ = ["VideoMaker"]


@safe_cached_property_invalidation
class VideoMaker:
    def __init__(self, nframes: int, run_manager: RunManager, initial_variable: FieldVariable = ne) -> None:
        self.run_manager = run_manager
        self.params_record = run_manager.params_record
        self.nframes = nframes
        self.set_variable(initial_variable)
        self._last_lmin = 0, 0
        self.case_name = ("Moment" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

    def _get_data(self, frame: int) -> xr.DataArray:
        var = self.param
        dataset = load_bp(self.run_manager.path_run, var.prefix_bp, self.frame_manager.steps[frame])
        c = self._centering

        if isinstance(var.varName, list):
            if var.combine == "magnitude":
                raw_data = (sum(dataset.get(var, c) ** 2 for var in var.varName)) ** 0.5
            elif var.combine == "sum":
                raw_data = sum(dataset.get(var, c) for var in var.varName)
            elif var.combine == "difference":
                raw_data = dataset.get(var.varName[0], c) - dataset.get(var.varName[1], c)
            else:
                raw_data_y = dataset.get(var.varName[0], c)
                raw_data_z = dataset.get(var.varName[1], c)

                # recenter structure
                def sumsq(p: tuple[float, float], ret_rawdata=False) -> float:
                    adjusted_axis_y = dataset.axis_y - p[0]
                    adjusted_axis_z = dataset.axis_z - p[1]
                    adjusted_grid_rho = (adjusted_axis_y**2 + adjusted_axis_z**2) ** 0.5

                    if var.combine == "radial":
                        raw_data = (raw_data_y * adjusted_axis_y + raw_data_z * adjusted_axis_z) / adjusted_grid_rho
                    elif var.combine == "azimuthal":
                        raw_data = (-raw_data_y * adjusted_axis_z + raw_data_z * adjusted_axis_y) / adjusted_grid_rho
                    else:
                        raise Exception(f"Invalid combine method: {var.combine}")
                    raw_data = raw_data.fillna(0)

                    if ret_rawdata:
                        return raw_data

                    return np.sum(raw_data**2)

                if var.recenter:
                    self._last_lmin = fmin(sumsq, self._last_lmin, disp=False)

                raw_data = sumsq(self._last_lmin, True)
        else:
            raw_data = dataset.get(var.varName, c)

        raw_data = raw_data.expand_dims({"t": [dataset.time]})
        self.lengths = dataset.lengths
        return var.coef * raw_data

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

    def set_variable(self, variable: FieldVariable) -> None:
        if hasattr(self, "param") and variable == self.param:
            return
        self.param = variable
        self._centering = "nc" if variable.prefix_bp == "pfd" else "cc"
        del self.frame_manager
        del self.datas
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
        return xr.apply_ufunc(np.linalg.norm, diffs, input_core_dims=[["x", "y", "z"]], vectorize=True)

    def get_means_at_origin(self, sample_size: int = 2) -> xr.DataArray:
        orig_idx = len(self._raw_datas.y) // 2
        if self._centering == "nc":
            sample_size -= (sample_size + 1) % 2
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + 1 + sample_size // 2)
        elif self._centering == "cc":
            orig_slice = slice(orig_idx - sample_size // 2, orig_idx + sample_size // 2)
        return self._raw_datas.isel(y=orig_slice, z=orig_slice).mean(["x", "y", "z"])

    def get_idx_period(self) -> int:
        data = self.get_means_at_origin()
        idx_freq, power = sig.periodogram(data, nfft=len(data) * 4)
        return round(1 / idx_freq[sig.find_peaks(power, prominence=power.max() / 10)[0][0]])

    def get_local_extrema_idxs(self, comparator=np.greater_equal) -> list[int]:
        expected_idx_period = self.get_idx_period()
        return list(sig.argrelextrema(self.get_means_at_origin().values, comparator, order=expected_idx_period // 2)[0])
