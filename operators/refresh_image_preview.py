from .. import ui

from .. engine import icons
from .. import engine

from .. import __package__ as addon_pkg

if "bpy" in locals():
    import importlib
    importlib.reload(ui)

import bpy

FPS = 60
IMAGES_PER_STEP = 10

class CPP_OT_refresh_image_preview(bpy.types.Operator):
    """
    Operator for addon internal use only.
        If called with 'INVOKE_DEFAULT', will be updated `bpy.data.images`
    by portions equal `IMAGES_PER_STEP`.
        If called with 'EXEC_DEFAULT', will be updated `bpy.data.images`
    all at once.
    """
    bl_idname = "cpp.refresh_image_preview"
    bl_label = "Refresh Previews"
    bl_description = "Refresh Previews. Warning: May take a few seconds to finish"
    bl_options = {'INTERNAL'}

    skip_already_set: bpy.props.BoolProperty(default=False)

    __slots__ = (
        "timer",
        "progress",
        "icon_id_index",
        "index_start",
        "progress_step",
        "skip_tics_left"
    )

    def _update_progress_icon(self, context: bpy.types.Context) -> None:
        """Simulates animated icon, loops `self.icon_id_index` in 0 ... 2

        Args:
            context (bpy.types.Context): Current context.
        """
        self.icon_id_index += 1
        if self.icon_id_index > 2:
            self.icon_id_index = 0

        self.progress.icon_id = icons.get_icon_id(f"update_previews_{self.icon_id_index}")

    def _set_preview_size_to_preferences(self, context):
        """Set preview and icon size to preferences values.
        """
        preferences = context.preferences.addons[addon_pkg].preferences
        engine.images.set_preview_size(preferences.previews_size)
        engine.images.set_icon_size(preferences.icons_size)

    def invoke(self, context, event):
        num_images = len(bpy.data.images)
        if num_images == 0:
            return {'CANCELLED'}

        self.icon_id_index = 0
        self.index_start = 0

        self.progress_step = 100.0 * ((IMAGES_PER_STEP - 1) / num_images)

        wm = context.window_manager
        wm.cpp.is_preview_refresh_modal = True

        self.skip_tics_left = 0

        self.progress = ui.common.invoke_progress()

        self.progress.title = "Update Previews"
        self.progress.icon_id = icons.get_icon_id("update_previews_0")

        # Set window cursor
        context.window.cursor_set('WAIT')

        self._set_preview_size_to_preferences(context)

        # Register modal operator routine
        wm.modal_handler_add(self)
        self.timer = wm.event_timer_add(time_step=1 / FPS, window=context.window)
        return {'RUNNING_MODAL'}

    def _report_succeded(self):
        self.report(type={'INFO'}, message="Previews updated")

    def cancel(self, context):
        # Complete interaction with window manager
        wm = context.window_manager
        # Restore cursor
        context.window.cursor_set('DEFAULT')
        context.window.cursor_modal_restore()
        ui.common.complete_progress(self.progress)
        wm.event_timer_remove(self.timer)
        wm.cpp.is_preview_refresh_modal = False

    def modal(self, context, event):
        if self.index_start >= len(bpy.data.images) - 1:
            self.cancel(context)
            self._report_succeded()
            return {'FINISHED'}

        if self.skip_tics_left > 0:
            self.skip_tics_left -= 1
            return {'RUNNING_MODAL'}

        elif self.skip_tics_left == 0:
            self.skip_tics_left = 5

        index_end = max(0, min(len(bpy.data.images), self.index_start + IMAGES_PER_STEP))

        engine.images.update_image_seq_previews(
            bpy.data.images[self.index_start:index_end],
            engine.images.UpdatePreviewsFlag.SKIP_ALREADY_SET
        )

        self.index_start = index_end

        wm = context.window_manager
        self._update_progress_icon(context)
        self.progress.add(self.progress_step)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        self._set_preview_size_to_preferences(context)
        engine.images.update_image_seq_previews(bpy.data.images, engine.images.UpdatePreviewsFlag.SKIP_ALREADY_SET)
        self._report_succeded()
        return {'FINISHED'}
