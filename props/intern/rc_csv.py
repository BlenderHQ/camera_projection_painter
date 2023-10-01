from __future__ import annotations
_G='as_array'
_F='draw'
_E='__annotations__'
_D='RC_XYAltProps'
_C='RC_OmegaPhiKappaProps'
_B='RC_HeadingPitchRollProps'
_A=None
from math import asin,atan2,cos,degrees,radians,sin
from.import double
from bpy.types import PropertyGroup,Context,UILayout
from bpy.props import BoolProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;RC_XYAltProps=TypeVar(_D,bound=PropertyGroup);RC_HeadingPitchRollProps=TypeVar(_B,bound=PropertyGroup);RC_OmegaPhiKappaProps=TypeVar(_C,bound=PropertyGroup);from..ob import ObjectProps;from.common import Float64ArrayT,LocationProps,RotationMatrixProps
__all__='create_props_rc_xyalt','create_props_rc_hpr','create_props_rc_opk'
def create_props_rc_xyalt()->RC_XYAltProps:
	A='alt';_annotations_dict=dict();_properties_dict=dict()
	def _x_remapped_to_negative_y_get(self):L:LocationProps=self.id_data.cpp.location;return-L.y
	def _x_remapped_to_negative_y_set(self,value:float):L:LocationProps=self.id_data.cpp.location;L.y=-value
	attr_name='x';_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_x_remapped_to_negative_y_get,set=_x_remapped_to_negative_y_set,translation_context=_D,name='X',description="The location of the object in the Reality Capture coordinate system along the X-axis. Corresponds to the value along the negative Y-axis in Blender's Cartesian coordinate system");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _y_remapped_to_x_get(self):L:LocationProps=self.id_data.cpp.location;return L.x
	def _y_remapped_to_x_set(self,value:float):L:LocationProps=self.id_data.cpp.location;L.x=value
	attr_name='y';_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_y_remapped_to_x_get,set=_y_remapped_to_x_set,name='Y',translation_context=_D,description="The location of the object in the Reality Capture coordinate system along the Y-axis. Corresponds to the value along the X-axis in Blender's Cartesian coordinate system");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _alt_remapped_to_z_get(self):L:LocationProps=self.id_data.cpp.location;return L.z
	def _alt_remapped_to_z_set(self,value:float):L:LocationProps=self.id_data.cpp.location;L.z=value
	attr_name=A;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_alt_remapped_to_z_get,set=_alt_remapped_to_z_set,translation_context=_D,name='Alt',description="The location of the object in the Reality Capture coordinate system along the Alt-axis. Corresponds to the value along the X-axis in Blender's Cartesian coordinate system");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _draw(self,context:Context,layout:UILayout):col=layout.column(align=True);double.properties_draw(self,'x',context,col);double.properties_draw(self,'y',context,col);double.properties_draw(self,A,context,col)
	def _impl_as_array(self,*,R:_A|Float64ArrayT,S:_A|float)->Float64ArrayT:import numpy as np;ob_props:ObjectProps=self.id_data.cpp;loc:LocationProps=ob_props.location;xyz=loc.as_array(R=R,S=S);return np.array((-xyz[1],xyz[0],xyz[2]),dtype=np.float64,order='C')
	return type(_D,(PropertyGroup,),{_E:_annotations_dict,_F:_draw,_G:_impl_as_array,**_properties_dict})
