from ...engine import icons
from ... import engine
from ... import __package__ as addon_pkg

from ... import ui
from ... import poll

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(poll)

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from io_scene_fbx import import_fbx

import os
import time
import random
from math import radians

FPS = 60
WAIT_SEC = 0.75

# ----------------- Utility ----------------- #


def _check(ob: bpy.types.Object) -> bool:
    """Check is object not `None` and does it have polygons and at least one UV map.

    Args:
        ob (bpy.types.Object): Object to check.

    Returns:
        bool: True if object is not `None` and have at least one polygon.
    """
    return poll.check_uv_layers(ob) and len(ob.data.polygons) 


def _get_valid_mesh_object(context: bpy.types.Context) -> bpy.types.Object:
    """Search behind `context.visible_objects` for an object with max poly count.

    Args:
        context (bpy.types.Context): Current context.

    Returns:
        bpy.types.Object: mesh object or `None`.
    """
    A_ob = None
    max_poly_count = 0
    for ob in context.visible_objects:
        if _check(ob):
            poly_count = len(ob.data.polygons)
            if poly_count > max_poly_count:
                max_poly_count = poly_count
                A_ob = ob
    return A_ob


def evaluate_valid_mesh_object(context: bpy.types.Context) -> bool:
    """Evaluates valid mesh object.

    Args:
        context (bpy.types.Context): Current context.

    Returns:
        bool: True if `context.active_object` after evaluation is valid.
    """
    if _check(context.active_object):
        return True
    else:
        valid_ob = _get_valid_mesh_object(context)
        if valid_ob is None:
            return False
        else:
            context.view_layer.objects.active = valid_ob
            return True
    return False

# ----------------- Context setup stages ----------------- #


def stage_import_fbx(self, context: bpy.types.Context) -> bool:
    addon_preferences = context.preferences.addons[addon_pkg].preferences

    if import_fbx.load(
        operator=self,
        context=context,
        filepath=self.filepath,
        use_image_search=True,
        use_anim=False
    ) != {'FINISHED'}:
        self.report(type={'WARNING'}, message="Import failed.")
        return False

    # Additional scene transformations after import:
    if addon_preferences.preferred_workflow == 'REALITY_CAPTURE':
        pass  # NOTE: Here may be placed some additional functionality after import

    elif addon_preferences.preferred_workflow == 'METASHAPE':
        scene = context.scene
        tool_settings = scene.tool_settings

        bpy.ops.object.select_all(action='DESELECT')
        for ob in context.view_layer.objects:
            if ob.type == 'CAMERA':
                ob.select_set(True)

        restore_transform_pivot_point = tool_settings.transform_pivot_point
        tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'

        bpy.ops.transform.rotate(
            value=radians(180.0),
            orient_axis='Y',
            orient_type='LOCAL',
            constraint_axis=(False, True, False),
            use_proportional_edit=False
        )
        tool_settings.transform_pivot_point = restore_transform_pivot_point

    return True


def stage_mesh_check(self, context: bpy.types.Context) -> bool:
    if not evaluate_valid_mesh_object(context):
        self.report(type={'WARNING'}, message="Not found valid mesh object.")
        return False
    return True


def stage_material_check(self, context: bpy.types.Context) -> bool:
    ob = context.active_object
    image_paint = context.scene.tool_settings.image_paint

    # Check for active material, create a new one if material is missing
    if ob.active_material is None:
        self.report(
            type={'INFO'},
            message="Created new material"
        )
        ob.data.materials.append(bpy.data.materials.new("Material"))

    # Check one more time
    material = ob.active_material
    if material is None:
        self.report(type={'WARNING'}, message="Missing active material")
        return False

    # Setup active material
    material.use_nodes = True

    tree = material.node_tree
    nodes = tree.nodes

    new_canvas = None
    for i, node in enumerate(nodes):
        if ((node.bl_idname == "ShaderNodeTexImage") and
            (node.image is not None) and
                (node.image.size[0] and node.image.size[1])):
            new_canvas = node.image
            break

    if (new_canvas is not None) and (new_canvas != image_paint.canvas):
        self.report(
            type={'INFO'},
            message=f"Image \"{new_canvas.name}\" set as texture (canvas)"
        )
        image_paint.canvas = new_canvas

    if tree.active_texnode_index == -1:
        addon_preferences = context.preferences.addons[addon_pkg].preferences
        new_texture_size = addon_preferences.new_texture_size

        bpy.ops.paint.add_texture_paint_slot(
            width=new_texture_size[0],
            height=new_texture_size[1],
            color=(0.8, 0.8, 0.8, 1.0),
            alpha=False,
            generated_type='BLANK',
            float=True
        )
        self.report(
            type={'INFO'},
            message=f"No texture found (canvas), a new one "
                    f"was created ({new_texture_size[0]}x{new_texture_size[1]}px)"
        )

    tex_node = nodes[tree.active_texnode_index]
    if ((tex_node is not None) and
        (tex_node.image is not None) and
            (tex_node.image.size[0] and tex_node.image.size[1])):
        image_paint.canvas = tex_node.image

    return True


