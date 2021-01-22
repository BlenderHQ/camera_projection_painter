from . import _engine as engine
from ._engine import icons

import bpy

__all__ = (
    "camera_data_file_type_enumerator_helper",
)

_ng_io_prop_as_type_items = [
]

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


def camera_data_file_type_enumerator_helper(ui_name: str, ui_description: str):
    """Class decorator function. Updates class annotations by enum property called
    `ng_io_prop_as_type` 
    contains supported by engine.io module
    camera data file types. 
n
    Args:
        ui_name (str): Name to be used in user interface.
        ui_description (str): Description to be used in user interface.
    """
    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        def _ng_io_prop_as_type_get(self):
            return 1

        def _ng_io_prop_as_type_set(self, value):
            print(value)

        cls.__annotations__.update(
            {
                "ng_io_prop_as_type": bpy.props.EnumProperty(
                    items=_ng_io_prop_as_type_items,
                    default=1,
                    name=ui_name,
                    description=ui_description,
                    get=_ng_io_prop_as_type_get,
                    set=_ng_io_prop_as_type_set,
                )
            }
        )

        return cls

    return wrapper
