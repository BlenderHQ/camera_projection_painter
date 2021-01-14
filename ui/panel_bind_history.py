from . import common

if "bpy" in locals():
    import importlib

    importlib.reload(common)

import bpy


class CPP_PT_bind_history(bpy.types.Panel):
    bl_label = "Bind History"
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

            layout.template_list(
                "DATA_UL_bind_history_item", "",
                camera, "cpp_bind_history", camera.cpp,
                "active_bind_index",
                rows=1
            )
