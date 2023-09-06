from __future__ import annotations
_D='utf-8'
_C=None
_B='.csv'
_A=','
from io import TextIOWrapper
from typing import Iterable
import csv,os
from..import common
from...import constants
from...import log
from typing import TYPE_CHECKING
if TYPE_CHECKING:from...props import Camera;from...props.camera import CameraProps;from...props.ob import ObjectProps;from...props.intern.rc_csv import RC_HeadingPitchRollProps,RC_OmegaPhiKappaProps,RC_XYAltProps
__all__='RC_IECP','RC_NXYZ','RC_NXYZHPR','RC_NXYZOPK'
class RC_CSV_ExportOptions(common.IOOptionsBase):
	__slots__='write_num_cameras',;write_num_cameras:bool
	def __init__(self,**kwargs):super().__init__(**kwargs);self.write_num_cameras=kwargs['rc_csv_write_num_cameras']
class RC_CSV_Common(common.IOFileHandler):
	rc_csv_line:str;export_options=RC_CSV_ExportOptions
	@classmethod
	def check(cls,*,file:TextIOWrapper)->bool:
		if len(file.read(1))>0:
			file.seek(0);line=file.readline()
			if line.startswith('#cameras '):line=file.readline()
			line=line.replace('\n','').replace('\r','');return line==cls.rc_csv_line
		return False
	@classmethod
	def evaluate_filename(cls,*,name:str)->str:return name.replace(' ','_')
	@staticmethod
	def set_xyalt(*,camera_props:ObjectProps,data:Iterable[str]):xyalt:RC_XYAltProps=camera_props.rc_xyalt;xyalt.x=data[0];xyalt.y=data[1];xyalt.alt=data[2]
	@staticmethod
	def set_hpr(*,camera_props:ObjectProps,data:Iterable[str]):hpr:RC_HeadingPitchRollProps=camera_props.rc_hpr;hpr.heading=data[0];hpr.pitch=data[1];hpr.roll=data[2]
	@classmethod
	def write_header(cls,*,file:TextIOWrapper,options:RC_CSV_ExportOptions):
		if options.write_num_cameras:file.write(f"#cameras {len(common.IOProcessor.cached_export_items)}\n")
		file.write(cls.rc_csv_line+'\n')
class RC_IECP(RC_CSV_Common):
	io_format=common.IOFormat.RC_IECP;extension=_B;rc_csv_line='#name,x,y,alt,heading,pitch,roll,f,px,py,k1,k2,k3,k4,t1,t2'
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:common.IOOptionsBaseT)->int:
		reader=csv.reader(file,delimiter=_A);skipped=0
		for(i,line)in enumerate(reader,start=1):
			if len(line)!=16:log.warning(f"Line {line} is skipped because it is not 16 elements long");continue
			camera=common.UnifiedNameCache.ensure_camera(name=line[0])
			if camera is _C:skipped+=1;continue
			camera_props:ObjectProps=camera.cpp;cam:Camera=camera.data;cam_props:CameraProps=cam.cpp;cls.set_xyalt(camera_props=camera_props,data=line[1:4]);cls.set_hpr(camera_props=camera_props,data=line[4:7])
			if options.has_transform:camera_props.apply_transform(options.R,options.S)
			f,px,py,k1,k2,k3,k4,t1,t2=line[7:16];cam_props.lens=f;cam_props.principal_x=px;cam_props.principal_y=py;cam_props.k1=k1;cam_props.k2=k2;cam_props.k3=k3;cam_props.k4=k4;cam_props.p1=t1;cam_props.p2=t2;cam.sensor_width=36.;cam.sensor_height=36.
			if cam_props.k1 or cam_props.k2 or cam_props.k3 or cam_props.k4 or cam_props.p1 or cam_props.p2:cam_props.distortion_model=constants.DistortionModel.BROWN.name
		return i-skipped
	@classmethod
	def write(cls,*,directory:str,filename:str,options:RC_CSV_ExportOptions):
		with open(os.path.join(directory,filename),'w',encoding=_D,newline='')as file:
			cls.write_header(file=file,options=options);writer=csv.writer(file,delimiter=_A)
			for(name,camera)in common.IOProcessor.cached_export_items:camera_props:ObjectProps=camera.cpp;xyalt:RC_XYAltProps=camera_props.rc_xyalt;hpr:RC_HeadingPitchRollProps=camera_props.rc_hpr;cam_props:CameraProps=camera.data.cpp;writer.writerow((name,*xyalt.as_array(R=options.R,S=options.S),*hpr.as_array(R=options.R,S=options.S),cam_props.lens_double,cam_props.principal_x_double,cam_props.principal_y_double,cam_props.k1_double,cam_props.k2_double,cam_props.k3_double,cam_props.k4_double,cam_props.p1_double,cam_props.p2_double))
		return 1
