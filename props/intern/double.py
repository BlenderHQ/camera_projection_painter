from __future__ import annotations
_A=None
from...import constants
import bpy
from bpy.types import Context,UILayout
from bpy.props import FloatProperty,StringProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..scene import SceneProps
__all__='eval_prop_single_name','eval_prop_double_name','properties_draw','property_group'
def eval_prop_single_name(*,name:str)->str:return f"{name}_single"
def eval_prop_double_name(*,name:str)->str:return f"{name}_double"
def properties_draw(self,attr_name:str,context:Context,layout:UILayout,*,text:_A|str=_A,text_ctxt:_A|str=_A):
	B='DOUBLE';A='SINGLE';attr_name_single=eval_prop_single_name(name=attr_name);attr_name_double=eval_prop_double_name(name=attr_name);scene_props:SceneProps=context.scene.cpp;both={A,B}==scene_props.precision;col=layout
	if both:col=layout.column(align=True)
	if A in scene_props.precision:
		if text is _A:col.prop(self,attr_name_single)
		else:col.prop(self,attr_name_single,text=text,text_ctxt=text_ctxt)
	if B in scene_props.precision:
		if both:
			if text is not _A and not text:col.prop(self,attr_name_double,text='')
			else:col.prop(self,attr_name_double,text=' ')
		elif text is _A:col.prop(self,attr_name_double)
		else:col.prop(self,attr_name_double,text=text,text_ctxt=text_ctxt)
def property_group(attr_name:str,**kwargs)->tuple[bpy.types.FloatProperty,bpy.types.StringProperty,property]:
	E='translation_context';D='name';C='precision';B='default';A='description';attr_name_double=eval_prop_double_name(name=attr_name);kwargs[A]=kwargs.get(A,'');arg_default=kwargs.get(B,.0);default=float(arg_default);str_default=str(arg_default)
	if C not in kwargs:kwargs[C]=constants.IEEE754.FLT_DIG
	str_kwargs=dict();str_kwargs[B]=str_default;str_kwargs[D]=kwargs.get(D,'Double');kwargs[A]=kwargs.get(A,'');str_kwargs[E]=kwargs.get(E,'*');cb_get=kwargs.pop('get',_A);cb_set=kwargs.pop('set',_A)
	def _get_single_precision_value(self)->float:return float(getattr(self,attr_name_double,default))
	def _set_single_precision_value(self,value:float)->_A:setattr(self,attr_name_double,str(value))
	def _get_double_precision_value(self)->str:
		if cb_get is not _A:
			existing_val=cb_get(self);double_val=float(self.get(attr_name_double,default));integral,_fractional=str(existing_val).split('.');roundness=max(0,constants.IEEE754.FLT_DIG-len(integral))
			if round(existing_val,roundness)!=round(double_val,roundness):self[attr_name_double]=str(existing_val)
		return self.get(attr_name_double,str_default)
	def _set_double_precision_value(self,value:str)->_A:
		try:double_val=float(value)
		except ValueError:return
		self[attr_name_double]=str(double_val)
		if cb_set is not _A:cb_set(self,double_val)
	def _get_value(self)->float:return float(getattr(self,attr_name_double,default))
	def _set_value(self,value:float|str)->_A:
		if not isinstance(value,str):value=str(value)
		setattr(self,attr_name_double,value)
	_prop_single=FloatProperty(get=_get_single_precision_value,set=_set_single_precision_value,**kwargs);_prop_double=StringProperty(get=_get_double_precision_value,set=_set_double_precision_value,subtype='NONE',options={'HIDDEN'},**str_kwargs);_accessor=property(fget=_get_value,fset=_set_value);return _prop_single,_prop_double,_accessor