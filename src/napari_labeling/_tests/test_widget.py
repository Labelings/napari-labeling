import napari

from src.napari_labeling import LabelingWidget
import numpy as np
import pytest


# this is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "napari-labeling"
# the name of your widget(s)
MY_WIDGET_NAMES = ["Labeling QWidget"]


#@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_something_with_viewer(make_napari_viewer, napari_plugin_manager):
    napari_plugin_manager.register(LabelingWidget, name=MY_PLUGIN_NAME)
    viewer = make_napari_viewer()
    num_dw = len(viewer.window._dock_widgets)
    viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1