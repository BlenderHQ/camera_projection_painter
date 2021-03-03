from ... import engine
from ...engine import icons

from ... import __package__ as addon_pkg

from ... import ui

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy
import bpy_extras
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    CollectionProperty
)

import os

BINDED_IMAGE_FILENAME_TEXT = "[Binded Image File Name]"


@bpy_extras.io_utils.orientation_helper(axis_forward='-Z', axis_up='Y')
class CPP_OT_import_camera_data(bpy.types.Operator):
    bl_idname = "cpp.import_camera_data"
    bl_label = "Import Camera Data"
    bl_description = "Import camera data from third-party software"
    bl_options = {'UNDO', 'PRESET'}

    __slots__ = ()

    directory: StringProperty(
        name="Directory",
        description="Input directory",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    filter_glob: StringProperty(
        default=engine.camera_data_io_properties.get_all_items_ext_filter_glob(),
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
        wm = context.window_manager
        wm.cpp.suspended = True

        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.cpp.suspended = True

    def check(self, _context):
        change_axis = bpy_extras.io_utils.axis_conversion_ensure(
            self,
            "axis_forward",
            "axis_up",
        )
        return change_axis

    @property
    def files_word(self):
        return "file" if len(self.files) == 1 else "files"

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

            if import_type == engine.io.CameraDataFileType.UNKNOWN:
                info_text = f"Unable to recognize {self.files_word} as camera data."
                info_icon_id = icons.get_icon_id("warning")
            else:
                info_text = f"Selected {self.files_word} recognized as type:"
                info_icon_id = icons.get_icon_id("import")
        else:
            info_text = "Please, select one or more camera data files of the same type."
            info_icon_id = icons.get_icon_id("info")

        ui.common.draw_wrapped_text(context, col, text=info_text, icon_id=info_icon_id)

        if import_type != engine.io.CameraDataFileType.UNKNOWN:
            readable_name, soft_icon_id = engine.camera_data_io_properties.get_readable_type_item_name(import_type)
            ui.common.draw_wrapped_text(context, col, text=f"\"{readable_name}\"", icon_id=soft_icon_id)

    def execute(self, context):
        file_names = [_.name for _ in self.files]

        data_type = engine.io.recognize_files(self.directory, file_names)
        num_succeeded = engine.io.import_camera_data(data_type, self.directory, file_names)

        if num_succeeded:
            self.report(type={'INFO'}, message=f"Imported {num_succeeded} {self.files_word}")
            self.cancel(context)
            return {'FINISHED'}
        else:
            self.report(type={'WARNING'}, message=f"Unable to import {self.files_word}")
            self.cancel(context)
            return {'CANCELLED'}


@bpy_extras.io_utils.orientation_helper(axis_forward='-Z', axis_up='Y')
class CPP_OT_export_camera_data(bpy.types.Operator):
    bl_idname = "cpp.export_camera_data"
    bl_label = "Export Camera Data"
    bl_description = "Export used cameras data"
    bl_options = {'PRESET'}

    __slots__ = ()

    filename: StringProperty(
        name="File Name",
        description="Output filename",
        maxlen=1024,
        subtype='FILE_NAME',
        options={'HIDDEN'}
    )

    filepath: StringProperty(
        name="File Path",
        description="Output filepath",
        maxlen=1024,
        subtype='FILE_PATH',
        options={'HIDDEN'}
    )

    directory: StringProperty(
        name="Directory",
        description="Output directory",
        maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN'}
    )

    filter_glob: StringProperty(
        default=engine.camera_data_io_properties.get_all_items_ext_filter_glob(),
        options={'HIDDEN'},
        maxlen=255
    )

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'}
    )

    ng_io_prop_as_type: EnumProperty(
        name="Export as",
        description="Export type for third - party software",
        items=engine.camera_data_io_properties.ng_io_prop_as_type_items,
        default=1
    )

    open_dir_at_succeeded: BoolProperty(
        name="Open Directory",
        default=True,
        description="Open output directory after export camera data"
    )

    scene_scale: FloatProperty(
        name="Scene Scale",
        default=1.0,
        min=0.01,
        max=10000.0
    )

    @classmethod
    def poll(cls, context):
        return context.scene.cpp.has_io_valid_objects

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        num_cameras = len(list(context.scene.cpp.io_valid_objects))

        cameras_word = "camera"
        if num_cameras > 1:
            cameras_word = "cameras"

        ui.common.draw_wrapped_text(
            context,
            col,
            f"Export {num_cameras} {cameras_word} data as type:",
            icon_id=icons.get_icon_id("export")
        )

        layout.prop(self, "ng_io_prop_as_type", text="")

        layout.prop(self, "open_dir_at_succeeded")

    @property
    def filename_ext(self) -> str:
        return engine.io.get_file_extension_for_camera_data_file_type(self.ng_io_prop_as_type)

    def invoke(self, context, _event):
        # Set export file type option to preferences defaults
        addon_preferences = context.preferences.addons[addon_pkg].preferences
        self.ng_io_prop_as_type = addon_preferences.ng_io_prop_as_type

        # Create default filepath
        if not self.filepath:
            blend_filepath = context.blend_data.filepath
            if not blend_filepath:
                blend_filepath = "untitled"
            else:
                blend_filepath = os.path.splitext(blend_filepath)[0]

            self.filepath = blend_filepath + self.filename_ext

        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, _context):
        change_filepath = False
        change_export_type = False

        # Automatically recognize existing file type for overwrite
        data_type = engine.io.CameraDataFileType(self.ng_io_prop_as_type)

        if (os.path.exists(self.filepath)):
            data_type = engine.io.recognize_files(self.directory, [_.name for _ in self.files])

        if data_type != engine.io.CameraDataFileType.UNKNOWN:
            str_data_type = str(data_type)

            if self.ng_io_prop_as_type != str_data_type:
                self.ng_io_prop_as_type = str(data_type)
                change_export_type = True

        dirname = os.path.dirname(self.filepath)
        basename = os.path.basename(self.filepath)

        if basename:
            name_noext = os.path.splitext(basename)[0]

            # Modify filename with respect to camrea data file type
            if data_type in (
                    engine.io.CameraDataFileType.RC_IECP,
                    engine.io.CameraDataFileType.RC_NXYZ,
                    engine.io.CameraDataFileType.RC_NXYZHPR,
                    engine.io.CameraDataFileType.RC_NXYZOPK,
            ):
                name_noext = name_noext.replace(' ', '_')

            elif data_type in (
                engine.io.CameraDataFileType.RC_METADATA_XMP,
            ):
                name_noext = BINDED_IMAGE_FILENAME_TEXT

            # Change file extension with respect to camera data file type
            filepath = bpy.path.ensure_ext(os.path.join(dirname, name_noext), self.filename_ext,)

            if filepath != self.filepath:
                self.filepath = filepath
                change_filepath = True

        return change_filepath or change_export_type

    def execute(self, context):
        scene = context.scene
        camera_ob_arr = list(scene.cpp.io_valid_objects)

        # Update all io-valid camera objects data `ng_prop` properties
        scene.cpp.update_ng_prop_for_io_valid_objects()

        num_succeeded = 0

        if camera_ob_arr:
            num_succeeded = engine.io.export_camera_data(self.ng_io_prop_as_type, self.filepath, camera_ob_arr)
        else:
            self.report(type={'WARNING'}, message="Used camera objects with binded images matched by name is missing")
            return {'CANCELLED'}

        files_word = "file"
        if (num_succeeded > 1):
            files_word = "files"

        if num_succeeded:
            self.report(type={'INFO'}, message=f"Exported {num_succeeded} camera data {files_word}")
            if self.open_dir_at_succeeded:
                bpy.ops.wm.path_open('EXEC_DEFAULT', filepath=self.directory)
            return {'FINISHED'}

        else:
            self.report(type={'WARNING'}, message=f"Unable to export camera data {files_word}")
            return {'CANCELLED'}


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
