from __future__ import annotations
_X='EXEC_DEFAULT'
_W='name_source'
_V='filename'
_U='num_files'
_T='IOParamsRegistry'
_S='IOExportOptionsBaseT'
_R='IOExportParamsBaseT'
_Q='PROP_UN_FLAGS'
_P='state'
_O='num_cameras'
_N='NEGATIVE_Z'
_M='NEGATIVE_Y'
_L='NEGATIVE_X'
_K='lval'
_J='XYZ'
_I='SKIP_SAVE'
_H='name_flags'
_G='directory'
_F='CPP_IO'
_E='HIDDEN'
_D='Z'
_C='Y'
_B=False
_A=None
import glob,os,abc,time
from importlib import reload
from enum import auto,IntEnum,IntFlag
from typing import TypeVar
import OpenImageIO as oiio
from...import Reports,log
from...import constants
from...import main
from...import icons
import bpy
from bpy.types import Context,Event,Operator,OperatorFileListElement
from bpy.props import CollectionProperty,EnumProperty,FloatProperty,StringProperty
import bpy_extras
from typing import TYPE_CHECKING
if TYPE_CHECKING:from io import TextIOWrapper;from typing import Callable,Iterable,Type;from...props import Object,Float64ArrayT;from...props import Camera,Image;from...props.wm import WMProps;from...props.camera import CameraProps
__all__='IONameOptions','DEFAULT_IONameOptions','IMAGE_FILE_EXTENSIONS','InputName','InputNameCache','OutputName','IOObjectBase','IOObjectLocation','IOObjectRotation','IOObjectTransform',_Q,'IOFileFormat','IOExportParamsBase','IOTransformOptionsBase',_R,_S,'IOFileFormatHandler','ImportCamerasResult','ExportCamerasResult','BindImagesMode','BindImagesResult','IOProcessor',_T,'IOName_Params','IOFileBaseParams','IOFileParams','IOTransformParams','CENTERED_DIALOG_ICON_SCALE','CENTERED_DIALOG_PROPS_UI_UNITS_X','invoke_props_dialog_centered','StageStatus','SetupContextOperator'
class IONameOptions(IntFlag):
	IGNORE_LETTER_CASE=auto();IGNORE_EXTENSION=auto();USE_CAMERA_NAME=auto();USE_CAM_NAME=auto();USE_IMAGE_NAME=auto();USE_IMAGE_FILEPATH=auto()
	@staticmethod
	def from_string_set(values:set[str])->IONameOptions:
		ret=0
		for item in values:ret|=IONameOptions[item]
		return ret
DEFAULT_IONameOptions=IONameOptions.IGNORE_LETTER_CASE|IONameOptions.IGNORE_EXTENSION|IONameOptions.USE_CAMERA_NAME|IONameOptions.USE_CAM_NAME|IONameOptions.USE_IMAGE_NAME|IONameOptions.USE_IMAGE_FILEPATH
__oiio_ext_attr=oiio.get_string_attribute('extension_list')
__oiio_ext_list=[_.split(':')[1].split(',')for _ in __oiio_ext_attr.split(';')]
IMAGE_FILE_EXTENSIONS={f".{y}"for x in __oiio_ext_list for y in x}
class InputName:
	__slots__='item',_K,'done';item:str|Object|Image;lval:set[str];done:bool
	def _evaluate_lval(self,*,names:set[str],flags:IONameOptions=DEFAULT_IONameOptions):
		self.lval=names
		if flags&IONameOptions.IGNORE_LETTER_CASE and flags&IONameOptions.IGNORE_EXTENSION:self.lval=set(os.path.splitext(_)[0].lower()for _ in self.lval);return
		if flags&IONameOptions.IGNORE_LETTER_CASE:self.lval=set(_.lower()for _ in self.lval)
		if flags&IONameOptions.IGNORE_EXTENSION:self.lval=set(os.path.splitext(_)[0]for _ in self.lval if'.'in _)
	@staticmethod
	def from_image(*,image:Image,flags:IONameOptions=DEFAULT_IONameOptions)->InputName:
		ret=InputName()
		def _iter_image_names()->str:
			if flags&IONameOptions.USE_IMAGE_NAME:yield image.name
			if flags&IONameOptions.USE_IMAGE_FILEPATH:
				if image.filepath and os.path.isfile(bpy.path.abspath(image.filepath)):yield os.path.basename(image.filepath)
		ret._evaluate_lval(names=set(_iter_image_names()),flags=flags);ret.item=image;ret.done=_B;return ret
	@staticmethod
	def from_object(*,ob:Object,flags:IONameOptions=DEFAULT_IONameOptions)->InputName:
		ret=InputName()
		def _iter_object_names()->str:
			if flags&IONameOptions.USE_CAMERA_NAME:yield ob.name
			if flags&IONameOptions.USE_CAM_NAME:yield ob.data.name
		ret._evaluate_lval(names=set(_iter_object_names()),flags=flags);ret.item=ob;ret.done=_B;return ret
	@staticmethod
	def from_path(*,fp:str,flags:IONameOptions=DEFAULT_IONameOptions)->InputName:ret=InputName();ret._evaluate_lval(names={os.path.basename(fp)},flags=flags);ret.item=fp;ret.done=_B;return ret
	@staticmethod
	def from_string(*,val:str,flags:IONameOptions=DEFAULT_IONameOptions)->InputName:ret=InputName();ret._evaluate_lval(names={val},flags=flags);ret.item=val;ret.done=_B;return ret
	def __hash__(self)->int:return hash(self.item)
	def __eq__(self,other:InputName)->bool:return self.lval&other.lval
	def __repr__(self)->str:return'|'.join(self.lval)
	def __getstate__(self):return{_K:self.lval}
	def __setstate__(self,state):self.lval=state[_K]
