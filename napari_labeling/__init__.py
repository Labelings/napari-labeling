
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._reader import napari_get_reader
from ._writer import napari_get_writer
from ._gui import napari_experimental_provide_dock_widget


