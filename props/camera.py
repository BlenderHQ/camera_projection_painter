from __future__ import annotations
_E='FACTOR'
_D='DISTANCE_CAMERA'
_C='VERTICAL'
_B='HIDDEN'
_A='CameraProps'
from..import constants
from..import register_class
from..lib import bhqdbl
import bpy
from bpy.types import Context,PropertyGroup
from bpy.props import CollectionProperty,EnumProperty,FloatProperty,FloatVectorProperty,IntProperty,PointerProperty
from mathutils import Vector
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;CameraProps=TypeVar(_A,bound=PropertyGroup);from.import Image,Camera;from.image import ImageProps
__all__='BindImageHistoryItem',_A,'create_props_camera'
class CameraProps(PropertyGroup):
	def _active_bind_index_update(self,_context:Context):
		item:BindImageHistoryItem=self.bind_history[self.active_bind_index]
		if item.image and item.image!=self.image:self.image=item.image
	active_bind_index:IntProperty(default=0,update=_active_bind_index_update,options={_B,'SKIP_SAVE'},translation_context=_A,name='Active',description='Active bind history index')
	def update_sensor_fit_from_image(self):
		cam:Camera=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:
				w,h=image_props.size
				if w>h:cam.sensor_fit='HORIZONTAL'
				else:cam.sensor_fit=_C
	def _image_update(self,_context:Context):
		if self.image:
			self.update_sensor_fit_from_image();bind_history_images=tuple(_.image for _ in self.bind_history)
			if self.image in bind_history_images:self.active_bind_index=bind_history_images.index(self.image)
			else:item:CameraProps.BindImageHistoryItem=self.bind_history.add();item.image=self.image;self.active_bind_index=len(self.bind_history)-1
	image:PointerProperty(type=bpy.types.Image,options=constants.PROPERTY.OPTIONS,update=_image_update,translation_context=_A,name='Image',description='Camera binded image. It will be used as a paint brush. Also, its size affects the distortion parameters in the pixel coordinate system (in which way - described in more detail for the corresponding parameters), and therefore - also the possibility of exporting to certain file formats')
	def _cb_get_lens(self)->float:cam:Camera=self.id_data;return cam.lens
	def _cb_set_lens(self,value:float):cam:Camera=self.id_data;cam.lens=value
	lens,_prop_lens=bhqdbl.double_property('lens',get=_cb_get_lens,set=_cb_set_lens,default=constants.CAMERA.LENS.DEFAULT,min=constants.CAMERA.LENS.MIN,soft_max=constants.CAMERA.LENS.SOFT_MAX,options=constants.PROPERTY.OPTIONS,precision=constants.IEEE754.FLT_DIG,subtype=_D,translation_context=_A,name='Millimeters Focal Length',description='Focal length of the camera in millimeters. The value is stored with double precision');s_lens:_prop_lens
	def _get_px_lens(self):
		cam=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:sensor_eval=self.sensor;return cam.lens*image_props.larger_side/sensor_eval
		return 0
	def _set_px_lens(self,value):
		cam:Camera=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:sensor_eval=self.sensor;cam.lens=value/image_props.larger_side*sensor_eval
	px_lens:FloatProperty(get=_get_px_lens,set=_set_px_lens,subtype='PIXEL',translation_context=_A,name='Pixels Focal Length',description='The focal length of the camera in pixels. Calculated by the formula:\n\n`Pixels Focal Lens = F * P / S`\n\nwhere `F` is the focal length in millimeters, `P` is the larger side of the image, `S` is the size of the camera sensor in millimeters')
	def _cb_get_sensor(self):
		cam:Camera=self.id_data;cam_props:CameraProps=cam.cpp
		if _C==cam.sensor_fit:return cam.sensor_height
		elif'AUTO'==cam.sensor_fit and cam_props.image:
			image:Image=cam_props.image;image_props:ImageProps=image.cpp;w,h=image_props.size
			if h>w:return cam.sensor_height
		return cam.sensor_width
	def _cb_set_sensor(self,value:float):
		cam:Camera=self.id_data;cam_props:CameraProps=cam.cpp
		if _C==cam.sensor_fit:cam.sensor_height=value;return
		elif'AUTO'==cam.sensor_fit and cam_props.image:
			image_props:ImageProps=cam_props.image.cpp;w,h=image_props.size
			if h>w:cam.sensor_height=value;return
		cam.sensor_width=value
	sensor,_prop_sensor=bhqdbl.double_property('sensor',get=_cb_get_sensor,set=_cb_set_sensor,precision=constants.IEEE754.FLT_DIG,min=constants.CAMERA.SENSOR.MIN,soft_max=constants.CAMERA.SENSOR.SOFT_MAX,translation_context=_A,name='Sensor',description='The size of the camera sensor in millimeters, taking into account the larger side of the attached image. This means that if the sensor fit option is set to horizontal - the width of the sensor will be used for calculations, for vertical fit type - height accordingly. These values can be set manually. But for when working with photogrammetric scenes, it is necessary to use the automatic type of sensor adjustment. In this case, if the image has a landscape orientation (or the sides are equal), the width of the sensor will be used, and in the case of a portrait - the height of the sensor. As you can see, there are opportunities for using non-standard workflows, but the main mode of operation is the automatic sensor type. Also note the camera-bound image, this is important for importing and exporting to some file formats. The value is stored with double precision');s_sensor:_prop_sensor;skew,_prop_skew=bhqdbl.double_property('skew',default=.0,soft_min=-1.,soft_max=1.,subtype=_E,translation_context=_A,name='Millimeters Skew',description='The horizontal skew of the image in millimeters relative to its center, excluding principal deviation. The value is stored with double precision');s_skew:_prop_skew
	def _get_px_skew(self)->float:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:return self.skew*image_props.larger_side
		return .0
	def _set_px_skew(self,value):
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:value_eval=value/image_props.larger_side;self.skew=value_eval
	px_skew:FloatProperty(get=_get_px_skew,set=_set_px_skew,subtype='PIXEL',translation_context=_A,name='Pixels Skew',description='Horizontal skew of the image in pixels relative to its center without taking into account deviation. Calculated by the formula:\n\n`Pixels Skew = S * P`\n\nwhere `S` is the skew value in millimeters, `P` is the size of the larger side of the image');aspect,_prop_aspect=bhqdbl.double_property('aspect',default=constants.CAMERA.ASPECT.DEFAULT,soft_min=constants.IEEE754.FLT_EXP,soft_max=2.-constants.IEEE754.FLT_EXP,subtype=_E,precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP,options=constants.PROPERTY.OPTIONS,translation_context=_A,name='Aspect Ratio',description='Image aspect ratio correction factor. It means the ratio of the height of the image to its width - that is, values \u200b\u200bgreater than 1.0 will stretch it vertically, smaller values \u200b\u200bwill compress it. The value is stored with double precision');s_aspect:_prop_aspect;_principal_kwargs=dict(precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP);principal_x,_prop_principal_x=bhqdbl.double_property('principal_x',options={_B},translation_context=_A,name='Principal X',description='Deviation of the camera principal point X. The value is stored with double precision',**_principal_kwargs);s_principal_x:_prop_principal_x;principal_y,_prop_principal_y=bhqdbl.double_property('principal_y',options={_B},translation_context=_A,name='Principal Y',description='Deviation of the camera principal point Y. The value is stored with double precision',**_principal_kwargs);s_principal_y:_prop_principal_y
	def _cb_get_principal_x_mm(self)->float:return self.principal_x*self.sensor
	def _cb_set_principal_x_mm(self,value:float):self.principal_x=value/self.sensor
	principal_x_mm,_prop_principal_x_mm=bhqdbl.double_property('principal_x_mm',get=_cb_get_principal_x_mm,set=_cb_set_principal_x_mm,options=constants.PROPERTY.OPTIONS,translation_context=_A,subtype=_D,name='Millimeters Principal X',description="The deviation from the center of the image in millimeters along the X axis. Calculated by the formula:\n\n`Millimeters Principal X = Px * S`\n\nwhere `Px' is the deviation factor, `S' is the size of the camera sensor",**_principal_kwargs);s_principal_x_mm:_prop_principal_x_mm
	def _cb_get_principal_y_mm(self)->float:return self.principal_y*self.sensor
	def _cb_set_principal_y_mm(self,value:float):self.principal_y=value/self.sensor
	principal_y_mm,_prop_principal_y_mm=bhqdbl.double_property('principal_y_mm',get=_cb_get_principal_y_mm,set=_cb_set_principal_y_mm,options=constants.PROPERTY.OPTIONS,translation_context=_A,subtype=_D,name='Millimeters Principal Y',description="The deviation from the center of the image in millimeters along the Y axis. Calculated by the formula:\n\n`Millimeters Principal Y = Py * S`\n\nwhere `Py' is the deviation factor, `S' is the size of the camera sensor",**_principal_kwargs);s_principal_y_mm:_prop_principal_y_mm
	def _get_px_principal(self)->Vector:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:half_size=Vector(image_props.size)*.5;return Vector((self.principal_x,self.principal_y))*image_props.larger_side+half_size
		return Vector((.0,.0))
	def _set_px_principal(self,value)->None:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:half_size=Vector(image_props.size)*.5;value_eval=(Vector(value)-half_size)/image_props.larger_side;self.principal_x=value_eval.x;self.principal_y=value_eval.y
	px_principal:FloatVectorProperty(get=_get_px_principal,set=_set_px_principal,size=2,subtype='XYZ',precision=constants.IEEE754.FLT_DIG,translation_context=_A,name='Pixels Principal',description='The deviation from the center of the image in pixels. Calculated by the formula:\n\n`Pixels Principal = Pxy * L + (Sxy / 2)`\n\nwhere `Pxy` is the deviation factor, `L` is the larger side of the image, `Sxy` is the image size');distortion_model:EnumProperty(items=((constants.DistortionModel.NONE.name,'None','No distortion, only correction'),(constants.DistortionModel.DIVISION.name,'Division','The division model with two radial distortion coefficients. This is the simplest mathematical model of linear division of image coordinates, which can be used if the distortion is small, for example, for scenes where the shooting took place close to the object'),(constants.DistortionModel.POLYNOMIAL.name,'Polynomial','A polynomial model with four radial and two tangential distortion coefficients. It uses polynomial functions instead of simple linear division, so it is a more accurate and flexible model that can be used for complex scenes with significant lens distortions'),(constants.DistortionModel.BROWN.name,'Brown-Conrady','Brown-Conrady polynomial model with four with four radial and two tangential distortion coefficients. It is the most accurate and flexible model that can be used for complex scenes with significant lens distortions. In general, it is used when a simple linear division model is no longer sufficient')),default='NONE',options=constants.PROPERTY.OPTIONS,translation_context=_A,name='Distortion Model',description='Mathematical model of lens distortion. Note that distortion coefficients may be inconsistent between different distortion models');_coefficient_kwargs=dict(default=.0,soft_min=-1.,soft_max=1.,subtype=_E,precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP,options=constants.PROPERTY.OPTIONS);k1,_prop_k1=bhqdbl.double_property('k1',translation_context=_A,name='K1',description='Represents linear radial distortion. It corrects or introduces distortion that increases linearly with radial distance. The value is stored with double precision',**_coefficient_kwargs);s_k1:_prop_k1;k2,_prop_k2=bhqdbl.double_property('k2',translation_context=_A,name='K2',description='Represents cubic radial distortion. It corrects or introduces distortion that increases with the cube of the radial distance. The value is stored with double precision',**_coefficient_kwargs);s_k2:_prop_k2;k3,_prop_k3=bhqdbl.double_property('k3',translation_context=_A,name='K3',description='Represents quintic (fifth-order) radial distortion. It corrects or introduces distortion that increases with the fifth power of the radial distance. The value is stored with double precision',**_coefficient_kwargs);s_k3:_prop_k3;k4,_prop_k4=bhqdbl.double_property('k4',translation_context=_A,name='K4',description='Represents seventh-order radial distortion. It corrects or introduces distortion that increases with the seventh power of the radial distance. The value is stored with double precision',**_coefficient_kwargs);s_k4:_prop_k4;p1,_prop_p1=bhqdbl.double_property('p1',translation_context=_A,name='P1',description='Represents linear tangential distortion. Corrects or introduces distortion that increases linearly with the distance from the image center. The value is stored with double precision',**_coefficient_kwargs);s_p1:_prop_p1;p2,_prop_p2=bhqdbl.double_property('p2',translation_context=_A,name='P2',description='Represents quadratic tangential distortion. Corrects or introduces distortion that increases with the square of the distance from the image center. The value is stored with double precision',**_coefficient_kwargs);s_p2:_prop_p2
	def update_render_settings(self,context:Context):
		render_settings=context.scene.render
		if self.image:
			image_props:ImageProps=self.image.cpp
			if image_props.valid:
				if render_settings.resolution_x!=image_props.size[0]:render_settings.resolution_x=image_props.size[0]
				if render_settings.resolution_y!=image_props.size[1]:render_settings.resolution_y=image_props.size[1]
	def update_tool_settings(self,context:Context):
		image_paint=context.tool_settings.image_paint
		if not image_paint.use_clone_layer:image_paint.use_clone_layer=True
		if image_paint.clone_image!=self.image:image_paint.clone_image=self.image
class BindImageHistoryItem(PropertyGroup):image:PointerProperty(type=bpy.types.Image,options=constants.PROPERTY.OPTIONS,translation_context=_A,name='Image',description='The image that was previously attached to this camera')
class RC_XMP_CameraProps(PropertyGroup):0
def create_props_camera()->CameraProps:register_class(BindImageHistoryItem);CameraProps.__annotations__['bind_history']=CollectionProperty(type=BindImageHistoryItem,translation_context=_A,name='Bind History',description='Images that were previously binded to this camera. The option is used if, for example, it is necessary to draw some area from another image, and then return to the previous one. Of course, this is not a standard workflow, but it is used sometimes');register_class(RC_XMP_CameraProps);CameraProps.__annotations__['rc_metadata_xmp']=PointerProperty(type=RC_XMP_CameraProps,translation_context=_A,name='Reality Capture Properties',description='The properties that were imported from Reality Capture.They will be used for export');return CameraProps