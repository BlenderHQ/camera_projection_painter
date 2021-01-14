from ..engine import icons
from .. import operators

if "bpy" in locals():
    import importlib

    importlib.reload(operators)

import bpy


class CPP_MT_camera_pie(bpy.types.Menu):
    bl_label = "Camera Paint"

    __slots__ = ()
    
    def draw(self, context):
        layout = self.layout

        scene = context.scene
        wm = context.window_manager
        selected_camera_ob = wm.cpp.current_selected_camera_ob
        if not isinstance(selected_camera_ob, bpy.types.Object):
            return

        pie = layout.menu_pie()
        col = pie.column(align=True)

        col.label(text="Camera:")
        col.emboss = 'RADIAL_MENU'
        col.label(text=selected_camera_ob.name)
        col.emboss = 'NORMAL'

        col = col.column(align=True)
        col.ui_units_x = 11

        camera = selected_camera_ob.data
        image = camera.cpp.image

        if image:
            if image.cpp.valid:
                col.template_ID_preview(
                    camera.cpp, "image", open="image.open", rows=4, cols=5)
            else:
                col.label(text="Invalid image",
                          icon_value=icons.get_icon_id("broken_image"))
                col.template_ID(camera.cpp, "image", open="image.open")
        else:
            col.template_ID(camera.cpp, "image", open="image.open")

        col.emboss = 'RADIAL_MENU'
        pie.operator(
            operator=operators.CPP_OT_bind_camera_image.bl_idname).mode = 'GS'

        if selected_camera_ob.initial_visible:
            text = "Disable"
            icon = 'HIDE_ON'
        else:
            text = "Enable"
            icon = 'HIDE_OFF'
        pie.operator(
            operator=operators.CPP_OT_toggle_camera_usage.bl_idname,
            text=text, icon=icon
        )

        text = "Set Active"
        if scene.camera == selected_camera_ob:
            text = "Already active"
        pie.operator(
            operator=operators.CPP_OT_set_tmp_camera_active.bl_idname, text=text)
