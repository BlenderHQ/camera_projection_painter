from __future__ import annotations
_Y='camera_select.frag'
_X='mesh_project'
_W='u_Image'
_V='u_ViewportMetrics'
_U='u_Intrinsics'
_T='distorted_image'
_S='put_atlas_tile'
_R='PRV_ATLAS_SIDE_TILES'
_Q='atlas_tile'
_P='u_Params'
_O='v_CenterHalfSize'
_N='ui_rectangle'
_M='outline_thickness'
_L='roundness'
_K='outline_color'
_J='transform'
_I='_pad0'
_H='camera_common.vert'
_G='ModelViewProjectionMatrix'
_F='MAT4'
_E='_pad1'
_D='f_Color'
_C='FLOAT_2D'
_B='VEC4'
_A='VEC2'
import os
from enum import IntEnum
import bpy,gpu
from gpu.types import GPUShader,GPUShaderCreateInfo,GPUStageInterfaceInfo
from..import constants
from..lib import bhqglsl
from..lib.bhqglsl.ubo import glsl_bool,glsl_float,glsl_int,glsl_mat4,glsl_vec2,glsl_vec4,IntrinsicsPixelCoo,StructUBO
__all__='DitheringParams','TooltipParams','PreviewParams','UVProjectParams','MeshProjectParams','CameraCommonParams','register','get'
INTERN_DIR=os.path.join(os.path.dirname(__file__),'intern')
def _gpu_shader_create_info_define_enum_items(*,info:GPUShaderCreateInfo,enum_cls:IntEnum):
	for enum_item in enum_cls:info.define(f"{enum_cls.__qualname__.upper()}_{enum_item.name}",str(enum_item.value))
def _define_enum_items(*,enum_cls:IntEnum)->str:
	defines=''
	for enum_item in enum_cls:defines+=f"#define {enum_cls.__qualname__.upper()}_{enum_item.name} {str(enum_item.value)}\n"
	return defines
