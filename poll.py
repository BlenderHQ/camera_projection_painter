import bpy

TEMP_DATA_NAME = "cpp_data"


def check_uv_layers(ob: bpy.types.Object) -> bool:
    """
    Positive if there is at least one layer and TEMP_DATA_NAME layer is not active.
    """
    if ob and ob.type == 'MESH':
        uv_layers = ob.data.uv_layers
        uv_layers_count = len(uv_layers)

        if TEMP_DATA_NAME in uv_layers:
            uv_layers_count -= 1

        if uv_layers_count and uv_layers.active.name != TEMP_DATA_NAME:
            return True

    return False


def tool_setup_poll(context: bpy.types.Context) -> bool:
    """
    The conditions under which the gizmo is available appears under the scene settings panel in the toolbar.
    """
    tool = context.workspace.tools.from_space_view3d_mode(
        context.mode, create=False)

    if not tool:
        return False

    if tool.idname != "builtin_brush.Clone":
        return False

    scene = context.scene
    image_paint = scene.tool_settings.image_paint

    if image_paint.mode != 'IMAGE':
        return False

    if not image_paint.use_clone_layer:
        return False

    if not check_uv_layers(context.image_paint_object):
        return False

    return True


def full_poll(context: bpy.types.Context) -> bool:
    """
    Conditions under which the start of the main operator.
    """
    if not tool_setup_poll(context):
        return False

    scene = context.scene
    image_paint = scene.tool_settings.image_paint

    # Image paint canvas
    canvas = image_paint.canvas
    if canvas is None:
        return False
    elif canvas.gl_load():
        return False

    # Scene
    camera_ob = scene.camera
    if camera_ob is None:
        return False

    if not image_paint.detect_data():
        return False

    return True
