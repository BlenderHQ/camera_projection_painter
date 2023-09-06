from __future__ import annotations
_B='CPP_OT_import_cameras'
_A=True
import logging,os,time
from.import common
from..import icons
from..import main
from..import reports
from..lib import bhqab
import bpy
from bpy.types import Context,Event,Operator
from bpy.props import BoolProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props.scene import SceneProps
__all__=_B,
class CPP_OT_import_cameras(common.IOUnifiedName_Params,common.IOFileBase_Params,common.IOFile_Params,common.IOTransform_Params,metaclass=common.SetupContextOperator):
	bl_idname='cpp.import_cameras';bl_label='Import Cameras';bl_description='Import camera data';bl_options={'REGISTER','UNDO','PRESET'};bl_translation_context=_B;use_existing_caches:BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
	def draw(self:Operator,context:Context):
		B='IOFormat';A='reality_capture';layout=self.layout;files_word=bpy.app.translations.pgettext('file(s)',B)
		for(io_format,count)in self.input_count.items():
			if count:
				match io_format:
					case common.IOFormat.UNKNOWN:name='Unknown';icon=''
					case common.IOFormat.RC_IECP:name='Internal/External camera parameters';icon=A
					case common.IOFormat.RC_NXYZ:name='Comma-separated Name, X, Y, Z';icon=A
					case common.IOFormat.RC_NXYZHPR:name='Comma-separated Name, X, Y, Z, Heading, Pitch, Roll';icon=A
					case common.IOFormat.RC_NXYZOPK:name='Comma-separated Name, X, Y, Z, Omega, Phi, Kappa';icon=A
					case common.IOFormat.RC_METADATA_XMP:name='Metadata (XMP)';icon=A
				name=bpy.app.translations.pgettext(name,msgctxt=B);row=layout.row(align=_A);row.label(icon_value=icons.get_id(icon));col=row.column(align=_A);bhqab.utils_ui.draw_wrapped_text(context,col,text=f'{count} {files_word} "{name}"')
	def check(self,context:Context)->bool:self.input_count=common.IOProcessor.check(directory=self.directory,files=self.files);return _A
	def invoke(self,context:Context,event:Event):
		scene_props:SceneProps=context.scene.cpp
		if scene_props.source_dir and os.path.isdir(scene_props.source_dir):self.directory=scene_props.source_dir
		wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		dt=time.time();msgctxt=self.__class__.__qualname__;scene_props:SceneProps=context.scene.cpp;num_files=len(self.files)
		if not(num_files and self.directory and os.path.isdir(self.directory)):return{'CANCELLED'}
		keywords=self.as_keywords(ignore=('filter_glob','global_scale_single','global_scale_double'));keywords['global_scale']=self.global_scale
		if not self.use_existing_caches:flags=common.UnifiedNameOptions.from_string_set(self.un_flags);common.UnifiedNameCache.update_eval_cameras_cache(context,flags=flags)
		done_num_files,done_num_cameras=common.IOProcessor.read(context,**keywords);main.CheckPoint.object_arr_has_changes=_A;done_in=time.time()-dt
		if done_num_cameras:scene_props.source_dir=self.directory;reports.report_and_log(self,level=logging.INFO,message='Imported data of {done_num_cameras:d} camera(s) from {done_num_files:d}/{num_files:d} file(s) in {elapsed:.3f} second(s)',msgctxt=msgctxt,done_num_cameras=done_num_cameras,done_num_files=done_num_files,num_files=num_files,elapsed=done_in)
		else:reports.report_and_log(self,level=logging.WARNING,message='Unable to import {num_files:d} file(s)',msgctxt=msgctxt,num_files=num_files)
		return{'FINISHED'}