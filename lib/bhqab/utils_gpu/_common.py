from __future__ import annotations
_J='MEDIUM'
_I='WINDOW'
_H='VIEW_3D'
_G='FLOAT'
_F='F32'
_E='TRIS'
_D=True
_C=.0
_B=1.
_A=None
from typing import Literal
from enum import auto,Enum,IntEnum
from..import utils_wm
import bpy
from bpy.types import AddonPreferences,Context,Region,UILayout
from mathutils import Vector,Matrix
import gpu
from gpu.types import GPUBatch,GPUBatch,GPUFrameBuffer,GPUIndexBuf,GPUOffScreen,GPUTexture,GPUVertBuf,GPUVertFormat
__all__='FrameBufferFramework','get_depth_map','get_viewport_metrics'
def get_viewport_metrics()->Vector:viewport=gpu.state.viewport_get();w,h=viewport[2],viewport[3];return Vector((_B/w,_B/h,w,h))
def get_depth_map(*,depth_format:str='DEPTH_COMPONENT32F')->GPUTexture:fb:GPUFrameBuffer=gpu.state.active_framebuffer_get();return gpu.types.GPUTexture(gpu.state.viewport_get()[2:],data=fb.read_depth(*fb.viewport_get()),format=depth_format)
class Mode(Enum):REGION=auto();TEXTURE=auto()
class FrameBufferFramework:
	__slots__='_mode','_region_framebuffer','_area_type','_region_type','_texture_offscreen_data';_mode:Mode;_region_framebuffer:dict[Region,tuple[GPUFrameBuffer,_A|GPUTexture,_A|GPUTexture]];_area_type:str;_region_type:str;_texture_offscreen_data:_A|GPUOffScreen
	def __init__(self,*,mode=Mode.REGION,area_type=_H,region_type=_I):
		self._mode=mode
		match self._mode:
			case Mode.REGION:self._region_framebuffer=dict();self._area_type=area_type;self._region_type=region_type
			case Mode.TEXTURE:self._texture_offscreen_data=_A
	def modal_eval(self,context:Context,*,texture_width:int=0,texture_height:int=0,color_format:str='',depth_format:str='',percentage:int=100):
		scale=max(10,min(400,percentage))/100
		match self._mode:
			case Mode.REGION:
				existing_regions=set(region for region in utils_wm.iter_regions(context,area_type=self._area_type,region_type=self._region_type));invalid_regions=set(self._region_framebuffer.keys());invalid_regions.difference_update(existing_regions)
				for region in invalid_regions:del self._region_framebuffer[region]
				for region in existing_regions:
					do_update=_D;do_update_depth_texture=_D;width=int(region.width*scale);height=int(region.height*scale)
					if region in self._region_framebuffer:framebuffer,texture,depth_texture=self._region_framebuffer[region];do_update=not(color_format and texture and(texture.width==width and texture.height==height and texture.format==color_format));do_update_depth_texture=not(depth_format and depth_texture and(depth_texture.width==width and depth_texture.height==height and depth_texture.format==depth_format))
					if do_update or do_update_depth_texture:
						if do_update:
							if color_format:texture=GPUTexture(size=(width,height),format=color_format)
							else:texture=_A
						if do_update_depth_texture:
							if depth_format:depth_texture=GPUTexture(size=(width,height),format=depth_format)
							else:depth_texture=_A
						framebuffer=GPUFrameBuffer(color_slots=texture,depth_slot=depth_texture);self._region_framebuffer[region]=framebuffer,texture,depth_texture
			case Mode.TEXTURE:
				assert color_format;offscreen=self._texture_offscreen_data;do_update=_D;required_width=int(texture_width*scale);required_height=int(texture_height*scale)
				if offscreen:width=int(offscreen.width*scale);height=int(offscreen.height*scale);do_update=not(width==required_width and height==required_height and offscreen.format==color_format)
				if do_update:self._texture_offscreen_data=GPUOffScreen(width=required_width,height=required_height,format=color_format)
	def get(self,*,region:_A|Region=_A)->_A|tuple[GPUFrameBuffer,_A|GPUTexture,_A|GPUTexture]|GPUOffScreen:
		match self._mode:
			case Mode.REGION:
				if not region:region=bpy.context.region
				if region in self._region_framebuffer:return self._region_framebuffer[region][0]
				return
			case Mode.TEXTURE:return self._texture_offscreen_data
	def get_color_texture(self,*,region:_A|Region=_A)->_A|GPUTexture:
		match self._mode:
			case Mode.REGION:
				if not region:region=bpy.context.region
				if region in self._region_framebuffer:return self._region_framebuffer[region][1]
				return
			case Mode.TEXTURE:return self._texture_offscreen_data.texture_color
	def get_depth_texture(self,*,region:_A|Region=_A)->_A|GPUTexture:
		match self._mode:
			case Mode.REGION:
				if not region:region=bpy.context.region
				if region in self._region_framebuffer:return self._region_framebuffer[region][2]
				return
			case Mode.TEXTURE:return
