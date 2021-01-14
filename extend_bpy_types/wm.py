import os
import importlib

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    IntVectorProperty,
    StringProperty,
    PointerProperty,
)


class WindowManagerProperties(PropertyGroup):
    """
    `context.window_manager.cpp`
    """
    running: BoolProperty(
        default=False,
        options={'HIDDEN'}
    )

    suspended: BoolProperty(
        default=False,
        options={'HIDDEN'}
    )

    mouse_pos: IntVectorProperty(
        size=2,
        default=(0, 0),
        options={'HIDDEN'}
    )

    current_selected_camera_ob: PointerProperty(
        type=bpy.types.Object,
        options={'HIDDEN'}
    )

    # Is `CPP_OT_refresh_image_preview` running modal
    is_preview_refresh_modal: BoolProperty(
        default=False,
        options={'HIDDEN'}
    )


class ProgressPropertyItem(PropertyGroup):
    """
    Item of `context.window_manager.cpp_progress`
    """
    id: IntProperty(options={'HIDDEN'})

    def _prop_update(self, context):
        # Dirty trick to refresh statusbar. Current API do not provide such possibility.
        # TODO(ivpe): Replace it to more apropriate method
        bpy.context.workspace.status_text_set(f"{self.val}")

    def add(self, value: float) -> None:
        """
        Increase progress value.

        Args:
            value (float): Value to add.
        """
        self.val += value
        # Clamp self.val in 0...100
        self.val = max(0, min(100, self.val))

    title: StringProperty(update=_prop_update)
    icon_id: IntProperty(update=_prop_update)

    def _value_get(self) -> float:
        return int(self.val)

    def _value_set(self, val) -> None:
        pass

    val: FloatProperty(
        options={'HIDDEN'},
        update=_prop_update
    )

    value: IntProperty(
        name="Progress",
        default=0, min=0, max=100,
        subtype='PERCENTAGE',
        options={'HIDDEN'},
        get=_value_get,
        set=_value_set
    )
