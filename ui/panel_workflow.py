from . import common

from ..engine import icons
from .. import operators

if "bpy" in locals():
    import importlib

    importlib.reload(common)
    importlib.reload(operators)

import bpy


class CPP_PT_workflow(bpy.types.Panel):
    bl_label = "Workflow"
    bl_parent_id = "CPP_PT_camera_painter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = set()  # Opened by default

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return len(context.scene.objects)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        wm = context.window_manager

        # Cameras Dataset
        col = layout.column(align=True)

        col.use_property_split = False
        row = col.row(align=True)
        row.separator()
        row.prop(scene.cpp, "used_all_cameras", text="")

        row.label(text="Cameras")
        row.label(text="Images")
        col.template_list(
            "DATA_UL_scene_camera_item", "", scene, "objects", scene.cpp,
            "active_camera_index", type='DEFAULT', rows=3)

        camera_ob = common.get_camera_object(context)
        if camera_ob:
            camera = camera_ob.data

            layout.template_ID(
                camera.cpp,
                "image",
                open="image.open",
                live_icon=True
            )

            props = layout.operator(
                operator=operators.CPP_OT_bind_camera_image.bl_idname,
                text="Bind Image",
                icon_value=icons.get_icon_id("bind_image")
            )
            if context.mode == 'OBJECT':
                props.mode = 'ACTIVEOB'
            else:
                props.mode = 'SCENECAM'