class InputNameCache:
	__slots__=();cached_image_names:set[InputName]=set();cached_camera_names:set[InputName]=set();num_cameras_create:int=0;cached_file_names:set[InputName]=set();cache_flags:IONameOptions=DEFAULT_IONameOptions;created_cameras:set[Object]=set()
	@classmethod
	def reset(cls):cls.cached_image_names=set();cls.cached_camera_names=set();cls.num_cameras_create=set();cls.cached_file_names=set();cls.cache_flags=DEFAULT_IONameOptions;cls.created_cameras=set()
	@classmethod
	def update_eval_images_cache(cls,*,flags:IONameOptions=DEFAULT_IONameOptions):cls.cached_image_names=set(InputName.from_image(image=image,flags=flags)for image in bpy.data.images);cls.cache_flags=flags
	@classmethod
	def update_eval_cameras_cache(cls,context:Context,*,flags:IONameOptions=DEFAULT_IONameOptions):cls.num_cameras_create=0;cls.cached_camera_names=set(InputName.from_object(ob=ob,flags=flags)for ob in context.scene.objects if main.Workflow.camera_poll(ob));cls.cache_flags=flags
	@classmethod
	def update_eval_images_directory_cache(cls,*,directory:str,flags:IONameOptions=DEFAULT_IONameOptions):extensions_filter_set=IMAGE_FILE_EXTENSIONS;cls.cached_file_names=set(InputName.from_path(fp=file,flags=flags)for file in glob.iglob(f"{directory}*.*")if os.path.splitext(file)[1].lower()in extensions_filter_set);cls.cache_flags=flags
	@classmethod
	def eval_unified_name_from_cache(cls,*,name:str)->InputName:
		un=InputName.from_string(val=name,flags=cls.cache_flags)
		for item in cls.cached_camera_names:
			item:InputName
			if item==un:
				if getattr(item,'done',_B):return
				if isinstance(item.item,bpy.types.Object):item.done=True;return item
				else:return
		un.done=True;cls.cached_camera_names.add(un);cls.num_cameras_create+=1;return un
	@classmethod
	def create_missing_cameras(cls):
		context=bpy.context
		for i in range(cls.num_cameras_create):cam=bpy.data.cameras.new(name='');camera=bpy.data.objects.new(name='',object_data=cam);context.collection.objects.link(camera);cls.created_cameras.add(camera)
class OutputNameCache:
	__slots__=();cached_camera_names:tuple[tuple[str,Object]]=()
	@classmethod
	def reset(cls):cls.cached_camera_names=()
	@classmethod
	def update_eval_cameras_cache(cls,context:Context,*,flags:IONameOptions=DEFAULT_IONameOptions):
		def _iter_items():
			scene=context.scene
			for camera in scene.objects:
				camera:Object
				if main.Workflow.camera_poll(ob=camera):
					name=''
					if flags&IONameOptions.USE_CAMERA_NAME:name=camera.name
					elif flags&IONameOptions.USE_CAM_NAME:name=camera.data.name
					elif flags&IONameOptions.USE_IMAGE_NAME:
						cam:Camera=camera.data;image:Image=cam.cpp.image
						if image:name=image.name
					elif flags&IONameOptions.USE_IMAGE_FILEPATH:
						cam:Camera=camera.data;image:Image=cam.cpp.image
						if image and image.filepath:name=os.path.basename(image.filepath)
					if name:yield(name,camera)
		cls.cached_camera_names=tuple(_iter_items())