def create_props_rc_hpr()->_B:
	C='roll';B='pitch';A='heading';_annotations_dict=dict();_properties_dict=dict()
	def _set_matrix_world_from_hpr(self,heading:float,pitch:float,roll:float):ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;y=radians(heading);p=radians(pitch);r=radians(roll);cx=cos(r);cy=cos(p);cz=cos(y);sx=sin(r);sy=sin(p);sz=sin(y);rmat.r00=cz*sx*sy-cx*sz;rmat.r01=cy*cz;rmat.r02=-(cx*cz*sy+sx*sz);rmat.r10=-(cx*cz+sx*sy*sz);rmat.r11=-cy*sz;rmat.r12=cx*sy*sz-cz*sx;rmat.r20=-cy*sx;rmat.r21=sy;rmat.r22=cx*cy
	def _heading_get(self:RC_HeadingPitchRollProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(-atan2(rmat.r11,rmat.r01))
	def _heading_set(self:RC_HeadingPitchRollProps,value:float)->_A:_set_matrix_world_from_hpr(self,value,self.pitch,self.roll)
	attr_name=A;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_heading_get,set=_heading_set,translation_context=_B,name='Heading',description="The object's heading value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`Heading = degrees(-atan2(M₁₁, M₀₁))`\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _pitch_get(self:RC_HeadingPitchRollProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(asin(rmat.r21))
	def _pitch_set(self:RC_HeadingPitchRollProps,value:float)->_A:_set_matrix_world_from_hpr(self,self.heading,value,self.roll)
	attr_name=B;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_pitch_get,set=_pitch_set,translation_context=_B,name='Pitch',description="The object's pitch value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`Pitch = degrees(asin(M₂₁))`\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _roll_get(self:RC_HeadingPitchRollProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(-atan2(rmat.r20,rmat.r22))
	def _roll_set(self:RC_HeadingPitchRollProps,value:float)->_A:_set_matrix_world_from_hpr(self,self.heading,self.pitch,value)
	attr_name=C;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_roll_get,set=_roll_set,translation_context=_B,name='Roll',description="The object's roll value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`Roll = degrees(-atan2(M₂₀, M₂₂))`\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _draw(self,context:Context,layout:UILayout):col=layout.column(align=True);double.properties_draw(self,A,context,col);double.properties_draw(self,B,context,col);double.properties_draw(self,C,context,col)
	def _impl_as_array(self,*,R:_A|Float64ArrayT,S:_A|float)->Float64ArrayT:import numpy as np;ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;rot=rmat.as_array(R=R,S=S);return np.array((degrees(-atan2(rot[1][1],rot[0][1])),degrees(asin(rot[2][1])),degrees(-atan2(rot[2][0],rot[2][2]))),dtype=np.float64,order='C')
	return type(_B,(PropertyGroup,),{_E:_annotations_dict,_F:_draw,_G:_impl_as_array,**_properties_dict})
def create_props_rc_opk()->_C:
	C='kappa';B='phi';A='omega';_annotations_dict=dict();_properties_dict=dict()
	def _set_matrix_world_from_opk(self,omega:float,phi:float,kappa:float):ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;o=radians(omega);p=radians(phi);k=radians(kappa);cx=cos(o);cy=cos(p);cz=cos(k);sx=sin(o);sy=sin(p);sz=sin(k);rmat.r00=-sx*cy;rmat.r01=cx*cy;rmat.r02=-sy;rmat.r10=-(cz*cx-sz*sx*sy);rmat.r11=-(sz*cx*sy+cz*sx);rmat.r12=-sz*cy;rmat.r20=-(cz*sx*sy+sz*cx);rmat.r21=-(sz*sx-cz*cx*sy);rmat.r22=cz*cy
	def _omega_get(self:RC_OmegaPhiKappaProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(-atan2(rmat.r00,rmat.r01))
	def _omega_set(self:RC_OmegaPhiKappaProps,value:float)->_A:_set_matrix_world_from_opk(self,value,self.phi,self.kappa)
	attr_name=A;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_omega_get,set=_omega_set,translation_context=_C,name='Omega',description="The object's omega value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`ω = degrees(-atan2(M₀₀, M₀₁))`\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _phi_get(self:RC_OmegaPhiKappaProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(-asin(rmat.r02))
	def _phi_set(self:RC_OmegaPhiKappaProps,value:float)->_A:_set_matrix_world_from_opk(self,self.omega,value,self.kappa)
	attr_name=B;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_phi_get,set=_phi_set,translation_context=_C,name='Phi',description="The object's phi value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`φ = degrees(-asin(M₀₂))`\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _kappa_get(self:RC_OmegaPhiKappaProps)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return degrees(-atan2(rmat.r12,rmat.r22))
	def _kappa_set(self:RC_OmegaPhiKappaProps,value:float)->_A:_set_matrix_world_from_opk(self,self.omega,self.phi,value)
	attr_name=C;_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,get=_kappa_get,set=_kappa_set,translation_context=_C,name='Kappa',description="The object's kappa value in the Reality Capture coordinate system. Corresponds to the matrix elements in to the Blender coordinate system according to the formula:\n\n`κ = degrees(atan2(M₁₂, M₂₂))\n\nwhere `Mᵢⱼ` is an element of the rotation matrix");_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _draw(self,context:Context,layout:UILayout):col=layout.column(align=True);double.properties_draw(self,A,context,col);double.properties_draw(self,B,context,col);double.properties_draw(self,C,context,col)
	def _impl_as_array(self,*,R:_A|Float64ArrayT,S:_A|float)->Float64ArrayT:import numpy as np;ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;rot=rmat.as_array(R=R,S=S);return np.array((degrees(-atan2(rot[0][0],rot[0][1])),degrees(-asin(rot[0][2])),degrees(-atan2(rot[1][2],rot[2][2]))),dtype=np.float64,order='C')
	return type(_C,(PropertyGroup,),{_E:_annotations_dict,_F:_draw,_G:_impl_as_array,**_properties_dict})
class RC_CSV_ExportParams:
	rc_csv_write_num_cameras:BoolProperty(default=False,options={'HIDDEN'},translation_context='CPP_OT_export_cameras',name='Number of Cameras',description='Write number of cameras into a file')
	def ui_draw_rc_csv_export_params(self,context:Context,layout:UILayout):layout.prop(self,'rc_csv_write_num_cameras')