from __future__ import annotations
_F='open_directory'
_E='Untitled'
_D=False
_C='HIDDEN'
_B='CPP_OT_export_cameras'
_A=True
import logging,os,time
from..import Reports
from.import common
from..import constants
from..import main
import bpy
from bpy.types import Context,Event,Operator
from bpy.props import BoolProperty,EnumProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props.wm import WMProps
__all__=_B,
class CPP_OT_export_cameras(Operator,common.IOFileBaseParams,common.IOFileParams,common.IOTransformParams,common.ExportParamsRegistry):
	bl_idname='cpp.export_cameras';bl_label='Export Cameras';bl_description='Export camera data';bl_options={'REGISTER','UNDO','PRESET'};bl_translation_context=_B;check_existing:BoolProperty(default=_A,options={_C},translation_context=_B,name='Check Existing',description='Check and warn on overwriting existing files');fmt_locked:BoolProperty(description='',default=_A,options={_C},translation_context=_B,name='Format Locked');open_directory:BoolProperty(default=_A,options={_C},translation_context=_B,name='Open Directory',description='Open directory after export');name_source:EnumProperty(items=((common.IONameOptions.USE_CAMERA_NAME.name,'Use Object Name','Use camera object name as source'),(common.IONameOptions.USE_CAM_NAME.name,'Use Camera Name','Use camera data name as source'),(common.IONameOptions.USE_IMAGE_NAME.name,'Use Image Name','Use image data-block name as source'),(common.IONameOptions.USE_IMAGE_FILEPATH.name,'Use Image File Name','Use image file name as source')),default=common.IONameOptions.USE_CAMERA_NAME.name,options={_C},translation_context=_B,name='Name Source',description='Name source for export')
	def _check_filepath(self):
		format=common.IOFileFormat[self.fmt];ext=common.IOProcessor.extension_of(format=format);basename=os.path.basename(self.filepath)
		if not basename:basename=_E
		dirname=os.path.dirname(self.filepath);name_noext=common.IOProcessor.eval_filename(format=format,name=os.path.splitext(basename)[0]);filepath=bpy.path.ensure_ext(os.path.join(dirname,name_noext),ext)
		if self.filepath!=filepath:self.filepath=filepath;return _A
	def _check_fmt(self):
		self.fmt_locked=_D
		if self.filepath:
			abs_fp=bpy.path.abspath(self.filepath)
			if os.path.isfile(abs_fp):
				input_count=common.IOProcessor.check_camera_data(directory=self.directory,files=(self.filename,));file_format=common.IOFileFormat.UNKNOWN
				for(handler,count)in input_count.items():
					if count:file_format=handler.io_format;break
				if file_format!=common.IOFileFormat.UNKNOWN:
					self.fmt_locked=_A
					if self.fmt!=file_format.name:self.fmt=file_format.name
	def check(self,context:Context)->bool:self._check_fmt();return self._check_filepath()
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_D;layout.use_property_decorate=_D;col=layout.column(align=_A);col.enabled=not self.fmt_locked;col.prop(self,'fmt',text='');col=layout.column(align=_A);col.prop(self,'name_source',text='');col=layout.column(align=_A);col.use_property_split=_A;col.prop(self,_F)
	@classmethod
	def poll(cls,context:Context):
		wm_props:WMProps=context.window_manager.cpp
		if wm_props.setup_context_stage==constants.SetupStage.PASS_THROUGH.name:
			for ob in context.scene.objects:
				if main.Workflow.camera_poll(ob):return _A
		return _D
	def invoke(self,context:Context,event:Event):self.filename=_E;wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	@Reports.log_execution_helper
	def execute(self,context:Context):
		A='CANCELLED';dt=time.time();msgctxt=self.__class__.__qualname__;keywords:dict=self.as_keywords(ignore=('check_existing','fmt_locked','filter_glob',_F));params=common.ExportCamerasParams(**keywords)
		match params.state:
			case common.IOParamsState.NO_DIRECTORY:Reports.report_and_log(self,level=logging.WARNING,message='Empty export directory path',msgctxt=msgctxt);return{A}
			case common.IOParamsState.INVALID_DIRECTORY:Reports.report_and_log(self,level=logging.WARNING,message='Export directory path do not exist',msgctxt=msgctxt)
			case common.IOParamsState.NO_HANDLER:Reports.report_and_log(self,level=logging.WARNING,message='Unable to get export file handler',msgctxt=msgctxt);return{A}
		res=common.IOProcessor.write_camera_data(context,params=params);done_in=time.time()-dt
		if res.num_cameras and res.num_files:
			Reports.report_and_log(self,level=logging.INFO,message='Exported {num_cameras:d} camera(s) to {num_files:d} file(s) in {elapsed:.3f} second(s)',msgctxt=msgctxt,num_cameras=res.num_cameras,num_files=res.num_files,elapsed=done_in)
			if self.open_directory:bpy.ops.wm.path_open('EXEC_DEFAULT',filepath=self.directory)
		else:Reports.report_and_log(self,level=logging.WARNING,message='No file(s) exported',msgctxt=msgctxt)
		return{'FINISHED'}