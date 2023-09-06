from __future__ import annotations
if'bpy'in locals():from importlib import reload;reload(icons);reload(camera);reload(image);reload(intern);reload(ob);reload(pref);reload(scene);reload(wm)
else:from..import icons,register_class;from.import camera;from.import image;from.import intern;from.import ob;from.import pref;from.import scene;from.import wm
import bpy
from bpy.props import PointerProperty
__all__='camera','image','intern','ob','pref','scene','wm','register','unregister'
def register():register_class(pref.Preferences);ObjectProps=ob.create_props_ob();register_class(ObjectProps);bpy.types.Object.cpp=PointerProperty(type=ObjectProps);CameraProps=camera.create_props_camera();register_class(CameraProps);bpy.types.Camera.cpp=PointerProperty(type=CameraProps);register_class(image.ImageProps);bpy.types.Image.cpp=PointerProperty(type=image.ImageProps);register_class(scene.SceneProps);bpy.types.Scene.cpp=PointerProperty(type=scene.SceneProps);register_class(wm.WMProps);bpy.types.WindowManager.cpp=PointerProperty(type=wm.WMProps)
def unregister():del bpy.types.Camera.cpp;del bpy.types.Image.cpp;del bpy.types.Object.cpp;del bpy.types.Scene.cpp;del bpy.types.WindowManager.cpp