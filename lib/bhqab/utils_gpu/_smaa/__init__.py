from __future__ import annotations
_I='smaa_preset'
_H='attr_smaa_preset'
_G='blendTex'
_F='searchTex'
_E='areaTex'
_D='edgesTex'
_C='colorTex'
_B='u_ViewportMetrics'
_A=None
import os
from..import _common
from bpy.types import Context,AddonPreferences,UILayout
from bpy.props import EnumProperty
import gpu
from gpu.types import GPUShader,GPUTexture,GPUShaderCreateInfo,GPUStageInterfaceInfo
__all__='SMAA',
class SMAA(_common.AABase):
	__slots__='_fb_framework_stage_0','_fb_framework_stage_1','_shaders_eval';description:str='Sub-pixel morphological anti-aliasing';_fb_framework_stage_0:_common.FrameBufferFramework;_fb_framework_stage_1:_common.FrameBufferFramework;_shaders_eval:tuple[GPUShader];_cached_shader_code:tuple[str]=tuple();_search_texture:_A|GPUTexture=_A;_area_texture:_A|GPUTexture=_A
	@classmethod
	def get_prop_preset(cls):return EnumProperty(items=((_common.AAPreset.NONE.name,'None','Do not use sub-pixel morphological anti-aliasing'),(_common.AAPreset.LOW.name,'Low','60% of the quality. High threshold, very a few search steps, no detection of corners and diagonals'),(_common.AAPreset.MEDIUM.name,'Medium','80% of the quality. Medium threshold, few search steps, no detection of corners and diagonals'),(_common.AAPreset.HIGH.name,'High','95% of the quality. Medium threshold, more search steps, detection of corners and diagonals'),(_common.AAPreset.ULTRA.name,'Ultra','99% of the quality. A lot of search steps, diagonal and corner search steps, lowest threshold')),default=_common.AAPreset.HIGH.name,options={'HIDDEN','SKIP_SAVE'},translation_context='BHQAB_Preferences',name='Preset',description='Sub-pixel morphological anti-aliasing quality preset')
	@classmethod
	def _eval_textures(cls)->_A:
		A='FLOAT';import numpy as np
		if cls._search_texture is _A or cls._area_texture is _A:
			_SMAA_SEARCHTEX_WIDTH=64;_SMAA_SEARCHTEX_HEIGHT=16;_SMAA_SEARCHTEX_PITCH=_SMAA_SEARCHTEX_WIDTH;_SMAA_SEARCHTEX_SIZE=_SMAA_SEARCHTEX_HEIGHT*_SMAA_SEARCHTEX_PITCH;_SMAA_AREATEX_WIDTH=160;_SMAA_AREATEX_HEIGHT=560;_SMAA_AREATEX_PITCH=_SMAA_AREATEX_WIDTH*2;_SMAA_AREATEX_SIZE=_SMAA_AREATEX_HEIGHT*_SMAA_AREATEX_PITCH
			def _float32_arr_from_byte_file(name:str):return np.fromfile(os.path.join(os.path.dirname(__file__),name),dtype=np.ubyte).astype(dtype=np.float32)/255
			cls._search_texture=GPUTexture(size=(_SMAA_SEARCHTEX_WIDTH,_SMAA_SEARCHTEX_HEIGHT),format='R8',data=gpu.types.Buffer(A,_SMAA_SEARCHTEX_SIZE,_float32_arr_from_byte_file('searchtex.np')));cls._area_texture=GPUTexture(size=(_SMAA_AREATEX_WIDTH,_SMAA_AREATEX_HEIGHT),format='RG8',data=gpu.types.Buffer(A,_SMAA_AREATEX_SIZE,_float32_arr_from_byte_file('areatex.np')))
	def _eval_shaders(self):
		F='SMAA_STAGE';E='utf-8';D='r';C='VEC4';B='VEC2';A='FLOAT_2D';cls=self.__class__
		if _common.AAPreset.NONE!=self._preset:
			_do_update_on_preset_change=self._do_preset_eval()
			if not self._shaders_eval or _do_update_on_preset_change:
				if not cls._cached_shader_code:
					directory=os.path.dirname(__file__)
					with open(file=os.path.join(directory,'smaa.vert'),mode=D,encoding=E)as vert_file,open(file=os.path.join(directory,'smaa.frag'),mode=D,encoding=E)as frag_file,open(file=os.path.join(directory,'smaa_lib.glsl'),mode=D,encoding=E)as lib_file:cls._cached_shader_code=vert_file.read(),frag_file.read(),lib_file.read()
				vertexcode,fragcode,libcode=cls._cached_shader_code;vertexcode=f"{libcode}\n{vertexcode}";fragcode=f"{libcode}\n{fragcode}";vs_out=GPUStageInterfaceInfo('bhqab_smaa');vs_out.smooth(B,'v_pos');vs_out.smooth(B,'v_pixcoord');vs_out.smooth(C,'v_offset[3]')
				def _info_common(info):info.define('SMAA_GLSL_4','');info.define('SMAA_RT_METRICS',_B);info.define(f"SMAA_PRESET_{self._preset.name}",'');info.vertex_out(vs_out);info.vertex_in(0,B,'P');info.vertex_in(1,B,'UV');info.push_constant(C,_B,0);info.vertex_source(vertexcode);info.fragment_source(fragcode)
				info=GPUShaderCreateInfo();_info_common(info);info.define(F,'0');info.sampler(0,A,_C);info.fragment_out(0,B,'out_edges');shader_edge=gpu.shader.create_from_info(info);info=GPUShaderCreateInfo();_info_common(info);info.define(F,'1');info.sampler(0,A,_D);info.sampler(1,A,_E);info.sampler(2,A,_F);info.fragment_out(0,C,'out_weights');shader_weights=gpu.shader.create_from_info(info);info=GPUShaderCreateInfo();_info_common(info);info.define(F,'2');info.sampler(0,A,_C);info.sampler(1,A,_G);info.fragment_out(0,C,'out_color');shader_blending=gpu.shader.create_from_info(info);self._shaders_eval=shader_edge,shader_weights,shader_blending
		else:self._shaders_eval=tuple()
	def modal_eval(self,context:Context,*,texture_width:int=0,texture_height:int=0,color_format:str='',percentage:int=100):cls=self.__class__;cls._eval_textures();self._eval_shaders();self._fb_framework_stage_0.modal_eval(context,texture_width=texture_width,texture_height=texture_height,color_format='RG32F',depth_format='',percentage=percentage);self._fb_framework_stage_1.modal_eval(context,texture_width=texture_width,texture_height=texture_height,color_format=color_format,depth_format='',percentage=percentage)
	def __init__(self,*,mode:_common.Mode=_common.Mode.REGION,area_type='VIEW_3D',region_type='WINDOW'):super().__init__(area_type=area_type,region_type=region_type);self._shaders_eval=tuple();self._fb_framework_stage_0=_common.FrameBufferFramework(mode=mode,area_type=area_type,region_type=region_type);self._fb_framework_stage_1=_common.FrameBufferFramework(mode=mode,area_type=area_type,region_type=region_type)
	def draw(self,*,texture:GPUTexture)->_A:
		A=.0;super().draw(texture=texture);cls=self.__class__;viewport_metrics=_common.get_viewport_metrics();fb_framework_0=self._fb_framework_stage_0;fb=fb_framework_0.get()
		with fb.bind():fb=gpu.state.active_framebuffer_get();fb.clear(color=(A,A,A,A));self._setup_gpu_state();shader=self._shaders_eval[0];shader.uniform_sampler(_C,texture);shader.uniform_float(_B,viewport_metrics);_common.BatchPreset.get_ndc_rectangle_tris_P_UV().draw(shader)
		fb_framework_1=self._fb_framework_stage_1;fb=fb_framework_1.get()
		with fb.bind():fb=gpu.state.active_framebuffer_get();fb.clear(color=(A,A,A,A));self._setup_gpu_state();shader=self._shaders_eval[1];shader.uniform_sampler(_D,fb_framework_0.get_color_texture());shader.uniform_sampler(_F,cls._search_texture);shader.uniform_sampler(_E,cls._area_texture);shader.uniform_float(_B,viewport_metrics);_common.BatchPreset.get_ndc_rectangle_tris_P_UV().draw(shader)
		with gpu.matrix.push_pop():self._setup_gpu_state();shader=self._shaders_eval[2];shader.uniform_sampler(_C,texture);shader.uniform_sampler(_G,fb_framework_1.get_color_texture());shader.uniform_float(_B,viewport_metrics);_common.BatchPreset.get_ndc_rectangle_tris_P_UV().draw(shader)
	@staticmethod
	def ui_preferences(layout:UILayout,*,pref:AddonPreferences,**kwargs):layout.prop(pref,kwargs.get(_H,_I))
	def update_from_preferences(self,*,pref:AddonPreferences,**kwargs):self.preset=getattr(pref,kwargs.get(_H,_I))