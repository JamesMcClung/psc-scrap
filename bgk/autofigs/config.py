from __future__ import annotations

from typing import Any, Iterator

import yaml

from .options import FIGURE_TYPES

__all__ = ["AutofigsConfig", "AutofigsSuite"]


class AutofigsConfig:
    suites: AutofigsSuites
    instructions: AutofigsInstructions

    def __init__(self, path_config: str) -> None:
        with open(path_config, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                self.suites = AutofigsSuites(config["suites"])
                self.instructions = AutofigsInstructions(config["instructions"])
            except yaml.YAMLError as e:
                print(e)


class AutofigsSuites:
    def __init__(self, suites_raw: dict[str, dict[str, Any]]) -> None:
        self._suites = {suite_name: AutofigsSuite(suite_name, suite_raw) for suite_name, suite_raw in suites_raw.items()}

    def __getitem__(self, suite_name: str) -> AutofigsSuite:
        return self._suites[suite_name]


class AutofigsSuite:
    def __init__(self, suite_name: str, suite_raw: dict[str, Any]) -> None:
        self.name = suite_name
        self._suite = suite_raw

    @staticmethod
    def empty() -> AutofigsSuite:
        return AutofigsSuite("", {figure_type: [] for figure_type in FIGURE_TYPES})

    def __getitem__(self, value_name: str) -> Any:
        return self._suite[value_name]


class AutofigsInstructions:
    def __init__(self, instructions_raw: list[dict[str, Any]]) -> None:
        self._instructions = [AutofigsInstructionItem(instruction_item_raw) for instruction_item_raw in instructions_raw]

    def __iter__(self) -> Iterator[AutofigsInstructionItem]:
        return iter(self._instructions)


class AutofigsInstructionItem:
    def __init__(self, instruction_item_raw: dict[str, Any]) -> None:
        self._instruction_item = instruction_item_raw

    def __getitem__(self, value_name: str) -> Any:
        return self._instruction_item[value_name]
