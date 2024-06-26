from __future__ import annotations

from collections.abc import Container
from copy import deepcopy
from typing import Any, Iterator, TypeVar

import yaml

from .options import TRIVIAL_FIGURE_TYPES, FIGURE_TYPES, SETTINGS_OPTIONAL

__all__ = ["AutofigsConfig", "AutofigsSuite"]

T = TypeVar("T")


class AutofigsConfig:
    suites: AutofigsSuites
    instructions: AutofigsInstructions

    def __init__(self, suites: AutofigsSuites, instructions: AutofigsInstructions) -> None:
        self.suites = suites
        self.instructions = instructions
        self.instructions._apply_suites(self.suites)

    @staticmethod
    def from_dict(config: dict[str, Any]) -> AutofigsConfig:
        return AutofigsConfig(AutofigsSuites(config.get("suites", {})), AutofigsInstructions(config.get("instructions", [])))

    @staticmethod
    def from_file(path_config: str) -> AutofigsConfig:
        with open(path_config, "r") as stream:
            try:
                return AutofigsConfig.from_dict(yaml.safe_load(stream))
            except yaml.YAMLError as e:
                print(e)

    def save(self, path: str):
        with open(path, "w") as file:
            try:
                yaml.safe_dump({"instructions": [item._instruction_item for item in self.instructions]}, file)
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
        return AutofigsSuite("", {figure_type: [] for figure_type in FIGURE_TYPES} | SETTINGS_OPTIONAL)

    def __getitem__(self, value_name: str) -> Any:
        return self._suite[value_name]


class AutofigsInstructions:
    def __init__(self, instructions_raw: list[dict[str, Any]]) -> None:
        self._instructions = [AutofigsInstructionItem(instruction_item_raw) for instruction_item_raw in instructions_raw]

    def __iter__(self) -> Iterator[AutofigsInstructionItem]:
        return iter(self._instructions)

    def _apply_suites(self, suites: AutofigsSuites):
        for instruction_item in self._instructions:
            instruction_item._maybe_apply_suite(suites)

    def remove_figures_except(self, figure_type: str):
        for instruction_item in self:
            instruction_item.remove_keys(set(FIGURE_TYPES) - {figure_type})

    def append(self, item: AutofigsInstructionItem):
        self._instructions.append(item)


class AutofigsInstructionItem:
    def __init__(self, instruction_item_raw: dict[str, Any]) -> None:
        self._instruction_item = instruction_item_raw

    def __getitem__(self, value_name: str) -> Any:
        return self._instruction_item[value_name]

    def __setitem__(self, value_name: str, value: Any) -> None:
        self._instruction_item[value_name] = value

    def __contains__(self, value_name: str) -> bool:
        return value_name in self._instruction_item

    def get(self, key: str, default: T) -> T:
        return self._instruction_item.get(key, default)

    @property
    def path(self) -> str:
        return self["path"]

    @property
    def output_directory(self) -> str:
        return self["output_directory"]

    @property
    def prefix(self) -> str:
        return self["prefix"]

    def _maybe_apply_suite(self, suites: AutofigsSuites):
        filled_instruction_item = AutofigsSuite.empty()._suite
        if "suite" in self._instruction_item:
            filled_instruction_item.update(suites[self._instruction_item["suite"]]._suite)
        filled_instruction_item.update(self._instruction_item)
        self._instruction_item = filled_instruction_item

    def remove_keys(self, keys: Container[str], *, in_place: bool = True) -> AutofigsInstructionItem:
        if not in_place:
            return deepcopy(self).remove_keys(keys)

        for key in keys:
            self._instruction_item.pop(key, None)
        return self

    def get_variable_names_in_order(self) -> list[str]:
        empty_str_list: list[str] = []  # for linting
        trivial_field_variables = {var for figure_type in TRIVIAL_FIGURE_TYPES for var in self.get(figure_type, empty_str_list)}
        video_field_variables = {var for var in self.get("videos", empty_str_list) if not var.startswith("prt:")}
        variable_names = trivial_field_variables | video_field_variables
        if "ne" in variable_names:  # always put ne first
            variable_names.remove("ne")
            return ["ne"] + sorted(list(variable_names))
        return sorted(list(variable_names))
