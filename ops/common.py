from __future__ import annotations
_R='EXEC_DEFAULT'
_Q='un_flags'
_P='directory'
_O='global_scale'
_N='PROP_UN_FLAGS'
_M='utf-8'
_L='NEGATIVE_Z'
_K='NEGATIVE_Y'
_J='NEGATIVE_X'
_I=False
_H='lval'
_G='XYZ'
_F='SKIP_SAVE'
_E='HIDDEN'
_D='CPP_IO'
_C='Z'
_B='Y'
_A=None
import glob,os,time
from importlib import reload
from enum import auto,IntEnum,IntFlag
from typing import TypeVar
from..import Reports,log
from..import constants
from..import main
from..import icons
from..props.intern import double
import bpy
from bpy.types import Context,Event,Operator,OperatorFileListElement
from bpy.props import CollectionProperty,EnumProperty,StringProperty
import bpy_extras
from typing import TYPE_CHECKING
if TYPE_CHECKING:from io import TextIOWrapper;from typing import Callable,Iterable,Type;from..props import Object;from..props import Camera,Image;from..props.wm import WMProps;from..props.intern.common import Float64ArrayT
__all__='UnifiedNameOptions','DEFAULT_UnifiedNameOptions','FileFormat','IMAGE_FILE_EXTENSIONS','CSV_FILE_EXTENSIONS','XML_FILE_EXTENSIONS','UnifiedName','UnifiedNameCache',_N,'IOFormat','IOOptionsBase','IOFileHandler','IOProcessor','io_helper','CENTERED_DIALOG_ICON_SCALE','CENTERED_DIALOG_PROPS_UI_UNITS_X','invoke_props_dialog_centered','StageStatus','SetupContextOperator'
class UnifiedNameOptions(IntFlag):
	IGNORE_LETTER_CASE=auto();IGNORE_EXTENSION=auto();USE_CAMERA_NAME=auto();USE_CAM_NAME=auto();USE_IMAGE_NAME=auto();USE_IMAGE_FILEPATH=auto()
	@staticmethod
	def from_string_set(values:set[str])->UnifiedNameOptions:
		ret=0
		for item in values:ret|=UnifiedNameOptions[item]
		return ret
DEFAULT_UnifiedNameOptions=UnifiedNameOptions.IGNORE_LETTER_CASE|UnifiedNameOptions.IGNORE_EXTENSION|UnifiedNameOptions.USE_CAMERA_NAME|UnifiedNameOptions.USE_CAM_NAME|UnifiedNameOptions.USE_IMAGE_NAME|UnifiedNameOptions.USE_IMAGE_FILEPATH
class FileFormat(IntEnum):IMAGE=auto();CSV=auto();XML=auto()
IMAGE_FILE_EXTENSIONS={'.bmp','.sgi','.rgb','.bw','.png','.jpg','.jpeg','.jp2','.j2c','.tga','.cin','.dpx','.exr','.hdr','.tif','.tiff','.psd'}
CSV_FILE_EXTENSIONS={'.csv','.txt'}
XML_FILE_EXTENSIONS={'.xmp'}
class UnifiedName:
	__slots__='item',_H,'done';item:str|Object|Image;lval:set[str];done:bool
	def _evaluate_lval(self,*,names:set[str],flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions):
		self.lval=names
		if flags&UnifiedNameOptions.IGNORE_LETTER_CASE and flags&UnifiedNameOptions.IGNORE_EXTENSION:self.lval=set(os.path.splitext(_)[0].lower()for _ in self.lval);return
		if flags&UnifiedNameOptions.IGNORE_LETTER_CASE:self.lval=set(_.lower()for _ in self.lval)
		if flags&UnifiedNameOptions.IGNORE_EXTENSION:self.lval=set(os.path.splitext(_)[0]for _ in self.lval if'.'in _)
	@staticmethod
	def from_image(*,image:Image,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions)->UnifiedName:
		ret=UnifiedName()
		def _iter_image_names()->str:
			if flags&UnifiedNameOptions.USE_IMAGE_NAME:yield image.name
			if flags&UnifiedNameOptions.USE_IMAGE_FILEPATH:
				if image.filepath and os.path.isfile(bpy.path.abspath(image.filepath)):yield os.path.basename(image.filepath)
		ret._evaluate_lval(names=set(_iter_image_names()),flags=flags);ret.item=image;return ret
	@staticmethod
	def from_object(*,ob:Object,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions)->UnifiedName:
		ret=UnifiedName()
		def _iter_object_names()->str:
			if flags&UnifiedNameOptions.USE_CAMERA_NAME:yield ob.name
			if flags&UnifiedNameOptions.USE_CAM_NAME:yield ob.data.name
		ret._evaluate_lval(names=set(_iter_object_names()),flags=flags);ret.item=ob;return ret
	@staticmethod
	def from_path(*,fp:str,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions)->UnifiedName:ret=UnifiedName();ret._evaluate_lval(names={os.path.basename(fp)},flags=flags);ret.item=fp;return ret
	@staticmethod
	def from_string(*,val:str,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions)->UnifiedName:ret=UnifiedName();ret._evaluate_lval(names={val},flags=flags);ret.item=_A;return ret
	def __hash__(self)->int:return hash(self.item)
	def __eq__(self,other:UnifiedName)->bool:return self.lval&other.lval
	def __repr__(self)->str:return'|'.join(self.lval)
	def __getstate__(self):return{_H:self.lval}
	def __setstate__(self,state):self.lval=state[_H]
