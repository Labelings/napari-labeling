
from __future__ import annotations
from typing import TYPE_CHECKING, List, Any, Sequence, Tuple, Union

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def writer_function(path: str, data: List[FullLayerData], meta: dict):
    labeling = meta["metadata"]["labeling_obj"]
    labeling.save_result(path, True)
    return [path]