def stage_bind_images(self, context: bpy.types.Context) -> bool:
    scene = context.scene

    current_dataset_dir = ""
    if scene.cpp.source_dir:
        current_dataset_dir = bpy.path.abspath(scene.cpp.source_dir)
        if not os.path.isdir(current_dataset_dir):
            current_dataset_dir = ""

    if self.filepath and (not current_dataset_dir):
        dataset_dir = os.path.dirname(bpy.path.abspath(self.filepath))
        if os.path.isdir(dataset_dir):
            scene.cpp.source_dir = dataset_dir
        else:
            self.report(
                type={'WARNING'},
                message=f"Cannot find dir \"{dataset_dir}\""
            )

    if bpy.ops.cpp.bind_camera_image(
        'EXEC_DEFAULT',
        mode='ALL',
        search_blend=True,
        rename=True,
        refresh_image_previews=True
    ) != {'FINISHED'}:
        return False
    return True


def stage_tool_check(self, context: bpy.types.Context) -> bool:
    wm = context.window_manager

    ob = context.active_object
    scene = context.scene
    image_paint = scene.tool_settings.image_paint

    if ob.mode != 'TEXTURE_PAINT':
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT')

    tool = context.workspace.tools.from_space_view3d_mode(
        context.mode,
        create=False
    )

    if tool.idname != "builtin_brush.Clone":
        bpy.ops.wm.tool_set_by_id(
            name="builtin_brush.Clone",
            cycle=False,
            space_type='VIEW_3D'
        )

    if image_paint.mode != 'IMAGE':
        image_paint.mode = 'IMAGE'

    if not image_paint.use_clone_layer:
        image_paint.use_clone_layer = True

    if (not scene.camera) and scene.cpp.has_camera_objects:
        scene.camera = list(scene.cpp.camera_objects)[0]

    if scene.camera is not None:
        image = scene.camera.data.cpp.image
        if ((image is not None) and
            (image.size[0] and image.size[1]) and
                (image != image_paint.clone_image)):
            image_paint.clone_image = image

    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.light = 'FLAT'

    return True


# ----------------- "Setup Context" operator ----------------- #
prop_stage_items = [
    ('IMPORT', "", ""),
    ('VIEW_ALL', "", ""),
    ('MESH_CHECK', "", ""),
    ('MATERIAL_CHECK', "", ""),
    ('BIND_IMAGES', "", ""),
    ('REFRESH_PREVIEWS', "", ""),
    ('TOOL_CHECK', "", ""),
    # Always last
    ('END', "", ""),
]


