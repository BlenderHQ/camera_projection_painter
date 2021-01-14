import math

from ..engine import icons
from .. import operators

if "bpy" in locals():
    import importlib

    importlib.reload(operators)

import bpy
from mathutils import Vector


class DATA_UL_scene_camera_item(bpy.types.UIList):
    IMAGE = 1 << 0
    NONE_IMAGE = 1 << 1
    INVALID_IMAGE = 1 << 2

    order: bpy.props.EnumProperty(
        items=[
            ('ALPHA', "", "Cameras in alphabetical order", 'SORTALPHA', 0),
            ('RADIAL', "", "Cameras ordered by world direction in XY plane",
             'ORIENTATION_VIEW', 1)
        ],
        name="Filter Order",
        default='RADIAL'
    )

    filter_available: bpy.props.BoolProperty(
        name="Only Available",
        default=False,
        description="Show only cameras with binded valid images"
    )

    filter_used: bpy.props.BoolProperty(
        name="Only Used",
        default=True,
        description="Show only used cameras"
    )

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index, flt_flag):
        image = item.data.cpp.image

        if self.layout_type in {'DEFAULT', 'COMPACT', 'GRID'}:
            row = layout.row(align=True)

            row.prop(item, "initial_visible", text="")
            row.label(text=item.name)

            if flt_flag & self.IMAGE:
                row.label(text=image.name, icon_value=image.preview.icon_id)

            elif flt_flag & self.NONE_IMAGE:
                row.label(text="No Image", icon_value=icons.get_icon_id("info"))

            elif flt_flag & self.INVALID_IMAGE:
                row.label(
                    text=image.name,
                    icon_value=icons.get_icon_id("broken_image")
                )

        # elif self.layout_type in {'GRID'}:
            # TODO: https://developer.blender.org/T75784

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)

        def _get_bitflag(ob):
            if ob.type == 'CAMERA':
                image = ob.data.cpp.image
                if image is None:
                    return self.bitflag_filter_item + self.NONE_IMAGE
                elif not image.cpp.valid:
                    return self.bitflag_filter_item + self.INVALID_IMAGE
                else:
                    return self.bitflag_filter_item + self.IMAGE
            return self.bitflag_filter_item

        flt_flags = [_get_bitflag(ob) if (
            ob.type == 'CAMERA') else True for ob in objects]
        flt_neworder = list(range(len(objects)))

        helper_funcs = bpy.types.UI_UL_list

        if self.order == 'RADIAL':
            camera_angles = {}
            for ob in objects:
                mat = ob.matrix_world
                x, y = -Vector([mat[0][2], mat[1][2]]).normalized()
                camera_angles[ob] = math.atan2(x, y)

            cameras_radial = [i[0] for i in sorted(
                camera_angles.items(), key=lambda item: item[1], reverse=False)]
            for i, ob in enumerate(objects):
                if ob.type == 'CAMERA':
                    flt_flags[i] &= _get_bitflag(ob)
                    flt_neworder[i] = cameras_radial.index(ob)

        if self.filter_name:
            for i, val in enumerate(helper_funcs.filter_items_by_name(
                    self.filter_name, self.bitflag_filter_item, objects, "name", reverse=False)):
                if val == 0:
                    flt_flags[i] &= val

        if self.filter_available or self.filter_used:
            for i, ob in enumerate(objects):
                if ob.type == 'CAMERA':
                    if self.filter_available:
                        image = ob.data.cpp.image
                        if not (image and image.cpp.valid):
                            flt_flags[i] = True
                    if self.filter_used:
                        if not ob.initial_visible:
                            flt_flags[i] = True

        return flt_flags, flt_neworder

    def draw_filter(self, context, layout):
        col = layout.column(align=True)
        col.prop(self, "filter_available")
        col.prop(self, "filter_used")
        row = col.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "order", expand=True, emboss=True)


class DATA_UL_bind_history_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon_id, active_data, active_propname, index):
        row = layout.row(align=True)

        image = item.image
        if image:
            if image.cpp.valid:
                row.template_icon(icon_value=image.preview.icon_id)
            else:
                row.label(icon_value=icons.get_icon_id("broken_image"))

            row.prop(image, "name", text="", emboss=False)
        else:
            row.label(icon="ERROR")


        row.emboss = 'NONE'
        row.operator(
            operator=operators.CPP_OT_bind_history_remove.bl_idname,
            text="", icon="REMOVE"
        ).index = index


class DATA_UL_node_image_item(bpy.types.UIList):
    INVALID_NODE = 1 << 0
    DISCONN_NODE = 1 << 1
    TEX_NODE = 1 << 2

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        row = layout.row(align=True)
        image = item.image
        if flt_flag & self.TEX_NODE:
            icon_value = image.preview.icon_id
            row.prop(item.image, "name", icon_value=icon_value,
                     text="", emboss=False)
        elif flt_flag & self.DISCONN_NODE:
            row.prop(item.image, "name", icon='TEXTURE', text="", emboss=False)
        elif (flt_flag & self.INVALID_NODE):
            row.prop(item, "name", text="", emboss=False,
                     icon_value=icons.get_icon_id("broken_image"))

    def filter_items(self, context, data, propname):
        nodes = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(nodes)
        flt_neworder = []

        for i, node in enumerate(nodes):
            if node.bl_idname == "ShaderNodeTexImage":
                image = node.image

                flt_flags[i] = self.bitflag_filter_item

                if image and image.cpp.valid:
                    for out in node.outputs:
                        if out.is_linked and len(out.links):
                            flt_flags[i] |= self.TEX_NODE
                            break
                        else:
                            flt_flags[i] |= self.DISCONN_NODE
                else:
                    flt_flags[i] = True
            else:
                flt_flags[i] = True

        return flt_flags, flt_neworder
