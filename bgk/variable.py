from .typing import PrefixBp, PrefixH5


__all__ = ["Variable"]


class Variable:
    def __init__(
        self,
        name: str,
        latex: str,
        prefix: PrefixBp | PrefixH5,
        skip_first_step: bool,
        cmap_name: str,
    ) -> None:
        self.name = name
        self.latex = latex
        self.prefix = prefix
        self.skip_first_step = skip_first_step
        self.cmap_name = cmap_name
