import napari
import numpy as np
from labeling import Labeling
from magicgui import magic_factory


@magic_factory(call_button='Merge selected label layers',
              auto_call=False)
def create_widget() -> 'napari.types.LabelsData':
    viewer = napari.current_viewer()
    labeling = Labeling.fromValues([np.asarray(x.data, np.int32) for x in viewer.layers.selection][0])
    labeling.iterate_over_images([np.asarray(x.data, np.int32) for x in viewer.layers.selection][1:],  range(len([x.data for x in viewer.layers.selection])))
    img, data = labeling.get_result(False)
    viewer.add_labels(data=img, name="merged_labels", metadata={"labeling": vars(data),
                               "segment_to_fragment": labeling._Labeling__segment_fragment_mapping(),
                               "labeling_obj": labeling})