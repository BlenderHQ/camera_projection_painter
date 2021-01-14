from .. import poll

if "bpy" in locals():
    import importlib
    importlib.reload(poll)

import bpy


class CPP_OT_enable_all_cameras(bpy.types.Operator):
    bl_idname = "cpp.enable_all_cameras"
    bl_label = "Enable All Cameras"
    bl_options = {'INTERNAL'}
    bl_description = "Sets all cameras in the scene as used"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def execute(self, context):
        enabled_count = 0
        for camera_object in context.scene.cpp.camera_objects:
            if not camera_object.initial_visible:
                enabled_count += 1
            camera_object.initial_visible = True

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        if enabled_count:
            self.report(
                type={'INFO'},
                message=f"Enabled {enabled_count} cameras"
            )

        return {'FINISHED'}
