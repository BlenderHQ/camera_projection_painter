from __future__ import annotations
_K='In Meshing'
_J='In Texturing'
_I='Distortion Group'
_H='Calibration Group'
_G='Export Mode'
_F='RC_METADATA_XMP_ExportMode'
_E='RC_MetadataXMP_RotationComponentProps'
_D='CPP_OT_export_cameras'
_C='SKIP_SAVE'
_B='RC_MetadataXMP_Params'
_A=True
from enum import auto,IntEnum,IntFlag
from.import common
from.import double
from bpy.types import PropertyGroup,Context,UILayout
from bpy.props import EnumProperty,IntProperty,BoolProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import TypeVar;RC_MetadataXMP_RotationComponentProps=TypeVar(_E,bound=PropertyGroup);from.common import RotationMatrixProps,Float64ArrayT;from..ob import ObjectProps
__all__='RC_METADATA_XMP_PosePrior','RC_METADATA_XMP_CalibrationPrior','RC_METADATA_XMP_Coordinates',_F,'RC_METADATA_XMP_Overwrite',_B,'RC_MetadataXMP_ExportParams','RC_MetadataXMP_Props','create_props_rc_rotation'
class RC_METADATA_XMP_PosePrior(IntEnum):initial=auto();exact=auto();locked=auto()
class RC_METADATA_XMP_CalibrationPrior(IntEnum):initial=auto();exact=auto()
class RC_METADATA_XMP_Coordinates(IntEnum):absolute=auto();relative=auto()
class RC_METADATA_XMP_ExportMode(IntEnum):DO_NOT_EXPORT=auto();DRAFT=auto();EXACT=auto();LOCKED=auto()
class RC_METADATA_XMP_Overwrite(IntFlag):rc_metadata_xmp_export_mode=auto();rc_metadata_xmp_calibration_group=auto();rc_metadata_xmp_distortion_group=auto();rc_metadata_xmp_in_texturing=auto();rc_metadata_xmp_in_meshing=auto()
class RC_MetadataXMP_Params:rc_metadata_xmp_export_mode:EnumProperty(items=((RC_METADATA_XMP_ExportMode.DO_NOT_EXPORT.name,'Do Not Export',''),(RC_METADATA_XMP_ExportMode.DRAFT.name,'Draft','This will treat poses as an imperfect draft to be optimized in the future. The draft mode functions also as a flight log'),(RC_METADATA_XMP_ExportMode.EXACT.name,'Exact','If you trust the alignment absolutely. By choosing this option, you are saying to the application that poses are precise, but the global position, orientation, and scale is not known'),(RC_METADATA_XMP_ExportMode.LOCKED.name,'Locked','This is the same as the exact option with the difference that the camera position and calibration will not be changed, when locked')),default=RC_METADATA_XMP_ExportMode.DRAFT.name,options={_C},translation_context=_F,name=_G,description='Depending on how much you trust your registration, you can select the following options or you can also choose not to export camera poses');rc_metadata_xmp_calibration_group:IntProperty(default=-1,min=-1,options={_C},translation_context=_B,name=_H,description='By defining a group we state that all images in this group have the same calibration properties, e.g. the same focal length, the same principal point. Use "-1" if you do not want to group the parameters');rc_metadata_xmp_distortion_group:IntProperty(default=-1,min=-1,options={_C},translation_context=_B,name=_I,description='By defining a group we state that all images in this group have the same lens properties, e.g. the same lens distortion coefficients. Use "-1" if you do not want to group the parameters');rc_metadata_xmp_in_texturing:BoolProperty(default=_A,options={_C},translation_context=_B,name=_J);rc_metadata_xmp_in_meshing:BoolProperty(default=_A,options={_C},translation_context=_B,name=_K)
class RC_MetadataXMP_ExportParams:
	rc_metadata_xmp_overwrite_flags:EnumProperty(items=((RC_METADATA_XMP_Overwrite.rc_metadata_xmp_export_mode.name,_G,'Overwrite "Export Mode" parameter for export',0,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_export_mode.value),(RC_METADATA_XMP_Overwrite.rc_metadata_xmp_calibration_group.name,_H,'Overwrite "Calibration Group" parameter for export',0,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_calibration_group.value),(RC_METADATA_XMP_Overwrite.rc_metadata_xmp_distortion_group.name,_I,'Overwrite "Distortion Group" parameter for export',0,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_distortion_group.value),(RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_texturing.name,_J,'Overwrite "In Texturing" parameter for export',0,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_texturing.value),(RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_meshing.name,_K,'Overwrite "In Meshing" parameter for export',0,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_meshing.value)),default=set(),options={'HIDDEN','ENUM_FLAG'},translation_context=_D,name='Overwrite',description='What data to overwrite');rc_metadata_xmp_use_calibration_groups:BoolProperty(default=_A,translation_context=_D,name='Calibration Groups',description='Select to export the information on the created calibration groups');rc_metadata_xmp_include_editor_options:BoolProperty(default=_A,translation_context=_D,name='Include Editor Options',description='Export editor states, e.g. enabled/disabled flags for texturing, meshing, and similar')
	def ui_draw_rc_metadata_xmp_overwrite_props(self,context:Context,layout:UILayout):
		def _intern_draw_item(lay:UILayout,item:RC_METADATA_XMP_Overwrite):row=lay.row(align=_A);col=row.column();col.enabled=item.name in self.rc_metadata_xmp_overwrite_flags;col.prop(self,item.name);col=row.column(align=_A);col.emboss='NONE';col.ui_units_x=1;icon='CHECKBOX_HLT'if item.name in self.rc_metadata_xmp_overwrite_flags else'CHECKBOX_DEHLT';col.prop_enum(self,'rc_metadata_xmp_overwrite_flags',item.name,text='',icon=icon)
		_intern_draw_item(layout,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_export_mode);layout.prop(self,'rc_metadata_xmp_use_calibration_groups')
		if self.rc_metadata_xmp_use_calibration_groups:box=layout.box();_intern_draw_item(box,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_calibration_group);_intern_draw_item(box,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_distortion_group)
		layout.prop(self,'rc_metadata_xmp_include_editor_options')
		if self.rc_metadata_xmp_include_editor_options:box=layout.box();_intern_draw_item(box,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_texturing);_intern_draw_item(box,RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_meshing)
