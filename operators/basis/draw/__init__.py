from . import cameras
from . import mesh_preview

if "bpy" in locals():
    import importlib
    importlib.reload(cameras)
    importlib.reload(mesh_preview)

import bpy

# Class methods for controlling rendering in a viewport


def add_draw_handlers(self, context):
    args = (self, context)
    callback = mesh_preview.draw_projection_preview
    self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        callback, args, 'WINDOW', 'POST_VIEW')
    callback = cameras.draw_cameras
    self.draw_handler_cameras = bpy.types.SpaceView3D.draw_handler_add(
        callback, args, 'WINDOW', 'POST_VIEW')


def remove_draw_handlers(self):
    if self.draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
    if self.draw_handler_cameras:
        bpy.types.SpaceView3D.draw_handler_remove(
            self.draw_handler_cameras, 'WINDOW')
