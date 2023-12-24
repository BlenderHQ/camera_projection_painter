from __future__ import annotations
_B='CPP_OT_import_cameras'
_A=True
import logging,os,time
from..import Reports
from.import common
from..import icons
from..import main
from..lib import bhqab
import bpy
from bpy.types import Context,Event,Operator
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props import Scene;from..props.scene import SceneProps
__all__=_B,
class CPP_OT_import_cameras(common.IOName_Params,common.IOFileBaseParams,common.IOFileParams,common.IOTransformParams,metaclass=common.SetupContextOperator):
	bl_idname='cpp.import_cameras';bl_label='Import Cameras';bl_description='Import camera data';bl_options={'REGISTER','UNDO','PRESET'};bl_translation_context=_B
	def draw(self:Operator,context:Context):
		A='IOFormat';layout=self.layout;files_word=bpy.app.translations.pgettext('file(s)',A)
		for(io_format_handler,count)in self.input_count.items():
			if not count:continue
			row=layout.row(align=_A);row.label(icon_value=icons.get_id(io_format_handler.icon));col=row.column(align=_A);name_eval=bpy.app.translations.pgettext(io_format_handler.name,msgctxt=A);bhqab.utils_ui.draw_wrapped_text(context,col,text=f'{count} {files_word} "{name_eval}"')
	def check(self,context:Context)->bool:self.input_count=common.IOProcessor.check_camera_data(directory=self.directory,files=(_.name for _ in self.files));return _A
	def invoke(self,context:Context,event:Event):
		scene:Scene=context.scene;scene_props:SceneProps=scene.cpp
		if scene_props.source_dir and os.path.isdir(scene_props.source_dir):self.directory=scene_props.source_dir
		wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		A='CANCELLED';dt=time.time();msgctxt=self.__class__.__qualname__;keywords:dict=self.as_keywords(ignore=('filter_glob',));params=common.ImportCamerasParams(**keywords)
		match params.state:
			case common.IOParamsState.NO_DIRECTORY:Reports.report_and_log(self,level=logging.WARNING,message='Empty import directory path',msgctxt=msgctxt);return{A}
			case common.IOParamsState.INVALID_DIRECTORY:Reports.report_and_log(self,level=logging.WARNING,message='Import directory path do not exist',msgctxt=msgctxt);return{A}
			case common.IOParamsState.NO_FILES:Reports.report_and_log(self,level=logging.WARNING,message='No files selected for import',msgctxt=msgctxt);return{A}
		res=common.IOProcessor.read_camera_data(context,params=params);scene:Scene=context.scene;scene_props:SceneProps=scene.cpp;num_files=len(self.files);done_in=time.time()-dt
		if res.num_cameras:scene_props.source_dir=self.directory;main.CheckPoint.object_arr_has_changes=_A;Reports.report_and_log(self,level=logging.INFO,message='Imported data of {done_num_cameras:d} camera(s), created {created_num_cameras:d} from {done_num_files:d}/{num_files:d} file(s) in {elapsed:.3f} second(s)',msgctxt=msgctxt,done_num_cameras=res.num_cameras,created_num_cameras=res.num_cameras_created,done_num_files=res.num_files,num_files=num_files,elapsed=done_in)
		else:Reports.report_and_log(self,level=logging.WARNING,message='Unable to import {num_files:d} file(s)',msgctxt=msgctxt,num_files=num_files)
		return{'FINISHED'}