from . import basis
from . import bind_history_remove
from . import image_paint
from . import set_tmp_camera_active
from . import toggle_camera_usage
from . import enable_all_cameras
from . import io
from . import refresh_image_preview


if "bpy" in locals():
    import importlib
    importlib.reload(basis)
    importlib.reload(bind_history_remove)
    importlib.reload(image_paint)
    importlib.reload(set_tmp_camera_active)
    importlib.reload(toggle_camera_usage)
    importlib.reload(enable_all_cameras)
    importlib.reload(io)
    importlib.reload(refresh_image_preview)

import bpy

# Base
CPP_OT_listener = basis.CPP_OT_listener
CPP_OT_camera_projection_painter = basis.CPP_OT_camera_projection_painter
# Misk
CPP_OT_image_paint = image_paint.CPP_OT_image_paint
CPP_OT_set_tmp_camera_active = set_tmp_camera_active.CPP_OT_set_tmp_camera_active
CPP_OT_bind_history_remove = bind_history_remove.CPP_OT_bind_history_remove
CPP_OT_toggle_camera_usage = toggle_camera_usage.CPP_OT_toggle_camera_usage
CPP_OT_enable_all_cameras = enable_all_cameras.CPP_OT_enable_all_cameras
# IO
CPP_OT_bind_camera_image = io.bind_camera_image.CPP_OT_bind_camera_image
CPP_OT_setup_context = io.setup_context.CPP_OT_setup_context

CPP_OT_import_camera_data = io.camera_data.CPP_OT_import_camera_data
CPP_OT_export_camera_data = io.camera_data.CPP_OT_export_camera_data
CPP_PT_io_camera_data_transform = io.camera_data.CPP_PT_io_camera_data_transform

# Previews
CPP_OT_refresh_image_preview = refresh_image_preview.CPP_OT_refresh_image_preview

_classes = [
    # Base operators
    CPP_OT_listener,
    CPP_OT_camera_projection_painter,

    # Misc
    CPP_OT_image_paint,
    CPP_OT_set_tmp_camera_active,
    CPP_OT_bind_history_remove,
    CPP_OT_toggle_camera_usage,
    CPP_OT_enable_all_cameras,

    # IO
    CPP_OT_bind_camera_image,
    CPP_OT_setup_context,
    CPP_OT_import_camera_data,
    CPP_OT_export_camera_data,
    CPP_PT_io_camera_data_transform,

    # Previews
    CPP_OT_refresh_image_preview,
]

register, unregister = bpy.utils.register_classes_factory(_classes)
