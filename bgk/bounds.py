from __future__ import annotations
from typing import Iterator
from dataclasses import dataclass
from abc import ABC, abstractmethod

__all__ = ["Bounds3D", "Bounds1DPhysical", "Bounds1DRelative"]


@dataclass
class Bounds1D(ABC):
    lower: float
    upper: float

    @abstractmethod
    def concretize(self, domain_length: float, domain_center: float) -> Bounds1DConcrete:
        pass

    def __str__(self) -> str:
        return f"[{self.lower}, {self.upper}]"

    def __iter__(self) -> Iterator[float]:
        yield self.lower
        yield self.upper


class Bounds1DPhysical(Bounds1D):
    """Specifies an axis' lower and upper bounds in physical units."""

    def concretize(self, domain_length: float, domain_center: float) -> Bounds1DConcrete:
        is_whole = self._validate_and_get_is_whole(domain_length, domain_center)
        return Bounds1DConcrete(self.lower, self.upper, is_whole)

    def _validate_and_get_is_whole(self, domain_length: float, domain_center: float) -> bool:
        domain_lower = domain_center - domain_length / 2
        domain_upper = domain_center + domain_length / 2
        if not domain_lower <= self.lower <= self.upper <= domain_upper:
            raise Exception(f'physical bound must be nonempty subinterval of domain "[{domain_lower}, {domain_upper}]"; got "{self}"')
        return domain_lower == self.lower and domain_upper == self.upper


class Bounds1DRelative(Bounds1D):
    """Specifies an axis' lower and upper bounds relative to the full domain, such that [-1, 1] corresponds to the full axis domain."""

    def concretize(self, domain_length: float, domain_center: float) -> Bounds1DConcrete:
        self._validate()
        physical_lower = domain_center + self.lower * domain_length / 2
        physical_upper = domain_center + self.upper * domain_length / 2
        is_whole = self.lower == -1 and self.upper == 1
        return Bounds1DConcrete(physical_lower, physical_upper, is_whole)

    def _validate(self):
        if not -1 <= self.lower <= self.upper <= 1:
            raise Exception(f'relative bound must be nonempty subinterval of [-1, 1]; got "{self}"')


class Bounds1DConcrete(Bounds1D):
    def __init__(self, lower: float, upper: float, is_whole: bool) -> None:
        super().__init__(lower, upper)
        self._is_whole = is_whole

    def concretize(self, domain_length: float, domain_center: float) -> Bounds1DConcrete:
        raise Exception("already concretized")


def _guess_adjective(bounds: tuple[Bounds1DConcrete, Bounds1DConcrete, Bounds1DConcrete]) -> str:
    if bounds[0]._is_whole and bounds[1]._is_whole and bounds[2]._is_whole:
        return ""
    return "Central "


class Bounds3D:
    def __init__(self, bounds: tuple[Bounds1D, Bounds1D, Bounds1D], adjective: str | None = None) -> None:
        self.adjective = adjective
        self.bounds = bounds

    def concretize(self, domain_lengths: tuple[float, float, float], domain_center: tuple[float, float, float] = (0, 0, 0)) -> Bounds3DConcrete:
        bounds_concrete = tuple(bnd.concretize(len, cen) for bnd, len, cen in zip(self.bounds, domain_lengths, domain_center))
        adjective = self.adjective if self.adjective is not None else _guess_adjective(bounds_concrete)
        return Bounds3DConcrete(bounds_concrete, adjective)

    @classmethod
    def whole(cls) -> Bounds3D:
        return Bounds3D((Bounds1DRelative(-1, 1),) * 3)

    @classmethod
    def center_yz(cls, enclosed_radius: float) -> Bounds3D:
        yz_bounds = Bounds1DPhysical(-enclosed_radius, enclosed_radius)
        return Bounds3D((Bounds1DRelative(-1, 1), yz_bounds, yz_bounds))


class Bounds3DConcrete(Bounds3D):
    def __init__(self, bounds: tuple[Bounds1DConcrete, Bounds1DConcrete, Bounds1DConcrete], adjective: str) -> None:
        super().__init__(bounds, adjective)

    def concretize(self, domain_lengths: tuple[float, float, float], domain_center: tuple[float, float, float] = (0, 0, 0)) -> Bounds3DConcrete:
        raise Exception("already concretized")

    @property
    def xslice(self) -> slice:
        return slice(*self.bounds[0])

    @property
    def yslice(self) -> slice:
        return slice(*self.bounds[1])

    @property
    def zslice(self) -> slice:
        return slice(*self.bounds[2])

    def get_extent(self, horizontal_idx: int = 1, vertical_index: int = 2) -> tuple[float, float, float, float]:
        return (*self.bounds[horizontal_idx], *self.bounds[vertical_index])
