import yaml
import os

_SETTINGS = ["nframes", "slice", "periodic", "output_directory"]
_FIGURE_TYPES = ["videos", "profiles", "sequences", "stabilities", "origin_means", "periodograms"]


def _find_item_setting_differences(item1: dict, item2: dict):
    diffs = []
    for setting in _SETTINGS:
        if item1[setting] != item2[setting]:
            diffs.append(setting)
    return diffs


def _get_settings_as_str(item: dict, settings: list[str] = _SETTINGS) -> str:
    return " ".join(f"{setting}={item[setting]}" for setting in settings)


def _figlist_duplicates_removed(fig_list: list[str] | list[list[str]]) -> list:
    if not fig_list:
        return fig_list

    if isinstance(fig_list[0], str):
        return list(set(fig_list))

    fig_set = {tuple(fig) for fig in fig_list}
    return [list(fig) for fig in fig_set]


def _update_figure_lists(old_item: dict, new_item: dict):
    for fig_type in _FIGURE_TYPES:
        if new_item.get(fig_type, []):
            old_item[fig_type] = _figlist_duplicates_removed(old_item.get(fig_type, []) + new_item[fig_type])


class History:
    def __init__(self, file: str) -> None:
        self.file = file
        self.items: list[dict] = []

    def log_item(self, item: dict):
        self.items.append(item)

    def save(self):
        if not os.path.isfile(self.file):
            history = {"instructions": []}
        else:
            with open(self.file, "r") as stream:
                try:
                    history = yaml.safe_load(stream)
                except yaml.YAMLError as e:
                    print(e)

        for new_item in self.items:
            path = new_item["path"]

            old_items_same_path = [old_item for old_item in history["instructions"] if old_item["path"] == path]

            for old_item in old_items_same_path:
                if not _find_item_setting_differences(old_item, new_item):
                    _update_figure_lists(old_item, new_item)
                    break
            else:
                print(f"New settings used for {path} ({len(old_items_same_path)} old settings found)")
                for old_item in old_items_same_path:
                    print(f"  Old: " + _get_settings_as_str(old_item))
                print(f"  New: " + _get_settings_as_str(new_item))

                history["instructions"].append(new_item)

        with open(self.file, "w") as stream:
            try:
                yaml.safe_dump(history, stream)
            except yaml.YAMLError as e:
                print(e)
