from __future__ import annotations

__all__ = ["Stream"]

from typing import TypeVar, Iterable, Generic, Callable
from functools import reduce


T = TypeVar("T")
U = TypeVar("U")


class Stream(Generic[T]):
    """A lightweight wrapper around an iterator to provide a much better interface for stream operations such as `map` and `filter`."""

    def __init__(self, iter: Iterable[T]) -> None:
        self._iter = iter

    def __iter__(self) -> Stream[T]:
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def map(self, func: Callable[[T], U]) -> Stream[U]:
        return Stream(map(func, self._iter))

    def filter(self, func: Callable[[T], bool]) -> Stream[T]:
        return Stream(filter(func, self._iter))

    def collect(self, collector: Callable[[Iterable[T]], U]) -> U:
        return collector(self._iter)

    def fold(self, first: U, func: Callable[[U, T], U]) -> U:
        return reduce(func, self._iter, first)

    def reduce(self, func: Callable[[T, T], T]) -> T:
        return reduce(func, self._iter, next(self._iter))

    def any(self) -> bool:
        for x in self._iter:
            if x:
                return True
        return False

    def all(self) -> bool:
        for x in self._iter:
            if not x:
                return False
        return True
