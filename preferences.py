from . import engine
from .engine import icons
from .engine.io_properties import camera_data_file_type_enumerator_helper

from . import ui
from . import keymap
from . import sys_check
from . import operators

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    importlib.reload(keymap)
    importlib.reload(sys_check)
    importlib.reload(operators)

import bpy

from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    FloatProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
    IntVectorProperty
)

import os

URL_CAPTURING_REALITY = "https://www.capturingreality.com/"
URL_AGISOFT = "https://www.agisoft.com/"
URL_WORKFLOW_REQUEST = "https://github.com/BlenderHQ/camera_projection_painter/labels/enhancement"

doc_text = """
Camera Projection Painter addon is a community-driven project focused on photoscan texture refinements.
For additional technical information, support and addon tutorials you can visit links bellow.
"""


prop_tab_items = (
    (
        'WORKFLOW',
        "Workflow",
        "Workflow preferences tab",
        icons.get_icon_id("workflow"),
        0
    ),
    (
        'APPEARANCE',
        "Appearance",
        "Appearance preferences tab",
        icons.get_icon_id("appearance"),
        1
    ),
    (
        'KEYMAP',
        "Keymap",
        "Keymap preferences tab",
        icons.get_icon_id("keymap"),
        2),
    (
        'DOCS',
        "Documentation",
        "Offline documentation",
        icons.get_icon_id("documentation"),
        3
    ),
)

prop_outline_items = (
    (
        'OUTLINE_NONE',
        "None",
        "Outline not used",
        icons.get_icon_id("outline_none"),
        0
    ),
    (
        'OUTLINE_FILL',
        "Fill",
        "Single color outline",
        icons.get_icon_id("outline_fill"),
        1
    ),
    (
        'OUTLINE_CHECKER',
        "Checker",
        "Checker pattern outline",
        icons.get_icon_id("outline_checker"),
        2
    ),
    (
        'OUTLINE_LINES',
        "Lines",
        "Lines pattern outline",
        icons.get_icon_id("outline_lines"),
        3
    )
)

prop_preferred_workflow_items = (
    (
        'REALITY_CAPTURE',
        "Reality Capture \u00A9",
        "Use Capturing Reality \u00A9 Reality Capture \u00A9 oriented workflow",
        icons.get_icon_id("reality_capture"),
        1,
    ),
    (
        'METASHAPE',
        "Metashape \u00A9",
        "Use Agisoft \u00A9 Metashape \u00A9 oriented workflow",
        icons.get_icon_id("metashape"),
        2,
    ),

    # Always keep workflow request last
    (
        'REQUEST',
        "GitHub Request Workflow Support",
        "Open new enhancement labeled issue on GitHub",
        icons.get_icon_id("github"),
        100,
    )
)


