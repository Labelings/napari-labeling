from ._reader import napari_get_reader
from ._writer import writer_function
from ._widget import edit_widget
from ._create_widget import create_widget

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"



