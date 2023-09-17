from __future__ import annotations
_D=' '
_C=None
_B=True
_A=False
from io import TextIOWrapper
from xml.etree import ElementTree as et
from xml.sax.handler import ContentHandler
import os,xml.sax
from..import common
from...import constants
from...import log
from...props.intern.rc_xmp import RC_METADATA_XMP_CalibrationPrior,RC_METADATA_XMP_Coordinates,RC_METADATA_XMP_ExportMode,RC_METADATA_XMP_Overwrite,RC_METADATA_XMP_PosePrior
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import Generic,TypeVar;T=TypeVar('T');from...props import Camera;from...props.ob import ObjectProps;from...props.camera import CameraProps;from...props.intern.rc_csv import RC_XYAltProps;from...props.intern.rc_xmp import RC_MetadataXMP_Props,RC_MetadataXMP_RotationComponentProps
__all__='RC_METADATA_XMP',
root_name='x:xmpmeta'
rdf_name='rdf:RDF'
rdf_desc_name='rdf:Description'
xmlnsx_name='xmlns:x'
xmlnsrdf_name='xmlns:rdf'
xmlnsxcr_name='xmlns:xcr'
version_name='xcr:Version'
pose_prior_name='xcr:PosePrior'
calibration_prior_name='xcr:CalibrationPrior'
coordinates_name='xcr:Coordinates'
distortion_model_name='xcr:DistortionModel'
calibration_group_name='xcr:CalibrationGroup'
distortion_group_name='xcr:DistortionGroup'
in_texturing_name='xcr:InTexturing'
in_meshing_name='xcr:InMeshing'
focal_length_35mm_name='xcr:FocalLength35mm'
skew_name='xcr:Skew'
aspect_ratio_name='xcr:AspectRatio'
principal_point_u_name='xcr:PrincipalPointU'
principal_point_v_name='xcr:PrincipalPointV'
rotation_name='xcr:Rotation'
position_name='xcr:Position'
distortion_coeff_name='xcr:DistortionCoeficients'
NAMESPACE_X='adobe:ns:meta/'
NAMESPACE_RDF='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
NAMESPACE_XCR='http://www.capturingreality.com/ns/xcr/1.1#'
NAMESPACES={'x':NAMESPACE_X,'rdf':NAMESPACE_RDF,'xcr':NAMESPACE_XCR}
class XMPAttributeFound(xml.sax.SAXException):0
class XMPAttributeNotFound(xml.sax.SAXException):0
class XMP_HandlerCheck(ContentHandler):
	def __init__(self)->_C:super().__init__();self.check_root=_A;self.check_rdf=_A;self.check_desc=_A
	def _check_terminate(self):
		if self.check_root and self.check_rdf and self.check_desc:raise XMPAttributeFound('Ok')
	def startElement(self,name,attrs):
		if not self.check_root and name==root_name:
			if attrs.get(xmlnsx_name,'')==NAMESPACE_X:self.check_root=_B;self._check_terminate()
			else:raise XMPAttributeNotFound(f'Attribute "{xmlnsx_name}" not equals to "adobe:ns:meta/"')
		if not self.check_rdf and name==rdf_name:
			if attrs.get(xmlnsrdf_name,'')==NAMESPACE_RDF:self.check_rdf=_B;self._check_terminate()
			else:raise XMPAttributeNotFound(f'Attribute "{xmlnsrdf_name}" not equals to "{NAMESPACE_RDF}"')
		if not self.check_desc and name==rdf_desc_name:
			if attrs.get(xmlnsxcr_name,'')==NAMESPACE_XCR:self.check_desc=_B;self._check_terminate()
			else:raise XMPAttributeNotFound(f'Attribute "{xmlnsxcr_name}" not equals to "{NAMESPACE_XCR}"')
	def endDocument(self):
		if not self._check_terminate():
			not_found=[]
			if not self.check_root:not_found.append(root_name)
			if not self.check_rdf:not_found.append(rdf_name)
			if not self.check_desc:not_found.append(rdf_desc_name)
			not_found_fmt=', '.join(not_found);raise XMPAttributeNotFound(f"Document is missing <{not_found_fmt}> attribute(s)")
def find_xcr_value(root_elem:et.Element,attr_name:str)->_C|str:
	_attr_name_eval=f"{{{NAMESPACE_XCR}}}{attr_name}";found=root_elem.find(_attr_name_eval)
	if found is not _C:
		if found.text:return found.text
	attr=root_elem.get(_attr_name_eval)
	if attr is not _C:return attr
