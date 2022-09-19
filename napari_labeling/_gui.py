import numpy as np
from qtpy.QtWidgets import QWidget, QGridLayout, QCheckBox, QRadioButton, QButtonGroup
from napari_plugin_engine import napari_hook_implementation
from labeling import Labeling
from copy import deepcopy


class LabelingWidget(QWidget):
    fragment_highlighting = True
    segment_select = False

    def __init__(self, napari_viewer):
        self.viewer = napari_viewer
        super().__init__()
        layout = QGridLayout()

        checkbox = QCheckBox("Enable cursor tracking")
        checkbox.stateChanged.connect(self.toggle_highlighting)
        layout.addWidget(checkbox, 0, 0, 1, 1)

        highlight_button_group = QButtonGroup(layout)
        fragment_radio_btn = QRadioButton("Fragment Highlighting")
        fragment_radio_btn.setChecked(self.fragment_highlighting)
        fragment_radio_btn.toggled.connect(lambda:self.highlighting_switch(fragment_radio_btn))
        segment_radio_btn = QRadioButton("Segment Highlighting")
        segment_radio_btn.toggled.connect(lambda:self.highlighting_switch(segment_radio_btn))
        highlight_button_group.addButton(fragment_radio_btn)
        highlight_button_group.addButton(segment_radio_btn)
        layout.addWidget(fragment_radio_btn, 1, 0, 1, 1)
        layout.addWidget(segment_radio_btn, 2, 0, 1, 1)

        selection_button_group = QButtonGroup(layout)
        highlight_radio_btn = QRadioButton("Highlight")
        highlight_radio_btn.setChecked(not self.segment_select)
        highlight_radio_btn.toggled.connect(lambda:self.select_button(highlight_radio_btn))
        select_radio_btn = QRadioButton("Select")
        select_radio_btn.setChecked(self.segment_select)
        select_radio_btn.toggled.connect(lambda:self.select_button(select_radio_btn))
        selection_button_group.addButton(highlight_radio_btn)
        selection_button_group.addButton(select_radio_btn)
        layout.addWidget(highlight_radio_btn, 4, 0, 1, 1)
        layout.addWidget(select_radio_btn, 5, 0, 1, 1)
        self.setLayout(layout)

    def toggle_highlighting(self, state):
        """
        Sets and removes callback event handlers as well as add a highlight label layer.

        :param state:
        :return:
        """
        if state == 2:
            active_layer = [x for x in self.viewer.layers.selection][0]
            active_layer.mouse_move_callbacks.append(self.highlight)
            active_layer.mouse_drag_callbacks.append(self.add_remove_segments)
            self.viewer.add_labels(data=np.zeros(active_layer.level_shapes[0], dtype=np.int8),
                                     name="highlight")
            self.viewer.layers.selection.select_only(active_layer)
        if state == 0:
            active_layer = [x for x in self.viewer.layers.selection][0]
            active_layer.mouse_move_callbacks.remove(self.highlight)
            active_layer.mouse_drag_callbacks.remove(self.add_remove_segments)

    def highlight(self, layer, event):
        """
        Adds highlighting in the highlight layer depending on selection.
        If fragment highlighting is true, fragments will be highlighted,
        otherwise segments. If no label is in the metadata or it's background,
        nothing is highlighted.

        :param layer:
        :param event:
        :return:
        """
        cords = np.round(layer.world_to_data(self.viewer.cursor.position)).astype(int)
        val = layer.get_value(cords)
        # background
        if val == 0 or val is None:
            return
        # value not in list, happens with uncleaned data
        label_list = layer.metadata["labeling"]["labelSets"][str(val)]
        if len(label_list) == 0:
            highlight_layer = self.viewer.layers["highlight"]
            highlight_layer.data = np.zeros(layer.data.shape, dtype=np.uint8)
            return
        # highlights fragments
        if self.fragment_highlighting:
            marking = [int(x) for x, y in layer.metadata["labeling"]["labelSets"].items() if
                       any((True for a in label_list if a in y))]
            if marking is not None and len(marking) > 0:
                highlight_layer = self.viewer.layers["highlight"]
                highlight_layer.data = np.asarray(np.isin(layer.data, marking), dtype=np.uint8) * layer.data
        # highlights segments
        else:
            data = np.zeros(layer.data.shape, np.int8)
            for idx, label in enumerate(label_list):
                marking = [int(x) for x, y in layer.metadata["labeling"]["labelSets"].items() if
                           label in y]
                np.place(data, np.isin(layer.data, marking), idx + 1)
            highlight_layer = self.viewer.layers["highlight"]
            highlight_layer.data = data

    def add_remove_segments(self, layer, event):
        """
        If segment selection is enabled, a left click will add
        it to a new layer, the selection layer while a right mouse click
        will remove the segment from the selection layer.
        A Labeling object will be created for the selection layer and
        updated every time something changes.
        :param layer:
        :param event:
        :return:
        """
        if event.type == "mouse_press" and event.button == 1 and self.segment_select:
            val = layer.get_value(event.position, world=False)
            if "selection" not in self.viewer.layers:
                active_layer = [x for x in self.viewer.layers.selection][0]
                selection_layer = self.viewer.add_labels(data=np.zeros(active_layer.level_shapes[0], dtype=np.int8),
                                         name="selection")
                self.viewer.layers.selection.select_only(active_layer)
                selection_layer.metadata["labeling_obj"] = Labeling.Labeling.fromValues(np.zeros(layer.data.shape, np.uint8))
            selection_layer = self.viewer.layers["selection"]
            list_of_segments = layer.metadata["labeling"]["labelSets"][str(val)]
            segment_to_fragment = layer.metadata["segment_to_fragment"]
            labeling = selection_layer.metadata["labeling_obj"]
            labeling.add_image(np.asarray(np.isin(layer.data, list(segment_to_fragment[list_of_segments[0]])), dtype=np.uint8))
            img, label = labeling.get_result(False)
            print(vars(label)["labelSets"])

            segment_to_fragment = {}
            for key, value in label.labelSets.items():
                for v in value:
                    if v not in segment_to_fragment:
                        segment_to_fragment[v] = set()
                    segment_to_fragment[v].add(int(key))

            # selection_layer.data = np.asarray(np.isin(layer.data, list(segment_to_fragment[list_of_segments[0]])), dtype=np.uint8)
            selection_layer.data = img.astype(np.uint8)
            selection_layer.metadata["segment_to_fragment"]=segment_to_fragment
            selection_layer.metadata["labeling"]= vars(label)
        elif event.type == "mouse_press" and event.button == 2 and self.segment_select:
            if "selection" not in self.viewer.layers:
                pass

            selection_layer = self.viewer.layers["selection"]
            val = selection_layer.get_value(event.position, world=False)
            fragment_to_segment = deepcopy(selection_layer.metadata["labeling"]["labelSets"])
            list_of_segments = list(fragment_to_segment[str(val)])
            segment_to_fragment = deepcopy(selection_layer.metadata["segment_to_fragment"])
            first_segment = list_of_segments[0]
            #print("fragment_to_segment", fragment_to_segment)
            for fragment in segment_to_fragment[first_segment]:
                fragment_to_segment[str(fragment)].remove(first_segment)
            transformation_list = []
            #print("segment_to_fragment", segment_to_fragment)
            #print("fragment_to_segment removal", fragment_to_segment)
            #print("first segment_ID", first_segment)
            for fragment in segment_to_fragment[first_segment]:
                for fragment_id, segment_list in fragment_to_segment.items():
                    if set(fragment_to_segment[str(fragment)]) == set(segment_list):
                        if not any(elem in transformation_list for elem in [(int(fragment_id), fragment), (fragment, int(fragment_id))]) and fragment != int(fragment_id):
                            transformation_list.append((fragment, int(fragment_id)))
            #print("transformation_list", transformation_list)
            labeling = Labeling.Labeling.fromValues(np.zeros(selection_layer.data.shape, np.uint8))
            img = selection_layer.data
            for transformer in transformation_list:
                np.place(img, img == transformer[0], transformer[1])
            labeling.add_image(img.astype(np.uint8))
            img, label = labeling.get_result(False)
            segment_to_fragment = {}
            for key, value in label.labelSets.items():
                for v in value:
                    if v not in segment_to_fragment:
                        segment_to_fragment[v] = set()
                    segment_to_fragment[v].add(int(key))
            selection_layer.data = img.astype(np.uint8)
            selection_layer.metadata["labeling_obj"] = labeling
            selection_layer.metadata["labeling"] = vars(label)
            selection_layer.metadata["segment_to_fragment"] = segment_to_fragment

    def select_button(self, btn):
        if btn.text() == "Highlight":
            if btn.isChecked():
                self.segment_select = False
        if btn.text() == "Select":
            if btn.isChecked():
                self.segment_select = True

    def highlighting_switch(self, btn):
        if btn.text() == "Fragment Highlighting":
            if btn.isChecked():
                self.fragment_highlighting = True
        if btn.text() == "Segment Highlighting":
            if btn.isChecked():
                self.fragment_highlighting = False

    def load_layers_from_file(self, path):
        pass


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return LabelingWidget
