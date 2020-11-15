import numpy as np

from .... import engine
from .... import warnings
from .... import __package__ as addon_pkg

if "bpy" in locals():
    import importlib
    importlib.reload(warnings)

import bpy
import bgl
import gpu
from mathutils import Vector, Matrix


def f_clamp(value: float, min_value: float, max_value: float):
    return max(min(value, max_value), min_value)


def f_lerp(value0: float, value1: float, factor: float):
    return (value0 * (1.0 - factor)) + (value1 * factor)


def get_hovered_region_3d(context, mouse_position):
    mouse_x, mouse_y = mouse_position
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            header = next(r for r in area.regions if r.type == 'HEADER')
            tools = next(r for r in area.regions if r.type ==
                         'TOOLS')  # N-panel
            ui = next(r for r in area.regions if r.type == 'UI')  # T-panel

            min_x = area.x + tools.width
            max_x = area.x + area.width - ui.width
            min_y = area.y
            max_y = area.y + area.height

            if header.alignment == 'TOP':
                max_y -= header.height
            elif header.alignment == 'BOTTOM':
                min_y += header.height

            if min_x <= mouse_x < max_x and min_y <= mouse_y < max_y:
                if len(area.spaces.active.region_quadviews) == 0:
                    return area.spaces.active.region_3d
                else:
                    # Not sure quadview support required?
                    pass


def iter_curve_values(curve_mapping, steps: int):
    curve_mapping.initialize()
    curve = list(curve_mapping.curves)[0]

    clip_min_x = curve_mapping.clip_min_x
    clip_min_y = curve_mapping.clip_min_y
    clip_max_x = curve_mapping.clip_max_x
    clip_max_y = curve_mapping.clip_max_y

    for i in range(steps):
        fac = i / steps
        pos = f_lerp(clip_min_x, clip_max_x, fac)

        value = curve_mapping.evaluate(curve, pos)

        yield f_clamp(value, clip_min_y, clip_max_y)


def update_brush_texture_bindcode(self, context):
    scene = context.scene
    image_paint = scene.tool_settings.image_paint
    brush = image_paint.brush
    pixel_width = scene.tool_settings.unified_paint_settings.size

    # Check curve values for every 10% to check any updates. Its biased, but fast.
    check_steps = 10
    check_tuple = tuple((n for n in iter_curve_values(
        brush.curve, check_steps))) + (pixel_width,)

    if self.check_brush_curve_updated(check_tuple):
        pixels = [int(n * 255)
                  for n in iter_curve_values(brush.curve, pixel_width)]

        id_buff = bgl.Buffer(bgl.GL_INT, 1)
        bgl.glGenTextures(1, id_buff)

        bindcode = id_buff.to_list()[0]

        bgl.glBindTexture(bgl.GL_TEXTURE_2D, bindcode)
        image_buffer = bgl.Buffer(bgl.GL_INT, len(pixels), pixels)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER
                            | bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RED,
                         pixel_width, 1, 0, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, image_buffer)

        self.brush_texture_bindcode = bindcode


def get_object_batch(context, ob):
    """Returns object batch from evaluated depsgraph"""

    depsgraph = context.evaluated_depsgraph_get()

    # Get the modified version of the mesh from the depsgraph
    mesh = depsgraph.id_eval_get(ob).data
    mesh.calc_loop_triangles()

    vertices_count = len(mesh.vertices)
    loop_tris_count = len(mesh.loop_triangles)

    vertices_shape = (vertices_count, 3)
    loop_tris_shape = (loop_tris_count, 3)

    # Required attributes
    vertices_positions = np.empty(vertices_shape, dtype=np.float32)
    vertices_normals = np.empty(vertices_shape, dtype=np.float32)
    indices = np.empty(loop_tris_shape, dtype=np.int32)

    vertices_newshape = vertices_count * 3
    loop_tris_newshape = loop_tris_count * 3

    # 'foreach_get' is the fastest method
    mesh.vertices.foreach_get(
        "co", np.reshape(vertices_positions, vertices_newshape))
    mesh.vertices.foreach_get(
        "normal", np.reshape(vertices_normals, vertices_newshape))
    mesh.loop_triangles.foreach_get(
        "vertices", np.reshape(indices, loop_tris_newshape))

    # Batch generation
    buffer_type = 'TRIS'

    format_attributes = (
        ("pos", vertices_positions),
        ("normal", vertices_normals)
    )

    # Structure of a vertex buffer
    vert_format = gpu.types.GPUVertFormat()
    for format_attr in format_attributes:
        vert_format.attr_add(
            id=format_attr[0], comp_type='F32', len=3, fetch_mode='FLOAT')

    # Index buffer
    ibo = gpu.types.GPUIndexBuf(type=buffer_type, seq=indices)

    # Vertex buffer
    vbo = gpu.types.GPUVertBuf(len=vertices_count, format=vert_format)
    for attr_id, attr in format_attributes:
        vbo.attr_fill(id=attr_id, data=attr)

    # Batch
    batch = gpu.types.GPUBatch(type=buffer_type, buf=vbo, elem=ibo)

    return batch


