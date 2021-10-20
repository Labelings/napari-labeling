import numpy as np
from napari._qt.qthreading import thread_worker
from napari.utils.translations import trans
from qtpy.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, QCheckBox, QLabel, QFileDialog
from napari_plugin_engine import napari_hook_implementation


class LabelingWidget(QWidget):
    def __init__(self, napari_viewer):
        self.viewer = napari_viewer
        super().__init__()
        layout = QGridLayout()

        # file_selector = QFileDialog()
        # file_selector.setFileMode(QFileDialog.ExistingFile)
        # file_selector.setNameFilter("BSON files (*.bson)")
        # filenames, _ = file_selector.getOpenFileNames(
        #     parent=self,
        #     caption=trans._('Select file(s)...'),
        #     options=(
        #         QFileDialog.Options()
        #     ),
        # )
        #
        # if (filenames != []) and (filenames is not None):
        #     print(filenames)
        #
        # layout.addWidget(file_selector)

        def highlight(layer, event):
            cords = np.round(layer.world_to_data(self.viewer.cursor.position)).astype(int)
            val = layer.get_value(cords)
            label_list = layer.metadata["labeling"]["labelSets"][str(val)]
            if val == 0 or val is None or len(label_list) == 0:
                highlight_layer = self.viewer.layers["highlight"]
                highlight_layer.data = np.zeros(layer.data.shape, dtype=np.uint8)
                return
            marking = [int(x) for x, y in layer.metadata["labeling"]["labelSets"].items() if
                       any((True for a in label_list if a in y))]
            if marking is not None and len(marking) > 0:
                highlight_layer = self.viewer.layers["highlight"]
                highlight_layer.data = np.asarray(np.isin(layer.data, marking), dtype=np.uint8) * layer.data
                label.setText(str(cords) + ": " + str(val) + ": " + str(label_list))

        def func(state):
            print(state)
            if state == 2:
                active_layer = [x for x in napari_viewer.layers.selection][0]
                print(active_layer)
                print(active_layer.metadata)
                active_layer.mouse_move_callbacks.append(highlight)
                napari_viewer.add_labels(data=np.zeros(active_layer.level_shapes[0], dtype=np.int8),
                                         name="highlight")
                napari_viewer.layers.selection.select_only(active_layer)
            if state == 0:
                active_layer = [x for x in napari_viewer.layers.selection][0]
                active_layer.mouse_move_callbacks.remove(highlight)

        checkbox = QCheckBox("Enable cursor tracking")
        checkbox.stateChanged.connect(func)
        layout.addWidget(checkbox)

        label = QLabel("Foo-bar")
        layout.addWidget(label)

        self.setLayout(layout)

    def load_layers_from_file(self, path):
        pass


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return LabelingWidget
