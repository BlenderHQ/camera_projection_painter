# pep8 ignore=E402,W503

from . import preferences
from . import operators
from . import keymap
from . import gizmos
from . import extend_bpy_types
from . import ui
from . import handlers
from . import engine

sbver = preferences.SUPPORTED_BLENDER_VERSION

bl_info = {
    "name": "Camera Projection Painter",
    "author": "Vlad Kuzmin (ssh4), Ivan Perevala (ivpe)",
    "version": (0, 1, 7),
    "blender": (2, 83, 0),
    "description": "Expanding the capabilities of clone brush for working with photo scans",
    "location": "Tool settings > Camera Painter",
    "support": 'COMMUNITY',
    "category": "Paint",
    "doc_url": "https://github.com/BlenderHQ/camera_projection_painter",
}

if "bpy" in locals():
    unregister()

    import importlib
    importlib.reload(engine)
    importlib.reload(preferences)
    importlib.reload(operators)
    importlib.reload(keymap)
    importlib.reload(gizmos)
    importlib.reload(extend_bpy_types)
    importlib.reload(ui)
    importlib.reload(handlers)

    register_at_reload()
else:
    _module_registered = False

import bpy
from bpy.app.handlers import persistent


def register_at_reload():
    global _module_registered
    _module_registered = False
    register()
    load_post_register()
    handlers.load_post_handler()


_reg_modules = [
    extend_bpy_types,
    ui,
    operators,
    keymap,
    gizmos,
    handlers
]


@persistent
def load_post_register(dummy=None):
    global _module_registered
    if not _module_registered:
        _module_registered = True
        for module in _reg_modules:
            reg_func = getattr(module, "register")
            reg_func()


def register():
    import sys
    bpy.utils.register_class(preferences.CppPreferences)
    bver = bpy.app.version
    if sys.platform in preferences.SUPPORTED_PLATFORMS and (bver[0] >= sbver[0] and bver[1] >= sbver[1]):
        bpy.app.handlers.load_post.append(load_post_register)


def unregister():
    global _module_registered
    if _module_registered:
        for op in operators.basis.modal_ops:
            if hasattr(op, "cancel"):
                op.cancel(bpy.context)

        for module in reversed(_reg_modules):
            unreg_func = getattr(module, "unregister")
            unreg_func()

        bpy.utils.unregister_class(preferences.CppPreferences)

        _module_registered = False

    # handlers
    if load_post_register in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_register)
    handlers.unregister()
