import os

import numpy
from PIL import Image
from labeling import Labeling
from numpy import asarray

from napari_labeling import edit_widget, create_widget

if __name__ == '__main__':
    import napari
    from napari.plugins.io import read_data_with_plugins
    MY_PLUGIN_NAME = "napari-labeling"
    # create the viewer and window
    viewer = napari.Viewer()
    napari.plugins.plugin_manager.discover()

    viewer.window.add_dock_widget(
        create_widget()
    )
    viewer.window.add_dock_widget(
        edit_widget
    )
    #photographer = data.camera()
    #image_layer = viewer.add_image(photographer, name='photographer')
    image = Image.open('data/ISBI15/Training/EDF/frame004.png')
    # convert image to numpy array
    data = asarray(image)
    viewer.add_image(data, name="frame004")
    for filename in os.listdir('data/ISBI15/Training_annotations/Training/seg_frame004_png'):
        image = Image.open('data/ISBI15/Training_annotations/Training/seg_frame004_png/'+filename)
        # convert image to numpy array
        data = asarray(image)
        viewer.add_labels(data, name=filename)
    napari.run()
