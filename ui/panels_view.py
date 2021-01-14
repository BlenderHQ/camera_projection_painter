from ..engine import icons
from .. import poll

if "bpy" in locals():
    import importlib

    importlib.reload(poll)

import bpy


class ViewPanelBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = {'DEFAULT_CLOSED'}


class CPP_PT_view(bpy.types.Panel, ViewPanelBase):
    bl_label = "View"
    bl_parent_id = "CPP_PT_camera_painter"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw(self, context):
        pass


class CPP_PT_texture_preview(bpy.types.Panel, ViewPanelBase):
    bl_label = "Texture"
    bl_parent_id = "CPP_PT_view"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(context.scene.cpp, "current_image_alpha")
        layout.prop(context.scene.cpp, "current_image_size")


class CPP_PT_cameras_viewport(bpy.types.Panel, ViewPanelBase):
    bl_label = "Cameras"
    bl_parent_id = "CPP_PT_view"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(context.scene.cpp, "cameras_viewport_size")
        layout.prop(context.scene.cpp, "camera_axes_size")


class CPP_PT_brush_preview(bpy.types.Panel, ViewPanelBase):
    bl_label = "Brush Preview"
    bl_parent_id = "CPP_PT_view"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw_header(self, context):
        self.layout.prop(context.scene.cpp, "use_projection_preview", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.enabled = context.scene.cpp.use_projection_preview

        col.prop(context.scene.cpp, "use_normal_highlight")


class CPP_PT_warnings(bpy.types.Panel, ViewPanelBase):
    bl_label = "Warnings"
    bl_parent_id = "CPP_PT_view"

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw_header(self, context):
        self.layout.prop(context.scene.cpp, "use_warnings", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.enabled = context.scene.cpp.use_warnings
        col.prop(context.scene.cpp, "distance_warning")

        col = layout.column()
        col.prop(context.scene.cpp, "use_warning_action_draw")
        col.prop(context.scene.cpp, "use_warning_action_popup")
        col.prop(context.scene.cpp, "use_warning_action_lock")
