import os

from ..engine import icons
from .. import poll
from .. import operators
from .. import preferences

from .. import __package__ as addon_pkg

if "bpy" in locals():
    import importlib

    importlib.reload(poll)
    importlib.reload(operators)
    importlib.reload(preferences)

import bpy


class CPP_PT_dataset(bpy.types.Panel):
    bl_label = "Dataset"
    bl_parent_id = "CPP_PT_camera_painter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = set()  # Opened by default

    __slots__ = ()

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        addon_preferences = context.preferences.addons[addon_pkg].preferences

        preferred_workflow = addon_preferences.preferred_workflow

        # Setup context
        if not poll.full_poll(context):
            col = layout.column()
            col.scale_y = 1.5
            col.operator(
                operator=operators.CPP_OT_setup_context.bl_idname,
                icon_value=icons.get_icon_id("setup_context")
            )

        # Source image dataset directory
        col = layout.column(align=True)
        col.label(text="Source Images Directory:")
        row = col.row(align=True)
        row.prop(scene.cpp, "source_dir", text="")
        srow = row.row(align=True)
        srow.enabled = False
        if os.path.isdir(bpy.path.abspath(scene.cpp.source_dir)):
            srow.enabled = True
        props = srow.operator(operator="wm.path_open", text="", icon='EXTERNAL_DRIVE')
        props.filepath = scene.cpp.source_dir

        # Bind images
        col = layout.column()

        if context.mode == 'OBJECT' and scene.cpp.has_camera_objects_selected:
            col.operator(
                operator=operators.CPP_OT_bind_camera_image.bl_idname,
                text="Bind Selected Camera Images", icon_value=icons.get_icon_id("bind_image")
            ).mode = 'SELECTED'

        if scene.cpp.has_camera_objects:
            col.operator(
                operator=operators.CPP_OT_bind_camera_image.bl_idname,
                text="Bind All Camera Images", icon_value=icons.get_icon_id("bind_image")
            ).mode = 'ALL'

        # Camera data IO
        col.operator(
            operator=operators.CPP_OT_import_camera_data.bl_idname,
            icon_value=icons.get_icon_id("import")
        )

        col.operator(
            operator=operators.CPP_OT_export_camera_data.bl_idname,
            icon_value=icons.get_icon_id("export")
        )
