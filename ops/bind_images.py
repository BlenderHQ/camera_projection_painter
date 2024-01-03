from __future__ import annotations
_D='CPP_OT_bind_images'
_C='SKIP_SAVE'
_B=True
_A='HIDDEN'
import logging,os,time
from..import Reports
from.import common
from..import main
from bpy.types import Context,Event,Operator
from bpy.props import BoolProperty,EnumProperty,StringProperty
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props.scene import SceneProps
__all__=_D,
class CPP_OT_bind_images(common.IOName_Params,metaclass=common.SetupContextOperator):
	bl_idname='cpp.bind_images';bl_label='Bind Camera Images';bl_options={'REGISTER','UNDO'};bl_translation_context=_D;directory:StringProperty(subtype='DIR_PATH',maxlen=1024,options={_A},translation_context='CPP_IO',name='Directory');mode:EnumProperty(items=((common.BindImagesMode.ACTIVE.name,'Active',''),(common.BindImagesMode.ALL.name,'All','')),options={_A,_C});filter:BoolProperty(default=_B,options={_A,_C},name='',description='Filter items in File Browser');filter_image:BoolProperty(default=_B,options={_A,_C},name='',description='Show images in the File Browser')
	@classmethod
	def description(cls,context:Context,properties:CPP_OT_bind_images)->str:
		msgctxt=cls.__qualname__
		match properties.mode:
			case common.BindImagesMode.ACTIVE.name:return pgettext('Bind the image to the active camera',msgctxt)
			case common.BindImagesMode.ALL.name:return pgettext('Bind images to all cameras in the scene',msgctxt)
		return''
	def draw(self:Operator,context:Context):
		layout=self.layout
		if context.area.type=='VIEW_3D':layout.prop(self,'name_flags')
	def invoke(self,context:Context,_event:Event):
		scene_props:SceneProps=context.scene.cpp
		if scene_props.source_dir and os.path.isdir(scene_props.source_dir):self.directory=scene_props.source_dir
		self.use_filter=_B;wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		cls=self.__class__;dt=time.time();msgctxt=cls.__qualname__;keywords=self.as_keywords(ignore=('filter_glob',));params=common.BindImagesParams(**keywords)
		match params.state:
			case common.IOParamsState.INVALID_DIRECTORY:Reports.report_and_log(self,level=logging.WARNING,message='Directory do not exist',msgctxt=msgctxt);return{'CANCELLED'}
		res=common.IOProcessor.bind_camera_images(context,params=params);main.CheckPoint.image_arr_has_changes=_B;num_done=res.num_changed+res.num_remains;time_done=time.time()-dt;fmt_failed_to_open=''
		if res.num_opening_failed:fmt_failed_to_open=pgettext(', failed to open %d',msgctxt)%res.num_opening_failed
		if num_done:
			if num_done==res.num_cameras:
				if num_done==1:
					if res.num_changed:
						if res.num_opened:Reports.report_and_log(self,level=logging.INFO,message='The image is open and binded, the previous value has been changed. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
						else:Reports.report_and_log(self,level=logging.INFO,message='Binded image, the previous value has been changed. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
					else:Reports.report_and_log(self,level=logging.INFO,message='The appropriate image is already binded to the options selected. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
				elif res.num_changed:
					if res.num_opened:Reports.report_and_log(self,level=logging.INFO,message='Binded all images, opened {num_opened:d} new, replaced {num_changed:d}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_opened=res.num_opened,num_changed=res.num_changed,elapsed=time_done)
					else:Reports.report_and_log(self,level=logging.INFO,message='Binded all images, {num_changed:d} replaced. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_changed=res.num_changed,elapsed=time_done)
				else:Reports.report_and_log(self,level=logging.INFO,message='For the selected options, all the necessary images are already binded. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
			elif res.num_changed:
				if res.num_opened:Reports.report_and_log(self,level=logging.INFO,message='Binded {num_done:d}/{num_cameras:d} required images, opened {num_opened:d} new, replaced {num_changed:d}{fmt_failed_to_open:s}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=res.num_cameras,num_opened=res.num_opened,num_changed=res.num_changed,fmt_failed_to_open=fmt_failed_to_open,elapsed=time_done)
				else:Reports.report_and_log(self,level=logging.INFO,message='Binded {num_done:d}/{num_cameras:d} required images, replaced {num_changed:d}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=res.num_cameras,num_changed=res.num_changed,elapsed=time_done)
			else:Reports.report_and_log(self,level=logging.INFO,message='{num_done:d}/{num_cameras:d} of the necessary images are binded for the selected options. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=res.num_cameras,elapsed=time_done)
		elif res.directory_search:Reports.report_and_log(self,level=logging.INFO,message='Could not bind image(s) of either available or "{directory:s}" directory with selected options{fmt_failed_to_open:s}',msgctxt=msgctxt,directory=self.directory,fmt_failed_to_open=fmt_failed_to_open)
		else:Reports.report_and_log(self,level=logging.INFO,message='Could not bind image(s) with selected options{fmt_failed_to_open:s}',msgctxt=msgctxt,fmt_failed_to_open=fmt_failed_to_open)
		scene_props:SceneProps=context.scene.cpp;scene_props.source_dir=self.directory;return{'FINISHED'}