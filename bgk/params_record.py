__all__ = ["ParamsRecord"]


import os
from typing import TypeVar, Callable, Literal


T = TypeVar("T")


class ParamsRecord:
    B0: float
    length: float | None
    init_strategy: Literal["max", "exact"]
    reversed: bool

    k: float
    h0: float
    xi: float
    A_x0: float | None
    beta: float

    res: int
    nmax: int
    nicell: int

    path_input: str
    path_checkpoint: str | None

    interval_fields: int | None
    interval_moments: int | None
    interval_gauss: int | None
    interval_particles: int | None

    def __init__(self, path_run: str, params_record_name: str = "params_record.txt") -> None:
        self._raw_params: dict[str, str] = {}
        with open(os.path.join(path_run, params_record_name)) as records:
            for line in records:
                if line.strip():
                    [param_name, param_val, *_] = line.split()
                    self._raw_params[param_name] = param_val

        self.B0 = self._parse_param("H_x", float)
        self.length = max(0, self._parse_param("box_size", float, -1)) or None
        self.init_strategy = "max" if self._parse_param("maxwellian", bool, False) else "exact"
        self.reversed = self._parse_param("v_e_coef", float, 1.0) < 0

        self.k = self._parse_param("k", float, 0.1)
        self.h0 = self._parse_param("h0", float, 0.9)
        self.xi = self._parse_param("xi", float, 0.0)
        self.A_x0 = self._parse_param("A_x0", float) if self.xi else None
        self.beta = self._parse_param("beta", float, 1e-3)

        self.res = self._parse_param("n_grid", int)
        self.nmax = self._parse_param("nmax", int)
        self.nicell = self._parse_param("nicell", int, 100)

        self.path_input = self._parse_param("path_to_data", str)
        from_checkpoint = self._parse_param("read_checkpoint", bool, False)
        self.path_checkpoint = None if not from_checkpoint else self._parse_param("path_to_checkpoint", str)

        self.interval_fields = self._parse_param("fields_every", int, 200) or None
        self.interval_moments = self._parse_param("moments_every", int, 200) or None
        self.interval_gauss = self._parse_param("gauss_every", int, 200) or None
        self.interval_particles = self._parse_param("particles_every", int, 0) or None

    def _parse_param(self, param_name: str, param_type: Callable[[str], T], default_val: T = None) -> T:
        if param_name not in self._raw_params:
            if default_val is None:
                raise Exception(f"Param does not exist: '{param_name}'. Check if the name is correct or provide a default value.")
            return default_val

        param_val_str = self._raw_params[param_name]

        if param_type is bool:
            return param_val_str.lower() == "true"

        return param_type(param_val_str)