class IOObjectBase:
	name:InputName
	@abc.abstractmethod
	def set_camera_data(self,*,camera:Object):raise NotImplementedError()
class IOObjectLocation(IOObjectBase):
	location:Float64ArrayT
	def apply_location(self,R:_A|Float64ArrayT,S:_A|float):
		import numpy as np
		if R is _A and S is _A:return
		elif R is not _A:self.location=np.matmul(self.location,R)
		if S is not _A:self.location*=S
class IOObjectRotation(IOObjectBase):
	rotation:Float64ArrayT
	def apply_rotation(self,R:_A|Float64ArrayT,S:_A|float):
		import numpy as np
		if R is _A and S is _A:return
		elif R is not _A:self.rotation=np.matmul(R,self.rotation)
class IOObjectTransform(IOObjectLocation,IOObjectRotation):
	def apply_transform(self,R:_A|Float64ArrayT,S:_A|float):
		import numpy as np
		if R is _A and S is _A:return
		elif R is not _A:self.rotation=np.matmul(R,self.rotation);self.location=np.matmul(self.location,R)
		if S is not _A:self.location*=S
class IOFileFormat(IntEnum):UNKNOWN=auto();RC_IECP=auto();RC_NXYZ=auto();RC_NXYZHPR=auto();RC_NXYZOPK=auto();RC_METADATA_XMP=auto()
class IOExportParamsBase:0
class IOTransformOptionsBase:
	__slots__='has_transform','R','S';has_transform:bool;R:Float64ArrayT;S:float
	def __init__(self,**kwargs):
		import numpy as np;forward_axis=kwargs['forward_axis'];up_axis=kwargs['up_axis'];global_scale=kwargs['global_scale']
		if forward_axis==_C and up_axis==_D and global_scale==1.:self.has_transform=_B;self.R=_A;self.S=_A
		else:
			self.has_transform=True
			def _fix_axes_enum_name(value):return{'X':'X',_C:_C,_D:_D,_L:'-X',_M:'-Y',_N:'-Z'}[value]
			forward_axis=_fix_axes_enum_name(forward_axis);up_axis=_fix_axes_enum_name(up_axis);self.R=np.array(bpy_extras.io_utils.axis_conversion(from_forward=_C,from_up=_D,to_forward=forward_axis,to_up=up_axis),dtype=np.float64,order='C');self.S=global_scale
IOExportParamsBaseT=TypeVar(_R,bound=IOExportParamsBase)
IOExportOptionsBaseT=TypeVar(_S,bound=IOTransformOptionsBase)
class IOFileFormatHandler(metaclass=abc.ABCMeta):
	name:str;icon:str;io_format:IOFileFormat;extension:str;size_max:int=-1;export_params:IOExportParamsBaseT=IOExportParamsBase;export_options:IOExportOptionsBaseT=IOTransformOptionsBase
	@classmethod
	@abc.abstractmethod
	def check(cls,*,file:TextIOWrapper)->bool:raise NotImplementedError()
	@classmethod
	@abc.abstractmethod
	def evaluate_filename(cls,*,name:str)->str:raise NotImplementedError()
	@classmethod
	@abc.abstractmethod
	def read(cls,*,r_data:list,file:TextIOWrapper,options:IOExportOptionsBaseT)->int:raise NotImplementedError()
	@classmethod
	@abc.abstractmethod
	def write(cls,*,directory:str,filename:str,options:Type[IOTransformOptionsBase])->int:raise NotImplementedError()
class ImportCamerasResult:
	__slots__=_U,_O,'num_cameras_created';num_files:int;num_cameras:int;num_cameras_created:int
	def __init__(self):self.num_files=0;self.num_cameras=0;self.num_cameras_created=0
class ExportCamerasResult:
	__slots__=_U,_O;num_files:int;num_cameras:int
	def __init__(self):self.num_files=0;self.num_cameras=0
