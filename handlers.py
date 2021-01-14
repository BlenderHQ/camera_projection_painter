from . import engine
from . import operators
from . import poll

if "bpy" in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(poll)

import bpy
from bpy.app.handlers import persistent


@persistent
def render_pre_handler(scene=None):
    wm = bpy.context.window_manager
    if wm.cpp.running:
        wm.cpp.suspended = True


@persistent
def render_post_handler(scene=None):
    wm = bpy.context.window_manager
    if wm.cpp.running:
        wm.cpp.suspended = False


@persistent
def load_pre_handler(scene=None):
    for op in operators.basis.modal_ops:
        if hasattr(op, "cancel"):
            op.cancel(bpy.context)


@persistent
def load_post_handler(scene=None):
    context = bpy.context

    # Start listener at Blender / new file opening to check for main operator
    # context requirements.
    wm = bpy.context.window_manager

    wm.cpp.running = False
    wm.cpp.suspended = False
    bpy.ops.cpp.listener('INVOKE_DEFAULT')

    # Set internal `engine` module variable at Blender / new file opening
    # to enable / disable debig info in console.
    addon_preferences = bpy.context.preferences.addons[__package__].preferences
    engine.intern.set_debug_info(addon_preferences.debug_info)


@persistent
def save_pre_handler(scene=None):
    wm = bpy.context.window_manager

    if wm.cpp.running:
        wm.cpp.suspended = True

        for ob in bpy.context.scene.cpp.camera_objects:
            ob.hide_set(not ob.initial_visible)


@persistent
def save_post_handler(scene=None):
    if poll.full_poll(bpy.context):
        wm = bpy.context.window_manager
        wm.cpp.suspended = False

        for ob in bpy.context.scene.cpp.camera_objects:
            ob.hide_set(True)


# @persistent
# def depsgraph_update_pre_handler(scene=None):
#     # Remove missing images from the list of the camera palette
#     for camera_object in scene.cpp.camera_objects:
#         camera = camera_object.data
#         for item_index, item in enumerate(camera.cpp_bind_history):
#             if not item.image:
#                 camera.cpp_bind_history.remove(item_index)


_handlers = (
    (bpy.app.handlers.render_pre, render_pre_handler),
    (bpy.app.handlers.render_post, render_post_handler),
    (bpy.app.handlers.load_pre, load_pre_handler),
    (bpy.app.handlers.load_post, load_post_handler),
    (bpy.app.handlers.save_pre, save_pre_handler),
    (bpy.app.handlers.save_post, save_post_handler),
    #(bpy.app.handlers.depsgraph_update_pre, depsgraph_update_pre_handler)
)


def register():
    for handle, func in _handlers:
        handle.append(func)


def unregister():
    for handle, func in _handlers:
        if func in handle:
            handle.remove(func)