class UnifiedNameCache:
	__slots__=();_cached_image_names:set[UnifiedName]=set();_cached_camera_names:set[UnifiedName]=set();_cached_file_names:set[UnifiedName]=set();_cache_flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions
	@classmethod
	@property
	def cached_image_names(cls)->set[UnifiedName]:return cls._cached_image_names
	@classmethod
	def update_eval_images_cache(cls,*,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions):cls._cached_image_names=set(UnifiedName.from_image(image=image,flags=flags)for image in bpy.data.images);cls._cache_flags=flags
	@classmethod
	@property
	def cached_camera_names(cls)->set[UnifiedName]:return cls._cached_camera_names
	@classmethod
	def update_eval_cameras_cache(cls,context:Context,*,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions):cls._cached_camera_names=set(UnifiedName.from_object(ob=ob,flags=flags)for ob in context.scene.objects if main.Workflow.camera_poll(ob));cls._cache_flags=flags
	@classmethod
	@property
	def cached_file_names(cls)->set[UnifiedName]:return cls._cached_file_names
	@classmethod
	def update_eval_directory_cache(cls,*,directory:str,file_format:FileFormat=FileFormat.IMAGE,flags:UnifiedNameOptions=DEFAULT_UnifiedNameOptions):
		match file_format:
			case FileFormat.IMAGE:extensions_filter_set=IMAGE_FILE_EXTENSIONS
			case FileFormat.CSV:extensions_filter_set=CSV_FILE_EXTENSIONS
			case FileFormat.XML:extensions_filter_set=XML_FILE_EXTENSIONS
		cls._cached_file_names=set(UnifiedName.from_path(fp=file,flags=flags)for file in glob.iglob(f"{directory}*.*")if os.path.splitext(file)[1].lower()in extensions_filter_set);cls._cache_flags=flags
	@classmethod
	@property
	def cache_flags(cls)->UnifiedNameOptions:return cls._cache_flags
	@classmethod
	def ensure_camera(cls,*,name:str)->_A|Object:
		un=UnifiedName.from_string(val=name,flags=cls.cache_flags)
		for item in cls.cached_camera_names:
			if un==item:
				if getattr(item,'done',_I):log.info(f"{name} skipped as already done");return
				item.done=True;return item.item
		cam=bpy.data.cameras.new(name='');camera=bpy.data.objects.new(name=name,object_data=cam);bpy.context.collection.objects.link(camera);log.info(f'A missing camera object was created "{name}"');new_un=UnifiedName.from_object(ob=camera,flags=cls._cache_flags);new_un.done=True;cls._cached_camera_names.add(new_un);return camera
