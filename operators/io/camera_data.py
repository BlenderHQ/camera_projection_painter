from ... import engine
from ...engine import icons
from ... import __package__ as addon_pkg

from ... import ui

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy
from bpy_extras.io_utils import ImportHelper, orientation_helper
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

    import_camera_data_as_type: EnumProperty(
        items=engine.io_properties.file_type_items,
        default=engine.io_properties.file_type_items[0][0],
        name="Import Cameras File Type",
        description="Import type from third-party software"
    )

    scene_scale: FloatProperty(
        name="Scene Scale",
        default=1.0,
        min=0.01,
        max=10000
    )

    def draw(self, context):
        layout = self.layout
        addon_preferences = context.preferences.addons[addon_pkg].preferences
        preferred_workflow = addon_preferences.preferred_workflow
        is_file_preferred = True

        if os.path.isfile(bpy.path.abspath(self.filepath)):
            csv_file_type = engine.io.check_csv_file_type(self.filepath)

            text_recognized_as = "Selected file recognized as type:"

            text = ""
            icon_id = icons.get_icon_id("info")

            if csv_file_type == engine.io.CameraDataFileType.UNKNOWN:
                text = "Selected file cannot be recognized as any of supported"
                icon_id = icons.get_icon_id("warning")

            elif csv_file_type == engine.io.CameraDataFileType.REALITY_CAPTURE_IECP:
                text = f"{text_recognized_as}\n\"Internal/External camera parameters\""
                icon_id = icons.get_icon_id("reality_capture")
                is_file_preferred = (preferred_workflow == 'REALITY_CAPTURE')

            elif csv_file_type == engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZ:
                text = f"{text_recognized_as}\n\"Comma-separated Name, X, Y, Z\""
                icon_id = icons.get_icon_id("reality_capture")
                is_file_preferred = (preferred_workflow == 'REALITY_CAPTURE')

            elif csv_file_type == engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZHPR:
                text = f"{text_recognized_as}\n\"Comma-separated Name, X, Y, Z, Heading, Pitch, Roll\""
                icon_id = icons.get_icon_id("reality_capture")
                is_file_preferred = (preferred_workflow == 'REALITY_CAPTURE')

            elif csv_file_type == engine.io.CameraDataFileType.REALITY_CAPTURE_NXYZOPK:
                text = f"{text_recognized_as}\n\"Comma-separated Name, X, Y, Z, Omega, Phi, Kappa\""
                icon_id = icons.get_icon_id("reality_capture")
                is_file_preferred = (preferred_workflow == 'REALITY_CAPTURE')

            elif csv_file_type == engine.io.CameraDataFileType.METASHAPE_PIDXYZOPKR:
                text = f"{text_recognized_as}\n\"Omega Phi Kappa (*.txt)\""
                icon_id = icons.get_icon_id("metashape")
                is_file_preferred = (preferred_workflow == 'METASHAPE')

        else:
            text = "Please, select file."
            icon_id = icons.get_icon_id("info")

        ui.common.draw_wrapped_text(
            context,
            layout,
            text,
            icon_id
        )

        if not is_file_preferred:
            ui.common.draw_wrapped_text(
                context,
                layout,
                "Selected file is not relative to your preferred workflow.",
                icons.get_icon_id("warning")
            )

    @property
    def filename_ext(self):
        return engine.io_properties.get_file_extension_for_file_type(self.export_camera_data_as_type)

    def invoke(self, context, event):
        addon_preferences = context.preferences.addons[addon_pkg].preferences
        preferred_workflow = addon_preferences.preferred_workflow

        if preferred_workflow == 'REALITY_CAPTURE':
            self.filter_glob = "*.csv"
        elif preferred_workflow == 'METASHAPE':
            self.filter_glob = "*.txt"

        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def check(self, context):
        change_ext = False

        check_extension = self.filename_ext

        if check_extension is not None:
            filepath = self.filepath
            if os.path.basename(filepath):
                filepath = bpy.path.ensure_ext(
                    os.path.splitext(filepath)[0],
                    self.filename_ext
                    if check_extension
                    else "",
                )

                if filepath != self.filepath:
                    self.filepath = filepath
                    change_ext = True

        return change_ext

    def execute(self, context):
        result = engine.io.import_camera_data_csv(self.filepath)

        if result is None:
            self.report(type={'WARNING'}, message="Camera data import failed")
            return {'CANCELLED'}

        num_succeded, num_created, num_skipped = result

        report_text = f"Imported camera data for {num_succeded} cameras"

        if num_created:
            report_text += f", created {num_created} new cameras"

        if num_skipped:
            report_text += f", skipped {num_skipped} cameras"

        self.report(type={'INFO'}, message=report_text)

        return {'FINISHED'}


@orientation_helper(axis_forward='-Z', axis_up='Y')
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

    export_camera_data_as_type: EnumProperty(
        items=engine.io_properties.file_type_items,
        default=engine.io_properties.file_type_items[0][0],
        name="Export Cameras File Type",
        description="Export type for third-party software"
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
        return scene.cpp.has_initial_visible_camera_objects

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)

        num_cameras = len(list(context.scene.cpp.initial_visible_camera_objects))
        ui.common.draw_wrapped_text(
            context,
            col,
            f"Export {num_cameras} cameras as type:",
            icon_id=icons.get_icon_id("export")
        )

        col.prop(self, "export_camera_data_as_type", text="")

    @property
    def filename_ext(self):
        return engine.io_properties.get_file_extension_for_file_type(self.export_camera_data_as_type)

    def invoke(self, context, event):
        addon_preferences = context.preferences.addons[addon_pkg].preferences

        self.export_camera_data_as_type = addon_preferences.io_camera_data_as_type

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

    def check(self, context):
        change_ext = False

        check_extension = self.filename_ext

        if check_extension is not None:
            filepath = self.filepath
            if os.path.basename(filepath):
                filepath = bpy.path.ensure_ext(
                    os.path.splitext(filepath)[0],
                    self.filename_ext
                    if check_extension
                    else "",
                )

                if filepath != self.filepath:
                    self.filepath = filepath
                    change_ext = True

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
