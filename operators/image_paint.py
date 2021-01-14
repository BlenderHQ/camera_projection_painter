from .. import poll
from .. import warnings

if "bpy" in locals():
    import importlib
    importlib.reload(poll)
    importlib.reload(warnings)

import bpy


class CPP_OT_image_paint(bpy.types.Operator):
    bl_idname = "cpp.image_paint"
    bl_label = "Image Paint"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not scene.cpp.use_warnings:
            return False
        if context.area.type != 'VIEW_3D':
            return False
        return poll.full_poll(context)

    def execute(self, context):
        wm = context.window_manager

        if warnings.get_warning_status(context, wm.cpp.mouse_pos):
            self.report(type={'WARNING'}, message="Danger zone!")
            if context.scene.cpp.use_warning_action_popup:
                wm.popup_menu(self.danger_zone_popup_menu, title="Danger zone", icon='INFO')
            if context.scene.cpp.use_warning_action_lock:
                return {'FINISHED'}

        bpy.ops.paint.image_paint('INVOKE_DEFAULT')

        return {'FINISHED'}

    @staticmethod
    def danger_zone_popup_menu(self, context):
        scene = context.scene

        col = self.layout.column(align=True)
        col.emboss = 'NONE'
        col.label(text="Safe Options")
        col.separator()
        row = col.row()

        col = row.column()
        col.label(text="Unprojected Radius:")

        col = row.column()
        col.emboss = 'NORMAL'
        col.label(text=f"{scene.cpp.distance_warning} {str(scene.unit_settings.length_unit).capitalize()}")
