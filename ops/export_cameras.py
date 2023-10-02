from __future__ import annotations
_G='open_directory'
_F='Untitled'
_E=False
_D='CPP_OT_export_cameras'
_C='reality_capture'
_B='HIDDEN'
_A=True
import logging,os,time
from..import Reports
from.import common
from..import constants
from..import icons
from..import main
from..import props
import bpy
from bpy.types import Context,Event,Operator
from bpy.props import BoolProperty,EnumProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props.wm import WMProps
__all__=_D,
class CPP_OT_export_cameras(Operator,common.IOFileBase_Params,common.IOFile_Params,common.IOTransform_Params,props.intern.rc_csv.RC_CSV_ExportParams,props.intern.rc_xmp.RC_MetadataXMP_Params,props.intern.rc_xmp.RC_MetadataXMP_ExportParams):
	bl_idname='cpp.export_cameras';bl_label='Export Cameras';bl_description='Export camera data';bl_options={'REGISTER','UNDO','PRESET'};bl_translation_context=_D;check_existing:BoolProperty(default=_A,options={_B},name='Check Existing',description='Check and warn on overwriting existing files');fmt_locked:BoolProperty(description='',default=_A,options={_B},name='Format Locked');open_directory:BoolProperty(default=_A,options={_B},translation_context=_D,name='Open Directory',description='Open directory after export');fmt:EnumProperty(items=((common.IOFormat.RC_IECP.name,'Internal/External camera parameters','',icons.get_id(_C),common.IOFormat.RC_IECP.value),(common.IOFormat.RC_NXYZ.name,'Comma-separated Name, X, Y, Z','',icons.get_id(_C),common.IOFormat.RC_NXYZ.value),(common.IOFormat.RC_NXYZHPR.name,'Comma-separated Name, X, Y, Z, Heading, Pitch, Roll','',icons.get_id(_C),common.IOFormat.RC_NXYZHPR.value),(common.IOFormat.RC_NXYZOPK.name,'Comma-separated Name, X, Y, Z, Omega, Phi, Kappa','',icons.get_id(_C),common.IOFormat.RC_NXYZOPK.value),(common.IOFormat.RC_METADATA_XMP.name,'Metadata (XMP)','',icons.get_id(_C),common.IOFormat.RC_METADATA_XMP.value)),options={_B},translation_context='IOFormat',name='Format');name_source:EnumProperty(items=((common.UnifiedNameOptions.USE_CAMERA_NAME.name,'Use Object Name','Use camera object name as source'),(common.UnifiedNameOptions.USE_CAM_NAME.name,'Use Camera Name','Use camera data name as source'),(common.UnifiedNameOptions.USE_IMAGE_NAME.name,'Use Image Name','Use image data-block name as source'),(common.UnifiedNameOptions.USE_IMAGE_FILEPATH.name,'Use Image File Name','Use image file name as source')),default=common.UnifiedNameOptions.USE_CAMERA_NAME.name,options={_B},translation_context=_D,name='Name Source',description='Name source for export')
	def _check_filepath(self):
		format=common.IOFormat[self.fmt];ext=common.IOProcessor.extension_of(format=format);basename=os.path.basename(self.filepath)
		if not basename:basename=_F
		dirname=os.path.dirname(self.filepath);name_noext=common.IOProcessor.eval_filename(format=format,name=os.path.splitext(basename)[0]);filepath=bpy.path.ensure_ext(os.path.join(dirname,name_noext),ext)
		if self.filepath!=filepath:self.filepath=filepath;return _A
	def _check_fmt(self):
		self.fmt_locked=_E
		if self.files:
			file_format=common.IOProcessor.eval_fmt(directory=self.directory,files=self.files)
			if file_format!=common.IOFormat.UNKNOWN:
				self.fmt_locked=_A
				if self.fmt!=file_format.name:self.fmt=file_format.name;return self._check_filepath()
	def check(self,context:Context)->bool:change_filepath=self._check_filepath();change_fmt=self._check_fmt();return change_fmt or change_filepath
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_E;layout.use_property_decorate=_E;col=layout.column(align=_A);col.enabled=not self.fmt_locked;col.prop(self,'fmt',text='');col=layout.column(align=_A);col.prop(self,'name_source',text='');col=layout.column(align=_A);col.use_property_split=_A;col.prop(self,_G)
	@classmethod
	def poll(cls,context:Context):
		wm_props:WMProps=context.window_manager.cpp
		if wm_props.setup_context_stage==constants.SetupStage.PASS_THROUGH.name:
			for ob in context.scene.objects:
				if main.Workflow.camera_poll(ob):return _A
		return _E
	def invoke(self,context:Context,event:Event):self.filename=_F;wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	@Reports.log_execution_helper
	def execute(self,context:Context):
		dt=time.time();msgctxt=self.__class__.__qualname__
		if not(self.directory and os.path.isdir(self.directory)):return{'CANCELLED'}
		keywords=self.as_keywords(ignore=('check_existing','fmt_locked','filter_glob',_G,'global_scale_single','global_scale_double'));keywords['global_scale']=self.global_scale;done_num_files,done_num_cameras=common.IOProcessor.write(context,**keywords);done_in=time.time()-dt
		if done_num_files and done_num_cameras:
			Reports.report_and_log(self,level=logging.INFO,message='Exported {num_cameras:d} camera(s) to {num_files:d} file(s) in {elapsed:.3f} seconds',msgctxt=msgctxt,num_cameras=done_num_cameras,num_files=done_num_files,elapsed=done_in)
			if self.open_directory:bpy.ops.wm.path_open('EXEC_DEFAULT',filepath=self.directory)
		else:Reports.report_and_log(self,level=logging.WARNING,message='No file(s) exported',msgctxt=msgctxt)
		return{'FINISHED'}