class IOFormat(IntEnum):UNKNOWN=auto();RC_IECP=auto();RC_NXYZ=auto();RC_NXYZHPR=auto();RC_NXYZOPK=auto();RC_METADATA_XMP=auto()
class IOOptionsBase:
	__slots__='has_transform','R','S';has_transform:bool;R:Float64ArrayT;S:float
	def __init__(self,**kwargs):
		import numpy as np;forward_axis=kwargs['forward_axis'];up_axis=kwargs['up_axis'];global_scale=kwargs[_O]
		if forward_axis==_B and up_axis==_C and global_scale==1.:self.has_transform=_I;self.R=_A;self.S=_A
		else:
			self.has_transform=True
			def _fix_axes_enum_name(value):return{'X':'X',_B:_B,_C:_C,_J:'-X',_K:'-Y',_L:'-Z'}[value]
			forward_axis=_fix_axes_enum_name(forward_axis);up_axis=_fix_axes_enum_name(up_axis);self.R=np.array(bpy_extras.io_utils.axis_conversion(from_forward=_B,from_up=_C,to_forward=forward_axis,to_up=up_axis),dtype=np.float64,order='C');self.S=global_scale
IOOptionsBaseT=TypeVar('IOOptionsBaseT',bound=IOOptionsBase)
class IOFileHandler:
	io_format:IOFormat;extension:str;size_max:int=-1;export_options:Type[IOOptionsBase]=IOOptionsBase
	@classmethod
	def check(cls,*,file:TextIOWrapper)->bool:return _I
	@classmethod
	def evaluate_filename(cls,*,name:str)->str:return name
	@classmethod
	def read(cls,*,file:TextIOWrapper,options:IOOptionsBaseT)->int:0
	@classmethod
	def write(cls,*,directory:str,filename:str,options:Type[IOOptionsBase])->int:0
