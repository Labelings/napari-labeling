import napari
import numpy as np
from magicgui import magicgui
from labeling import Labeling


@magicgui(auto_call=True,
          img_layer={'label': 'Selected label layer'},
          enable_highlighting={'label': 'Enable Highlighting'},
          fragment_highlighting={'label': 'Toggle Highlighting', 'widget_type': 'RadioButtons',
                                 "orientation": "horizontal",
                                 "choices": [("Fragment", False), ("Segment", True)]},
          selection={'label': 'Enable Selection', 'widget_type': 'CheckBox', 'enabled': False},
          clear_selection_func={'widget_type': 'PushButton', 'label': 'Clear Selection', 'visible': True}
          )
def edit_widget(img_layer: "napari.layers.Labels", enable_highlighting: bool = False,
                 fragment_highlighting: bool = False, selection: bool = False,
                 clear_selection_func=True):
    pass


@edit_widget.clear_selection_func.clicked.connect
def clear_selection():
    viewer = napari.current_viewer()
    if "selection" in viewer.layers:
        print("delete all")
        selection_layer = viewer.layers["selection"]
        selection_layer.data = np.zeros(selection_layer.data.shape, np.uint8)


@edit_widget.enable_highlighting.changed.connect
def toggle_highlighting(state: bool):
    viewer = napari.current_viewer()
    print(state)
    if state:
        active_layer = edit_widget.img_layer.value
        active_layer.mouse_move_callbacks.append(highlight)
        active_layer.mouse_drag_callbacks.append(add_remove_segments)
        viewer.add_labels(data=np.zeros(active_layer.level_shapes[0], dtype=np.int8),
                          name="highlight", seed=1.0)
        viewer.layers.selection.select_only(active_layer)
        edit_widget.selection.enabled = True
    else:
        active_layer = edit_widget.img_layer.value
        active_layer.mouse_move_callbacks.remove(highlight)
        active_layer.mouse_drag_callbacks.remove(add_remove_segments)
        edit_widget.selection.enabled = False


def highlight(layer, event):
    viewer = napari.current_viewer()
    cords = np.round(layer.world_to_data(viewer.cursor.position)).astype(int)
    val = layer.get_value(cords)
    if val == 0 or val is None:
        return
    label_list = layer.metadata["labeling"]["labelSets"][str(val)]
    if len(label_list) == 0:
        highlight_layer = viewer.layers["highlight"]
        highlight_layer.data = np.zeros(layer.data.shape, dtype=np.uint8)
        return
    if not edit_widget.fragment_highlighting.value:
        marking = [int(x) for x, y in layer.metadata["labeling"]["labelSets"].items() if
                   any((True for a in label_list if a in y))]
        if marking is not None and len(marking) > 0:
            highlight_layer = viewer.layers["highlight"]
            highlight_layer.data = np.asarray(np.isin(layer.data, marking), dtype=np.uint8) * layer.data
    else:
        data = np.zeros(layer.data.shape, np.int8)
        for idx, label in enumerate(label_list):
            marking = [int(x) for x, y in layer.metadata["labeling"]["labelSets"].items() if
                       label in y]
            np.place(data, np.isin(layer.data, marking), idx + 1)
        highlight_layer = viewer.layers["highlight"]
        highlight_layer.data = data


def add_remove_segments(layer, event):
    viewer = napari.current_viewer()
    if event.type == "mouse_press" and event.button == 1 and edit_widget.selection.value:
        val = layer.get_value(event.position, world=False)
        if val == 0:
            return
        if "selection" not in viewer.layers:
            active_layer = edit_widget.img_layer.value
            selection_layer = viewer.add_labels(data=np.zeros(active_layer.level_shapes[0], dtype=np.int8),
                                                name="selection")
            viewer.layers.selection.select_only(active_layer)
            selection_layer.metadata["labeling_obj"] = Labeling.fromValues(
                np.zeros(layer.data.shape, np.uint8))
        selection_layer = viewer.layers["selection"]
        list_of_segments = layer.metadata["labeling"]["labelSets"][str(val)]
        segment_to_fragment = layer.metadata["segment_to_fragment"]
        labeling = selection_layer.metadata["labeling_obj"]
        labeling.add_image(
            np.asarray(np.isin(layer.data, list(segment_to_fragment[list_of_segments[0]])), dtype=np.uint8))
        img, label = labeling.get_result(True)
        selection_layer.data = img.astype(np.uint8)
        selection_layer.metadata["segment_to_fragment"] = labeling._Labeling__segment_fragment_mapping()
        selection_layer.metadata["labeling"] = vars(label)
    elif event.type == "mouse_press" and event.button == 2 and edit_widget.selection.value:
        if "selection" not in viewer.layers:
            return
        selection_layer = viewer.layers["selection"]
        val = selection_layer.get_value(event.position, world=False)
        if val > 0:
            remove_segment_from_selection(selection_layer, val)


def remove_segment_from_selection(selection_layer, val):
    labeling = selection_layer.metadata["labeling_obj"]
    labeling.remove_segment(val)
    img, label = labeling.get_result(True)
    selection_layer.data = img.astype(np.uint8)
    selection_layer.metadata["labeling"] = vars(label)
    selection_layer.metadata["segment_to_fragment"] = labeling._Labeling__segment_fragment_mapping()

def split_layer(layer, event):
    viewer = napari.current_viewer()
    segment_to_fragment = layer.metadata["segment_to_fragment"]