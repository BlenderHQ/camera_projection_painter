from __future__ import annotations
_N='property'
_M='sensor'
_L='sensors'
_K='metashape'
_J='value'
_I='transform'
_H='valid'
_G='cameras'
_F='components'
_E='id'
_D=True
_C=False
_B=None
_A=.0
import os,csv
from io import TextIOWrapper
import xml.sax
from xml.etree import ElementTree as et
from xml.sax.handler import ContentHandler
from math import atan2,asin
from...import constants
from...import Reports
from..import common
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import Generator,Generic,TypeVar,Iterator;T=TypeVar('T');from...props import Object,Camera,Float64ArrayT;from...props.ob import ObjectProps;from...props.camera import CameraProps
__all__='MS_XML',
class MS_PIDXYZOPK_ExportParams(common.IOExportParamsBase):0
class MS_PIDXYZOPK_ExportOptions(common.IOTransformOptionsBase):0
class MS_PIDXYZOPK_Camera(common.IOObjectTransform):
	def set_camera_data(self,*,camera:Object):camera_props:ObjectProps=camera.cpp;camera_props.location=self.location;camera_props.rotation=self.rotation
class MS_PIDXYZOPK(common.CSV_FileFormatHandlerBase):
	name='Omega, Phi, Kappa (.txt)';icon=_K;io_format=common.IOFileFormat.MS_PIDXYZOPK;possibilities=common.IOFileFormatPossibilities.IMPORT|common.IOFileFormatPossibilities.EXPORT;extension='.txt';export_params=MS_PIDXYZOPK_ExportParams;export_options=MS_PIDXYZOPK_ExportOptions;check_num_line_start='# Cameras (';csv_description_line='# PhotoID, X, Y, Z, Omega, Phi, Kappa, r11, r12, r13, r21, r22, r23, r31, r32, r33';sep_character='\t';comment_character='#';float_data_count=15
	@classmethod
	def evaluate_filename(cls,*,name:str)->str:return name
	@classmethod
	def read(cls,*,r_data:list,file:TextIOWrapper,options:common.IOExportOptionsBaseT)->int:
		import numpy as np;skipped=0
		for(i,line)in enumerate(cls.iter_lines(file=file)):
			if line is _B:skipped+=1
			else:
				name,data=line;un=common.InputNameCache.eval_unified_name_from_cache(name=name)
				if un is _B:skipped+=1;continue
				c=MS_PIDXYZOPK_Camera();c.name=un;c.location=data[:3];c.rotation=np.transpose(data[6:].reshape((3,3)))
				if options.has_transform:c.apply_transform(R=options.R,S=options.S)
				r_data.append(c)
		return i-skipped
	@classmethod
	def write(cls,*,directory:str,filename:str,options:MS_PIDXYZOPK_ExportOptions)->int:
		import numpy as np
		with open(os.path.join(directory,filename),'w',encoding='utf-8',newline='')as file:
			cls.write_header(file=file,num_format='# Cameras ({num})\n');writer=csv.writer(file,delimiter=cls.sep_character)
			for(name,camera)in common.OutputNameCache.cached_camera_names:camera_props:ObjectProps=camera.cpp;loc=camera_props.location_as_array(R=options.R,S=options.S);rot=camera_props.rotation_as_array(R=options.R,S=options.S);opk=np.degrees(np.array((-atan2(rot[1][2],rot[2][2]),asin(rot[0][2]),atan2(-rot[0][1],rot[0][0])),dtype=np.float64,order='C'));writer.writerow((name,*loc,*opk,*np.transpose(rot).ravel()))
		return 1
