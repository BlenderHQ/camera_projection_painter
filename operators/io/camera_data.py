from ... import engine
from ...engine import icons
from ...engine.io_properties import camera_data_file_type_enumerator_helper

from ... import __package__ as addon_pkg

from ... import ui

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy
from bpy_extras.io_utils import orientation_helper
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty

import os


@orientation_helper(axis_forward='-Z', axis_up='Y')
class CPP_OT_import_camera_data(bpy.types.Operator):
    bl_idname = "cpp.import_camera_data"
    bl_label = "Import Camera Data"
    bl_options = {'REGISTER', 'UNDO'}

    __slots__ = ()
    filepath: StringProperty(
        name="File Path",
        description="Input filepath",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    directory: StringProperty(
        name="Directory",
        description="Input directory",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255
    )

    scene_scale: FloatProperty(
        name="Scene Scale",
        default=1.0,
        min=0.01,
        max=10000
    )

    def invoke(self, context, event):

        wm = context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

    def execute(self, context):

        return {'FINISHED'}


@orientation_helper(axis_forward='-Z', axis_up='Y')
@camera_data_file_type_enumerator_helper(ui_name="Export as", ui_description="Export type for third - party software")
class CPP_OT_export_camera_data(bpy.types.Operator):
    bl_idname = "cpp.export_camera_data"
    bl_label = "Export Camera Data"
    bl_options = {'REGISTER', 'UNDO'}

    __slots__ = ()

    filepath: StringProperty(
        name="File Path",
        description="Output filepath",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    directory: StringProperty(
        name="Directory",
        description="Output directory",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255
    )

    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'}
    )

    scene_scale: FloatProperty(
        name="Scene Scale",
        default=1.0,
        min=0.01,
        max=10000
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.cpp.has_used_camera_objects

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        num_cameras = len(list(context.scene.cpp.used_camera_objects))
        ui.common.draw_wrapped_text(
            context,
            col,
            f"Export {num_cameras} cameras as type:",
            icon_id=icons.get_icon_id("export")
        )

        col.prop(self, "ng_io_prop_as_type", text="")

    @property
    def filename_ext(self):
        return engine.io.get_file_extension_for_camera_data_file_type(self.ng_io_prop_as_type)

    def invoke(self, context, event):
        addon_preferences = context.preferences.addons[addon_pkg].preferences

        # self.ng_io_prop_as_type = addon_preferences.ng_io_prop_as_type

        # if not self.filepath:
        #     blend_filepath = context.blend_data.filepath
        #     if not blend_filepath:
        #         blend_filepath = "untitled"
        #     else:
        #         blend_filepath = os.path.splitext(blend_filepath)[0]

        #     self.filepath = blend_filepath + self.filename_ext

        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, context):
        change_ext = False

        # check_extension = self.filename_ext

        # if check_extension is not None:
        #     filepath = self.filepath
        #     if os.path.basename(filepath):
        #         filepath = bpy.path.ensure_ext(
        #             os.path.splitext(filepath)[0],
        #             self.filename_ext
        #             if check_extension
        #             else "",
        #         )

        #         if filepath != self.filepath:
        #             self.filepath = filepath
        #             change_ext = True

        return change_ext

    def execute(self, context):
        print(self.filepath)
        print(self.directory)
        return {'FINISHED'}


class CPP_PT_export_camera_data_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == 'CPP_OT_export_camera_data'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scene_scale")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")
