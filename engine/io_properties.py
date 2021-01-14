from . import _engine as engine
from ._engine import icons

__all__ = (
    "file_type_items",
    "get_file_extension_for_file_type"
)

file_type_items = [

    # Capturing Reality Reality Capture:
    (
        'REALITY_CAPTURE_IECP',
        "Internal/External camera parameters",
        "",
        icons.get_icon_id("reality_capture"),
        0
    ),
    (
        'REALITY_CAPTURE_NXYZ',
        "Comma-separated Name, X, Y, Z",
        "",
        icons.get_icon_id("reality_capture"),
        1
    ),
    (
        'REALITY_CAPTURE_NXYZHPR',
        "Comma-separated Name, X, Y, Z, Heading, Pitch, Roll",
        "",
        icons.get_icon_id("reality_capture"),
        2
    ),
    (
        'REALITY_CAPTURE_NXYZOPK',
        "Comma-separated Name, X, Y, Z, Omega, Phi, Kappa",
        "",
        icons.get_icon_id("reality_capture"),
        3
    ),

    # Agisoft Metashape:
    (
        'METASHAPE_PIDXYZOPKR',
        "Omega Phi Kappa",
        "",
        icons.get_icon_id("metashape"),
        4
    ),
]


def get_file_extension_for_file_type(type: str) -> str:
    """Returns correspondent file extension for given file type.

    Args:
        type (str): File type (file_type_items[n][0])

    Returns:
        str: File extension.
    """
    if type in (
        'REALITY_CAPTURE_IECP',
        'REALITY_CAPTURE_NXYZ',
        'REALITY_CAPTURE_NXYZHPR',
        'REALITY_CAPTURE_NXYZOPK'
    ):
        return ".csv"
    elif type in (
        'METASHAPE_PIDXYZOPKR',
    ):
        return ".txt"

    return ""
