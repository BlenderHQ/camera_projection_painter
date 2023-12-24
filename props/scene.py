from __future__ import annotations
_H='MILLIMETERS'
_G='HIDDEN'
_F='highlight_border_facing'
_E='COLOR'
_D=1.
_C=.0
_B='SKIP_SAVE'
_A='SceneProps'
from..import Reports
from..import constants
from..import icons
from bpy.types import PropertyGroup
from bpy.props import BoolProperty,EnumProperty,FloatProperty,FloatVectorProperty,IntProperty,StringProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;SceneProps=TypeVar(_A,bound=PropertyGroup)
__all__=_A,
class SceneProps(PropertyGroup):
	version:IntProperty(options={_G},update=Reports.update_log_setting_changed(identifier='version'));units:EnumProperty(items=((_H,'Millimeters','Camera parameters in millimeters',icons.get_id('unit_mm'),1),('PIXELS','Pixels','Camera parameters relative to image sizes in pixels',icons.get_id('unit_px'),2)),default=_H,options={_B},translation_context=_A,update=Reports.update_log_setting_changed(identifier='units'),name='Unit',description='Display units of camera parameters');source_dir:StringProperty(subtype='DIR_PATH',options={_G},update=Reports.update_log_setting_changed(identifier='source_dir'),name='Source Directory');highlight_orientation:BoolProperty(default=False,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_orientation'),translation_context=_A,name='Highlight Cameras Orientation',description='Use a different color for cameras whose images have landscape (including square) and portrait orientation');highlight_orientation_landscape_color:FloatVectorProperty(min=_C,max=_D,size=3,default=(_D,.036889,.0865),subtype=_E,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_orientation_landscape_color'),translation_context=_A,name='Cameras Landscape Orientation Color',description='The color of the display of cameras in which the images have a landscape (including square) orientation');highlight_orientation_portrait_color:FloatVectorProperty(min=_C,max=_D,size=3,default=(.254152,.708376,_C),subtype=_E,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_orientation_portrait_color'),translation_context=_A,name='Cameras Portrait Orientation Color',description='The color of the display of cameras in which the images have a portrait orientation');highlight_border:BoolProperty(default=True,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_border'),translation_context=_A,name='Highlight Projected Border',description='Whether to highlight the borders of the frame of the projected image on the object');highlight_border_color_0:FloatVectorProperty(min=_C,max=_D,size=4,default=(.212229,.98225,.991102,.55),subtype=_E,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_border_color_0'),translation_context=_A,name='Highlight Projected Border First Color',description='The first color that will be used to highlight the parts of the object that are outside of camera frustum');highlight_border_color_1:FloatVectorProperty(min=_C,max=_D,size=4,default=(.002731,.274677,.783538,.55),subtype=_E,options={_B},update=Reports.update_log_setting_changed(identifier='highlight_border_color_1'),translation_context=_A,name='Highlight Projected Border Second Color',description='The second color that will be used to highlight the parts of the object that are outside of camera frustum');highlight_border_type:EnumProperty(items=((constants.BorderType.FILL.name,'Fill Color','Single color outline',icons.get_id('outline_fill'),constants.BorderType.FILL.value),(constants.BorderType.CHECKER.name,'Checker','Checker pattern outline',icons.get_id('outline_checker'),constants.BorderType.CHECKER.value),(constants.BorderType.LINES.name,'Lines','Lines pattern outline',icons.get_id('outline_lines'),constants.BorderType.LINES.value)),options={_B},default='LINES',update=Reports.update_log_setting_changed(identifier='highlight_border_type'),translation_context=_A,name='Highlight Projected Border Type',description='The fill type of the highlighted area')
	def _get_highlight_border_facing(self):return self.get(_F,constants.Facing.FRONT|constants.Facing.BACK)
	def _set_highlight_border_facing(self,value:int):
		if value:self[_F]=value
	highlight_border_facing:EnumProperty(items=((constants.Facing.FRONT.name,'Front','Show the front of polygons',icons.get_id('facing_front'),constants.Facing.FRONT.value),(constants.Facing.BACK.name,'Back','Show the back of polygons',icons.get_id('facing_back'),constants.Facing.BACK.value)),default={constants.Facing.FRONT.name,constants.Facing.BACK.name},options={'ENUM_FLAG',_B},get=_get_highlight_border_facing,set=_set_highlight_border_facing,update=Reports.update_log_setting_changed(identifier=_F),name='Highlight Projected Border Facing',description='Which side of the polygons that are outside the frame of the projected image to display. Сan be useful for a scene where there is a closed space, for example a room or a street. At least one of the options should be selected');cameras_viewport_size:FloatProperty(default=_D,soft_min=.5,soft_max=5.,min=.1,step=.1,subtype='DISTANCE',options={_B},update=Reports.update_log_setting_changed(identifier='cameras_viewport_size'),translation_context=_A,name='Viewport Cameras Size',description='The size of the cameras in the viewport');current_image_alpha:FloatProperty(default=_C,soft_min=_C,soft_max=_D,step=1,subtype='FACTOR',options={_B},update=Reports.update_log_setting_changed(identifier='current_image_alpha'),translation_context=_A,name='Current Image Viewport Transparency',description='Transparency of the image when viewed from the camera')
def create_props_scene()->SceneProps:return SceneProps