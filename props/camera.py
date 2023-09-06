from __future__ import annotations
_Q='principal_y_mm'
_P='principal_x_mm'
_O='Principal X'
_N='Aspect Ratio'
_M='aspect'
_L='Sensor'
_K='sensor'
_J='FACTOR'
_I='AUTO'
_H='DISTANCE_CAMERA'
_G='HIDDEN'
_F='Image'
_E=True
_D='k2'
_C='k1'
_B='VERTICAL'
_A='CameraProps'
from.import intern
from..import constants
from..import register_class
import bpy
from bpy.types import Context,PropertyGroup,UILayout
from bpy.props import CollectionProperty,EnumProperty,FloatProperty,FloatVectorProperty,IntProperty,PointerProperty
from mathutils import Vector
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;CameraProps=TypeVar(_A,bound=PropertyGroup);from.import Image,Camera;from.image import ImageProps;from.scene import SceneProps
__all__='BindImageHistoryItem',_A,'create_props_camera'
class BindImageHistoryItem(PropertyGroup):image:PointerProperty(type=bpy.types.Image,options=constants.PROPERTY.OPTIONS,name=_F,description=_F)
class CameraProps(PropertyGroup):
	def _active_bind_index_update(self,_context:Context):
		item:BindImageHistoryItem=self.bind_history[self.active_bind_index]
		if item.image and item.image!=self.image:self.image=item.image
	active_bind_index:IntProperty(default=0,update=_active_bind_index_update,options={_G,'SKIP_SAVE'},translation_context=_A,name='Active',description='Active bind history index')
	def update_sensor_fit_from_image(self):
		cam:Camera=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:
				w,h=image_props.size
				if w>h:cam.sensor_fit='HORIZONTAL'
				else:cam.sensor_fit=_B
	def _image_update(self,_context:Context):
		if self.image:
			self.update_sensor_fit_from_image();bind_history_images=tuple(_.image for _ in self.bind_history)
			if self.image in bind_history_images:self.active_bind_index=bind_history_images.index(self.image)
			else:item:CameraProps.BindImageHistoryItem=self.bind_history.add();item.image=self.image;self.active_bind_index=len(self.bind_history)-1
	image:PointerProperty(type=bpy.types.Image,options=constants.PROPERTY.OPTIONS,update=_image_update,translation_context=_A,name=_F,description='Camera binded image. It will be used as a paint brush. Also, its size affects the distortion parameters in the pixel coordinate system (in which way - described in more detail for the corresponding parameters), and therefore - also the possibility of exporting to certain file formats')
	def _cb_get_lens(self)->float:cam:Camera=self.id_data;return cam.lens
	def _cb_set_lens(self,value:float):cam:Camera=self.id_data;cam.lens=value
	_lens_single_T,_lens_double_T,lens=intern.double.property_group('lens',get=_cb_get_lens,set=_cb_set_lens,default=constants.CAMERA.LENS.DEFAULT,min=constants.CAMERA.LENS.MIN,soft_max=constants.CAMERA.LENS.SOFT_MAX,options=constants.PROPERTY.OPTIONS,precision=constants.IEEE754.FLT_DIG,subtype=_H,translation_context=_A,name='Millimeters Focal Length',description='Camera focal length in millimeters');lens_single:_lens_single_T;lens_double:_lens_double_T
	def get_lens_px(self):
		cam=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:sensor_eval=self.sensor;return cam.lens*image_props.larger_side/sensor_eval
		return 0
	def set_lens_px(self,value):
		cam:Camera=self.id_data;image:Image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:sensor_eval=self.sensor;cam.lens=value/image_props.larger_side*sensor_eval
	lens_px:FloatProperty(get=get_lens_px,set=set_lens_px,subtype='PIXEL',translation_context=_A,name='Pixels Focal Length',description='Camera focal length in pixels')
	def _cb_get_sensor(self):
		cam:Camera=self.id_data;cam_props:CameraProps=cam.cpp
		if _B==cam.sensor_fit:return cam.sensor_height
		elif _I==cam.sensor_fit and cam_props.image:
			image_props:ImageProps=cam_props.image.cpp;w,h=image_props.size
			if h>w:return cam.sensor_height
		return cam.sensor_width
	def _cb_set_sensor(self,value:float):
		cam:Camera=self.id_data;cam_props:CameraProps=cam.cpp
		if _B==cam.sensor_fit:cam.sensor_height=value;return
		elif _I==cam.sensor_fit and cam_props.image:
			image_props:ImageProps=cam_props.image.cpp;w,h=image_props.size
			if h>w:cam.sensor_height=value;return
		cam.sensor_width=value
	_sensor_single_T,_sensor_double_T,sensor=intern.double.property_group(_K,get=_cb_get_sensor,set=_cb_set_sensor,precision=constants.IEEE754.FLT_DIG,min=constants.CAMERA.SENSOR.MIN,soft_max=constants.CAMERA.SENSOR.SOFT_MAX,translation_context=_A,name=_L,description='The size of the camera sensor in millimeters, taking into account the larger side of the binded image');sensor_single:_sensor_single_T;sensor_double:_sensor_double_T;_skew_single_T,_skew_double_T,skew=intern.double.property_group('skew',default=.0,soft_min=-1.,soft_max=1.,subtype=_J,translation_context=_A,name='Millimeters Skew',description='Horizontal camera skew in millimeters');skew_single:_skew_single_T;skew_double:_skew_double_T
	def _cb_get_skew_px(self)->float:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:return self.skew*image_props.larger_side
		return .0
	def _cb_set_skew_px(self,value):
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:value_eval=value/image_props.larger_side;self.skew=value_eval
	skew_px:FloatProperty(get=_cb_get_skew_px,set=_cb_set_skew_px,subtype='PIXEL',translation_context=_A,name='Pixels Skew',description='Horizontal camera skew in pixels');_aspect_single_T,_aspect_double_T,aspect=intern.double.property_group(_M,default=constants.CAMERA.ASPECT.DEFAULT,soft_min=constants.IEEE754.FLT_EXP,soft_max=2.-constants.IEEE754.FLT_EXP,subtype=_J,precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP,options=constants.PROPERTY.OPTIONS,translation_context=_A,name=_N,description='Camera aspect ratio correction factor');aspect_single:_aspect_single_T;aspect_double:_aspect_double_T;_principal_kwargs=dict(precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP,options=constants.PROPERTY.OPTIONS);_principal_x_single_T,_principal_x_double_T,principal_x=intern.double.property_group('principal_x',translation_context=_A,name=_O,description='Deviation of the camera principal point X',**_principal_kwargs);principal_x_single:_principal_x_single_T;principal_x_double:_principal_x_double_T;_principal_y_single_T,_principal_y_double_T,principal_y=intern.double.property_group('principal_y',translation_context=_A,name='Principal Y',description='Deviation of the camera principal point Y',**_principal_kwargs);principal_y_single:_principal_y_single_T;principal_y_double:_principal_y_double_T
	def _cb_get_principal_x_mm(self)->float:return self.principal_x*self.sensor
	def _cb_set_principal_x_mm(self,value:float):self.principal_x=value/self.sensor
	_principal_x_mm_single_T,_principal_x_mm_double_T,principal_x_mm=intern.double.property_group(_P,get=_cb_get_principal_x_mm,set=_cb_set_principal_x_mm,translation_context=_A,subtype=_H,name='Millimeters Principal X',description='Deviation of the camera principal point X in millimeters',**_principal_kwargs);principal_x_mm_single:_principal_x_mm_single_T;principal_x_mm_double:_principal_x_mm_double_T
	def _cb_get_principal_y_mm(self)->float:return self.principal_y*self.sensor
	def _cb_set_principal_y_mm(self,value:float):self.principal_y=value/self.sensor
	_principal_y_mm_single_T,_principal_y_mm_double_T,principal_y_mm=intern.double.property_group(_Q,get=_cb_get_principal_y_mm,set=_cb_set_principal_y_mm,translation_context=_A,subtype=_H,name='Millimeters Principal Y',description='Deviation of the camera principal point Y in millimeters',**_principal_kwargs);principal_y_mm_single:_principal_y_mm_single_T;principal_y_mm_double:_principal_y_mm_double_T
	def _cb_get_principal_px(self)->Vector:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:half_size=Vector(image_props.size)*.5;return Vector((self.principal_x,self.principal_y))*image_props.larger_side+half_size
		return Vector((.0,.0))
	def _cb_set_principal_px(self,value)->None:
		image=self.image
		if image:
			image_props:ImageProps=image.cpp
			if image_props.valid:half_size=Vector(image_props.size)*.5;value_eval=(Vector(value)-half_size)/image_props.larger_side;self.principal_x=value_eval.x;self.principal_y=value_eval.y
	principal_px:FloatVectorProperty(get=_cb_get_principal_px,set=_cb_set_principal_px,size=2,subtype='XYZ',precision=constants.IEEE754.FLT_DIG,translation_context=_A,name='Pixels Principal',description='Deviation of the camera principal point in pixels');distortion_model:EnumProperty(items=((constants.DistortionModel.NONE.name,'None','No distortion, only correction'),(constants.DistortionModel.DIVISION.name,'Division','Division lens distortion model with two radial distortion coefficients'),(constants.DistortionModel.POLYNOMIAL.name,'Polynomial','Polynomial lens distortion model with four radial and two tangential lens distortion coefficients'),(constants.DistortionModel.BROWN.name,'Brown','Brown-Conrady lens distortion model with four radial and two tangential lens distortion coefficients')),default='NONE',options=constants.PROPERTY.OPTIONS,translation_context=_A,name='Distortion Model',description='Camera mathematical lens distortion model');_coefficient_kwargs=dict(default=.0,soft_min=-1.,soft_max=1.,subtype=_J,precision=constants.PROPERTY.FLOAT.PRECISION,step=constants.PROPERTY.FLOAT.STEP,options=constants.PROPERTY.OPTIONS);_k1_single_T,_k1_double_T,k1=intern.double.property_group(_C,translation_context=_A,name='K1',description='First radial coefficient',**_coefficient_kwargs);k1_single:_k1_single_T;k1_double:_k1_double_T;_k2_single_T,_k2_double_T,k2=intern.double.property_group(_D,translation_context=_A,name='K2',description='Second radial coefficient',**_coefficient_kwargs);k2_single:_k2_single_T;k2_double:_k2_double_T;_k3_single_T,_k3_double_T,k3=intern.double.property_group('k3',translation_context=_A,name='K3',description='Third radial coefficient',**_coefficient_kwargs);k3_single:_k3_single_T;k3_double:_k3_double_T;_k4_single_T,_k4_double_T,k4=intern.double.property_group('k4',translation_context=_A,name='K4',description='Fourth radial coefficient',**_coefficient_kwargs);k4_single:_k4_single_T;k4_double:_k4_double_T;_p1_single_T,_p1_double_T,p1=intern.double.property_group('p1',translation_context=_A,name='P1',description='First tangential coefficient',**_coefficient_kwargs);p1_single:_p1_single_T;p1_double:_p1_double_T;_p2_single_T,_p2_double_T,p2=intern.double.property_group('p2',translation_context=_A,name='P2',description='Second tangential coefficient',**_coefficient_kwargs);p2_single:_p2_single_T;p2_double:_p2_double_T
	@property
	def is_any_non_default(self)->bool:cam:Camera=self.id_data;return self.lens!=constants.CAMERA.LENS.DEFAULT or cam.sensor_width!=constants.CAMERA.SENSOR.DEFAULT_WIDTH or cam.sensor_height!=constants.CAMERA.SENSOR.DEFAULT_HEIGHT or self.skew or self.aspect!=constants.CAMERA.ASPECT.DEFAULT or self.principal_x or self.principal_y or self.distortion_model!='NONE'and(self.k1 or self.k2 or self.k3 or self.k4 or self.p1 or self.p2)
	def eval_sensor(self)->float:
		cam:Camera=self.id_data;sensor=cam.sensor_width
		if _B==cam.sensor_fit:sensor=cam.sensor_height
		elif _I==cam.sensor_fit and self.image:
			image_props:ImageProps=self.image.cpp;w,h=image_props.size
			if h>w:sensor=cam.sensor_height
		return sensor
	def ui_draw_calibration(self,context:Context,layout:UILayout):
		B='Skew';A='Lens';cam:Camera=self.id_data;scene=context.scene;scene_props:SceneProps=scene.cpp
		match scene_props.units:
			case'MILLIMETERS':intern.double.properties_draw(self,'lens',context,layout,text=A,text_ctxt=_A)
			case'PIXELS':layout.prop(self,'lens_px',text=A,text_ctxt=_A)
		col=layout.column(align=_E);col.prop(cam,'sensor_fit');intern.double.properties_draw(self,_K,context,layout,text=_L,text_ctxt=_A);col=layout.column(align=_E);col.prop(cam,'clip_start');col.prop(cam,'clip_end');col=layout.column(align=_E)
		match scene_props.units:
			case'MILLIMETERS':intern.double.properties_draw(self,_P,context,col,text=_O,text_ctxt=_A);intern.double.properties_draw(self,_Q,context,col,text='Y',text_ctxt=_A);intern.double.properties_draw(self,'skew',context,layout,text=B,text_ctxt=_A)
			case'PIXELS':col.prop(self,'principal_px',text='Principal',text_ctxt=_A);layout.prop(self,'skew_px',text=B,text_ctxt=_A)
		intern.double.properties_draw(self,_M,context,layout,text=_N,text_ctxt=_A)
	def update_render_settings(self,context:Context):
		render_settings=context.scene.render
		if self.image:
			image_props:ImageProps=self.image.cpp
			if image_props.valid:
				if render_settings.resolution_x!=image_props.size[0]:render_settings.resolution_x=image_props.size[0]
				if render_settings.resolution_y!=image_props.size[1]:render_settings.resolution_y=image_props.size[1]
	def update_tool_settings(self,context:Context):
		image_paint=context.tool_settings.image_paint
		if not image_paint.use_clone_layer:image_paint.use_clone_layer=_E
		if image_paint.clone_image!=self.image:image_paint.clone_image=self.image
	def ui_draw_lens_distortion(self,context:Context,layout:UILayout):
		layout.prop(self,'distortion_model')
		match self.distortion_model:
			case constants.DistortionModel.BROWN.name:col=layout.column();intern.double.properties_draw(self,_C,context,col);intern.double.properties_draw(self,_D,context,col);intern.double.properties_draw(self,'k3',context,col);intern.double.properties_draw(self,'k4',context,col);col.separator();intern.double.properties_draw(self,'p1',context,col);intern.double.properties_draw(self,'p2',context,col)
			case constants.DistortionModel.POLYNOMIAL.name:col=layout.column();intern.double.properties_draw(self,_C,context,col);intern.double.properties_draw(self,_D,context,col);intern.double.properties_draw(self,'k3',context,col);intern.double.properties_draw(self,'k4',context,col)
			case constants.DistortionModel.DIVISION.name:col=layout.column();intern.double.properties_draw(self,_C,context,col);intern.double.properties_draw(self,_D,context,col)
def create_props_camera()->CameraProps:register_class(BindImageHistoryItem);CameraProps.__annotations__['bind_history']=CollectionProperty(type=BindImageHistoryItem,options={_G});register_class(intern.rc_xmp.RC_MetadataXMP_Props);CameraProps.__annotations__['rc_metadata_xmp_props']=PointerProperty(type=intern.rc_xmp.RC_MetadataXMP_Props,options={_G});return CameraProps