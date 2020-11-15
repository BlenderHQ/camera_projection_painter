from .... import engine
from .... import __package__ as addon_pkg

import bpy
import bgl
from gpu_extras.batch import batch_for_shader


def get_camera_batches():
    # Camera and binded image batches
    vertices = (
        (0.0, 0.0, 0.0),
        (0.5, 0.5, -1.0),
        (0.5, -0.5, -1.0),
        (-0.5, -0.5, -1.0),
        (-0.5, 0.5, -1.0)
    )

    wire_indices = (
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (2, 3), (3, 4), (1, 4)
    )

    shader_camera = engine.getCachedShader("camera")
    shader_camera_image_preview = engine.getCachedShader("camera_image_preview")

    camera_wire_batch = batch_for_shader(
        shader_camera, 'LINES',
        {"pos": vertices},
        indices=wire_indices,
    )

    vertices = (
        (0.5, 0.5, -1.0),
        (0.5, -0.5, -1.0),
        (-0.5, -0.5, -1.0),
        (-0.5, 0.5, -1.0)
    )

    image_rect_uv = (
        (0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5),
    )

    image_rect_batch = batch_for_shader(
        shader_camera_image_preview, 'TRI_FAN',
        {"pos": vertices, "uv": image_rect_uv}
    )

    return camera_wire_batch, image_rect_batch


def get_axes_batch():
    vertices = (
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0)
    )

    vertex_colors = (
        (0.5, 0.5, 0.5, 0.0),
        (1.0, 0.0, 0.0, 0.6),
        (0.0, 1.0, 0.0, 0.6),
        (0.0, 0.0, 1.0, 0.6)
    )

    indices = ((0, 1), (0, 2), (0, 3))

    shader_axes = engine.getCachedShader("axes")

    batch_axes = batch_for_shader(
        shader_axes, 'LINES',
        {"pos": vertices, "color": vertex_colors},
        indices=indices,
    )

    return batch_axes


def draw_cameras(self, context):
    preferences = context.preferences.addons[addon_pkg].preferences
    scene = context.scene
    cameras_viewport_size = scene.cpp.cameras_viewport_size

    image_paint = scene.tool_settings.image_paint
    clone_image = image_paint.clone_image

    # Shaders
    shader_camera = engine.getCachedShader("camera")
    shader_camera_image_preview = engine.getCachedShader("camera_image_preview")
    shader_axes = engine.getCachedShader("axes")

    # Batches
    axes_batch = self.axes_batch
    camera_wire_batch = self.camera_batch
    image_rect_batch = self.image_rect_batch

    # OpenGL setup
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glDisable(bgl.GL_MULTISAMPLE)

    for camera_object in scene.cpp.initial_visible_camera_objects:
        camera = camera_object.data
        model_matrix = camera_object.matrix_world
        image = camera.cpp.image
        image_has_data = False
        line_width = preferences.camera_line_width

        if camera_object == scene.camera:
            if context.region_data.view_perspective == 'CAMERA':
                continue
            image = clone_image
            line_width = preferences.active_camera_line_width

        aspect_scale = 1.0, 1.0
        sensor_size = camera.lens / camera.sensor_width

        if camera.sensor_fit == 'HORIZONTAL':
            horizontal_fit = True
            sensor_size = camera.lens / camera.sensor_width
        elif camera.sensor_fit == 'VERTICAL':
            horizontal_fit = False
            sensor_size = camera.lens / camera.sensor_height

        if image and image.cpp.valid:
            image_has_data = image.has_data

            width, height = image.cpp.static_size

            if camera.sensor_fit == 'AUTO':
                horizontal_fit = width > height
                sensor_size = camera.lens / camera.sensor_width

            if horizontal_fit:
                aspect_scale = 1.0, height / width
            else:
                aspect_scale = width / height, 1.0

            if width > height:
                uv_aspect_scale = 1.0, height / width
            else:
                uv_aspect_scale = width / height, 1.0

            bindcode = image.cpp.preview_bindcode
            if bindcode:
                bgl.glActiveTexture(bgl.GL_TEXTURE0)
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, bindcode)

                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_BORDER)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_BORDER)

                shader_camera_image_preview.bind()

                shader_camera_image_preview.uniform_float("model_matrix", model_matrix)
                shader_camera_image_preview.uniform_float("aspect_scale", aspect_scale)
                shader_camera_image_preview.uniform_float("uv_aspect_scale", uv_aspect_scale)
                shader_camera_image_preview.uniform_float("sensor_size", sensor_size)
                shader_camera_image_preview.uniform_float("cameras_viewport_size", cameras_viewport_size)
                shader_camera_image_preview.uniform_float("image_space_color", preferences.image_space_color)
                shader_camera_image_preview.uniform_int("image", 0)

                camera.cpp.set_shader_calibration(shader_camera_image_preview)

                image_rect_batch.draw(shader_camera_image_preview)

        bgl.glLineWidth(line_width)

        shader_camera.bind()
        if image_has_data:
            wire_color = preferences.camera_color_loaded_data
        else:
            wire_color = preferences.camera_color
        if camera_object == scene.camera:
            wire_color = preferences.camera_color_highlight

        shader_camera.uniform_float("model_matrix", model_matrix)
        shader_camera.uniform_float("aspect_scale", aspect_scale)
        shader_camera.uniform_float("sensor_size", sensor_size)
        shader_camera.uniform_float("cameras_viewport_size", cameras_viewport_size)

        shader_camera.uniform_float("wire_color", wire_color)

        camera_wire_batch.draw(shader_camera)

        # Display the axes of the camera object
        if scene.cpp.camera_axes_size:
            camera_axes_size = scene.cpp.camera_axes_size

            bgl.glLineWidth(2.0)
            shader_axes.bind()
            shader_axes.uniform_float("modelMatrix", model_matrix)
            shader_axes.uniform_float("camera_axes_size", camera_axes_size)
            axes_batch.draw(shader_axes)

    # OpenGL restore defaults
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_MULTISAMPLE)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
    bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glLineWidth(1.0)
