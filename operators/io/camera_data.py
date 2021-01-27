from ... import engine
from ...engine import icons

from ... import __package__ as addon_pkg

from ... import ui

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy
import bpy_extras
from bpy.props import BoolProperty, FloatProperty, StringProperty, EnumProperty, CollectionProperty

import os


@bpy_extras.io_utils.orientation_helper(axis_forward='-Z', axis_up='Y')
class CPP_OT_import_camera_data(bpy.types.Operator):
    bl_idname = "cpp.import_camera_data"
    bl_label = "Import Camera Data"
    bl_options = {'REGISTER', 'UNDO'}

    __slots__ = ()

    directory: StringProperty(
        name="Directory",
        description="Input directory",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default=engine.io_properties.get_all_items_ext_filter_glob(),
        options={'HIDDEN'},
        maxlen=255
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    scene_scale: FloatProperty(
        name="Scene Scale",
        default=1.0,
        min=0.01,
        max=10000
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, _context):
        change_axis = bpy_extras.io_utils.axis_conversion_ensure(
            self,
            "axis_forward",
            "axis_up",
        )
        return change_axis

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        info_text = ""
        info_icon_id = 0

        import_type = engine.io.CameraDataFileType.UNKNOWN

        if len(self.files):
            import_type = engine.io.recognize_files(self.directory, [_.name for _ in self.files])

            file_word = "file" if len(self.files) == 1 else "files"

            if import_type == engine.io.CameraDataFileType.UNKNOWN:
                info_text = f"Unable to recognize {file_word} as camera data."
                info_icon_id = icons.get_icon_id("warning")
            else:
                info_text = f"Selected {file_word} recognized as type:"
                info_icon_id = icons.get_icon_id("info")
        else:
            info_text = "Please, select one or more camera data files of the same type."
            info_icon_id = icons.get_icon_id("info")

        ui.common.draw_wrapped_text(context, col, text=info_text, icon_id=info_icon_id)

        if import_type != engine.io.CameraDataFileType.UNKNOWN:
            readable_name, soft_icon_id = engine.io_properties.get_readable_type_item_name(import_type)
            ui.common.draw_wrapped_text(context, col, text=f"\"{readable_name}\"", icon_id=soft_icon_id)

    def execute(self, context):
        # import_type = engine.io.recognize_files(self.directory, [_.name for _ in self.files])
        # file_word = "file" if len(self.files) == 1 else "files"
        # if import_type == engine.io.CameraDataFileType.UNKNOWN:
        #     self.report(type={'WARNING'}, message=f"Failed to import unknown {file_word}")
        #     return {'CANCELLED'}

        num_succeeded = engine.io.import_camera_data(self.directory, [_.name for _ in self.files])

        self.report(type={'INFO'}, message=f"Imported {num_succeeded} files")

        return {'FINISHED'}


@bpy_extras.io_utils.orientation_helper(axis_forward='-Z', axis_up='Y')
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

    ng_io_prop_as_type: engine.io_properties.get_ng_io_prop_as_type(
        ui_name="Export as",
        ui_description="Export type for third - party software"
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
        print(self.ng_io_prop_as_type)
        return {'FINISHED'}


class CPP_PT_io_camera_data_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname in (
            'CPP_OT_import_camera_data',
            'CPP_OT_export_camera_data',
        )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scene_scale")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")
