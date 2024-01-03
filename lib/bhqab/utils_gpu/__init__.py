from __future__ import annotations
_D='aa_method'
_C='attr_aa_method'
_B='u_Image'
_A=None
if'bpy'in locals():from importlib import reload;reload(_common);reload(_smaa);reload(_fxaa)
else:from.import _common
import bpy
from bpy.types import AddonPreferences,Context,UILayout
from bpy.props import EnumProperty
import gpu
from gpu.types import GPUShader,GPUShaderCreateInfo,GPUStageInterfaceInfo,GPUTexture
__all__='BatchPreset','Mode','AAPreset','get_depth_map','get_viewport_metrics','FrameBufferFramework','DrawFramework','AABase','SMAA','FXAA'
BatchPreset=_common.BatchPreset
Mode=_common.Mode
AAPreset=_common.AAPreset
AABase=_common.AABase
get_depth_map=_common.get_depth_map
get_viewport_metrics=_common.get_viewport_metrics
FrameBufferFramework=_common.FrameBufferFramework
class DrawFramework:
	__slots__='_aa_instance','_fb_frameworks';__aa_methods_registry__:list[AABase]=list();_aa_instance:_A|AABase;_fb_frameworks:tuple[FrameBufferFramework];__shader_2d_image__:_A|GPUShader=_A
	@classmethod
	def get_shader_2d_image(cls)->_A|GPUShader:
		A='VEC2'
		if not cls.__shader_2d_image__ and not bpy.app.background:info=GPUShaderCreateInfo();info.vertex_in(0,A,'P');info.vertex_in(1,A,'UV');vs_out=GPUStageInterfaceInfo('image');vs_out.smooth(A,'v_UV');info.vertex_out(vs_out);info.push_constant('MAT4','ModelViewProjectionMatrix');info.sampler(0,'FLOAT_2D',_B);info.fragment_out(0,'VEC4','f_Color');info.vertex_source('\n                void main() {\n                    v_UV = UV;\n                    gl_Position = ModelViewProjectionMatrix * vec4(P, 0.0, 1.0);\n                }\n                ');info.fragment_source('void main() { f_Color = texture(u_Image, v_UV); }');cls.__shader_2d_image__=gpu.shader.create_from_info(info)
		return cls.__shader_2d_image__
	@classmethod
	def get_prop_aa_method(cls)->EnumProperty:return EnumProperty(items=tuple((_.get_name(),_.get_name(),_.description)for _ in cls.__aa_methods_registry__),options={'HIDDEN','SKIP_SAVE'},translation_context='BHQAB_Preferences',name='AA Method',description='Anti-aliasing method to be used')
	@classmethod
	def register_aa_method(cls,method_class:AABase):cls.__aa_methods_registry__.append(method_class)
	@property
	def aa_method(self)->str:
		if self._aa_instance is _A:return'NONE'
		return self._aa_instance.get_name()
	@aa_method.setter
	def aa_method(self,value:str):
		cls=self.__class__;area_type=self._fb_frameworks[0]._area_type;region_type=self._fb_frameworks[0]._region_type
		if not self._aa_instance or self._aa_instance and self._aa_instance.get_name()!=value:
			for item in cls.__aa_methods_registry__:
				if item.get_name()==value:self._aa_instance=item(area_type=area_type,region_type=region_type)
	@property
	def aa(self)->AABase|_A:return self._aa_instance
	def get(self,*,index:int=0)->FrameBufferFramework:return self._fb_frameworks[index]
	def modal_eval(self,context:Context,*,color_format:str='',depth_format:str='',percentage:int=100):
		for fb_framework in self._fb_frameworks:fb_framework.modal_eval(context,color_format=color_format,depth_format=depth_format,percentage=percentage)
		if self._aa_instance:self._aa_instance.modal_eval(context,color_format=color_format,percentage=percentage)
	def __init__(self,*,num:int=1,area_type='VIEW_3D',region_type='WINDOW'):self._fb_frameworks=tuple(_common.FrameBufferFramework(area_type=area_type,region_type=region_type)for _ in range(max(1,num)));self._aa_instance=_A
	def draw(self,*,texture:GPUTexture)->_A:
		cls=self.__class__;mvp_restore=gpu.matrix.get_projection_matrix()@gpu.matrix.get_model_view_matrix()
		if self._aa_instance is _A or self._aa_instance._preset is AAPreset.NONE:
			with gpu.matrix.push_pop():AABase._setup_gpu_state(alpha_premult=True);shader=cls.get_shader_2d_image();shader.uniform_sampler(_B,texture);BatchPreset.get_ndc_rectangle_tris_P_UV().draw(shader)
		else:self._aa_instance.draw(texture=texture)
		gpu.matrix.load_matrix(mvp_restore)
	@classmethod
	def ui_preferences(cls,layout:UILayout,*,pref:AddonPreferences,**kwargs):
		attr_aa_method=kwargs.get(_C,_D);row=layout.row(align=True);row.prop(pref,attr_aa_method,expand=True);aa_method=getattr(pref,attr_aa_method)
		for cls in cls.__aa_methods_registry__:
			if aa_method==cls.__name__:cls.ui_preferences(layout,pref=pref,**kwargs)
	def update_from_preferences(self,*,pref:AddonPreferences,**kwargs):
		cls=self.__class__;attr_aa_method=kwargs.get(_C,_D);aa_method=getattr(pref,attr_aa_method);self.aa_method=aa_method
		for cls in cls.__aa_methods_registry__:
			if aa_method==cls.__name__:self._aa_instance.update_from_preferences(pref=pref,**kwargs)
from.import _smaa
from.import _fxaa
SMAA=_smaa.SMAA
FXAA=_fxaa.FXAA
DrawFramework.register_aa_method(SMAA)
DrawFramework.register_aa_method(FXAA)