class IOProcessor:
	__format_registry:list[IOFileHandler]=list();supported_extensions:list[str]=list();_filter_glob:str='';cached_export_items:tuple[tuple[str,Object]]=tuple()
	@classmethod
	def register_file_format(cls,item:IOFileHandler):cls.__format_registry.append(item);cls.supported_extensions.append(item.extension)
	@classmethod
	@property
	def filter_glob(cls)->str:
		if not cls._filter_glob:cls.filter_glob=';'.join({f"*{_}"for _ in cls.supported_extensions})
		return cls._filter_glob
	@classmethod
	def filter_glob_of(cls,*,format:IOFormat)->str:
		ext=cls.extension_of(format=format)
		if ext:return f"*{ext}"
		return''
	@classmethod
	def extension_of(cls,*,format:IOFormat)->str:
		for item in cls.__format_registry:
			if item.io_format==format:return item.extension
		return''
	@classmethod
	def eval_filename(cls,*,format:IOFormat,name:str)->str:
		for item in cls.__format_registry:
			if item.io_format==format:return item.evaluate_filename(name=name)
		return name
	@classmethod
	def check(cls,*,directory:str,files:Iterable[OperatorFileListElement])->dict[IOFormat,int]:
		ret=dict.fromkeys(IOFormat,0)
		for elem in files:
			_name,ext=os.path.splitext(elem.name);ext=ext.lower()
			if ext in cls.supported_extensions:
				filepath=os.path.join(directory,elem.name)
				if os.path.isfile(filepath):
					with open(filepath,'r',encoding=_M,newline='')as file:
						for handler_cls in cls.__format_registry:
							if ext==handler_cls.extension:
								if handler_cls.size_max!=-1:
									if handler_cls.size_max<os.path.getsize(filepath):continue
								file.seek(0)
								if handler_cls.check(file=file):ret[handler_cls.io_format]+=1
		return ret
	@classmethod
	def eval_fmt(cls,*,directory:str,files:Iterable[OperatorFileListElement])->IOFormat:
		for elem in files:
			_name,ext=os.path.splitext(elem.name);ext=ext.lower()
			if ext in cls.supported_extensions:
				filepath=os.path.join(directory,elem.name)
				if os.path.isfile(filepath):
					with open(filepath,'r',encoding=_M,newline='')as file:
						for handler_cls in cls.__format_registry:
							if ext==handler_cls.extension:
								if handler_cls.size_max!=-1:
									if handler_cls.size_max<os.path.getsize(filepath):continue
								file.seek(0)
								if handler_cls.check(file=file):return handler_cls.io_format
		return IOFormat.UNKNOWN
	@classmethod
	def read(cls,context:Context,**kwargs)->tuple[int,int]:
		num_cameras=0;num_files=0;directory=kwargs[_P];files=kwargs['files'];options=IOOptionsBase(**kwargs)
		for elem in files:
			_name,ext=os.path.splitext(elem.name);ext=ext.lower()
			if ext in cls.supported_extensions:
				filepath=os.path.join(directory,elem.name)
				if os.path.isfile(filepath):
					with open(filepath,'r',encoding=_M,newline='')as file:
						for handler_cls in cls.__format_registry:
							if ext==handler_cls.extension:
								file.seek(0)
								if handler_cls.check(file=file):
									done_num_cameras=handler_cls.read(file=file,options=options);num_cameras+=done_num_cameras
									if done_num_cameras:num_files+=1
		return num_files,num_cameras
	@classmethod
	def eval_export_cameras(cls,context:Context,*,flags:UnifiedNameOptions):
		def _iter_items():
			scene=context.scene
			for camera in scene.objects:
				if main.Workflow.camera_poll(ob=camera):
					name=''
					if flags&UnifiedNameOptions.USE_CAMERA_NAME:name=camera.name
					elif flags&UnifiedNameOptions.USE_CAM_NAME:name=camera.data.name
					elif flags&UnifiedNameOptions.USE_IMAGE_NAME:
						cam:Camera=camera.data;image:Image=cam.cpp.image
						if image:name=image.name
					elif flags&UnifiedNameOptions.USE_IMAGE_FILEPATH:
						cam:Camera=camera.data;image:Image=cam.cpp.image
						if image and image.filepath:name=os.path.basename(image.filepath)
					if name:yield(name,camera)
		cls.cached_export_items=tuple(_iter_items())
	@classmethod
	def write(cls,context:Context,**kwargs)->tuple[int,int]:
		flags=UnifiedNameOptions.from_string_set({kwargs['name_source']});directory=kwargs[_P];filename=kwargs['filename'];format=IOFormat[kwargs['fmt']];num_files=0;cls.eval_export_cameras(context,flags=flags);num_cameras=len(cls.cached_export_items)
		if num_cameras:
			for handler_cls in cls.__format_registry:
				if handler_cls.io_format==format:options=handler_cls.export_options(**kwargs);num_files=handler_cls.write(directory=directory,filename=filename,options=options)
		return num_files,num_cameras
