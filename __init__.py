#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

#  The Original Code is Copyright (C) 2001-2002 by NaN Holding BV.
#  All rights reserved.

# pep8 ignore=E402,W503

from . import engine
from . import sys_check
from . import preferences
from . import operators
from . import keymap
from . import gizmos
from . import extend_bpy_types
from . import ui
from . import handlers

bl_info = {
    "name": "Camera Projection Painter",
    "author": "Vlad Kuzmin (ssh4), Ivan Perevala (ivpe)",
    "version": (0, 1, 7),
    "blender": (2, 90, 0),
    "description": "Expanding the capabilities of clone brush for working with photo scans",
    "location": "Tool settings > Camera Painter",
    "support": 'COMMUNITY',
    "category": "Paint",
    "doc_url": "https://github.com/BlenderHQ/camera_projection_painter",
}

if "bpy" in locals():
    unregister()

    import importlib
    # Always keep reload order
    importlib.reload(engine)
    importlib.reload(sys_check)
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

    import atexit
    atexit.register(engine.icons.unregister_icons)


import bpy
from bpy.app.handlers import persistent


sys_check.SUPPORTED_BLENDER_VERSION = bl_info["blender"]


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
    preferences.register()
    if sys_check.check_sys_platform() and sys_check.check_blender_version():
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

        preferences.unregister()

        _module_registered = False

    # Handlers
    if load_post_register in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_register)
    handlers.unregister()