class DitheringParams(StructUBO):use:glsl_bool;mix_factor:glsl_float;_fields_=('use',glsl_bool),('mix_factor',glsl_float),('_pad',glsl_vec2)
class TooltipParams(StructUBO):transform:glsl_vec4;color:glsl_vec4;outline_color:glsl_vec4;shade_top_bottom:glsl_vec2;roundness:glsl_float;outline_thickness:glsl_float;show_shaded:glsl_bool;_fields_=[(_J,glsl_vec4),('color',glsl_vec4),(_K,glsl_vec4),('shade_top_bottom',glsl_vec2),(_L,glsl_float),(_M,glsl_float),('show_shaded',glsl_bool),(_I,glsl_bool),(_E,glsl_vec2)]
def _create_shader_ui_rectangle()->GPUShader:vertexcode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('ui_rectangle.vert','ui_rectangle.frag'));info=GPUShaderCreateInfo();info.vertex_in(0,_A,'P');vs_out=GPUStageInterfaceInfo(_N);vs_out.smooth(_B,'v_Color');vs_out.smooth(_B,_O);info.vertex_out(vs_out);info.push_constant(_F,_G,0);info.uniform_buf(0,TooltipParams.__qualname__,_P);info.fragment_out(0,_B,_D);info.typedef_source(TooltipParams.as_struct());info.vertex_source(vertexcode);info.fragment_source(fragcode);return gpu.shader.create_from_info(info)
class PreviewParams(StructUBO):transform:glsl_vec4;outline_color:glsl_vec4;aspect:glsl_vec2;roundness:glsl_float;outline_thickness:glsl_float;tile_index:glsl_int;_fields_=[(_J,glsl_vec4),(_K,glsl_vec4),('aspect',glsl_vec2),(_L,glsl_float),(_M,glsl_float),('tile_index',glsl_int),(_I,glsl_int),(_E,glsl_vec2)]
def _create_shader_atlas_tile()->GPUShader:vertexcode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('atlas_tile.vert','atlas_tile.frag'));info=GPUShaderCreateInfo();info.vertex_in(0,_A,'P');vs_out=GPUStageInterfaceInfo(_Q);vs_out.smooth(_A,'v_AtlasUV');vs_out.smooth(_B,_O);info.vertex_out(vs_out);info.push_constant(_F,_G,0);info.uniform_buf(0,PreviewParams.__qualname__,_P);info.uniform_buf(1,DitheringParams.__qualname__,'u_Dithering');info.sampler(0,_C,'u_TileMapping');info.sampler(1,_C,'u_Atlas');info.fragment_out(0,_B,_D);info.define(_R,f"{constants.UI.PRV.SIDE}");typedefs=f"{PreviewParams.as_struct()}\n{DitheringParams.as_struct()}\n";info.typedef_source(typedefs);info.vertex_source(vertexcode);info.fragment_source(fragcode);return gpu.shader.create_from_info(info)
def _create_shader_put_atlas_tile()->GPUShader:vertexcode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('put_atlas_tile.vert','put_atlas_tile.frag'));info=GPUShaderCreateInfo();info.vertex_in(0,_A,'P');vs_out=GPUStageInterfaceInfo(_S);vs_out.smooth(_A,'v_UV');info.vertex_out(vs_out);info.push_constant('INT','u_Index');info.sampler(0,_C,'u_Preview');info.push_constant('BOOL','u_UseFXAA');info.fragment_out(0,_B,_D);info.define(_R,f"{constants.UI.PRV.SIDE}");info.define('FXAA_QUALITY__PRESET','39');info.vertex_source(vertexcode);info.fragment_source(fragcode);return gpu.shader.create_from_info(info)
def _create_shader_distorted_image()->GPUShader:vertexcode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('distorted_image.vert','distorted_image.frag'));info=GPUShaderCreateInfo();info.vertex_in(0,_A,'P');info.vertex_in(1,_A,'UV');vs_out=GPUStageInterfaceInfo(_T);vs_out.smooth(_A,'v_UV');info.vertex_out(vs_out);info.push_constant(_F,_G,0);info.uniform_buf(0,IntrinsicsPixelCoo.__qualname__,_U);info.push_constant('FLOAT','u_Opacity');info.push_constant(_A,'u_Aspect');info.push_constant(_B,'u_Transform');info.push_constant(_B,_V);info.sampler(0,_C,_W);_gpu_shader_create_info_define_enum_items(info=info,enum_cls=constants.DistortionModel);info.fragment_out(0,_B,_D);info.typedef_source(IntrinsicsPixelCoo.as_struct());info.vertex_source(vertexcode);info.fragment_source(fragcode);return gpu.shader.create_from_info(info)
class UVProjectParams(StructUBO):camera_matrix:glsl_mat4;uv_texture_resolution:glsl_int;_fields_=('camera_matrix',glsl_mat4),('uv_texture_resolution',glsl_int),(_I,glsl_float),(_E,glsl_vec2)
def _create_shader_uv_project()->GPUShader:vertexcode,geocode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('uv_project.vert','uv_project.geom','uv_project.frag'));geocode=f"layout(lines) in;\nlayout(points, max_vertices = 1) out;\n{geocode}\n";defines=f"{_define_enum_items(enum_cls=constants.DistortionModel)}\n{IntrinsicsPixelCoo.as_struct()}\n{UVProjectParams.as_struct()}\n";return GPUShader(vertexcode=vertexcode,geocode=geocode,fragcode=fragcode,defines=defines)
class MeshProjectParams(StructUBO):model_matrix:glsl_mat4;highlight_border_color0:glsl_vec4;highlight_border_color1:glsl_vec4;brush_radius:glsl_float;highlight_border_type:glsl_int;draw_preview:glsl_bool;use_uniforms:glsl_bool;_fields_=('model_matrix',glsl_mat4),('highlight_border_color0',glsl_vec4),('highlight_border_color1',glsl_vec4),('brush_radius',glsl_float),('highlight_border_type',glsl_int),('draw_preview',glsl_bool),('use_uniforms',glsl_bool)
def _create_shader_mesh_project()->GPUShader:A='VEC3';vertexcode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=('mesh_project.vert','mesh_project.frag'));info=GPUShaderCreateInfo();info.vertex_in(0,A,'P');info.vertex_in(1,'INT','ID');vs_out=GPUStageInterfaceInfo(_X);vs_out.smooth(_A,'v_ProjectedDistortedUV');vs_out.smooth(A,'v_ProjectedUV');info.vertex_out(vs_out);info.push_constant(_F,_G);info.push_constant(_B,_V);info.push_constant(_A,'u_BrushPos');info.uniform_buf(0,IntrinsicsPixelCoo.__qualname__,_U);info.uniform_buf(1,UVProjectParams.__qualname__,'u_UVProjectParams');info.uniform_buf(2,MeshProjectParams.__qualname__,'u_MeshProjectParams');info.sampler(0,_C,'u_UVProjectTexture');info.sampler(1,'DEPTH_2D','u_DepthTexture');info.sampler(2,_C,_W);info.sampler(3,'FLOAT_1D','u_BrushMask');_gpu_shader_create_info_define_enum_items(info=info,enum_cls=constants.DistortionModel);_gpu_shader_create_info_define_enum_items(info=info,enum_cls=constants.BorderType);info.fragment_out(0,_B,_D);typedefs=f"{IntrinsicsPixelCoo.as_struct()}\n{UVProjectParams.as_struct()}\n{MeshProjectParams.as_struct()}\n";info.typedef_source(typedefs);info.vertex_source(vertexcode);info.fragment_source(fragcode);return gpu.shader.create_from_info(info)
class CameraCommonParams(StructUBO):data:glsl_mat4;color:glsl_vec4;color_active:glsl_vec4;color_landscape:glsl_vec4;color_portrait:glsl_vec4;scale:glsl_float;line_thickness:glsl_float;index_hover:glsl_int;index_active:glsl_int;highlight_orientation:glsl_bool;transparency:glsl_float;_fields_=('data',glsl_mat4),('color',glsl_vec4),('color_active',glsl_vec4),('color_landscape',glsl_vec4),('color_portrait',glsl_vec4),('scale',glsl_float),('line_thickness',glsl_float),('index_hover',glsl_int),('index_active',glsl_int),('highlight_orientation',glsl_bool),('transparency',glsl_float),(_E,glsl_vec2)
def _create_shader_camera_wires()->GPUShader:vertexcode,geocode,fragcode,defines=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=(_H,'camera_wires.geom','camera_wires.frag','camera_wires.glsl'));geocode=f"layout(points) in;\nlayout(line_strip, max_vertices = 22) out;\n{geocode}\n";defines=f"{defines}\n{CameraCommonParams.as_struct()}\n";return GPUShader(vertexcode=vertexcode,geocode=geocode,fragcode=fragcode,defines=defines)
def _create_shader_camera_frames()->GPUShader:vertexcode,geocode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=(_H,'camera_frames.geom','camera_frames.frag'));geocode=f"layout(points) in;\nlayout(triangle_strip, max_vertices = 7) out;\n{geocode}\n";defines=f"{CameraCommonParams.as_struct()}\n{DitheringParams.as_struct()}\n#define PRV_ATLAS_SIDE_TILES {constants.UI.PRV.SIDE}\n";return GPUShader(vertexcode=vertexcode,fragcode=fragcode,geocode=geocode,defines=defines)
def _create_shader_camera_select()->GPUShader:vertexcode,geocode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=(_H,'camera_select.geom',_Y));geocode=f"layout(points) in;\nlayout(triangle_strip, max_vertices = 13) out;\n{geocode}";defines=f"{CameraCommonParams.as_struct()}\n#define CAMERA_SELECT_OFFSET {constants.CAMERA.SELECT.OFFSET}\n";return GPUShader(vertexcode=vertexcode,geocode=geocode,fragcode=fragcode,defines=defines)
def _create_shader_camera_roi()->GPUShader:vertexcode,geocode,fragcode=bhqglsl.read_shader_files(directory=INTERN_DIR,filenames=(_H,'camera_roi.geom',_Y));geocode=f"layout(points) in;\nlayout(triangle_strip, max_vertices=4) out;\n{geocode}";defines=f"#define CAMERA_SELECT_OFFSET {constants.CAMERA.SELECT.OFFSET}\n";return GPUShader(vertexcode=vertexcode,fragcode=fragcode,geocode=geocode,defines=defines)
_shaders=dict()
def register():
	if bpy.app.background:return
	_shaders[_N]=_create_shader_ui_rectangle();_shaders[_Q]=_create_shader_atlas_tile();_shaders[_S]=_create_shader_put_atlas_tile();_shaders[_T]=_create_shader_distorted_image();_shaders['uv_project']=_create_shader_uv_project();_shaders[_X]=_create_shader_mesh_project();_shaders['camera_wires']=_create_shader_camera_wires();_shaders['camera_frames']=_create_shader_camera_frames();_shaders['camera_select']=_create_shader_camera_select();_shaders['camera_roi']=_create_shader_camera_roi()
def get(name:str)->GPUShader:return _shaders[name]