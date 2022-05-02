"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/plugins/stable/npe2_manifest_specification.html

Replace code below according to your needs.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Any, Sequence, Tuple, Union
from labeling import Labeling

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def writer_function(path: str, data: List[FullLayerData], meta: dict):
    labeling = data[0][1]["metadata"]["labeling_obj"]
    labeling.save_result(path, True)
    return [path]
