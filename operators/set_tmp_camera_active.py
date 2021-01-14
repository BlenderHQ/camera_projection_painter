import bpy


class CPP_OT_set_tmp_camera_active(bpy.types.Operator):
    bl_idname = "cpp.set_tmp_camera_active"
    bl_label = "Set Active"
    bl_description = "Set the camera as active for the scene"
    bl_options = {'REGISTER', 'UNDO'}

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        scene = context.scene
        wm = context.window_manager

        return scene.camera != wm.cpp.current_selected_camera_ob

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager

        camera_ob = wm.cpp.current_selected_camera_ob
        if camera_ob and camera_ob.type == 'CAMERA':
            scene.camera = camera_ob
            scene.camera.initial_visible = True

            self.report(
                type={'INFO'},
                message=f"\"{camera_ob.name}\" now is active scene camera."
            )
            return {'FINISHED'}

        return {'CANCELLED'}