def draw_projection_preview(self, context):
    wm = context.window_manager
    if wm.cpp.suspended:
        return

    # Base checks
    ob = context.image_paint_object
    if ob is None:
        return

    scene = context.scene
    image_paint = scene.tool_settings.image_paint
    if not(scene.cpp.use_projection_preview or (scene.cpp.use_warnings and scene.cpp.use_warning_action_draw)):
        return

    if not(scene.camera and scene.camera.type == 'CAMERA'):
        return
    camera = scene.camera.data

    image = image_paint.clone_image
    if not(image and image.cpp.valid and (not image.cpp.gl_load(context))):
        return

    batch = self.mesh_batch
    if batch is None:
        return

    preferences = context.preferences.addons[addon_pkg].preferences

    # openGL setup
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    bgl.glEnable(bgl.GL_DEPTH_TEST)

    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

    bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                        bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                        bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                        bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_BORDER)
    bgl.glTexParameteri(bgl.GL_TEXTURE_2D,
                        bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_BORDER)

    bgl.glActiveTexture(bgl.GL_TEXTURE1)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.brush_texture_bindcode)

    # Uniforms
    shader = engine.getCachedShader("mesh_preview")
    shader.bind()

    shader.uniform_float("model_matrix", ob.matrix_world)
    shader.uniform_float("proj_MVP", Matrix(self.environment.projector_MVP))

    # Images
    shader.uniform_int("image", 0)
    shader.uniform_int("image_brush", 1)

    # Switches
    is_warning = ((scene.cpp.use_warnings and scene.cpp.use_warning_action_draw)
                  and warnings.get_warning_status(context, wm.cpp.mouse_pos))
    shader.uniform_bool("is_warning", (is_warning,))

    is_active_view = context.area.spaces.active.region_3d == get_hovered_region_3d(
        context, wm.cpp.mouse_pos)
    shader.uniform_int("is_active_view", is_active_view)

    shader.uniform_bool("is_full_draw", (self.full_draw,))
    shader.uniform_bool("is_brush", (scene.cpp.use_projection_preview,))
    shader.uniform_bool("is_normal_highlight",
                        (scene.cpp.use_normal_highlight,))

    # Colors
    shader.uniform_float("image_space_color", preferences.image_space_color)
    shader.uniform_float("warning_color", preferences.warning_color)
    shader.uniform_float("normal_highlight_color",
                         preferences.normal_highlight_color)

    # Outline and Highlight
    outline_type = {'NO_OUTLINE': 0, 'FILL': 1,
                    'CHECKER': 2, 'LINES': 3}[preferences.outline_type]
    if outline_type:
        outline_color = preferences.outline_color
        shader.uniform_float("outline_color", outline_color)
        outline_scale = preferences.outline_scale
        shader.uniform_float("outline_scale", outline_scale)
        outline_width = preferences.outline_width * 0.1
        shader.uniform_float("outline_width", outline_width)
    shader.uniform_int("outline_type", outline_type)

    shader.uniform_float(
        "camera_forward", (scene.camera.matrix_world @ Vector([0.0, 0.0, -1.0]).normalized()))

    # Brush
    if is_active_view:
        mouse_pos = (wm.cpp.mouse_pos[0] - context.area.x,
                     wm.cpp.mouse_pos[1] - context.area.y)
        shader.uniform_float("mouse_pos", mouse_pos)
    shader.uniform_float(
        "brush_radius", scene.tool_settings.unified_paint_settings.size)
    shader.uniform_float("brush_strength", image_paint.brush.strength)

    camera.cpp.set_shader_calibration(shader)
    # Draw

    batch.draw(shader)