root_name='document'
version_name='version'
chunk_name='chunk'
sensors_name=_L
sensor_name=_M
components_name=_F
cameras_name=_G
class XMLAttributeFound(xml.sax.SAXException):0
class XMLAttributeNotFound(xml.sax.SAXException):0
class XML_HandlerCheck(ContentHandler):
	def __init__(self):super().__init__();self.check_root=_C;self.check_chunk=_C;self.check_sensors=_C;self.check_components=_C;self.check_cameras=_C
	def _check_terminate(self):
		if self.check_root and self.check_chunk and self.check_sensors and self.check_components and self.check_cameras:raise XMLAttributeFound('Ok')
	def startElement(self,name,attrs):
		if not self.check_root and name==root_name:
			if attrs.get(version_name,'')=='2.0.0':self.check_root=_D;self._check_terminate()
			else:raise XMLAttributeNotFound(f'Attribute "{version_name}" not equals to "2.0.0"')
		if not self.check_chunk and name==chunk_name:self.check_chunk=_D;self._check_terminate()
		if not self.check_sensors and name==sensors_name:self.check_sensors=_D;self._check_terminate()
		if not self.check_components and name==components_name:self.check_components=_D;self._check_terminate()
		if not self.check_cameras and name==cameras_name:self.check_cameras=_D;self._check_terminate()
	def endDocument(self):
		if not self._check_terminate():
			not_found=[]
			if not self.check_root:not_found.append(root_name)
			if not self.check_chunk:not_found.append(chunk_name)
			if not self.check_sensors:not_found.append(sensors_name)
			if not self.check_components:not_found.append(components_name)
			if not self.check_cameras:not_found.append(cameras_name)
			not_found_fmt=', '.join(not_found);raise XMLAttributeNotFound(f"Document is missing <{not_found_fmt}> attribute(s)")
class XMLComponent:
	__slots__=_H,_E,_I;valid:bool;id:int;transform:_B|Float64ArrayT
	def __init__(self,elem:et.Element)->_B:
		C='translation';B='Document component translation data is missing rotation node';A='rotation';import numpy as np;self.valid=_C;self.id=0;self.transform=_B;self.id=get_value(as_type=int,root_elem=elem,attr_name=_E,default=0);_transform=elem.find(_I)
		if _transform is _B:Reports.log.warning('Document component data is missing transform node');return
		_transform_rotation=_transform.find(A)
		if _transform_rotation is _B:Reports.log.warning(B);return
		str_val=find_value(_transform,A)
		try:R:Float64ArrayT=np.fromstring(str_val,dtype=np.float64,count=9,sep=' ')
		except ValueError:Reports.log.warning(B);return
		_transform_translation=_transform.find(C)
		if _transform_translation is _B:Reports.log.warning('Document component translation data is missing translation node');return
		str_val=find_value(_transform,C)
		try:P:Float64ArrayT=np.fromstring(str_val,dtype=np.float64,count=3,sep=' ')
		except ValueError:Reports.log.warning(f"Unable to evaluate component transform translation data");return
		M=np.zeros((4,4),dtype=np.float64);M[:3,:3]=R.reshape((3,3));M[:3,3]=P;M[3,3]=1.;self.transform=M;self.valid=_D
class XMLChunk:
	__slots__=_H,_F,_L,_G;valid:bool;components:dict[int,XMLComponent];sensors:dict[int,XMLSensor];cameras:list[MS_XML_Camera]
	def __init__(self,*,elem:et.Element):
		self.valid=_C;self.components=dict();self.sensors=dict();self.cameras=list();_components=elem.find(_F)
		if _components is _B:Reports.log.warning('Document is missing components data');return
		for _component in _components:_c=XMLComponent(_component);self.components[_c.id]=_c
		_sensors=elem.find(sensors_name)
		if _sensors is _B:Reports.log.warning('Missing sensors data in chunk');return
		self.sensors=dict()
		for _sensor in iter_sub_elements(_sensors,sensor_name):_s=XMLSensor(_sensor);self.sensors[_s.id]=_s
		_cameras=elem.find(_G)
		if _cameras is _B:Reports.log.warning('Document is missing cameras extrinsic parameters');return
		self.cameras=list()
		for _camera in iter_sub_elements(_cameras,attr_name='camera'):
			_c=MS_XML_Camera(chunk=self,elem=_camera)
			if _c.valid:self.cameras.append(_c)
		if self.cameras:self.valid=_D
