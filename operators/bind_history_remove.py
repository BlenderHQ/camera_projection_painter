import bpy


class CPP_OT_bind_history_remove(bpy.types.Operator):
    bl_idname = "cpp.bind_history_remove"
    bl_label = "Remove"
    bl_description = "Remove item from image palette list"
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        if context.mode == 'PAINT_TEXTURE':
            camera_ob = context.scene.camera
        elif context.mode == 'OBJECT':
            camera_ob = context.active_object
            if camera_ob and camera_ob.type != 'CAMERA':
                camera_ob = None

        if camera_ob is not None:
            camera = camera_ob.data
            camera.cpp_bind_history.remove(self.index)
            if len(camera.cpp_bind_history):
                camera.cpp.active_bind_index = min(
                    max(self.index - 1, 0), len(camera.cpp_bind_history) - 1)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
