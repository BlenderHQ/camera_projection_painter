from . import common

from ..engine import icons

if "bpy" in locals():
    import importlib

    importlib.reload(common)

import bpy


class CPP_PT_image_preview(bpy.types.Panel):
    bl_label = "Image Preview"
    bl_parent_id = "CPP_PT_workflow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = set()  # Opened by default

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        camera_ob = common.get_camera_object(context)
        if camera_ob:
            camera = camera_ob.data
            image = camera.cpp.image
            if image is not None:
                return True
        return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        camera_ob = common.get_camera_object(context)
        if camera_ob:
            camera = camera_ob.data
            image = camera.cpp.image

            icon_wrap_scale = common.get_icon_wrap_scale(context)

            if image.cpp.valid:
                icon_value = camera.cpp.image.preview.icon_id
            else:
                icon_value = icons.get_icon_id("broken_image")

            layout.template_icon(icon_value=icon_value, scale=icon_wrap_scale)
