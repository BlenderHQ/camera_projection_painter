from __future__ import annotations
_D='default'
_C='set'
_B='get'
_A=None
import math
from bpy.props import FloatProperty
__all__='double_property','double_array'
def double_property(attr_name,**kwargs):
	arg_default=float(kwargs.get(_D,.0));cb_get=kwargs.pop(_B,_A);cb_set=kwargs.pop(_C,_A)
	def _get_accessor_value(self):return getattr(self,attr_name,arg_default)
	def _set_accessor_value(self,new_value:str|float):setattr(self,attr_name,new_value)
	kwargs[_B]=_get_accessor_value;kwargs[_C]=_set_accessor_value
	def _get_prop_value(self)->float:
		if attr_name in self:val=self.__getitem__(attr_name)
		else:val=arg_default
		if cb_get is not _A:
			existing_value=cb_get(self)
			if not math.isclose(val,existing_value,rel_tol=1e-05,abs_tol=1e-09):self.__setitem__(attr_name,existing_value);val=existing_value
		return val
	def _set_prop_value(self,new_value:float):
		if isinstance(new_value,str):
			try:new_value=float(new_value)
			except ValueError:pass
		self.__setitem__(attr_name,new_value)
		if cb_set is not _A:cb_set(self,new_value)
	return property(fget=_get_prop_value,fset=_set_prop_value),FloatProperty(**kwargs)
def double_array(attr_name:str,**kwargs):
	B=False;A='C';import numpy as np;arg_size=kwargs.get('size');arg_default=kwargs.get(_D,np.zeros(shape=arg_size,dtype=np.float64,order=A));cb_get=kwargs.pop(_B,_A);cb_set=kwargs.pop(_C,_A)
	def _get_prop_value(self)->float:
		if attr_name in self:val=self.__getitem__(attr_name)
		else:val=arg_default
		val=np.array(val,dtype=np.float64,copy=B,order=A).reshape(arg_size)
		if cb_get is not _A:
			existing_arr=np.array(cb_get(self),copy=B,order=A).reshape(arg_size)
			if not np.allclose(val,existing_arr,rtol=1e-05,atol=1e-09):self.__setitem__(attr_name,existing_arr);val=existing_arr
		return val
	def _set_prop_value(self,new_value:tuple[str|float]):
		val=np.array(new_value,dtype=np.float64,copy=B);self.__setitem__(attr_name,val)
		if cb_set is not _A:cb_set(self,val)
	return property(fget=_get_prop_value,fset=_set_prop_value)