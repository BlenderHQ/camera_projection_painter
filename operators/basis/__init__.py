from ... import engine
from ... import poll
from ... import extend_bpy_types

from . import draw

if "bpy" in locals():
    import importlib
    importlib.reload(draw)
    importlib.reload(poll)
    importlib.reload(extend_bpy_types)

    # Cancel running model operators at addon reload.
    for operator in modal_ops:
        try:
            operator.cancel(bpy.context)
        except AttributeError:
            print("AttributeError. Missing cancel method", operator)
        except ReferenceError:
            import traceback
            engine.intern.err_log(f"Camera Projection Painter: Reload module error:\n{traceback.format_exc()}\n")

import bpy

modal_ops = []
LISTEN_TIME_STEP = 1 / 4
TIME_STEP = 1 / 60


class PropertyTracker(object):
    """
    Utility class to detect value changes between calls.
    """
    __slots__ = ("value",)

    def __init__(self, value=None):
        self.value = value

    def __call__(self, value=None):
        if self.value != value:
            self.value = value
            return True
        return False


class CPP_OT_listener(bpy.types.Operator):
    """
    Listener operator. Running when
    `CPP_OT_camera_projection_painter` not running and not `poll.full_poll(context)`
    """
    bl_idname = "cpp.listener"
    bl_label = "Listener"
    bl_options = {'INTERNAL'}

    __slots__ = ("timer", )

    def invoke(self, context, _event):
        # Handle module reloading situation
        if self not in modal_ops:
            modal_ops.append(self)
        else:
            engine.intern.err_log("CPP_OT_listener: invoke cancelled (already running).\n")
            return {'CANCELLED'}

        wm = context.window_manager
        self.timer = wm.event_timer_add(time_step=LISTEN_TIME_STEP, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Handle module reloading situation
        if self in modal_ops:
            modal_ops.remove(self)

        # Remove `LISTEN_TIME_STEP` timer
        context.window_manager.event_timer_remove(self.timer)

    def modal(self, context, event):
        wm = context.window_manager

        # Stop modal execution if `CPP_OT_camera_projection_painter` invoked
        if wm.cpp.running:
            self.cancel(context)
            return {'FINISHED'}

        # Detect context to start `CPP_OT_camera_projection_painter`
        if event.type == 'TIMER' and (not wm.cpp.running) and (poll.full_poll(context)):
            wm.cpp.running = True
            wm.cpp.suspended = False
            bpy.ops.cpp.camera_projection_painter('INVOKE_DEFAULT')

        return {'PASS_THROUGH'}


class CPP_OT_camera_projection_painter(bpy.types.Operator):
    """
    Main modal operator.
    """
    bl_idname = "cpp.camera_projection_painter"
    bl_label = "Camera Projection Painter"
    bl_options = {'INTERNAL'}

    __slots__ = (
        "environment",
        "timer",
        "suspended",
        "suspended_mouse",
        "paint_time",
        "paint_step",

        "draw_handler",
        "draw_handler_cameras",
        "mesh_batch",
        "axes_batch",
        "camera_batch",
        "image_rect_batch",
        "brush_texture_bindcode",

        "check_data_updated",
        "data_updated",
        "check_brush_curve_updated",
    )

    def set_properties_defaults(self):
        """
        Set default values at startup and after exit available context
        """
        self.environment = None

        self.timer = None
        self.suspended = False
        self.suspended_mouse = False
        self.paint_time = 0.0
        self.paint_step = 0

        self.draw_handler = None
        self.draw_handler_cameras = None
        self.mesh_batch = None
        self.axes_batch = None
        self.camera_batch = None
        self.image_rect_batch = None
        self.brush_texture_bindcode = 0
        self.check_data_updated = PropertyTracker()
        self.data_updated = PropertyTracker()
        self.check_brush_curve_updated = PropertyTracker()

    @staticmethod
    def get_active_clone_layer(image_paint_ob):
        """
        Return clone UV layer named `poll.TEMP_DATA_NAME`.
        If layer do not exist, create a new one clone layer.
        """
        uv_layers = image_paint_ob.data.uv_layers
        if poll.TEMP_DATA_NAME not in uv_layers:
            uv_layer = uv_layers.new(name=poll.TEMP_DATA_NAME, do_init=False)
            uv_layer.active = False
            uv_layer.active_clone = True

        assert poll.TEMP_DATA_NAME in uv_layers
        uv_layer = uv_layers[poll.TEMP_DATA_NAME]

        return uv_layer

    @staticmethod
    def remove_uv_layer(ob):
        """
        Remove temporary UV layer from mesh data.
        """
        if ob and ob.type == 'MESH':
            uv_layers = ob.data.uv_layers
            if poll.TEMP_DATA_NAME in uv_layers:
                uv_layers.remove(uv_layers[poll.TEMP_DATA_NAME])

    def invoke(self, context, event):
        # Handle module reloading situation
        if self not in modal_ops:
            modal_ops.append(self)
        else:
            engine.intern.err_log("CPP_OT_camera_projection_painter: invoke cancelled (already running).\n")
            return {'CANCELLED'}

        self.set_properties_defaults()

        wm = context.window_manager
        self.timer = wm.event_timer_add(time_step=TIME_STEP, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # Handle module reloading situation
        if self in modal_ops:
            modal_ops.remove(self)

        # active_ob = context.active_object
        # wm = context.window_manager
        # if self.timer is not None:
        #     wm.event_timer_remove(self.timer)

        # extend_bpy_types.image.ImageCache.clear()

        # # draw.remove_draw_handlers(self)
        # self.remove_uv_layer(active_ob)

        # for ob in context.scene.cpp.camera_objects:
        #     ob.hide_set(not active_ob.initial_visible)

        wm.cpp.running = False
        wm.cpp.suspended = False

        #self.set_properties_defaults()

    def modal(self, context, event):
        wm = context.window_manager

        if not poll.full_poll(context):
            self.cancel(context)
            bpy.ops.cpp.listener('INVOKE_DEFAULT')
            return {'FINISHED'}

        if wm.cpp.suspended:
            return {'PASS_THROUGH'}

        # scene = context.scene
        # camera_ob = scene.camera
        # camera = camera_ob.data
        # image_paint = scene.tool_settings.image_paint

        # # Update images static size.
        # engine.images.update_image_seq_static_size(
        #     list(scene.cpp.used_images),
        #     skip_already_set=True
        # )

        # camera_image = camera.cpp.image
        # if not (camera_image and camera_image.cpp.valid):
        #     return {'PASS_THROUGH'}

        # # The only place where clone image should be set
        # if image_paint.clone_image != camera_image:
        #     image_paint.clone_image = camera_image

        # # Update viewports on mouse movements for dynamic brush preview
        # if event.type == 'MOUSEMOVE':
        #     for area in context.screen.areas:
        #         if area.type == 'VIEW_3D':
        #             area.tag_redraw()

        # # Handle hotkey-adjust brush radius/strength (standard is F | Shift + F)
        # km_default = wm.keyconfigs.get("blender").keymaps
        # km_paint = km_default["Image Paint"]

        # kmi = km_paint.keymap_items.match_event(event)
        # if kmi and getattr(kmi.properties, "data_path_primary", None) in (
        #     "tool_settings.image_paint.brush.size",
        #         "tool_settings.image_paint.brush.strength"):
        #     self.suspended_mouse = True

        # elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        #     self.suspended_mouse = False
        # elif event.value == 'RELEASE':
        #     self.suspended_mouse = False

        # if not self.suspended_mouse:
        #     wm.cpp.mouse_pos = event.mouse_x, event.mouse_y

        # # if (scene.cpp.use_projection_preview or (scene.cpp.use_warnings and scene.cpp.use_warning_action_draw)):
        #     #draw.mesh_preview.update_brush_texture_bindcode(self, context)

        # scene.cpp.update_initial_visible_cameras_sensors()

        # check_tuple = (
        #     # Base properties
        #     camera_ob,
        #     camera,
        #     camera_image,
        #     camera_image.cpp.static_size,

        #     # Enum properties
        #     camera.cpp.dm_reality_capture,
        #     camera.cpp.dm_metashape,
        #     camera.cpp.pano_type,

        #     # Camera extrinsics
        #     camera_ob.matrix_world,

        #     # Camera intrinsics
        #     camera.lens,
        #     camera.sensor_width,
        #     camera.sensor_height,

        #     camera.cpp.principal_x,
        #     camera.cpp.principal_y,
        #     camera.cpp.skew,
        #     camera.cpp.affinity,
        #     camera.cpp.pixel_aspect,

        #     camera.cpp.polynomial_k1,
        #     camera.cpp.polynomial_k2,
        #     camera.cpp.polynomial_k3,

        #     camera.cpp.division_k1,
        #     camera.cpp.division_k2,

        #     camera.cpp.nuke_k1,
        #     camera.cpp.nuke_k2,

        #     camera.cpp.brown_k1,
        #     camera.cpp.brown_k2,
        #     camera.cpp.brown_k3,
        #     camera.cpp.brown_k4,
        #     camera.cpp.brown_p1,
        #     camera.cpp.brown_p2,
        #     camera.cpp.brown_p3,
        #     camera.cpp.brown_p4,
        # )

        # if self.check_data_updated(check_tuple):
        #     width, height = camera_image.cpp.static_size
        #     scene.render.resolution_x = width
        #     scene.render.resolution_y = height

        # if event.type not in ('TIMER', 'TIMER_REPORT'):
        #     if self.data_updated(check_tuple):
        #         #result = self.environment.project_from_camera(camera_ob)
        #         # if result is False:
        #         #     self.report(type={'WARNING'},
        #         #                 message="Cannot set projector (see console for details)")

        return {'PASS_THROUGH'}
