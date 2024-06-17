__all__ = ["History"]

import os

from .config import AutofigsInstructionItem, AutofigsConfig
from .options import SETTINGS, FIGURE_TYPES, METASETTINGS


def _find_item_setting_differences(item1: dict, item2: dict) -> list[str]:
    diffs = []
    for setting in SETTINGS:
        if item1[setting] != item2[setting]:
            diffs.append(setting)
    return diffs


def _get_settings_as_str(item: dict, settings: list[str] = SETTINGS) -> str:
    return " ".join(f"{setting}={item[setting]}" for setting in settings)


def _figlist_duplicates_removed(fig_list: list[str] | list[list[str]]) -> list:
    if not fig_list:
        return fig_list

    if isinstance(fig_list[0], str):
        return list(set(fig_list))

    fig_set = {tuple(fig) for fig in fig_list}
    return [list(fig) for fig in fig_set]


def _update_figure_lists(old_item: dict, new_item: dict):
    for fig_type in FIGURE_TYPES:
        if new_item.get(fig_type, []):
            old_item[fig_type] = _figlist_duplicates_removed(old_item.get(fig_type, []) + new_item[fig_type])


class History:
    def __init__(self, file: str) -> None:
        self.file = file
        self.history = AutofigsConfig.from_file(self.file) if os.path.isfile(self.file) else AutofigsConfig.from_dict({"instructions": []})

    def log_item(self, new_item: AutofigsInstructionItem, warn: bool = False):
        new_item = new_item.remove_keys(METASETTINGS, in_place=False)
        path = new_item.path

        old_items_same_path = [old_item for old_item in self.history.instructions if old_item.path == path]

        for old_item in old_items_same_path:
            if not _find_item_setting_differences(old_item, new_item._instruction_item):
                _update_figure_lists(old_item, new_item._instruction_item)
                break
        else:
            print(f"New settings used for {path} ({len(old_items_same_path)} old settings found)")
            for old_item in old_items_same_path:
                print(f"  Old: " + _get_settings_as_str(old_item))
            print(f"  New: " + _get_settings_as_str(new_item._instruction_item))

            if warn and new_item._instruction_item["output_directory"] in {old_item["output_directory"] for old_item in old_items_same_path}:
                answer = input("Generating this figure will override an existing figure made using different settings. Continue? Y/n ")
                while answer.lower() not in {"", "y", "yes", "n", "no"}:
                    answer = input('Invalid response. Answer "yes" (default) or "no": ')
                if answer.lower() in {"n", "no"}:
                    exit(0)

            self.history.instructions.append(new_item._instruction_item)

    def save(self):
        self.history.save(self.file)