class XMLSensor:
	__slots__=_H,_E,'lens',_M,'sensor_fit','principal_x','principal_y','k1','k2','k3','k4','p1','p2';valid:bool;id:int;lens:float;sensor:float;sensor_fit:str;principal_x:float;principal_y:float;k1:float;k2:float;k3:float;k4:float;p1:float;p2:float
	def __init__(self,elem:et.Element):
		self.valid=_C;self.id=0;self.lens=_A;self.sensor=_A;self.sensor_fit='';self.principal_x=_A;self.principal_y=_A;self.k1=_A;self.k2=_A;self.k3=_A;self.k4=_A;self.p1=_A;self.p2=_A;self.id=get_value(as_type=int,root_elem=elem,attr_name=_E,default=0);_resolution=elem.find('resolution')
		if _resolution is _B:Reports.log.warning(f'Sensor {self.id} data is missing "resolution" node');return
		width=get_value(as_type=int,root_elem=_resolution,attr_name='width',default=0);height=get_value(as_type=int,root_elem=_resolution,attr_name='height',default=0)
		if not(width and height):Reports.log.warning(f"Sensor {self.id} data has zero resolution");return
		for _prop in iter_sub_elements(elem,_N):
			_name=find_value(_prop,'name')
			if _name is _B:Reports.log.warning(f"One of sensor {self.id} properties is missing name attribute");return
			match _name:
				case'pixel_width':pixel_width=get_value(as_type=float,root_elem=_prop,attr_name=_J,default=_A)
				case'pixel_height':pixel_height=get_value(as_type=float,root_elem=_prop,attr_name=_J,default=_A)
		_calibration=elem.find('calibration')
		if _calibration is _B:Reports.log.warning(f"Sensor {self.id} is missing calibration node");return
		f=get_value(as_type=float,root_elem=_calibration,attr_name='f',default=_A);self.lens=f*((pixel_width+pixel_height)/2.)
		if height>width:self.sensor_fit='VERTICAL';self.sensor=height*pixel_height
		else:self.sensor_fit='HORIZONTAL';self.sensor=width*pixel_width
		cx=get_value(as_type=float,root_elem=_calibration,attr_name='cx',default=_A);cy=get_value(as_type=float,root_elem=_calibration,attr_name='cy',default=_A);self.principal_x=cx/width;self.principal_y=-cy/height;self.k1=get_value(as_type=float,root_elem=_calibration,attr_name='k1',default=_A);self.k2=get_value(as_type=float,root_elem=_calibration,attr_name='k2',default=_A);self.k3=get_value(as_type=float,root_elem=_calibration,attr_name='k3',default=_A);self.k4=get_value(as_type=float,root_elem=_calibration,attr_name='k4',default=_A);self.p1=get_value(as_type=float,root_elem=_calibration,attr_name='p1',default=_A);self.p2=get_value(as_type=float,root_elem=_calibration,attr_name='p2',default=_A);self.valid=_D
