from . import camera
from . import scene
from . import image
from . import node
from . import wm

from .. import engine

if "bpy" in locals():
    import importlib
    importlib.reload(camera)
    importlib.reload(scene)
    importlib.reload(image)
    importlib.reload(node)
    importlib.reload(wm)

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
]

_cls_register, _cls_unregister = bpy.utils.register_classes_factory(_classes)


_engine_properties_items = (
    (Camera, camera.CameraProperties),
    (Scene, scene.SceneProperties),
    (Image, image.ImageProperties),
    (WindowManager, wm.WindowManagerProperties),
)


def register():
    _cls_register()

    module_attr_name = engine.module_attr_name()
    for cls, pointer_type in _engine_properties_items:
        if not hasattr(cls, module_attr_name):
            setattr(cls, module_attr_name, PointerProperty(type=pointer_type))

    WindowManager.cpp_progress = CollectionProperty(type=wm.ProgressPropertyItem)
    ShaderNodeTree.active_texnode_index = node.active_texnode_index
    Object.initial_visible = BoolProperty(name="Used", default=True)
    Camera.cpp_bind_history = CollectionProperty(type=camera.BindImageHistoryItem)


def unregister():
    _cls_unregister()

    module_attr_name = engine.module_attr_name()
    for cls, _ in _engine_properties_items:
        if hasattr(cls, module_attr_name):
            delattr(cls, module_attr_name)

    del Camera.cpp_bind_history
    del WindowManager.cpp_progress
    del ShaderNodeTree.active_texnode_index
    del Object.initial_visible
