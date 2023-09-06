from __future__ import annotations
from..import log
import bpy
from bpy.types import PropertyGroup
from bpy.props import IntVectorProperty
from mathutils import Vector
try:import OpenImageIO as oiio
except ImportError:HAS_OIIO=False
else:HAS_OIIO=True
from typing import TYPE_CHECKING
if TYPE_CHECKING:from.import Image
__all__='ImageProps',
class ImageProps(PropertyGroup):
	@property
	def valid(self)->bool:return self.size[0]
	@property
	def size(self)->tuple[int,int]:
		image:Image=self.id_data
		if'GENERATED'==image.source:return image.generated_width,image.generated_height
		if image.has_data:
			if self.static_size[0]!=image.size[0]or self.static_size[1]!=image.size[1]:self.static_size=image.size
		return self.static_size
	@property
	def larger_side(self)->int:return max(self.size)
	@property
	def aspect(self)->float:
		w,h=self.size
		if w==h:return 1.
		elif w>h:return 1.+h/w
		else:return w/h
	@property
	def aspect_ratio(self)->Vector:
		w,h=self.size
		if w and h:
			if w>h:return Vector((1.,h/w))
			else:return Vector((w/h,1.))
		return Vector((1.,1.))
	static_size:IntVectorProperty(size=2,default=(0,0),options={'HIDDEN'},name='Size',description='Image width and height')
	def update_size_info(self,*,force:bool=False,free:bool=True):
		image:Image=self.id_data
		if HAS_OIIO:
			if not(force or self.valid):
				fp=bpy.path.abspath(image.filepath)
				if fp:
					inp=oiio.ImageInput.open(fp)
					if not inp:log.error(oiio.geterror());inp.close()
					else:spec=inp.spec();self.static_size=spec.width,spec.height;inp.close();return
		if not(force or self.valid):
			self.static_size=image.size
			if free:image.buffers_free();image.gl_free()