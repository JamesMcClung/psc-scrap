import xarray as xr
import numpy as np
import scipy.signal as sig
from scipy.optimize import fmin
from functools import cached_property

from .field_variables import FieldVariable, ne
from .bounds import Bounds3D
from .backend import load_bp
from .run_manager import RunManager, FrameManagerLinear, FrameManager
from .params_record import ParamsRecord
from .util.safe_cache_invalidation import safe_cached_property_invalidation
from .util.stream import Stream


__all__ = ["FieldData"]


@safe_cached_property_invalidation
class FieldData:
    def __init__(self, nframes: int, run_manager: RunManager, initial_variable: FieldVariable = ne) -> None:
        self.run_manager = run_manager
        self.nframes = nframes
        self.set_variable(initial_variable)
        self.case_name = ("Moment" if self.params_record.init_strategy == "max" else "Exact") + (", Reversed" if self.params_record.reversed else "")

    @property
    def params_record(self) -> ParamsRecord:
        return self.run_manager.params_record

    def _get_data(self, frame: int) -> xr.DataArray:
        var = self.variable
        dataset = load_bp(self.run_manager.path_run, var.prefix, self.frame_manager.steps[frame])
        c = self._centering

        if not var.shift_hole_center:
            raw_data = var.data_mapper([dataset.get(var_name, c) for var_name in var.bp_variable_names])
        else:
            raw_raw_datas = [dataset.get(var_name, c) for var_name in var.bp_variable_names]

            def sumsq(p: tuple[float, float], ret_rawdata=False) -> float:
                raw_data = var.data_mapper(raw_raw_datas, p)

                if ret_rawdata:
                    return raw_data

                return np.sum(raw_data**2)

            self._last_lmin = fmin(sumsq, self._last_lmin, disp=False)

            raw_data = sumsq(self._last_lmin, True)

        raw_data = raw_data.expand_dims({"t": [dataset.time]})
        self.lengths = dataset.lengths
        return raw_data

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
        if hasattr(self, "variable") and variable == self.variable:
            return
        self.variable = variable
        self._centering = "nc" if variable.prefix == "pfd" else "cc"
        self._last_lmin = 0, 0
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
        return self.run_manager.get_frame_manager(FrameManagerLinear, self.nframes, [self.variable])

    @cached_property
    def _val_bounds(self) -> tuple[float, float]:
        vmax = self.variable.val_bounds[1] if self.variable.val_bounds[1] is not None else self.datas.quantile(1, ["y", "z"]).max("t")
        vmin = self.variable.val_bounds[0] if self.variable.val_bounds[0] is not None else self.datas.quantile(0, ["y", "z"]).min("t")
        if self.variable.val_bounds[1] is self.variable.val_bounds[0] is None:
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
