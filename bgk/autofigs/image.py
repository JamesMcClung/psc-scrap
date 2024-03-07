from ..field_data import FieldData

__all__ = ["ImageParams"]


class ImageParams:
    duration_in_title: str
    time_cutoff_idx: int
    fields: FieldData