class CPP_OT_setup_context(bpy.types.Operator):
    bl_idname = "cpp.setup_context"
    bl_label = "Setup Context"
    bl_description = "Sets the contextual conditions "
    "of the current scene required for work, "
    "respecting the selected preferred workflow"
    bl_options = {'REGISTER', 'UNDO'}

    __slots__ = (
        "timer",
        "progress",
        "step_percentage",
        "end_sleep_time",
    )

    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )

    stage: EnumProperty(
        items=prop_stage_items,
        default=prop_stage_items[0][0],
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        return not poll.full_poll(context)

    def draw(self, context):
        layout = self.layout

        layout.label(
            text="Import reconstructed scene (FBX)",
            icon_value=icons.get_icon_id("info")
        )

    def restore_defaults(self):
        """
        Restore defaults. Must be used in `cancel` method to avoid issues
        when operator called not the first time.
        """
        self.timer = None
        self.progress = None
        self.step_percentage = 0.0
        self.end_sleep_time = None
        #self.filepath = ""
        #self.filter_glob = ""
        self.stage = prop_stage_items[0][0]

    def invoke(self, context, _event):
        self.restore_defaults()

        self.progress = ui.common.invoke_progress()
        self.progress.icon_id = icons.get_icon_id("setup_context")

        # Check for possible valid mesh object
        if not evaluate_valid_mesh_object(context):
            self.stage = 'IMPORT'
            self.progress.title = "Import"
            self.step_percentage = 100.0 / (len(prop_stage_items) - 2)

            wm = context.window_manager
            wm.fileselect_add(self)
        else:
            self.stage = 'VIEW_ALL'
            self.progress.title = "Setup Context"
            self.step_percentage = 100.0 / (len(prop_stage_items) - 3)
            # Manually call `execute` method, because in case of import it would be called
            # by fileselect, here it should be handled
            self.execute(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        ui.common.complete_progress(self.progress)

        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        self.restore_defaults()  # Always last

    def execute(self, context):
        # For user convience, view all exact after valid mesh found
        if self.stage == 'VIEW_ALL':
            if context.area.type == 'VIEW_3D':
                bpy.ops.view3d.view_all('INVOKE_DEFAULT')

        # Register modal operator routine
        wm = context.window_manager
        wm.modal_handler_add(self)
        self.timer = wm.event_timer_add(
            time_step=1 / FPS,
            window=context.window
        )
        return {'RUNNING_MODAL'}

    def wait(self, duration: float) -> bool:
        """Utility method that implements "wait" some second to make UI
        changes visible and readable.

        Args:
            duration (float): Duration in seconds to wait.

        Returns:
            bool: True if still waiting, if so, `{'PASS_THROUGH'}` should be returned.
        """
        if self.end_sleep_time is None:
            self.end_sleep_time = time.time() + duration
            return True
        elif time.time() < self.end_sleep_time:
            return True
        else:
            self.end_sleep_time = None
            return False

    def modal(self, context, event):
        wm = context.window_manager
        # ------------------------ VIEW_ALL ------------------------ #
        if self.stage == 'IMPORT':
            if not stage_import_fbx(self, context):
                self.cancel(context)
                return {'CANCELLED'}

            # For user convience, view all exact after valid mesh found
            if context.area.type == 'VIEW_3D':
                bpy.ops.view3d.view_all('INVOKE_DEFAULT')

            self.progress.add(self.step_percentage)
            self.stage = 'VIEW_ALL'  # Go to next stage

        # ------------------------ VIEW_ALL ------------------------ #
        elif self.stage == 'VIEW_ALL':
            preferences_view = context.preferences.view
            if self.wait(preferences_view.smooth_view / 1000.0):
                return {'RUNNING_MODAL'}
            self.stage = 'MESH_CHECK'  # Go to next stage

        # ------------------------ MESH_CHECK ------------------------ #
        elif self.stage == 'MESH_CHECK':
            self.progress.title = "Mesh Check"
            self.progress.icon_id = icons.get_icon_id("check_mesh")

            if self.wait(WAIT_SEC):
                return {'RUNNING_MODAL'}

            if not stage_mesh_check(self, context):
                self.cancel(context)
                return {'CANCELLED'}

            self.progress.add(self.step_percentage)
            self.stage = 'MATERIAL_CHECK'  # Go to next stage

        # ------------------------ MATERIAL_CHECK ------------------------ #
        elif self.stage == 'MATERIAL_CHECK':
            self.progress.title = "Material Check"
            self.progress.icon_id = icons.get_icon_id("check_material")

            if self.wait(WAIT_SEC):
                return {'RUNNING_MODAL'}

            if not stage_material_check(self, context):
                self.cancel(context)
                return {'CANCELLED'}

            self.progress.add(self.step_percentage)
            self.stage = 'BIND_IMAGES'  # Go to next stage

        # ------------------------ BIND_IMAGES ------------------------ #
        elif self.stage == 'BIND_IMAGES':
            self.progress.title = "Bind Images"
            self.progress.icon_id = icons.get_icon_id("bind_image")

            if self.wait(WAIT_SEC):
                return {'RUNNING_MODAL'}

            if not stage_bind_images(self, context):
                self.cancel(context)
                return {'CANCELLED'}

            self.progress.add(self.step_percentage)
            self.stage = 'REFRESH_PREVIEWS'  # Go to next stage

        # ------------------------ BIND_IMAGES ------------------------ #
        elif self.stage == 'REFRESH_PREVIEWS':
            # In fact, preview generation was called on previous stage,
            # this stage just track the progress.
            if not wm.cpp.is_preview_refresh_modal:
                self.progress.add(self.step_percentage)
                self.stage = 'TOOL_CHECK'  # Go to next stage

        # ------------------------ TOOL_CHECK ------------------------ #
        elif self.stage == 'TOOL_CHECK':
            self.progress.title = "Tool Check"
            self.progress.icon_id = icons.get_icon_id("check_tool")

            if self.wait(WAIT_SEC):
                return {'RUNNING_MODAL'}

            if not stage_tool_check(self, context):
                self.cancel(context)
                return {'CANCELLED'}

            self.progress.add(self.step_percentage)
            self.stage = 'END'  # Go to next stage

        # ---
        elif self.stage == 'END':
            if self.wait(0.1):
                return {'RUNNING_MODAL'}

            self.cancel(context)  # Final stage
            if poll.full_poll(context):
                self.report(type={'INFO'}, message="Context is ready")
            return {'FINISHED'}

        return {'RUNNING_MODAL'}
