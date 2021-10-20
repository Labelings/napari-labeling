"""
This module is an example of a barebones writer plugin for napari

It implements the ``napari_get_writer`` and ``napari_write_image`` hook specifications.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs
"""
from typing import List, Tuple, Any, Dict

from labeling import Labeling
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_get_writer(path: str, layer_types: [str]):

    if not path.endswith(".bson"):
        return None
    if "labels" not in layer_types:
        return None
    return writer_function


def writer_function(path: str, layer_data: List[Tuple[Any, Dict, str]]):
    labeling = Labeling.Labeling()
    for img, data, layer_type in layer_data:
        if layer_type is "labels":
            labeling.add_image(img)
    labeling.save_result(path)
