import bpy


class CPP_OT_toggle_camera_usage(bpy.types.Operator):
    bl_idname = "cpp.toggle_camera_usage"
    bl_label = "Toogle Usage"
    bl_options = {'INTERNAL'}

    __slots__ = ()
    
    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        ob = wm.cpp.current_selected_camera_ob
        return ob and ob.type == 'CAMERA'

    @classmethod
    def description(cls, context, properties):
        wm = context.window_manager
        ob = wm.cpp.current_selected_camera_ob
        if ob and ob.cpp.used:
            return "Disable camera"
        else:
            return "Enable camera"

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        camera_ob = wm.cpp.current_selected_camera_ob
        camera_ob.cpp.used = not camera_ob.cpp.used
        if (scene.camera == camera_ob) and (not camera_ob.cpp.used):
            scene.camera = None
            self.report(type={'WARNING'}, message="Active camera hidden!")

        return {'FINISHED'}