def get_value(*,as_type:T,root_elem:et.Element,attr_name:str,default:T)->Generic[T]:
	str_val=find_xcr_value(root_elem=root_elem,attr_name=attr_name)
	if str_val:
		try:ret=as_type(str_val)
		except ValueError:return default
		return ret
	return default
class RC_MetadataXMP_ExportOptions(common.IOOptionsBase):
	__slots__='use_calibration_groups','use_include_editor_options','overwrite_flags','overwrite_export_mode','overwrite_calibration_group','overwrite_distortion_group','overwrite_in_texturing','overwrite_in_meshing';use_calibration_groups:bool;use_include_editor_options:bool;overwrite_flags:RC_METADATA_XMP_Overwrite;overwrite_export_mode:RC_METADATA_XMP_ExportMode;overwrite_calibration_group:int;overwrite_distortion_group:int;overwrite_in_texturing:bool;overwrite_in_meshing:bool
	def __init__(self,**kwargs):
		super().__init__(**kwargs);self.use_calibration_groups=kwargs['rc_metadata_xmp_use_calibration_groups'];self.use_include_editor_options=kwargs['rc_metadata_xmp_include_editor_options'];self.overwrite_flags=0
		for item in kwargs['rc_metadata_xmp_overwrite_flags']:self.overwrite_flags|=RC_METADATA_XMP_Overwrite[item]
		self.overwrite_export_mode=RC_METADATA_XMP_ExportMode[kwargs['rc_metadata_xmp_export_mode']];self.overwrite_calibration_group=kwargs['rc_metadata_xmp_calibration_group'];self.overwrite_distortion_group=kwargs['rc_metadata_xmp_distortion_group'];self.overwrite_in_texturing=kwargs['rc_metadata_xmp_in_texturing'];self.overwrite_in_meshing=kwargs['rc_metadata_xmp_in_meshing']
