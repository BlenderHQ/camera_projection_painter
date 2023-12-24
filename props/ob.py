from __future__ import annotations
_A=None
from..lib import bhqdbl
from bpy.types import PropertyGroup
from typing import TYPE_CHECKING
if TYPE_CHECKING:from.import Float64ArrayT,Object
__all__='ObjectProps',
class ObjectProps(PropertyGroup):
	def _get_location(self):ob:Object=self.id_data;return ob.location
	def _set_location(self,value):ob:Object=self.id_data;ob.matrix_world[0][3]=value[0];ob.matrix_world[1][3]=value[1];ob.matrix_world[2][3]=value[2]
	location=bhqdbl.double_array('location',get=_get_location,set=_set_location,size=3,precision=6)
	def _get_rotation(self):ob:Object=self.id_data;return ob.matrix_world.to_3x3()
	def _set_rotation(self,value):ob:Object=self.id_data;ob.matrix_world[0][:3]=value[0];ob.matrix_world[1][:3]=value[1];ob.matrix_world[2][:3]=value[2]
	rotation=bhqdbl.double_array(attr_name='rotation',get=_get_rotation,set=_set_rotation,size=(3,3))
	def location_as_array(self,R:_A|Float64ArrayT,S:_A|float):
		import numpy as np
		if R is _A and S is _A:return self.location
		ret=self.location
		if R is not _A:ret=np.matmul(ret,R)
		if S is _A:return ret
		return ret*S
	def rotation_as_array(self,R:_A|Float64ArrayT,S:_A|float):
		import numpy as np
		if R is _A:return self.rotation
		return np.matmul(R,self.rotation)