class BindImagesMode(IntEnum):ACTIVE=auto();ALL=auto()
class BindImagesResult:
	__slots__='directory_search',_O,'num_remains','num_changed','num_opened','num_opening_failed';directory_search:bool;num_cameras:int;num_remains:int;num_changed:int;num_opened:int;num_opening_failed:int
	def __init__(self):self.directory_search=0;self.num_cameras=0;self.num_remains=0;self.num_changed=0;self.num_opened=0;self.num_opening_failed=0
class IOParamsState(IntEnum):UNDEFINED=auto();VALID=auto();NO_DIRECTORY=auto();INVALID_DIRECTORY=auto();NO_FILES=auto();NO_HANDLER=auto()
class ImportCamerasParams:
	__slots__=_P,_G,'files',_H,'transform_options';state:IOParamsState;directory:str;files:tuple[str];name_flags:IONameOptions;transform_options:_A|IOTransformOptionsBase
	def __init__(self,**kwargs):
		self.state=IOParamsState.UNDEFINED;self.directory='';self.files=tuple();self.name_flags=0;self.transform_options=_A;kw_directory=kwargs.get(_G,'')
		if not kw_directory:self.state=IOParamsState.NO_DIRECTORY;return
		directory_eval=bpy.path.abspath(kw_directory)
		if not os.path.isdir(directory_eval):self.state=IOParamsState.INVALID_DIRECTORY;return
		self.directory=directory_eval;kw_files:list[OperatorFileListElement]=kwargs.get('files',list())
		if not kw_files:self.state=IOParamsState.NO_FILES;return
		self.files=tuple(_.name for _ in kw_files);self.name_flags=IONameOptions.from_string_set(kwargs.get(_H));self.transform_options=IOTransformOptionsBase(**kwargs);self.state=IOParamsState.VALID
class ExportCamerasParams:
	__slots__=_P,_G,_V,'file_format','export_options',_W;state:IOParamsState;directory:str;filename:str;file_format:IOFileFormat;export_options:_A|IOExportOptionsBaseT;name_source:IONameOptions
	def __init__(self,**kwargs):
		self.state=IOParamsState.UNDEFINED;self.directory='';self.filename='';self.file_format=IOFileFormat.UNKNOWN;self.export_options=_A;self.name_source=0;kw_directory=kwargs.get(_G,'')
		if not kw_directory:self.state=IOParamsState.NO_DIRECTORY;return
		directory_eval=bpy.path.abspath(kw_directory)
		if not os.path.isdir(directory_eval):self.state=IOParamsState.INVALID_DIRECTORY;return
		self.directory=directory_eval;self.filename=kwargs.get(_V,'');self.file_format=IOFileFormat[kwargs['fmt']];handler=IOProcessor.handler_of(format=self.file_format)
		if handler is _A:self.state=IOParamsState.NO_HANDLER;return
		self.export_options=handler.export_options(**kwargs);self.name_source=IONameOptions.from_string_set({kwargs[_W]});self.state=IOParamsState.VALID
class BindImagesParams:
	__slots__=_P,_G,_H,'mode';directory:str;name_flags:IONameOptions;mode:BindImagesMode
	def __init__(self,**kwargs):
		self.state=IOParamsState.UNDEFINED;self.directory='';self.name_flags=0;self.mode=BindImagesMode.ALL;kw_directory=kwargs.get(_G,'');directory_eval=''
		if kw_directory:
			directory_eval=bpy.path.abspath(kw_directory)
			if not os.path.isdir(directory_eval):self.state=IOParamsState.INVALID_DIRECTORY;return
		self.directory=directory_eval;self.name_flags=IONameOptions.from_string_set(kwargs.get(_H));self.mode=BindImagesMode[kwargs.get('mode')];self.state=IOParamsState.VALID
