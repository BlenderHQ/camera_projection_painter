from __future__ import annotations
_A='import'
from..import constants
from..import icons
from bpy.types import PropertyGroup
from bpy.props import BoolProperty,EnumProperty
__all__='WMProps',
class WMProps(PropertyGroup):setup_context_stage:EnumProperty(items=((constants.SetupStage.PASS_THROUGH.name,'Pass-Through','',0,constants.SetupStage.PASS_THROUGH.value),(constants.SetupStage.INVOKED.name,'Invoked','',0,constants.SetupStage.INVOKED.value),(constants.SetupStage.PRE_CLEANUP.name,'Pre-Cleanup','',icons.get_id('cleanup'),constants.SetupStage.PRE_CLEANUP.value),(constants.SetupStage.IMPORT_SCENE.name,'Import Scene','',icons.get_id(_A),constants.SetupStage.IMPORT_SCENE.value),(constants.SetupStage.CHECK_CANVAS.name,'Check Canvas','',icons.get_id('image'),constants.SetupStage.CHECK_CANVAS.value),(constants.SetupStage.CHECK_CAMERAS.name,'Check Cameras','',icons.get_id(_A),constants.SetupStage.CHECK_CAMERAS.value),(constants.SetupStage.CHECK_IMAGES.name,'Check Images','',icons.get_id('bind'),constants.SetupStage.CHECK_IMAGES.value),(constants.SetupStage.CHECK_TOOL.name,'Check Tool','',0,constants.SetupStage.CHECK_TOOL.value)),default=constants.SetupStage.PASS_THROUGH.name);apply_udim_materials_fix:BoolProperty(default=True,options={'HIDDEN'},name='Apply UDIM Materials Fix',description='The standard import imports UDIM images as multiple materials and multiple images')