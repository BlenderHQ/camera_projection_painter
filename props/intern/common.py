from __future__ import annotations
_E='apply_transform'
_D='as_array'
_C='__annotations__'
_B=True
_A=None
from.import double
from bpy.types import Context,PropertyGroup,UILayout
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeAlias,TypeVar;from..import Object;from..ob import ObjectProps;RotationMatrixProps=TypeVar('RotationMatrixProps',bound=PropertyGroup);LocationProps=TypeVar('LocationProps',bound=PropertyGroup);import numpy as np;Float64ArrayT:TypeAlias=np.ndarray[np.float64]
__all__='matrix_getter_helper','matrix_setter_helper','remapped_matrix_getter_helper','remapped_matrix_setter_helper','matrix_eval_attr_name','create_props_rotation_matrix','create_props_location'
def matrix_getter_helper(i:int,j:int):
	def get_value(self)->float:ob:Object=self.id_data;return ob.matrix_world[i][j]
	return get_value
def matrix_setter_helper(i:int,j:int):
	def set_value(self,value:float):ob:Object=self.id_data;ob.matrix_world[i][j]=value
	return set_value
def remapped_matrix_getter_helper(mapping:tuple[int,int,int],i:int,j:int):
	col,row,multiplier=mapping[i][j];attr_name=matrix_eval_attr_name(col,row)
	def get_value(self)->float:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;return getattr(rmat,attr_name)*multiplier
	return get_value
def remapped_matrix_setter_helper(mapping:tuple[int,int,int],i:int,j:int):
	col,row,multiplier=mapping[i][j];attr_name=matrix_eval_attr_name(col,row)
	def set_value(self,value:float):ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;setattr(rmat,attr_name,float(value)*multiplier)
	return set_value
def matrix_eval_attr_name(i:int,j:int):return f"r{i}{j}"
def create_props_rotation_matrix()->RotationMatrixProps:
	_annotations_dict=dict();_properties_dict=dict()
	for i in range(3):
		for j in range(3):attr_name=matrix_eval_attr_name(i,j);_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,name=f"Row: {i+1}, Column: {j+1}",get=matrix_getter_helper(i,j),set=matrix_setter_helper(i,j));_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _impl_draw(self,context:Context,layout:UILayout):
		grid=layout.grid_flow(row_major=_B,columns=3,even_columns=_B,align=_B);grid.use_property_split=_B;grid.use_property_decorate=False
		for i in range(3):
			for j in range(3):double.properties_draw(self,matrix_eval_attr_name(i,j),context,grid,text='')
	def _impl_as_array(self,*,R:_A|Float64ArrayT,S:_A|float)->Float64ArrayT:
		import numpy as np;rmat:Float64ArrayT=np.array(((self.r00,self.r01,self.r02),(self.r10,self.r11,self.r12),(self.r20,self.r21,self.r22)),dtype=np.float64,order='C')
		if R is _A:return rmat
		else:return np.matmul(R,rmat)
	def _impl_apply_transform(self,*,R:_A|Float64ArrayT,S:_A|float):self.r00,self.r01,self.r02;self.r10,self.r11,self.r12;self.r20,self.r21,self.r22=self.as_array(R=R,S=S)
	return type('RotationMatrixProperties',(PropertyGroup,),{_C:_annotations_dict,'draw':_impl_draw,_D:_impl_as_array,_E:_impl_apply_transform,**_properties_dict})
def create_props_location()->LocationProps:
	_annotations_dict=dict();_properties_dict=dict();attr_name='x';_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,name='X',get=matrix_getter_helper(0,3),set=matrix_setter_helper(0,3));_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop;attr_name='y';_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,name='Y',get=matrix_getter_helper(1,3),set=matrix_setter_helper(1,3));_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop;attr_name='z';_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,name='Z',get=matrix_getter_helper(2,3),set=matrix_setter_helper(2,3));_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _impl_draw(self,context:Context,layout:UILayout):col=layout.column(align=_B);double.properties_draw(self,'x',context,col);double.properties_draw(self,'y',context,col);double.properties_draw(self,'z',context,col)
	def _impl_as_array(self,*,R:_A|Float64ArrayT,S:_A|float)->Float64ArrayT:
		import numpy as np;loc=np.array((self.x,self.y,self.z),dtype=np.float64,order='C')
		if R is _A and S is _A:return loc
		if R is not _A:loc=np.matmul(loc,R)
		if S is _A:return loc
		else:return loc*S
	def _impl_apply_transform(self,*,R:_A|Float64ArrayT,S:_A|float):self.x,self.y,self.z=self.as_array(R=R,S=S)
	return type('LocationProperties',(PropertyGroup,),{_C:_annotations_dict,'draw':_impl_draw,_D:_impl_as_array,_E:_impl_apply_transform,**_properties_dict})