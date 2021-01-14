import bpy
from .. import __file__ as addon_file
from .. import __package__ as addon_pkg

import importlib
import os
import sys


class CPPDEV_OT_reload(bpy.types.Operator):
    bl_idname = "cppdev.reload"
    bl_label = "Reload Addon"
    bl_description = "This operation may be unstable. Please, save your data before running."
    bl_options = {'INTERNAL'}

    __slots__ = ()

    @classmethod
    def poll(cls, context):
        preferences = context.preferences
        return preferences.view.show_developer_ui

    # NOTE(ivpe): uncomment this method if required.
    #
    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_confirm(self, event)

    def execute(self, context):
        try:
            addon_dir = os.path.dirname(addon_file)
            if addon_dir not in sys.path:
                sys.path.append(addon_dir)

            addon = __import__(addon_pkg)
            importlib.reload(addon)
        except ImportError:
            self.report(
                type={'WARNING'},
                message="Reload addon failed, please, restart Blender"
            )
            return {'CANCELLED'}

        self.report(
            type={'INFO'},
            message="%s package reloaded successful, modules re-registered" % addon_pkg
        )
        return {'FINISHED'}