class IOProcessor:
	__format_registry:list[IOFileFormatHandler]=list();supported_extensions:list[str]=list();_filter_glob:str=''
	@classmethod
	def register_file_format(cls,item:IOFileFormatHandler):cls.__format_registry.append(item);cls.supported_extensions.append(item.extension)
	@classmethod
	def eval_io_third_party_params(cls)->object:
		fmt_items=list();export_params_bases_set=set()
		for item in cls.__format_registry:export_params_bases_set.add(item.export_params);fmt_items.append((item.io_format.name,item.name,'',item.icon,item.io_format.value))
		prop_fmt=EnumProperty(items=fmt_items,options={_E},translation_context='IOFormat',name='Format');return type(_T,tuple(export_params_bases_set),dict(__annotations__=dict(fmt=prop_fmt)))
	@classmethod
	def eval_filter_glob(cls)->str:
		if not cls._filter_glob:cls._filter_glob=';'.join({f"*{_}"for _ in cls.supported_extensions})
		return cls._filter_glob
	@classmethod
	def handler_of(cls,*,format:IOFileFormat)->_A|IOFileFormatHandler:
		for item in cls.__format_registry:
			if item.io_format==format:return item
	@classmethod
	def extension_of(cls,*,format:IOFileFormat)->str:
		handler=cls.handler_of(format=format)
		if handler is _A:return''
		return handler.extension
	@classmethod
	def eval_filename(cls,*,format:IOFileFormat,name:str)->str:
		for item in cls.__format_registry:
			if item.io_format==format:return item.evaluate_filename(name=name)
		return name
	@classmethod
	def check_camera_data(cls,*,directory:str,files:Iterable[str])->dict[IOFileFormatHandler,int]:
		ret=dict.fromkeys(cls.__format_registry,0)
		for item in files:
			_name,ext=os.path.splitext(item);ext=ext.lower()
			if ext in cls.supported_extensions:
				filepath=os.path.join(directory,item)
				if os.path.isfile(filepath):
					with open(filepath,'r',encoding='utf-8',newline='')as file:
						for handler_cls in cls.__format_registry:
							if ext==handler_cls.extension:
								if handler_cls.size_max!=-1:
									if handler_cls.size_max<os.path.getsize(filepath):continue
								file.seek(0)
								if handler_cls.check(file=file):ret[handler_cls]+=1
		return ret
	@classmethod
	def read_camera_data(cls,context:Context,*,params:ImportCamerasParams)->ImportCamerasResult:
		res=ImportCamerasResult()
		if params.state!=IOParamsState.VALID:return res
		InputNameCache.update_eval_cameras_cache(context,flags=params.name_flags);data:dict[IOFileFormatHandler,list[IOObjectBase]]=dict()
		for item in cls.__format_registry:data[item]=list()
		for name in params.files:
			ext=os.path.splitext(name)[1].lower()
			if ext in cls.supported_extensions:
				filepath=os.path.join(params.directory,name)
				if os.path.isfile(filepath):
					with open(filepath,'r',encoding='utf-8',newline='')as file:
						for handler_cls in cls.__format_registry:
							if ext==handler_cls.extension:
								file.seek(0)
								if handler_cls.check(file=file):
									num_cameras_done=handler_cls.read(r_data=data[handler_cls],file=file,options=params.transform_options);res.num_cameras+=num_cameras_done
									if num_cameras_done:res.num_files+=1
		InputNameCache.create_missing_cameras();res.num_cameras_created=InputNameCache.num_cameras_create
		for(handler_cls,cams)in data.items():
			for c in cams:
				un:InputName=c.name
				if isinstance(un.item,str):camera=InputNameCache.created_cameras.pop();camera.name=un.item
				else:camera=un.item
				c.set_camera_data(camera=camera)
		InputNameCache.reset();return res
	@classmethod
	def write_camera_data(cls,context:Context,*,params:ExportCamerasParams)->ExportCamerasResult:
		res=ExportCamerasResult()
		if params.state!=IOParamsState.VALID:return res
		OutputNameCache.update_eval_cameras_cache(context,flags=params.name_source);res.num_cameras=len(OutputNameCache.cached_camera_names)
		if res.num_cameras:handler=cls.handler_of(format=params.file_format);res.num_files=handler.write(directory=params.directory,filename=params.filename,options=params.export_options)
		OutputNameCache.reset();return res
	@classmethod
	def bind_camera_images(cls,context:Context,params:BindImagesParams)->BindImagesResult:
		res=BindImagesResult()
		if params.state!=IOParamsState.VALID:return res
		do_directory_search=params.directory;res.directory_search=do_directory_search
		match params.mode:
			case BindImagesMode.ACTIVE:
				camera=main.Workflow.get_camera()
				if not camera:return res
				camera_names={InputName().from_object(ob=camera,flags=params.name_flags)}
			case BindImagesMode.ALL:InputNameCache.update_eval_cameras_cache(context,flags=params.name_flags);camera_names=InputNameCache.cached_camera_names
		InputNameCache.update_eval_images_cache(flags=params.name_flags);image_names=list(InputNameCache.cached_image_names);file_names:list[InputName]=list()
		if do_directory_search:InputNameCache.update_eval_images_directory_cache(directory=params.directory,flags=params.name_flags);file_names=list(InputNameCache.cached_file_names)
		res.num_cameras=len(camera_names);n_camera:InputName
		for n_camera in camera_names:
			for n_image in image_names:
				if n_camera==n_image:
					image_names.remove(n_image);cam:Camera=n_camera.item.data;cam_props:CameraProps=cam.cpp;image:Image=n_image.item
					if cam_props.image!=image:cam_props.image=image;res.num_changed+=1
					else:res.num_remains+=1
					break
			else:
				if do_directory_search:
					for n_fp in file_names:
						if n_camera==n_fp:
							file_names.remove(n_fp);image=bpy.data.images.load(n_fp.item,check_existing=_B)
							if image:
								res.num_opened+=1;cam:Camera=n_camera.item.data;cam_props:CameraProps=cam.cpp
								if cam_props.image!=image:cam_props.image=image;res.num_changed+=1
								else:res.num_remains+=1
								break
							else:res.num_opening_failed+=1
							break
		InputNameCache.reset();return res
