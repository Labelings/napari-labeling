"""

It implements the ``napari_get_reader`` hook specification to create
a reader plugin)
see: https://napari.org/docs/dev/plugins/hook_specifications.html

"""
import numpy as np
from labeling import Labeling
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation()
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".bson"):
        return None
    # otherwise we return the *function* that can read ``path``.
    return reader_function


def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    # load all files into array
    labeling = Labeling.Labeling.from_file(paths[0])
    img, data = labeling.get_result()



    label_to_pixel = {}
    for key, value in data.labelSets.items():
        for v in value:
            if v not in label_to_pixel:
                label_to_pixel[v] = []
            label_to_pixel[v].append(int(key))

    layers = [(img, {"metadata": {"labeling": vars(data), "label_to_pixel": label_to_pixel}}, "image")]

    for key, value in label_to_pixel.items():
        label = np.asarray(np.isin(img, value), dtype=np.uint8)
        #layers.append((label, {"name": key}, "labels"))
    return layers