class MS_XML_Camera(common.IOObjectTransform):
	valid:bool;sensor:XMLSensor
	def __init__(self,chunk:XMLChunk,elem:et.Element):
		import numpy as np;self.valid=_C;label=find_value(elem,'label')
		if label is _B:Reports.log.warning('One of camera nodes is missing name label');return
		un=common.InputNameCache.eval_unified_name_from_cache(name=label)
		if un is _B:return
		self.name=un;sensor_id=get_value(as_type=int,root_elem=elem,attr_name='sensor_id',default=0);self.sensor=chunk.sensors.get(sensor_id,_B)
		if self.sensor is _B:Reports.log.warning(f"Camera {label} points to missing sensor index {sensor_id}");return
		component_id=get_value(as_type=int,root_elem=elem,attr_name='component_id',default=0);component:XMLComponent=chunk.components.get(component_id,_B)
		if component is _B:Reports.log.warning(f'Camera "{label}" points to missing component id {component_id}');return
		self.component=component;str_transform=find_value(elem,_I)
		if str_transform is _B:Reports.log.warning(f'Camera "{label}" is missing transform node');return
		try:transform=np.fromstring(str_transform,dtype=np.float64,count=16,sep=' ')
		except ValueError:Reports.log.warning(f'Camera "{label}" unable to evaluate transform data');return
		transform=transform.reshape((4,4));M:Float64ArrayT=np.matmul(component.transform,transform);_ROTATION_CONVERSION_MATRIX=np.array(((1.,_A,_A),(_A,-1.,_A),(_A,_A,-1.)),dtype=np.float64,order='C');self.rotation=np.matmul(M[:3,:3],_ROTATION_CONVERSION_MATRIX);self.location=M[:3,3];self.valid=_D
	def set_camera_data(self,*,camera:Object):camera_props:ObjectProps=camera.cpp;cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;camera_props.location=self.location;camera_props.rotation=self.rotation;cam_props.lens=self.sensor.lens;cam_props.sensor=self.sensor.sensor;cam.sensor_fit=self.sensor.sensor_fit;cam_props.principal_x=self.sensor.principal_x;cam_props.principal_y=self.sensor.principal_y;cam_props.distortion_model=constants.DistortionModel.BROWN.name;cam_props.k1=self.sensor.k1;cam_props.k2=self.sensor.k2;cam_props.k3=self.sensor.k3;cam_props.k4=self.sensor.k4;cam_props.p1=self.sensor.p1;cam_props.p2=self.sensor.p2
def find_value(root_elem:et.Element,attr_name:str)->_B|str:
	found=root_elem.find(attr_name)
	if found is not _B:
		if found.text:return found.text
	attr=root_elem.get(attr_name)
	if attr is not _B:return attr
def get_value(*,as_type:T,root_elem:et.Element,attr_name:str,default:T)->Generic[T]:
	str_val=find_value(root_elem=root_elem,attr_name=attr_name)
	if str_val:
		try:ret=as_type(str_val)
		except ValueError:return default
		return ret
	return default
def iter_sub_elements(root_elem:et.Element,attr_name:str)->Generator[et.Element]:
	for elem in root_elem.iterfind(attr_name):yield elem
def get_sub_properties(root_elem:et.Element):
	ret=dict()
	for prop in root_elem.iter(_N):
		prop_name=find_value(prop,'name');prop_value=find_value(prop,_J)
		if prop_name is not _B and prop_value is not _B:ret[prop_name]=prop_value
	return ret
class MS_XML(common.IOFileFormatHandler):
	name='Agisoft XML';icon=_K;io_format=common.IOFileFormat.MS_XML;extension='.xml';possibilities=common.IOFileFormatPossibilities.IMPORT
	@classmethod
	def check(cls,*,file:TextIOWrapper)->bool:
		handler=XML_HandlerCheck();reader=xml.sax.make_parser();reader.setContentHandler(handler)
		try:reader.parse(file)
		except XMLAttributeFound as e:return _D
		except XMLAttributeNotFound as e:Reports.log.warning(f"Not passed for reason: {e}")
		except xml.sax.SAXParseException as e:Reports.log.warning(f"Not passed due to parsing exception: {e}");return _C
		return _C
	@classmethod
	def evaluate_filename(cls,*,name:str)->str:return name
	@classmethod
	def read(cls,*,r_data:list,file:TextIOWrapper,options:common.IOExportOptionsBaseT)->int:
		tree=et.parse(file.name);document=tree.getroot();chunks:list[XMLChunk]=list()
		for _elem in iter_sub_elements(document,chunk_name):
			chunk=XMLChunk(elem=_elem)
			if chunk.valid:chunks.append(chunk)
		if not chunks:Reports.log.warning('No valid chunks in file');return 0
		r_data.extend(_c for chunk in chunks for _c in chunk.cameras);return 1
	@classmethod
	def write(cls,*,directory:str,filename:str,options:common.IOTransformOptionsBase)->int:return 0