class IOParamsRegistry:fmt:bpy.types.EnumProperty
if'rc'in locals():reload(rc)
else:from.import rc
IOProcessor.register_file_format(rc.RC_METADATA_XMP)
IOProcessor.register_file_format(rc.RC_IECP)
IOProcessor.register_file_format(rc.RC_NXYZ)
IOProcessor.register_file_format(rc.RC_NXYZHPR)
IOProcessor.register_file_format(rc.RC_NXYZOPK)
IOParamsRegistry=IOProcessor.eval_io_third_party_params()
class IOName_Params:
	def _get_name_flags(self):return self.get(_H,DEFAULT_IONameOptions)
	def _set_name_flags(self,value:int):
		curr_enum_value=IONameOptions.from_string_set(self.name_flags);enum_value=IONameOptions(value)
		if IONameOptions.USE_CAMERA_NAME not in enum_value and IONameOptions.USE_CAM_NAME not in enum_value:
			if curr_enum_value&IONameOptions.USE_CAMERA_NAME:enum_value|=IONameOptions.USE_CAM_NAME
			if curr_enum_value&IONameOptions.USE_CAM_NAME:enum_value|=IONameOptions.USE_CAMERA_NAME
		if IONameOptions.USE_IMAGE_NAME not in enum_value and IONameOptions.USE_IMAGE_FILEPATH not in enum_value:
			if curr_enum_value&IONameOptions.USE_IMAGE_NAME:enum_value|=IONameOptions.USE_IMAGE_FILEPATH
			if curr_enum_value&IONameOptions.USE_IMAGE_FILEPATH:enum_value|=IONameOptions.USE_IMAGE_NAME
		self[_H]=enum_value
	name_flags:EnumProperty(items=((IONameOptions.IGNORE_LETTER_CASE.name,'Ignore Letter Case','Ignore character register for matching',icons.get_id('ignore_letter_case'),IONameOptions.IGNORE_LETTER_CASE.value),(IONameOptions.IGNORE_EXTENSION.name,'Ignore Extensions','Use name only, no file extension when searching',icons.get_id('ignore_extension'),IONameOptions.IGNORE_EXTENSION.value),_A,(IONameOptions.USE_CAMERA_NAME.name,'Use Object Name','Use camera object name for comparison',icons.get_id('use_camera_name'),IONameOptions.USE_CAMERA_NAME.value),(IONameOptions.USE_CAM_NAME.name,'Use Camera Name','Use camera data name for comparison',icons.get_id('use_cam_name'),IONameOptions.USE_CAM_NAME.value),_A,(IONameOptions.USE_IMAGE_NAME.name,'Use Image Name','Use image data-block name for comparison',icons.get_id('image'),IONameOptions.USE_IMAGE_NAME.value),(IONameOptions.USE_IMAGE_FILEPATH.name,'Use Image File Name','Use image file name for comparison',icons.get_id('use_image_filepath'),IONameOptions.USE_IMAGE_FILEPATH.value)),options={'ENUM_FLAG',_I},get=_get_name_flags,set=_set_name_flags,translation_context=_Q,name='Comparison Options',description='Options for comparing names. At least one of the options must be selected for each compared type (object, image, etc.)')