class BatchPreset:
	_unit_rectangle_tris_P_vbo:_A|GPUVertBuf=_A;_unit_rectangle_tris_P_ibo:_A|GPUIndexBuf=_A;_ndc_rectangle_tris_P_UV_vbo:_A|GPUVertBuf=_A;_ndc_rectangle_tris_P_UV_ibo:_A|GPUIndexBuf=_A
	@classmethod
	def get_unit_rectangle_tris_P(cls)->GPUBatch:
		if not cls._unit_rectangle_tris_P_vbo or not cls._unit_rectangle_tris_P_ibo:cls._update_unit_rectangle_tris_P_buffer_objects()
		return GPUBatch(type=_E,buf=cls._unit_rectangle_tris_P_vbo,elem=cls._unit_rectangle_tris_P_ibo)
	@classmethod
	def _update_unit_rectangle_tris_P_buffer_objects(cls):vert_fmt=GPUVertFormat();vert_fmt.attr_add(id='P',comp_type=_F,len=2,fetch_mode=_G);vbo=GPUVertBuf(format=vert_fmt,len=4);vbo.attr_fill(id='P',data=((_C,_C),(_C,_B),(_B,_B),(_B,_C)));ibo=GPUIndexBuf(type=_E,seq=((0,1,2),(0,2,3)));cls._unit_rectangle_tris_P_vbo=vbo;cls._unit_rectangle_tris_P_ibo=ibo
	@classmethod
	def get_ndc_rectangle_tris_P_UV(cls)->GPUBatch:
		if not cls._ndc_rectangle_tris_P_UV_vbo or not cls._ndc_rectangle_tris_P_UV_ibo:cls._update_ndc_rectangle_tris_P_UV_buffer_objects()
		return GPUBatch(type=_E,buf=cls._ndc_rectangle_tris_P_UV_vbo,elem=cls._ndc_rectangle_tris_P_UV_ibo)
	@classmethod
	def _update_ndc_rectangle_tris_P_UV_buffer_objects(cls):vert_fmt=GPUVertFormat();vert_fmt.attr_add(id='P',comp_type=_F,len=2,fetch_mode=_G);vert_fmt.attr_add(id='UV',comp_type=_F,len=2,fetch_mode=_G);vbo=GPUVertBuf(format=vert_fmt,len=4);vbo.attr_fill(id='P',data=((-_B,-_B),(-_B,_B),(_B,_B),(_B,-_B))),;vbo.attr_fill(id='UV',data=((_C,_C),(_C,_B),(_B,_B),(_B,_C))),;ibo=GPUIndexBuf(type=_E,seq=((0,1,2),(0,2,3)));cls._ndc_rectangle_tris_P_UV_vbo=vbo;cls._ndc_rectangle_tris_P_UV_ibo=ibo
class AAPreset(IntEnum):NONE=auto();LOW=auto();MEDIUM=auto();HIGH=auto();ULTRA=auto()
class AABase:
	__slots__='_preset','_preset_0';_preset:AAPreset;_preset_0:AAPreset;description:str=''
	def __init__(self,*,area_type=_H,region_type=_I):self._preset=AAPreset.NONE;self._preset_0=AAPreset.NONE
	@classmethod
	def get_name(cls)->str:return cls.__name__
	@property
	def preset(self)->Literal['NONE','LOW',_J,'HIGH','ULTRA']:return self._preset.name
	@preset.setter
	def preset(self,value:Literal['NONE','LOW',_J,'HIGH','ULTRA']):
		val_eval=AAPreset.NONE
		try:val_eval=AAPreset[value]
		except KeyError:str_possible_values=', '.join(AAPreset.__members__.keys());raise KeyError(f"Key '{value}' not found in {str_possible_values}")
		else:self._preset=val_eval
	def _do_preset_eval(self)->bool:
		if self._preset_0!=self._preset:self._preset_0=self._preset;return _D
		return False
	@staticmethod
	def _setup_gpu_state(alpha_premult:bool=_D):gpu.matrix.load_matrix(Matrix.Identity(4));gpu.matrix.load_projection_matrix(Matrix.Identity(4));gpu.state.blend_set('ALPHA_PREMULT'if alpha_premult else'ALPHA');gpu.state.depth_mask_set(False);gpu.state.depth_test_set('ALWAYS')
	def modal_eval(self,context:Context,*,texture_width:int=0,texture_height:int=0,color_format:str='',percentage:int=100):0
	def draw(self,*,texture:GPUTexture)->_A:0
	@staticmethod
	def ui_preferences(layout:UILayout,*,pref:AddonPreferences,**kwargs):0
	def update_from_preferences(self,*,pref:AddonPreferences,**kwargs):0