if'rc_xmp'in locals():reload(rc_xmp)
else:from.intern import rc_xmp
if'rc_csv'in locals():reload(rc_csv)
else:from.intern import rc_csv
IOProcessor.register_file_format(rc_xmp.RC_METADATA_XMP)
IOProcessor.register_file_format(rc_csv.RC_IECP)
IOProcessor.register_file_format(rc_csv.RC_NXYZ)
IOProcessor.register_file_format(rc_csv.RC_NXYZHPR)
IOProcessor.register_file_format(rc_csv.RC_NXYZOPK)
class IOUnifiedName_Params:
	def _get_un_flags(self):return self.get(_Q,DEFAULT_UnifiedNameOptions)
	def _set_un_flags(self,value:int):
		curr_enum_value=UnifiedNameOptions.from_string_set(self.un_flags);enum_value=UnifiedNameOptions(value)
		if UnifiedNameOptions.USE_CAMERA_NAME not in enum_value and UnifiedNameOptions.USE_CAM_NAME not in enum_value:
			if curr_enum_value&UnifiedNameOptions.USE_CAMERA_NAME:enum_value|=UnifiedNameOptions.USE_CAM_NAME
			if curr_enum_value&UnifiedNameOptions.USE_CAM_NAME:enum_value|=UnifiedNameOptions.USE_CAMERA_NAME
		if UnifiedNameOptions.USE_IMAGE_NAME not in enum_value and UnifiedNameOptions.USE_IMAGE_FILEPATH not in enum_value:
			if curr_enum_value&UnifiedNameOptions.USE_IMAGE_NAME:enum_value|=UnifiedNameOptions.USE_IMAGE_FILEPATH
			if curr_enum_value&UnifiedNameOptions.USE_IMAGE_FILEPATH:enum_value|=UnifiedNameOptions.USE_IMAGE_NAME
		self[_Q]=enum_value
	un_flags:EnumProperty(items=((UnifiedNameOptions.IGNORE_LETTER_CASE.name,'Ignore Letter Case','Ignore character register for matching',icons.get_id('ignore_letter_case'),UnifiedNameOptions.IGNORE_LETTER_CASE.value),(UnifiedNameOptions.IGNORE_EXTENSION.name,'Ignore Extensions','Use name only, no file extension when searching',icons.get_id('ignore_extension'),UnifiedNameOptions.IGNORE_EXTENSION.value),_A,(UnifiedNameOptions.USE_CAMERA_NAME.name,'Use Object Name','Use camera object name for comparison',icons.get_id('use_camera_name'),UnifiedNameOptions.USE_CAMERA_NAME.value),(UnifiedNameOptions.USE_CAM_NAME.name,'Use Camera Name','Use camera data name for comparison',icons.get_id('use_cam_name'),UnifiedNameOptions.USE_CAM_NAME.value),_A,(UnifiedNameOptions.USE_IMAGE_NAME.name,'Use Image Name','Use image data-block name for comparison',icons.get_id('image'),UnifiedNameOptions.USE_IMAGE_NAME.value),(UnifiedNameOptions.USE_IMAGE_FILEPATH.name,'Use Image File Name','Use image file name for comparison',icons.get_id('use_image_filepath'),UnifiedNameOptions.USE_IMAGE_FILEPATH.value)),options={'ENUM_FLAG',_F},get=_get_un_flags,set=_set_un_flags,translation_context=_N,name='Comparison Options',description='Options for comparing names. At least one of the options must be selected for each compared type (object, image, etc.)')
class IOFileBase_Params:filename:StringProperty(maxlen=1024,subtype='FILE_NAME',options={_E},translation_context=_D,name='File Name');directory:StringProperty(subtype='DIR_PATH',maxlen=1024,options={_E},translation_context=_D,name='Directory');filepath:StringProperty(subtype='FILE_PATH',maxlen=1024,options={_E},translation_context=_D,name='File Path')
class IOFile_Params:
	files:CollectionProperty(type=OperatorFileListElement,options={_E,_F})
	def _get_filter_glob(self):return IOProcessor.filter_glob
	filter_glob:StringProperty(get=_get_filter_glob,maxlen=255,options={_E},translation_context=_D)