class IOFileBaseParams:filename:StringProperty(maxlen=1024,subtype='FILE_NAME',options={_E},translation_context=_F,name='File Name');directory:StringProperty(subtype='DIR_PATH',maxlen=1024,options={_E},translation_context=_F,name='Directory');filepath:StringProperty(subtype='FILE_PATH',maxlen=1024,options={_E},translation_context=_F,name='File Path')
class IOFileParams:
	files:CollectionProperty(type=OperatorFileListElement,options={_E,_I})
	def _get_filter_glob(self):return IOProcessor.eval_filter_glob()
	filter_glob:StringProperty(get=_get_filter_glob,maxlen=255,options={_E},translation_context=_F)
class IOTransformParams:
	global_scale:FloatProperty(default=1.,min=constants.IEEE754.FLT_EXP,max=constants.IEEE754.FLT_MAX,options={_E},translation_context=_F,name='Global Scale',description='The global scale of the dataset')
	def _update_forward_axis(self,context):
		if self.forward_axis[-1]==self.up_axis[-1]:self.up_axis=self.up_axis[0:-1]+_J[(_J.index(self.up_axis[-1])+1)%3]
		self._cb_handler_frame_change_pre(context)
	forward_axis:EnumProperty(items=(('X','X Forward','Use the global X axis as the forward direction'),(_C,'Y Forward','Use the global Y axis as the forward direction'),(_D,'Z Forward','Use the global Z axis as the forward direction'),(_L,'Negative X Forward','Use the negative global X axis as the forward direction'),(_M,'Negative Y Forward','Use the negative global Y axis as the forward direction'),(_N,'Negative Z Forward','Use the negative global Z axis as the forward direction')),default=_C,options={_I},translation_context=_F,update=_update_forward_axis,name='Forward',description='Axis forward')
	def _update_up_axis(self,context):
		if self.up_axis[-1]==self.forward_axis[-1]:self.forward_axis=self.forward_axis[0:-1]+_J[(_J.index(self.forward_axis[-1])+1)%3]
		self._cb_handler_frame_change_pre(context)
	up_axis:EnumProperty(items=(('X','X Up','Use the global X axis as the up direction'),(_C,'Y Up','Use the global Y axis as the up direction'),(_D,'Z Up','Use the global Z axis as the up direction'),(_L,'Negative X Up','Use the negative global X axis as the up direction'),(_M,'Negative Y Up','Use the negative global Y axis as the up direction'),(_N,'Negative Z Up','Use the negative global Z axis as the up direction')),default=_D,options={_I},translation_context=_F,update=_update_up_axis,name='Up',description='Axis up')
CENTERED_DIALOG_ICON_SCALE=6.
CENTERED_DIALOG_PROPS_UI_UNITS_X=8
def invoke_props_dialog_centered(context:Context,event:Event,*,operator:Operator):dialog_height=284;wm=context.window_manager;window=context.window;initial_mouse_x,initial_mouse_y=event.mouse_x,event.mouse_y;window.cursor_warp(int(window.width/2),int(window.height/2)+int(dialog_height/2));wm.invoke_props_dialog(operator,width=400);window.cursor_warp(initial_mouse_x,initial_mouse_y)
class StageStatus(IntEnum):FINISHED=auto();CANCELLED=auto();ABORTED=auto()
class SetupContextOperator(type):
	@staticmethod
	def __cancel(self,context:Context):
		wm_props:WMProps=context.window_manager.cpp
		if wm_props.setup_context_stage!=constants.SetupStage.PASS_THROUGH.name:wm_props.setup_context_stage=constants.SetupStage.PASS_THROUGH.name;bpy.ops.cpp.setup_context(_X,status=StageStatus.ABORTED.name)
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
			if wm_props.setup_context_stage!=constants.SetupStage.PASS_THROUGH.name:bpy.ops.cpp.setup_context(_X,status=next(iter(ret)))
			return ret
		return _wrapper
	def __new__(cls,name,bases,dct:dict):
		C='execute';B='invoke';A='cancel';bases=(Operator,)+bases;func_cancel=dct.get(A,cls.__cancel)
		if func_cancel!=cls.__cancel:func_cancel=cls.__cancel_wrapped(func_cancel)
		dct[A]=func_cancel;func_invoke=dct.get(B,_A)
		if func_invoke is not _A:dct[B]=cls.__invoke_wrapped(label=dct['bl_label'],func=func_invoke)
		func_execute=dct.get(C,_A);dct[C]=cls.__execute_wrapped(func_execute);return type(name,bases,dct)