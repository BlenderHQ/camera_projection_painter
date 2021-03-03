from . import camera
from . import scene
from . import image
from . import node
from . import wm
from . import ob

from .. import engine

if "bpy" in locals():
    import importlib
    importlib.reload(camera)
    importlib.reload(scene)
    importlib.reload(image)
    importlib.reload(node)
    importlib.reload(wm)
    importlib.reload(ob)

import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty,
    CollectionProperty
)
from bpy.types import (
    Camera,
    Object,
    Scene,
    ShaderNodeTree,
    Image,
    WindowManager
)


_classes = [
    wm.WindowManagerProperties,
    wm.ProgressPropertyItem,
    camera.BindImageHistoryItem,
    camera.CameraProperties,
    scene.SceneProperties,
    image.ImageProperties,
    ob.ObjectProperties,
]

_cls_register, _cls_unregister = bpy.utils.register_classes_factory(_classes)


_engine_properties_items = (
    (Camera, camera.CameraProperties),
    (Scene, scene.SceneProperties),
    (Image, image.ImageProperties),
    (WindowManager, wm.WindowManagerProperties),
    (Object, ob.ObjectProperties),
)


def register():
    _cls_register()

    for cls, pointer_type in _engine_properties_items:
        if not hasattr(cls, engine.MODULE_ATTR):
            setattr(cls, engine.MODULE_ATTR, PointerProperty(type=pointer_type))

    WindowManager.cpp_progress = CollectionProperty(type=wm.ProgressPropertyItem)
    ShaderNodeTree.active_texnode_index = node.active_texnode_index
    Camera.cpp_bind_history = CollectionProperty(type=camera.BindImageHistoryItem)


def unregister():
    _cls_unregister()

    for cls, _ in _engine_properties_items:
        if hasattr(cls, engine.MODULE_ATTR):
            delattr(cls, engine.MODULE_ATTR)

    del Camera.cpp_bind_history
    del WindowManager.cpp_progress
    del ShaderNodeTree.active_texnode_index