class RC_NXYZ(RC_CSV_Common):
	io_format=common.IOFormat.RC_NXYZ;extension=_B;rc_csv_line='#name,x,y,z'
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:common.IOOptionsBaseT)->int:
		reader=csv.reader(file,delimiter=_A);skipped=0
		for(i,line)in enumerate(reader,start=1):
			if len(line)!=4:log.warning(f"Line {line} is skipped because it is not 4 elements long");continue
			camera=common.UnifiedNameCache.ensure_camera(name=line[0])
			if camera is _C:skipped+=1;continue
			camera_props:ObjectProps=camera.cpp;cls.set_xyalt(camera_props=camera_props,data=line[1:4])
			if options.has_transform:camera_props.apply_transform(options.R,options.S)
		return i-skipped
	@classmethod
	def write(cls,*,directory:str,filename:str,options:RC_CSV_ExportOptions):
		with open(os.path.join(directory,filename),'w',encoding=_D,newline='')as file:
			cls.write_header(file=file,options=options);writer=csv.writer(file,delimiter=_A)
			for(name,camera)in common.IOProcessor.cached_export_items:camera_props:ObjectProps=camera.cpp;xyalt:RC_XYAltProps=camera_props.rc_xyalt;writer.writerow((name,*xyalt.as_array(R=options.R,S=options.S)))
		return 1
class RC_NXYZHPR(RC_CSV_Common):
	io_format=common.IOFormat.RC_NXYZHPR;extension=_B;rc_csv_line='#name,x,y,z,omega,phi,kappa'
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:common.IOOptionsBaseT)->int:
		reader=csv.reader(file,delimiter=_A);skipped=0
		for(i,line)in enumerate(reader,start=1):
			if len(line)!=7:log.warning(f"Line {line} is skipped because it is not 7 elements long");continue
			camera=common.UnifiedNameCache.ensure_camera(name=line[0])
			if camera is _C:skipped+=1;continue
			camera_props:ObjectProps=camera.cpp;cls.set_xyalt(camera_props=camera_props,data=line[1:4]);cls.set_hpr(camera_props=camera_props,data=line[4:7])
			if options.has_transform:camera_props.apply_transform(options.R,options.S)
		return i-skipped
	@classmethod
	def write(cls,*,directory:str,filename:str,options:RC_CSV_ExportOptions):
		with open(os.path.join(directory,filename),'w',encoding=_D,newline='')as file:
			cls.write_header(file=file,options=options);writer=csv.writer(file,delimiter=_A)
			for(name,camera)in common.IOProcessor.cached_export_items:camera_props:ObjectProps=camera.cpp;xyalt:RC_XYAltProps=camera_props.rc_xyalt;hpr:RC_HeadingPitchRollProps=camera_props.rc_hpr;writer.writerow((name,*xyalt.as_array(R=options.R,S=options.S),*hpr.as_array(R=options.R,S=options.S)))
		return 1
class RC_NXYZOPK(RC_CSV_Common):
	io_format=common.IOFormat.RC_NXYZOPK;extension=_B;rc_csv_line='#name,x,y,z,heading,pitch,roll'
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:common.IOOptionsBaseT)->int:
		reader=csv.reader(file,delimiter=_A);skipped=0
		for(i,line)in enumerate(reader,start=1):
			if len(line)!=7:log.warning(f"Line {line} is skipped because it is not 7 elements long");continue
			camera=common.UnifiedNameCache.ensure_camera(name=line[0])
			if camera is _C:skipped+=1;continue
			camera_props:ObjectProps=camera.cpp;cls.set_xyalt(camera_props=camera_props,data=line[1:4]);opk:RC_OmegaPhiKappaProps=camera_props.rc_opk;opk.omega=line[4];opk.phi=line[5];opk.kappa=line[6]
			if options.has_transform:camera_props.apply_transform(options.R,options.S)
		return i-skipped
	@classmethod
	def write(cls,*,directory:str,filename:str,options:RC_CSV_ExportOptions):
		with open(os.path.join(directory,filename),'w',encoding=_D,newline='')as file:
			cls.write_header(file=file,options=options);writer=csv.writer(file,delimiter=_A)
			for(name,camera)in common.IOProcessor.cached_export_items:camera_props:ObjectProps=camera.cpp;xyalt:RC_XYAltProps=camera_props.rc_xyalt;opk:RC_OmegaPhiKappaProps=camera_props.rc_opk;writer.writerow((name,*xyalt.as_array(R=options.R,S=options.S),*opk.as_array(R=options.R,S=options.S)))
		return 1