_EXPORT_MODE_ENUMS={RC_METADATA_XMP_ExportMode.DO_NOT_EXPORT:dict(),RC_METADATA_XMP_ExportMode.DRAFT:{pose_prior_name:RC_METADATA_XMP_PosePrior.initial.name,coordinates_name:RC_METADATA_XMP_Coordinates.absolute.name,calibration_prior_name:RC_METADATA_XMP_CalibrationPrior.initial.name},RC_METADATA_XMP_ExportMode.EXACT:{pose_prior_name:RC_METADATA_XMP_PosePrior.exact.name,coordinates_name:RC_METADATA_XMP_Coordinates.relative.name,calibration_prior_name:RC_METADATA_XMP_CalibrationPrior.exact.name},RC_METADATA_XMP_ExportMode.LOCKED:{pose_prior_name:RC_METADATA_XMP_PosePrior.locked.name,coordinates_name:RC_METADATA_XMP_Coordinates.absolute.name,calibration_prior_name:RC_METADATA_XMP_CalibrationPrior.exact.name}}
class RC_METADATA_XMP(common.IOFileHandler):
	io_format=common.IOFormat.RC_METADATA_XMP;extension='.xmp';size_max=2000;export_options=RC_MetadataXMP_ExportOptions
	@classmethod
	def check(cls,*,file:TextIOWrapper)->bool:
		handler=XMP_HandlerCheck();reader=xml.sax.make_parser();reader.setContentHandler(handler)
		try:reader.parse(file)
		except XMPAttributeFound as e:return _B
		except XMPAttributeNotFound as e:log.warning(f"Not passed for reason: {e}")
		except xml.sax.SAXParseException as e:log.warning(f"Not passed due to parsing exception: {e}");return _A
		return _A
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:common.IOOptionsBaseT)->int:
		tree=et.parse(file.name);root=tree.getroot();rdf=root.find(rdf_name,NAMESPACES);desc=rdf.find(rdf_desc_name,NAMESPACES);str_version=find_xcr_value(desc,'Version')
		if str_version!='3':log.warning('"Version" component not equals to "3"');return 0
		camera=common.UnifiedNameCache.ensure_camera(name=os.path.splitext(os.path.basename(file.name))[0])
		if camera is _C:return 0
		camera_props:ObjectProps=camera.cpp;cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;xmp_params:RC_MetadataXMP_Props=cam_props.rc_metadata_xmp_props;xmp_params.rc_metadata_xmp_in_texturing=get_value(as_type=bool,root_elem=desc,attr_name='InTexturing',default=_B);xmp_params.rc_metadata_xmp_in_meshing=get_value(as_type=bool,root_elem=desc,attr_name='InMeshing',default=_B);xmp_params.rc_metadata_xmp_calibration_group=get_value(as_type=int,root_elem=desc,attr_name='CalibrationGroup',default=-1);xmp_params.rc_metadata_xmp_distortion_group=get_value(as_type=int,root_elem=desc,attr_name='DistortionGroup',default=-1);pose_prior=find_xcr_value(desc,'PosePrior');coordinates=find_xcr_value(desc,'Coordinates');calibration_prior=find_xcr_value(desc,'CalibrationPrior');xmp_params.rc_metadata_xmp_export_mode=RC_METADATA_XMP_ExportMode.DO_NOT_EXPORT.name
		if pose_prior and calibration_prior and coordinates:
			export_set=pose_prior,coordinates,calibration_prior
			match export_set:
				case'initial','absolute','initial':xmp_params.rc_metadata_xmp_export_mode=RC_METADATA_XMP_ExportMode.DRAFT.name
				case'exact','relative','exact':xmp_params.rc_metadata_xmp_export_mode=RC_METADATA_XMP_ExportMode.EXACT.name
				case'locked','absolute','exact':xmp_params.rc_metadata_xmp_export_mode=RC_METADATA_XMP_ExportMode.LOCKED.name
		distortion_model=find_xcr_value(desc,'DistortionModel');cam_props.distortion_model=constants.DistortionModel.NONE.name
		match distortion_model:
			case'division':cam_props.distortion_model=constants.DistortionModel.DIVISION.name
			case'brown3'|'brown4'|'brown3t2'|'brown4t2':cam_props.distortion_model=constants.DistortionModel.BROWN.name
		cam_props.lens=find_xcr_value(desc,'FocalLength35mm');cam.sensor_fit='AUTO';cam.sensor_width=36.;cam.sensor_height=36.;cam.clip_start=.1;cam.clip_end=1e3
		if options.S:cam.clip_start*=options.S;cam.clip_end*=options.S
		cam_props.skew=find_xcr_value(desc,'Skew');cam_props.aspect=find_xcr_value(desc,'AspectRatio');cam_props.principal_x=find_xcr_value(desc,'PrincipalPointU');cam_props.principal_y=find_xcr_value(desc,'PrincipalPointV');cam_props.principal_y=-cam_props.principal_y;do_transform=_A;str_position=find_xcr_value(desc,'Position')
		if str_position is not _C:
			position=str_position.split(_D,maxsplit=2)
			if len(position)!=3:log.warning('"Position" component can not be splitted to 3 values');return 0
			xyalt:RC_XYAltProps=camera_props.rc_xyalt;xyalt.x,xyalt.y,xyalt.alt=position;do_transform=_B
		str_rotation=find_xcr_value(desc,'Rotation')
		if str_rotation is not _C:
			rotation=str_rotation.split(_D,maxsplit=8)
			if len(rotation)!=9:log.warning('"Rotation" component can not be splitted to 9 values');return 0
			rot:RC_MetadataXMP_RotationComponentProps=camera_props.rc_rotation;rot.r00,rot.r01,rot.r02,rot.r10,rot.r11,rot.r12,rot.r20,rot.r21,rot.r22=rotation;do_transform=_B
		if do_transform and options.has_transform:camera_props.apply_transform(options.R,options.S)
		str_distortion_coefficients=find_xcr_value(desc,'DistortionCoeficients')
		if str_distortion_coefficients is not _C:
			distortion_coefficients=str_distortion_coefficients.split(_D,maxsplit=5)
			if len(distortion_coefficients)!=6:log.warning('"DistortionCoeficients" component can not be splitted to 6 values');return 0
			cam_props.k1,cam_props.k2,cam_props.k3,cam_props.k4,cam_props.p1,cam_props.p2=distortion_coefficients
		return 1
	@classmethod
	def write(cls,*,directory:str,filename:str,options:RC_MetadataXMP_ExportOptions)->int:
		A='0.0';num_files=0;root=et.Element(root_name,{xmlnsx_name:NAMESPACE_X});rdf=et.SubElement(root,rdf_name,{xmlnsrdf_name:NAMESPACE_RDF});desc=et.SubElement(rdf,rdf_desc_name,{xmlnsxcr_name:NAMESPACE_XCR,version_name:'3'});tree=et.ElementTree(root);do_export_mode=_B;do_data=_B
		if options.overwrite_flags&RC_METADATA_XMP_Overwrite.rc_metadata_xmp_export_mode:
			export_mode=options.overwrite_export_mode;desc.attrib.update(_EXPORT_MODE_ENUMS[export_mode]);do_export_mode=_A
			if export_mode==RC_METADATA_XMP_ExportMode.DO_NOT_EXPORT:do_data=_A
		if do_data:position=et.SubElement(desc,position_name);rotation=et.SubElement(desc,rotation_name);distortion_coeff=et.SubElement(desc,distortion_coeff_name)
		do_calibration_group=options.use_calibration_groups
		if do_calibration_group and options.overwrite_flags&RC_METADATA_XMP_Overwrite.rc_metadata_xmp_calibration_group:desc.attrib[calibration_group_name]=str(options.overwrite_calibration_group);do_calibration_group=_A
		do_distortion_group=options.use_calibration_groups
		if do_distortion_group and options.overwrite_flags&RC_METADATA_XMP_Overwrite.rc_metadata_xmp_distortion_group:desc.attrib[distortion_group_name]=str(options.overwrite_distortion_group);do_distortion_group=_A
		do_in_texturing=options.use_include_editor_options
		if do_in_texturing and options.overwrite_flags&RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_texturing:desc.attrib[in_texturing_name]=str(int(options.overwrite_in_texturing));do_in_texturing=_A
		do_in_meshing=options.use_include_editor_options
		if do_in_meshing and options.overwrite_flags&RC_METADATA_XMP_Overwrite.rc_metadata_xmp_in_meshing:desc.attrib[in_meshing_name]=str(int(options.overwrite_in_meshing));do_in_meshing=_A
		for(name,camera)in common.IOProcessor.cached_export_items:
			fp=os.path.join(directory,os.path.splitext(name)[0]+cls.extension);camera_props:ObjectProps=camera.cpp;cam_props:CameraProps=camera.data.cpp;rc_xmp_props:RC_MetadataXMP_Props=cam_props.rc_metadata_xmp_props
			if do_export_mode:
				export_mode=RC_METADATA_XMP_ExportMode[rc_xmp_props.rc_metadata_xmp_export_mode]
				if export_mode==RC_METADATA_XMP_ExportMode.DO_NOT_EXPORT:do_data=_A
				else:desc.attrib.update(_EXPORT_MODE_ENUMS[export_mode])
			if do_data:
				xyalt:RC_XYAltProps=camera_props.rc_xyalt;rot:RC_MetadataXMP_RotationComponentProps=camera_props.rc_rotation;position.text=_D.join(str(_)for _ in xyalt.as_array(R=options.R,S=options.S));rotation.text=_D.join(str(_)for _ in rot.as_array(R=options.R,S=options.S))
				if cam_props.distortion_model==constants.DistortionModel.NONE.name:desc.attrib[distortion_model_name]='perspective';coeff=(A for _ in range(6))
				elif cam_props.distortion_model==constants.DistortionModel.DIVISION.name:desc.attrib[distortion_model_name]='division';coeff=(cam_props.k1_double,)+tuple(A for _ in range(5))
				else:
					dm='brown'
					if cam_props.k4:dm+='4'
					else:dm+='3'
					if cam_props.p1 or cam_props.p2:dm+='t2'
					desc.attrib[distortion_model_name]=dm;coeff=cam_props.k1_double,cam_props.k2_double,cam_props.k3_double,cam_props.k4_double,cam_props.p1_double,cam_props.p2_double
				distortion_coeff.text=_D.join(coeff);desc.attrib[focal_length_35mm_name]=cam_props.lens_double;desc.attrib[skew_name]=cam_props.skew_double;desc.attrib[aspect_ratio_name]=cam_props.aspect_double;desc.attrib[principal_point_u_name]=cam_props.principal_x_double;desc.attrib[principal_point_v_name]=str(-cam_props.principal_y)
			if do_calibration_group:desc.attrib[calibration_group_name]=str(rc_xmp_props.rc_metadata_xmp_calibration_group)
			if do_distortion_group:desc.attrib[distortion_group_name]=str(rc_xmp_props.rc_metadata_xmp_distortion_group)
			if do_in_texturing:desc.attrib[in_texturing_name]=str(int(rc_xmp_props.rc_metadata_xmp_in_texturing))
			if do_in_meshing:desc.attrib[in_meshing_name]=str(int(rc_xmp_props.rc_metadata_xmp_in_meshing))
			et.indent(tree,space=_D*4,level=0);tree.write(fp,encoding='utf-8',short_empty_elements=_A);num_files+=1
		return num_files