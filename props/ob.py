from __future__ import annotations
_A='ObjectProps'
from.import intern
from..import register_class
from bpy.types import PropertyGroup
from bpy.props import PointerProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;ObjectProps=TypeVar(_A,bound=PropertyGroup);from.intern.common import Float64ArrayT,RotationMatrixProps,LocationProps
__all__='create_props_ob',
def create_props_ob():
	A='';_annotations_dict=dict();RotationMatrixProps=intern.common.create_props_rotation_matrix();register_class(RotationMatrixProps);_annotations_dict['rotation_matrix']=PointerProperty(type=RotationMatrixProps,name='Rotation Matrix',description=A);LocationProps=intern.common.create_props_location();register_class(LocationProps);_annotations_dict['location']=PointerProperty(type=LocationProps,name='Location',description=A);RC_XYAltProps=intern.rc_csv.create_props_rc_xyalt();register_class(RC_XYAltProps);_annotations_dict['rc_xyalt']=PointerProperty(type=RC_XYAltProps,name='RC X, Y, Alt',description=A);RC_HeadingPitchRollProps=intern.rc_csv.create_props_rc_hpr();register_class(RC_HeadingPitchRollProps);_annotations_dict['rc_hpr']=PointerProperty(type=RC_HeadingPitchRollProps,name='RC Heading, Pitch, Roll',description=A);RC_OmegaPhiKappaProps=intern.rc_csv.create_props_rc_opk();register_class(RC_OmegaPhiKappaProps);_annotations_dict['rc_opk']=PointerProperty(type=RC_OmegaPhiKappaProps,name='RC Omega, Phi, Kappa',description=A);RC_MetadataXMP_RotationComponentProps=intern.rc_xmp.create_props_rc_rotation();register_class(RC_MetadataXMP_RotationComponentProps);_annotations_dict['rc_rotation']=PointerProperty(type=RC_MetadataXMP_RotationComponentProps,name='RC Rotation Component',description=A)
	def _impl_apply_transform(self,*,R:None|Float64ArrayT,S:None|float):location:LocationProps=self.location;location.apply_transform(R=R,S=S);rotation:RotationMatrixProps=self.rotation_matrix;rotation.apply_transform(R=R,S=S)
	return type(_A,(PropertyGroup,),{'__annotations__':_annotations_dict,'apply_transform':_impl_apply_transform})