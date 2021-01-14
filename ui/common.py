from bl_ui import space_statusbar
from .. import extend_bpy_types

if "bpy" in locals():
    importlib.reload(space_statusbar)
    bpy.types.STATUSBAR_HT_header.draw = space_statusbar.STATUSBAR_HT_header.draw

import bpy
import blf

import textwrap
import importlib
from collections.abc import Iterable


def get_camera_object(context: bpy.types.Context):
    """`bpy.types.Object` of 'CAMERA' type that currently contextual for UI or `None` if missing.
    In object mode it will be active object, in other modes - scene active camera.

    Args:
        context (bpy.types.Context): Current context.

    Returns:
        `bpy.types.Object` or `None`
    """
    active_ob = context.active_object
    if active_ob and context.mode == 'OBJECT' and active_ob.type == 'CAMERA':
        return active_ob

    camera_ob = context.scene.camera
    if camera_ob and camera_ob.type == 'CAMERA':
        return camera_ob


def get_system_dpi(context: bpy.types.Context) -> float:
    """User preferences system dpi * pixel size * ui scale.

    Args:
        context (bpy.types.Context): Current context.

    Returns:
        float: System dpi.
    """
    preferences = context.preferences
    system = preferences.system
    dpi = system.dpi * system.pixel_size * preferences.view.ui_scale
    return dpi


def get_icon_wrap_scale(context: bpy.types.Context) -> float:
    """Scale parameters of icons to be placed in one line.

    Args:
        context (bpy.types.Context): Current context.

    Returns:
        float: Scale.
    """
    return (context.region.width / get_system_dpi(context) / bpy.app.render_icon_size) * 110  # scale 1.0 = 12 px width


def draw_wrapped_text(context: bpy.types.Context, layout: bpy.types.UILayout, text: str, icon_id=0):
    """Draw UI text (labels) wrapped by width of active UI region.

    Args:
        context (bpy.types.Context): Current context.
        layout (bpy.types.UILayout): Current layout.
        text (str): Text to be wrapped. In most cases, separated by `str.split("\n")` paragraph.
        icon_id (int): Optional icon for the first line.
    """

    def fwidth(_str) -> int:
        return int(blf.dimensions(0, _str)[0])

    col = layout.column(align=True)
    wrap_width = context.region.width - fwidth("W" * 5)

    space_width = fwidth(' ')

    is_icon_should_be_drawn = bool(icon_id)
    for line in text.split("\n"):
        line_width = fwidth(line)
        if is_icon_should_be_drawn:
            line_width += 16 / get_system_dpi(context)

        if line_width < wrap_width:
            if is_icon_should_be_drawn:
                col.label(text=line, icon_value=icon_id)
                is_icon_should_be_drawn = False
            else:
                col.label(text=line)
        else:
            line_split = line.split(' ')
            words_width = list([fwidth(_) for _ in line_split])
            num_words = len(line_split)

            substr = ""
            sum_width = 0.0

            if is_icon_should_be_drawn:
                sum_width += 16 / get_system_dpi(context)

            for i in range(num_words):
                word = line_split[i]
                next_word_width = 0.0

                if i != num_words - 1:
                    sum_width += space_width
                    word += ' '
                    next_word_width = words_width[i + 1]

                sum_width += words_width[i]

                substr += word

                if (sum_width + next_word_width >= wrap_width) or ((i == num_words - 1) and substr):

                    if is_icon_should_be_drawn:
                        col.label(text=substr, icon_value=icon_id)
                        is_icon_should_be_drawn = False
                    else:
                        col.label(text=substr)

                    substr = ""
                    sum_width = 0.0

        col.separator()


def submenu_active(self, layout: bpy.types.UILayout, label: str, icon_value: int, attr: str, index=0) -> bool:
    """Draw submenu. Used just as emulation of sub-panels.

    Args:
        layout (bpy.types.UILayout): Current layout
        label (str): Short text label
        icon_value (int): Additional icon id to be drawn in header
        attr (str): Attribute name from which to take subpanel open/closed state. Should be `bpy.props.BoolProperty`.
        index (int, optional): Used in case of attr is bpy.props.BoolVectorProperty. Defaults to 0.

    Returns:
        bool: True is subpanel is active, should be used as switch for main draw.
    """

    is_attr_iterable = isinstance(getattr(self, attr), Iterable)

    if is_attr_iterable:
        is_active = getattr(self, attr)[index]
    else:
        is_active = getattr(self, attr)
    tria_icon = 'DISCLOSURE_TRI_RIGHT'
    if is_active:
        tria_icon = 'DISCLOSURE_TRI_DOWN'
    row = layout.row(align=True)
    row.use_property_split = False

    prop_index = -1
    if is_attr_iterable:
        prop_index = index
    row.prop(self, attr, text="", icon=tria_icon,
             emboss=False, index=prop_index)
    row.label(text=label, icon_value=icon_value)

    return is_active


def _draw_progress_item(
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        item: extend_bpy_types.wm.ProgressPropertyItem) -> None:
    """Draw single progress item.

    Args:
        context (bpy.types.Context): Current context.
        layout (bpy.types.UILayout): Current layout.
        item (extend_bpy_types.wm.ProgressPropertyItem): Item data for display.
    """
    wm = context.window_manager
    row = layout.row(align=True)
    row.label(text=item.title, icon_value=item.icon_id)
    srow = row.row(align=True)
    srow.ui_units_x = 6
    srow.prop(item, "value", text="", emboss=True)


def draw_progress(self, context: bpy.types.Context) -> None:
    """Function to be drawn in statusbar. Use window manager

    Args:
        context (bpy.types.Context): Current context.
    """
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False
    wm = context.window_manager

    layout.separator_spacer()

    for item in wm.cpp_progress:
        _draw_progress_item(context, layout, item)

    layout.separator_spacer()
    layout.template_reports_banner()


def invoke_progress() -> extend_bpy_types.wm.ProgressPropertyItem:
    """Set custom draw method for statusbar.

    Returns:
        extend_bpy_types.wm.ProgressPropertyItem: New progress item.
    """
    wm = bpy.context.window_manager

    if not len(wm.cpp_progress):
        bpy.types.STATUSBAR_HT_header.draw = draw_progress

    item = wm.cpp_progress.add()
    item.id = len(wm.cpp_progress) - 1
    return item


def complete_progress(item: extend_bpy_types.wm.ProgressPropertyItem) -> None:
    """Restore original draw method for statusbar.

    Args:
        item (extend_bpy_types.wm.ProgressPropertyItem): Progress item which progress is completed.
    """
    wm = bpy.context.window_manager

    for i, _ in enumerate(wm.cpp_progress):
        if _.id == item.id:
            wm.cpp_progress.remove(i)

    if not len(wm.cpp_progress):
        # Restore statusbar
        importlib.reload(space_statusbar)
        bpy.types.STATUSBAR_HT_header.draw = space_statusbar.STATUSBAR_HT_header.draw

        bpy.context.workspace.status_text_set(None)
