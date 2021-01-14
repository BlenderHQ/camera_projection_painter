from ..engine import icons
from .. import poll

if "bpy" in locals():
    import importlib

    importlib.reload(poll)

import bpy


class CPP_PT_brush(bpy.types.Panel):
    bl_label = "Brush"
    bl_parent_id = "CPP_PT_camera_painter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = {'DEFAULT_CLOSED'}

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        brush = context.tool_settings.image_paint.brush
        layout.prop(brush, "size")
        layout.prop(brush, "strength")

        layout.prop(brush, "curve_preset", text="")

        row = layout.row()

        if brush.curve_preset == 'CUSTOM':
            col = row.column()
            col.template_curve_mapping(brush, "curve", brush=True)

            col = row.column(align=True)
            col.operator("brush.curve_preset",
                         icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
            col.operator("brush.curve_preset",
                         icon='SPHERECURVE', text="").shape = 'ROUND'
            col.operator("brush.curve_preset", icon='ROOTCURVE',
                         text="").shape = 'ROOT'
            col.operator("brush.curve_preset", icon='SHARPCURVE',
                         text="").shape = 'SHARP'
            col.operator("brush.curve_preset", icon='LINCURVE',
                         text="").shape = 'LINE'
            col.operator("brush.curve_preset", icon='NOCURVE',
                         text="").shape = 'MAX'
