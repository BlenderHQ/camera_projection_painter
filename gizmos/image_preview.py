from .. import engine
from .. import __package__ as addon_pkg
from .. import poll

if "bpy" in locals():  # In case of module reloading
    import importlib
    importlib.reload(poll)

import bpy
import gpu
import bgl
from mathutils import Vector
from mathutils.geometry import intersect_point_quad_2d
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader


GIZMO_SNAP_POINTS = [
    (0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (0.0, 1.0),
    (0.5, 1.0), (1.0, 1.0), (0.0, 0.5), (1.0, 0.5)
]


def f_lerp(value0: float, value1: float, factor: float):
    return (value0 * (1.0 - factor)) + (value1 * factor)


def f_clamp(value: float, min_value: float, max_value: float):
    return max(min(value, max_value), min_value)


def v_clamp(value: Vector):
    return Vector((f_clamp(value[n], 0.0, 1.0) for n in range(2)))


def get_curr_img_pos_from_context(context):
    scene = context.scene
    image_paint = context.scene.tool_settings.image_paint
    image = image_paint.clone_image

    if image and image.cpp.valid:
        preferences = context.preferences.addons[addon_pkg].preferences
        empty_space = preferences.border_empty_space

        area = context.area
        tools_width = [n for n in area.regions if n.type == 'TOOLS'][-1].width
        ui_width = [n for n in area.regions if n.type == 'UI'][-1].width

        areasx = area.width - ui_width - tools_width - empty_space
        areasy = area.height - empty_space

        w, h = image.cpp.static_size

        aspx = 1.0
        aspy = 1.0
        if w > h:
            aspy = h / w
        elif w < h:
            aspx = w / h

        gizmosx = aspx * scene.cpp.current_image_size
        gizmosy = aspy * scene.cpp.current_image_size

        possible = True
        if (gizmosx > areasx - empty_space) or (gizmosy > areasy - empty_space):
            possible = False

        rpx, rpy = scene.cpp.current_image_position
        gizmopx = f_lerp(empty_space, areasx - gizmosx, rpx) + tools_width
        gizmopy = f_lerp(empty_space, areasy - gizmosy, rpy)

        return Vector((gizmopx, gizmopy)), Vector([gizmosx, gizmosy]), possible


class CPP_GT_current_image_preview(bpy.types.Gizmo):
    bl_idname = "CPP_GT_current_image_preview"

    image_batch: gpu.types.GPUBatch
    pixel_pos: Vector
    pixel_size: Vector
    rel_offset: Vector
    initial_show_brush: bool

    __slots__ = (
        "image_batch",
        "pixel_pos",
        "pixel_size",
        "rel_offset",
        "initial_show_brush",
    )

    @staticmethod
    def _get_image_rel_pos(context, event):
        area = context.area
        return Vector([(event.mouse_x - area.x) / area.width, (event.mouse_y - area.y) / area.height])

    def setup(self):
        self.image_batch = batch_for_shader(
            engine.getCachedShader("current_image"), 'TRI_FAN',
            {"pos": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
             "uv": ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))})

    def draw(self, context):
        scene = context.scene
        camob = scene.camera
        preferences = context.preferences.addons[addon_pkg].preferences
        if camob and camob.type == 'CAMERA':
            camera = camob.data
            image = camera.cpp.image

            if image and image.cpp.valid:
                shader = engine.getCachedShader("current_image")
                if shader is None:
                    return
                
                batch = self.image_batch

                imapos = get_curr_img_pos_from_context(context)
                if imapos:
                    self.pixel_pos, self.pixel_size, possible = imapos

                    # If we look from the camera
                    rv3d = context.region_data
                    if rv3d.view_perspective == 'CAMERA':
                        view_frame = [camob.matrix_world @ v for v in camera.view_frame(scene=scene)]
                        p0 = view3d_utils.location_3d_to_region_2d(context.region, rv3d, coord=view_frame[2])
                        p1 = view3d_utils.location_3d_to_region_2d(context.region, rv3d, coord=view_frame[0])
                        pos = p0
                        size = p1.x - p0.x, p1.y - p0.y
                        possible = True
                    else:
                        pos = self.pixel_pos
                        size = self.pixel_size

                    if possible:
                        if image.cpp.gl_load(context):
                            raise Exception()

                        bgl.glEnable(bgl.GL_BLEND)
                        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
                        bgl.glDisable(bgl.GL_POLYGON_SMOOTH)

                        bgl.glActiveTexture(bgl.GL_TEXTURE0)
                        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
                        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_BORDER)
                        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_BORDER)

                        shader.bind()
                        shader.uniform_int("image", 0)
                        camera.cpp.set_shader_calibration(shader)
                        shader.uniform_float("pixel_pos", pos)
                        shader.uniform_float("pixel_size", size)

                        alpha = self.alpha_highlight if self.is_highlight else scene.cpp.current_image_alpha
                        shader.uniform_float("alpha", alpha)
                        shader.uniform_float("image_space_color", preferences.image_space_color)

                        batch.draw(shader)

                        bgl.glDisable(bgl.GL_BLEND)
                        bgl.glEnable(bgl.GL_POLYGON_SMOOTH)

    def test_select(self, context, location):
        rv3d = context.region_data

        if rv3d.view_perspective == 'CAMERA':
            return -1
        curr_img_pos = get_curr_img_pos_from_context(context)
        if not curr_img_pos:
            return -1
        possible = curr_img_pos[2]
        if not possible:
            return -1

        mouse_pos = Vector(location)
        mpr_pos = self.pixel_pos
        quad_p1 = mpr_pos
        quad_p2 = mpr_pos + Vector((0.0, self.pixel_size.y))
        quad_p3 = mpr_pos + self.pixel_size
        quad_p4 = mpr_pos + Vector((self.pixel_size.x, 0.0))
        res = intersect_point_quad_2d(
            mouse_pos, quad_p1, quad_p2, quad_p3, quad_p4)
        if res == -1:
            return 0
        return -1

    def invoke(self, context, event):
        wm = context.window_manager
        scene = context.scene
        image_paint = scene.tool_settings.image_paint

        self.initial_show_brush = bool(image_paint.show_brush)
        image_paint.show_brush = False

        rel_pos = self._get_image_rel_pos(context, event)
        self.rel_offset = Vector(scene.cpp.current_image_position) - rel_pos

        wm.cpp.suspended = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event, tweak):
        scene = context.scene
        rel_pos = self._get_image_rel_pos(context, event) + self.rel_offset

        if 'PRECISE' in tweak:
            pass
        elif 'SNAP' in tweak:
            rel_pos = Vector(
                (sorted(GIZMO_SNAP_POINTS, key=lambda dist: (Vector(dist) - rel_pos).length)[0]))

        scene.cpp.current_image_position = rel_pos

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        wm = context.window_manager
        wm.cpp.suspended = False
        image_paint = context.scene.tool_settings.image_paint
        image_paint.show_brush = self.initial_show_brush


class CPP_GGT_image_preview_gizmo_group(bpy.types.GizmoGroup):
    bl_idname = "CPP_GGT_image_preview_gizmo_group"
    bl_label = "Image Preview Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'PERSISTENT', 'SCALE'}

    mpr: bpy.types.Gizmo
    mpr_scale: bpy.types.Gizmo

    @classmethod
    def poll(cls, context):
        if not poll.full_poll(context):
            return False
        return context.scene.cpp.current_image_alpha

    def setup(self, context):
        mpr = self.gizmos.new(CPP_GT_current_image_preview.bl_idname)
        mpr.use_draw_scale = True
        mpr.alpha_highlight = 1.0
        mpr.use_draw_modal = True
        mpr.use_select_background = True
        mpr.use_grab_cursor = True

        self.mpr = mpr
