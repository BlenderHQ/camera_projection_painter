from . import camera
from . import image_preview

if "bpy" in locals():
    import importlib
    importlib.reload(camera)
    importlib.reload(image_preview)

import bpy

_classes = [
    camera.CPP_GT_camera_gizmo,
    camera.CPP_GGT_camera_gizmo_group,
    image_preview.CPP_GT_current_image_preview,
    image_preview.CPP_GGT_image_preview_gizmo_group
]


register, unregister = bpy.utils.register_classes_factory(_classes)
