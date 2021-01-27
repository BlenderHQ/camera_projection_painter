from . import _engine as engine
from ._engine import icons

import bpy

__all__ = (
    "get_ng_io_prop_as_type",
    "get_readable_type_item_name",
)

_ng_io_prop_as_type_items = []

_csv_camera_data_file_type_items = [
    # Reality Capture:
    (
        'REALITY_CAPTURE_IECP',
        "Internal/External camera parameters",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.REALITY_CAPTURE_IECP)
    ),
    (
        'REALITY_CAPTURE_NXYZ',
        "Comma-separated Name, X, Y, Z",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZ)
    ),
    (
        'REALITY_CAPTURE_NXYZHPR',
        "Comma-separated Name, X, Y, Z, Heading, Pitch, Roll",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZHPR)
    ),
    (
        'REALITY_CAPTURE_NXYZOPK',
        "Comma-separated Name, X, Y, Z, Omega, Phi, Kappa",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZOPK)
    ),

    # Metashape:
    (
        'METASHAPE_PIDXYZOPKR',
        "Omega Phi Kappa",
        "",
        icons.get_icon_id("metashape"),
        int(engine.io.CameraDataFileType.METASHAPE_PIDXYZOPKR)
    ),
]

_xml_camera_data_file_type_items = [
    # Reality Capture:
    (
        'REALITY_CAPTURE_METADATA_XMP',
        "Metadata (XMP)",
        "",
        icons.get_icon_id("reality_capture"),
        int(engine.io.CameraDataFileType.REALITY_CAPTURE_METADATA_XMP)
    ),

    # Metashape:
    (
        'METASHAPE_AGISOFT_XML',
        "Agisoft XML",
        "",
        icons.get_icon_id("metashape"),
        int(engine.io.CameraDataFileType.METASHAPE_AGISOFT_XML)
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


def get_ng_io_prop_as_type(ui_name: str, ui_description: str):
    return bpy.props.EnumProperty(
        # Items can be sorted w.r.t third-party software:
        # items=reversed(sorted(_ng_io_prop_as_type_items, key=lambda item: item[3])),
        items=_ng_io_prop_as_type_items,
        default=1,  # 'UNKNOWN' item skipped.
        name=ui_name,
        description=ui_description,
    )
