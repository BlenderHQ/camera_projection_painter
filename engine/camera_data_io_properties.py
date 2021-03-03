from . import _engine as engine
from ._engine import icons

import bpy

__all__ = (
    "ng_io_prop_as_type_items",
    "get_readable_type_item_name",
)

_ng_io_prop_as_type_items = []

_csv_camera_data_file_type_items = [
    # Reality Capture:
    (
        'RC_IECP',
        "Internal/External camera parameters",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.RC_IECP)
    ),
    (
        'RC_NXYZ',
        "Comma-separated Name, X, Y, Z",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.RC_NXYZ)
    ),
    (
        'RC_NXYZHPR',
        "Comma-separated Name, X, Y, Z, Heading, Pitch, Roll",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.RC_NXYZHPR)
    ),
    (
        'RC_NXYZOPK',
        "Comma-separated Name, X, Y, Z, Omega, Phi, Kappa",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.RC_NXYZOPK)
    ),

    # Metashape:
    (
        'MS_PIDXYZOPKR',
        "Omega Phi Kappa",
        "",
        icons.get_icon_id("metashape"),
        int(engine.io.CameraDataFileType.MS_PIDXYZOPKR)
    ),
]

_xml_camera_data_file_type_items = [
    # Reality Capture:
    (
        'RC_METADATA_XMP',
        "Metadata (XMP)",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.RC_METADATA_XMP)
    ),

    # Metashape:
    (
        'MS_AGISOFT_XML',
        "Agisoft XML",
        "",
        icons.get_icon_id("metashape"),
        int(engine.io.CameraDataFileType.MS_AGISOFT_XML)
    ),
]

if engine.WITH_NG_IO_CSV:
    _ng_io_prop_as_type_items.extend(_csv_camera_data_file_type_items)

if engine.WITH_NG_IO_XML:
    _ng_io_prop_as_type_items.extend(_xml_camera_data_file_type_items)


def get_all_items_ext_filter_glob():
    extlist = []
    for item in _ng_io_prop_as_type_items:
        ext = engine.io.get_file_extension_for_camera_data_file_type(item[0])
        if ext not in extlist:
            extlist.append(ext)

    filter_glob = ""
    for i, ext in enumerate(extlist):
        filter_glob += f"*{ext}"
        if i < len(extlist) - 1:
            filter_glob += ";"
    return filter_glob


def get_readable_type_item_name(file_type: engine.io.CameraDataFileType) -> tuple:
    """Returns readable item name and icon id.

    Args:
        file_type (engine.io.CameraDataFileType): File type.

    Returns:
        tuple: Descriptive name and icon id.
    """
    for item in _ng_io_prop_as_type_items:
        if int(file_type) == item[4]:
            return item[1], item[3]

    return "", 0


ng_io_prop_as_type_items = list(reversed(sorted(_ng_io_prop_as_type_items, key=lambda item: item[3])))