class IOTransform_Params:
	attr_name=_O;_global_scale_single_T,_global_scale_double_T,global_scale=double.property_group(attr_name,default=1.,min=constants.IEEE754.FLT_EXP,max=constants.IEEE754.FLT_MAX,options={_E},translation_context=_D,name='Global Scale',description='The global scale of the dataset');global_scale_single:_global_scale_single_T;global_scale_double:_global_scale_double_T
	def _update_forward_axis(self,context):
		if self.forward_axis[-1]==self.up_axis[-1]:self.up_axis=self.up_axis[0:-1]+_G[(_G.index(self.up_axis[-1])+1)%3]
		self._cb_handler_frame_change_pre(context)
	forward_axis:EnumProperty(items=(('X','X Forward','Use the global X axis as the forward direction'),(_B,'Y Forward','Use the global Y axis as the forward direction'),(_C,'Z Forward','Use the global Z axis as the forward direction'),(_J,'Negative X Forward','Use the negative global X axis as the forward direction'),(_K,'Negative Y Forward','Use the negative global Y axis as the forward direction'),(_L,'Negative Z Forward','Use the negative global Z axis as the forward direction')),default=_B,options={_F},translation_context=_D,update=_update_forward_axis,name='Forward',description='Axis forward')
	def _update_up_axis(self,context):
		if self.up_axis[-1]==self.forward_axis[-1]:self.forward_axis=self.forward_axis[0:-1]+_G[(_G.index(self.forward_axis[-1])+1)%3]
		self._cb_handler_frame_change_pre(context)
	up_axis:EnumProperty(items=(('X','X Up','Use the global X axis as the up direction'),(_B,'Y Up','Use the global Y axis as the up direction'),(_C,'Z Up','Use the global Z axis as the up direction'),(_J,'Negative X Up','Use the negative global X axis as the up direction'),(_K,'Negative Y Up','Use the negative global Y axis as the up direction'),(_L,'Negative Z Up','Use the negative global Z axis as the up direction')),default=_C,options={_F},translation_context=_D,update=_update_up_axis,name='Up',description='Axis up')
CENTERED_DIALOG_ICON_SCALE=6.
CENTERED_DIALOG_PROPS_UI_UNITS_X=8
def invoke_props_dialog_centered(context:Context,event:Event,*,operator:Operator):dialog_height=284;wm=context.window_manager;window=context.window;initial_mouse_x,initial_mouse_y=event.mouse_x,event.mouse_y;window.cursor_warp(int(window.width/2),int(window.height/2)+int(dialog_height/2));wm.invoke_props_dialog(operator,width=400);window.cursor_warp(initial_mouse_x,initial_mouse_y)
class StageStatus(IntEnum):FINISHED=auto();CANCELLED=auto();ABORTED=auto()
class SetupContextOperator(type):
	@staticmethod
	def __cancel(self,context:Context):
		wm_props:WMProps=context.window_manager.cpp
		if wm_props.setup_context_stage!=constants.SetupStage.PASS_THROUGH.name:wm_props.setup_context_stage=constants.SetupStage.PASS_THROUGH.name;bpy.ops.cpp.setup_context(_R,status=StageStatus.ABORTED.name)
	@classmethod
	def __cancel_wrapped(cls,func):
		def _wrapper(self,context:Context):func(self,context);cls.__cancel(self,context)
		return _wrapper
	@staticmethod
	def __invoke_wrapped(label:str,func:Callable):
		def _wrapper(self,context:Context,event:Event):log.debug('"{label}" invoke begin'.format(label=label));dt=time.time();ret=func(self,context,event);log.debug('"{label}" invoke end as {flag} in {elapsed:.6f} second(s)'.format(label=label,flag=ret,elapsed=time.time()-dt));return ret
		return _wrapper
	@staticmethod
	def __execute_wrapped(func:Callable):
		func_wrapped_report=Reports.log_execution_helper(func)
		def _wrapper(self,context:Context):
			ret=func_wrapped_report(self,context);wm_props:WMProps=context.window_manager.cpp
			if wm_props.setup_context_stage!=constants.SetupStage.PASS_THROUGH.name:bpy.ops.cpp.setup_context(_R,status=next(iter(ret)))
			return ret
		return _wrapper
	def __new__(cls,name,bases,dct:dict):
		C='execute';B='invoke';A='cancel';bases=(Operator,)+bases;func_cancel=dct.get(A,cls.__cancel)
		if func_cancel!=cls.__cancel:func_cancel=cls.__cancel_wrapped(func_cancel)
		dct[A]=func_cancel;func_invoke=dct.get(B,_A)
		if func_invoke is not _A:dct[B]=cls.__invoke_wrapped(label=dct['bl_label'],func=func_invoke)
		func_execute=dct.get(C,_A);dct[C]=cls.__execute_wrapped(func_execute);return type(name,bases,dct)