@camera_data_file_type_enumerator_helper(ui_name="IO Cameras File Type", ui_description="Default IO file type for cameras data")
class PreferencesProperties:
    """Class contains addon preferences properties.
    """
    # -------------- Workflow -------------- #
    tab: EnumProperty(
        items=prop_tab_items,
        default=prop_tab_items[0][0]
    )

    # Preferred workflow /
    restore_preferred_workflow: EnumProperty(
        items=prop_preferred_workflow_items,
        default='REALITY_CAPTURE',
    )

    def preferred_workflow_update(self, context):
        if self.preferred_workflow == 'REQUEST':
            self.preferred_workflow = self.restore_preferred_workflow
            bpy.ops.wm.url_open(url=URL_WORKFLOW_REQUEST)
        self.restore_preferred_workflow = self.preferred_workflow

        # Update corresponding preferences defaults
        if self.preferred_workflow == 'REALITY_CAPTURE':
            self.ng_io_prop_as_type = 'REALITY_CAPTURE_IECP'

        elif self.preferred_workflow == 'METASHAPE':
            self.ng_io_prop_as_type = 'METASHAPE_PIDXYZOPKR'

    preferred_workflow: EnumProperty(
        items=prop_preferred_workflow_items,
        default='REALITY_CAPTURE',
        name="Preferred Software Workflow",
        description="Use specific algorithms for import camera "
                    "calibration and lens distortion parameters."
                    " \"Setup Context\" operator will try to simplify *.fbx "
                    "import stage",
        update=preferred_workflow_update
    )
    # \ Preferred workflow

    # UI Tags /
    # Handled in "handlers.py"
    show_defaults: BoolProperty()
    show_dev_extras: BoolProperty()
    show_viewport_inspection: BoolProperty()
    show_outline: BoolProperty()
    show_cameras: BoolProperty()
    show_camera_gizmo: BoolProperty()
    # \ UI Tags

    # Defaults /
    new_texture_size: IntVectorProperty(
        name="New Texture Size",
        size=2,
        default=(2048, 2048),
        min=512, soft_max=16384,
        description="Width and height for automatically generated textures"
    )

    def _debug_info_update(self, context):
        engine.intern.set_debug_info(self.debug_info)

    debug_info: BoolProperty(
        name="Print debug info",
        default=True,
        description="Print information about execution time into console",
        update=_debug_info_update
    )

    previews_size: IntProperty(
        name="Previews Size",
        default=256,
        min=128,
        max=512,
        description="Dimension of larger side of generated image previews. "
        "Do not affect already generated image previews."
    )

    icons_size: IntProperty(
        name="Icons Size",
        default=32,
        min=16,
        max=64,
        description="Dimension of larger side of generated image icons. "
        "Do not affect already generated image icons."
    )

    # \ Defaults

    # -------------- Viewport Inspection -------------- #

    # Outline /
    outline_type: EnumProperty(
        items=prop_outline_items,
        name="Type",
        default='OUTLINE_LINES',
        description="Outline to be drawn outside camera rectangle for preview")

    outline_width: FloatProperty(
        name="Width",
        default=0.25,
        soft_min=0.0,
        soft_max=5.0,
        subtype='FACTOR',
        description="Outline width")

    outline_scale: FloatProperty(
        name="Scale",
        default=50.0,
        soft_min=1.0,
        soft_max=100.0,
        subtype='FACTOR',
        description="Outline scale")

    outline_color: FloatVectorProperty(
        name="Color",
        default=[0.784363, 0.735347, 0.787399, 0.792857],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Outline color")
    # \ Outline

    # Highlight /
    image_space_color: FloatVectorProperty(
        name="Image Space Color",
        default=[0.013411, 0.013411, 0.013411, 0.950000],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Color of empty space arround undistorted image")

    normal_highlight_color: FloatVectorProperty(
        name="Normal Highlight",
        default=[0.088655, 0.208637, 0.527115, 0.770000],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Highlight stretched projection color")

    warning_color: FloatVectorProperty(
        name="Warning Color",
        default=[1.000000, 0.102228, 0.030697, 1.000000],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Highlight brush warning color")
    # \ Highlight

    # Camera /
    camera_line_width: FloatProperty(
        name="Line Width",
        default=0.5,
        soft_min=0.5,
        soft_max=5.0,
        subtype='PIXEL',
        description="Width of camera primitive wireframe")

    active_camera_line_width: FloatProperty(
        name="Active Line Width",
        default=1.5,
        soft_min=0.5,
        soft_max=5.0,
        subtype='PIXEL',
        description="Width of active camera primitive wireframe")

    camera_color: FloatVectorProperty(
        name="Color",
        default=[0.000963, 0.001284, 0.002579, 0.564286],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Camera color")

    camera_color_highlight: FloatVectorProperty(
        name="Color Highlight",
        default=[0.019613, 0.356583, 0.827556, 0.957143],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Camera color")

    camera_color_loaded_data: FloatVectorProperty(
        name="Color Loaded",
        default=[0.062277, 0.092429, 0.246195, 0.714286],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Camera image has data loaded into memory")
    # \ Camera

    # -------------- Gizmos -------------- #
    gizmo_color: FloatVectorProperty(
        name="Color",
        default=[0.199764, 0.650005, 0.363861, 0.770000],
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        description="Gizmo color")

    gizmo_radius: FloatProperty(
        name="Radius",
        default=0.1,
        soft_min=0.1,
        soft_max=1.0,
        subtype='DISTANCE',
        description="Gizmo radius")

    border_empty_space: IntProperty(
        name="Border Empty Space",
        default=25,
        soft_min=5,
        soft_max=100,
        subtype='PIXEL',
        description="Border Empty Space")


def at_open_preferences():
    context = bpy.context
    preferences = context.preferences.addons[__package__].preferences

    # UI Tags /
    preferences.tab = 'WORKFLOW'
    preferences.show_defaults = False
    preferences.show_dev_extras = False
    preferences.show_viewport_inspection = False
    preferences.show_outline = False
    preferences.show_cameras = False
    preferences.show_camera_gizmo = False
    # \ UI Tags


def draw_preferred_workflow(self, layout: bpy.types.UILayout) -> None:
    """Draw preferred workflow options in addon user preferences.

    Args:
        layout (bpy.types.UILayout): Current layout.
    """
    col = layout.column()
    col.scale_y = 1.5

    col.prop(self, "preferred_workflow", expand=True, emboss=True)

    if self.preferred_workflow == 'REALITY_CAPTURE':
        props = col.operator(
            "wm.url_open",
            text="Capturing Reality \u00A9 Website",
            icon_value=icons.get_icon_id("reality_capture")
        )
        props.url = URL_CAPTURING_REALITY

    elif self.preferred_workflow == 'METASHAPE':
        props = col.operator(
            "wm.url_open",
            text="Agisoft \u00A9 Website",
            icon_value=icons.get_icon_id("metashape")
        )
        props.url = URL_AGISOFT


def draw_dev(self, context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw developer extras in addon user preferences.

    Args:
        context (bpy.types.Context): Current context.
        layout (bpy.types.UILayout): Current layout.
    """
    preferences = context.preferences
    if not preferences.view.show_developer_ui:
        return

    if ui.common.submenu_active(self, layout, "Developer Extras", icons.get_icon_id("dev_extras"), "show_dev_extras"):
        dev_extras_text = "WARNING: Current section used for addon development.\n" \
            "Operators provided here may be unstable.\n" \
            "You can see this section because \"Interface > Display > Developer Extras\" option is enabled."

        box = layout.box()
        ui.common.draw_wrapped_text(context, box, text=dev_extras_text, icon_id=icons.get_icon_id("warning"))

        # Debug info
        box = layout.box()
        box.prop(self, "debug_info")

        # Reload
        box = layout.box()

        col = box.column()
        col.scale_y = 1.5
        col.operator(operator="cppdev.reload", icon='PLUGIN')

        col = box.column(align=False)
        keymap.draw_kmi(context, col, "Window", "cppdev.reload")

        # Dev only defaults
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Previews:")
        col.prop(self, "previews_size")
        col.prop(self, "icons_size")

        # Icon Viewer
        box = layout.box()
        box.label(text="Available cached icons:")

        col_flow = box.column_flow(columns=3, align=True)

        for item in icons.icon_names():
            col_flow.label(text=item, icon_value=icons.get_icon_id(item))

        box = layout.box()
        box.label(text="Available cached shaders:")
        col = box.column(align=True)
        for item in engine.shaders.shader_names():
            col.label(text=f"\"{item}\"")


def draw_keymap(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    """Draw keymap of addon in user interface.

    Args:
        context (bpy.types.Context): Current context.
        layout (bpy.types.UILayout): Current layout.
    """
    col = layout.column(align=False)

    keymap.draw_kmi(context, col, "Image Paint", operators.CPP_OT_image_paint.bl_idname)
    keymap.draw_kmi(context, col, "Image Paint", "view3d.view_center_pick")
    keymap.draw_kmi(context, col, "Image Paint", operators.CPP_OT_enable_all_cameras.bl_idname)


class CameraProjectionPainterPreferences(bpy.types.AddonPreferences, PreferencesProperties):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        wm = context.window_manager

        if not sys_check.draw_check_supported(layout):
            return

        if not hasattr(wm, "cpp"):
            col = layout.column()
            col.label(text="Please, reload Blender or open any file to begin.",
                      icon_value=icons.get_icon_id("info"))
            return

        # Tab
        col = layout.column(align=True)
        row = col.row()
        row.use_property_split = False
        row.prop_tabs_enum(self, "tab")

        box = col.box()

        # WORKFLOW
        if self.tab == 'WORKFLOW':
            draw_preferred_workflow(self, box)

            if ui.common.submenu_active(
                    self, box, "Defaults",
                    icons.get_icon_id("defaults"), "show_defaults"):
                col = box.column(align=False)

                col.prop(self, "ng_io_prop_as_type")
                col.prop(self, "new_texture_size")

            draw_dev(self, context, box)

        # APPEARANCE
        elif self.tab == 'APPEARANCE':
            # Viewport
            if ui.common.submenu_active(
                    self, box, "Viewport Inspection",
                    icons.get_icon_id("inspection"),
                    "show_viewport_inspection"):
                col = box.column()
                col.prop(self, "normal_highlight_color")
                col.prop(self, "warning_color")

            # Outline
            outline_icon_value = 0
            for n in prop_outline_items:
                if self.outline_type == n[0]:
                    outline_icon_value = n[3]

            if ui.common.submenu_active(
                    self, box, "Outline",
                    outline_icon_value, "show_outline"):
                col = box.column()
                row = col.row()
                row.prop(self, "outline_type", expand=True, emboss=True)

                if self.outline_type != 'OUTLINE_NONE':
                    col.prop(self, "outline_width")
                    col.prop(self, "outline_scale")
                    col.prop(self, "outline_color")
                    col.prop(self, "image_space_color")

            # Cameras
            if ui.common.submenu_active(
                    self, box, "Cameras", icons.get_icon_id("camera_draw"),
                    "show_cameras"):
                col = box.column()
                col.prop(self, "camera_line_width")
                col.prop(self, "active_camera_line_width")
                col.prop(self, "camera_color")
                col.prop(self, "camera_color_highlight")
                col.prop(self, "camera_color_loaded_data")

            # Camera Gizmo
            if ui.common.submenu_active(
                    self, box, "Camera Gizmo", icons.get_icon_id("cam_gizmo"), "show_camera_gizmo"):
                col = box.column()
                col.prop(self, "gizmo_radius")
                col.prop(self, "gizmo_color")

        # KEYMAP
        elif self.tab == 'KEYMAP':
            box.label(text="Keymap")
            draw_keymap(context, box)

        # DOCS
        elif self.tab == 'DOCS':
            ui.common.draw_wrapped_text(context, box, doc_text)

            # Support /
            p = box.operator(
                "wm.url_open",
                text="Patreon.com",
                icon_value=icons.get_icon_id("patreon"))
            p.url = "https://www.patreon.com/BlenderHQ"
            # \ Support


def register():
    bpy.utils.register_class(CameraProjectionPainterPreferences)
    at_open_preferences()


def unregister():
    bpy.utils.unregister_class(CameraProjectionPainterPreferences)