class RC_MetadataXMP_Props(PropertyGroup,RC_MetadataXMP_Params):
	def ui_draw_rc_metadata_xmp_params(self,_context:Context,layout:UILayout):layout.prop(self,'rc_metadata_xmp_export_mode');layout.prop(self,'rc_metadata_xmp_calibration_group');layout.prop(self,'rc_metadata_xmp_distortion_group');layout.prop(self,'rc_metadata_xmp_in_texturing');layout.prop(self,'rc_metadata_xmp_in_meshing')
def create_props_rc_rotation()->RC_MetadataXMP_RotationComponentProps:
	import numpy as np;_annotations_dict=dict();_properties_dict=dict();mapping=((1,0,-1),(0,0,1),(2,0,1)),((1,1,1),(0,1,-1),(2,1,-1)),((1,2,1),(0,2,-1),(2,2,-1))
	for i in range(3):
		for j in range(3):attr_name=common.matrix_eval_attr_name(i,j);_prop_single_T,_prop_double_T,_prop=double.property_group(attr_name,name=f"Item: {i*3+j+1} (Row: {i+1}, Column: {j+1})",get=common.remapped_matrix_getter_helper(mapping,i,j),set=common.remapped_matrix_setter_helper(mapping,i,j));_annotations_dict[double.eval_prop_single_name(name=attr_name)]=_prop_single_T;_annotations_dict[double.eval_prop_double_name(name=attr_name)]=_prop_double_T;_properties_dict[attr_name]=_prop
	def _draw(self,context:Context,layout:UILayout):
		for i in range(3):
			row=layout.row(align=_A);row.use_property_split=_A;row.use_property_decorate=False
			for j in range(3):double.properties_draw(self,common.matrix_eval_attr_name(i,j),context,row,text='')
	def _impl_as_array(self,*,R:None|Float64ArrayT,S:None|float)->Float64ArrayT:ob_props:ObjectProps=self.id_data.cpp;rmat:RotationMatrixProps=ob_props.rotation_matrix;rot=rmat.as_array(R=R,S=S);return np.array((-rot[1][0],rot[0][0],rot[2][0],rot[1][1],-rot[0][1],-rot[2][1],rot[1][2],-rot[0][2],-rot[2][2]),dtype=np.float64,order='C')
	return type(_E,(PropertyGroup,),{'__annotations__':_annotations_dict,'draw':_draw,'as_array':_impl_as_array,**_properties_dict})