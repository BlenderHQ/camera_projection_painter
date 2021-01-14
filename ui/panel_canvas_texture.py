from ..engine import icons

import bpy


class CPP_PT_canvas_texture(bpy.types.Panel):
    bl_label = "Texture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_parent_id = "CPP_PT_camera_painter"
    bl_options = {'DEFAULT_CLOSED'}

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        active_ob = context.active_object
        if active_ob and active_ob.type == 'MESH':
            return True
        return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        active_ob = context.active_object
        layout.template_list("MATERIAL_UL_matslots", "", active_ob, "material_slots",
                             active_ob, "active_material_index", rows=1)
        layout.template_ID(active_ob, "active_material", new="material.new")

        active_mat = active_ob.active_material
        is_valid_mat = False
        if active_mat and active_mat.use_nodes:
            is_valid_mat = True

        if not is_valid_mat:
            # Single image workflow
            layout.label(text="Missing valid material", icon='INFO')
            scene = context.scene
            image_paint = scene.tool_settings.image_paint
            layout.prop(image_paint, "canvas", text="Texture")
        else:
            # Emulate material workflow
            row = layout.row()
            tree = active_mat.node_tree

            is_image_node = False
            if tree:
                for node in tree.nodes:
                    if node.bl_idname == "ShaderNodeTexImage":
                        is_image_node = True
                        break
            
            if is_image_node:
                row.template_list("DATA_UL_node_image_item", "", tree,
                                "nodes", tree, "active_texnode_index", rows=2)
            else:
                row.label(text="Missing Textures", icon='ERROR')

            row.operator_menu_enum(
                "paint.add_texture_paint_slot", "type", icon='ADD', text="")
