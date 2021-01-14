import bpy


class CPP_PT_camera_painter(bpy.types.Panel):
    bl_label = "Camera Painter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = set()  # Opened by default

    __slots__ = ()

    def draw(self, context):
        pass
