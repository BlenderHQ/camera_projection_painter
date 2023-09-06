from __future__ import annotations
import ctypes
from typing import TypeVar,Generic
from gpu.types import GPUUniformBuf
__all__='glsl_bool','glsl_int','glsl_float','glsl_vec2','glsl_vec3','glsl_vec4','glsl_mat3','glsl_mat4','T','StructUBO','UBO'
T=TypeVar('T')
class glsl_bool(ctypes.c_int):0
class glsl_float(ctypes.c_float):0
class glsl_int(ctypes.c_int):0
class glsl_vec2(ctypes.c_float*2):0
class glsl_vec4(ctypes.c_float*4):0
class glsl_mat4(glsl_vec4*4):0
_glsl_types_representation={glsl_bool:'bool',glsl_int:'int',glsl_float:'float',glsl_vec2:'vec2',glsl_vec4:'vec4',glsl_mat4:'mat4'}
class StructUBO(ctypes.Structure):
	_pack_=16
	@classmethod
	def _fields_fmt(cls)->str:return'\n'.join([f"  {_glsl_types_representation[glsl_type]} {member};"for(member,glsl_type)in cls._fields_])
	@classmethod
	def as_struct(cls)->str:return'struct {struct_name} {{\n{fields_fmt}\n}};\n'.format(struct_name=cls.__qualname__,fields_fmt=cls._fields_fmt())
	@classmethod
	def check_alignment(cls)->bool:return ctypes.sizeof(cls)%cls._pack_==0 and ctypes.sizeof(cls)==ctypes.sizeof(cls())
class UBO(Generic[T]):
	ubo:GPUUniformBuf;data:T
	def __init__(self,*,ubo_type:T):self.data=ubo_type();self.ubo=GPUUniformBuf(self.data)
	def update(self):self.ubo.update(self.data)
class IntrinsicsPixelCoo(StructUBO):res:glsl_vec2;lens:glsl_float;principal:glsl_vec2;skew:glsl_float;aspect:glsl_float;distortion_model:glsl_int;k1:glsl_float;k2:glsl_float;k3:glsl_float;k4:glsl_float;p1:glsl_float;p2:glsl_float;_fields_=('res',glsl_vec2),('principal',glsl_vec2),('lens',glsl_float),('skew',glsl_float),('aspect',glsl_float),('distortion_model',glsl_int),('k1',glsl_float),('k2',glsl_float),('k3',glsl_float),('k4',glsl_float),('p1',glsl_float),('p2',glsl_float),('_pad',glsl_vec2)