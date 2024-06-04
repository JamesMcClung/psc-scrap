from __future__ import annotations

from typing import Any, Iterator

import yaml

from .options import TRIVIAL_FIGURE_TYPES, FIGURE_TYPES

__all__ = ["AutofigsConfig", "AutofigsSuite"]


class AutofigsConfig:
    suites: AutofigsSuites
    instructions: AutofigsInstructions

    def __init__(self, path_config: str) -> None:
        with open(path_config, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        self.suites = AutofigsSuites(config["suites"])
        self.instructions = AutofigsInstructions(config["instructions"])

        self.instructions._apply_suites(self.suites)


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

    def _apply_suites(self, suites: AutofigsSuites):
        for instruction_item in self._instructions:
            instruction_item._maybe_apply_suite(suites)

    def remove_figures_except(self, figure_type: str):
        for instruction_item in self:
            instruction_item._remove_figures_except(figure_type)


class AutofigsInstructionItem:
    def __init__(self, instruction_item_raw: dict[str, Any]) -> None:
        self._instruction_item = instruction_item_raw

    def __getitem__(self, value_name: str) -> Any:
        return self._instruction_item[value_name]

    def _maybe_apply_suite(self, suites: AutofigsSuites):
        filled_instruction_item = AutofigsSuite.empty()._suite
        if "suite" in self._instruction_item:
            filled_instruction_item.update(suites[self._instruction_item["suite"]]._suite)
        filled_instruction_item.update(self._instruction_item)
        self._instruction_item = filled_instruction_item

    def _remove_figures_except(self, figure_type: str):
        for maybe_figure_type in self._instruction_item:
            if maybe_figure_type in FIGURE_TYPES and maybe_figure_type != figure_type:
                self._instruction_item[maybe_figure_type] = []

    def get_variable_names_in_order(self) -> list[str]:
        trivial_field_variables = {var for figure_name in TRIVIAL_FIGURE_TYPES for var in self[figure_name]}
        video_field_variables = {var for var in self["videos"] if not var.startswith("prt:")}
        variable_names = trivial_field_variables | video_field_variables
        if "ne" in variable_names:  # always put ne first
            variable_names.remove("ne")
            return ["ne"] + sorted(list(variable_names))
        return sorted(list(variable_names))
