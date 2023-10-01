from __future__ import annotations
_D='SKIP_SAVE'
_C='CPP_OT_bind_images'
_B='HIDDEN'
_A=False
import logging,os,time
from.import common
from..import main
from..import reports
from..import log
import bpy
from bpy.types import Context,Event,Operator
from bpy.props import BoolProperty,EnumProperty,StringProperty
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props import Image;from..props.camera import CameraProps;from..props.scene import SceneProps
__all__=_C,
class CPP_OT_bind_images(common.IOUnifiedName_Params,metaclass=common.SetupContextOperator):
	bl_idname='cpp.bind_images';bl_description='';bl_label='Bind Camera Images';bl_options={'REGISTER','UNDO'};bl_translation_context=_C;use_existing_caches:BoolProperty(default=_A,options={_B,_D});directory:StringProperty(subtype='DIR_PATH',maxlen=1024,options={_B},translation_context='CPP_IO',name='Directory');mode:EnumProperty(items=(('ACTIVE','Active',''),('ALL','All','')),options={_B,_D})
	@classmethod
	def description(cls,context:Context,properties:CPP_OT_bind_images)->str:
		msgctxt=cls.__qualname__
		match properties.mode:
			case'ACTIVE':return pgettext('Bind the image to the active camera',msgctxt)
			case'ALL':return pgettext('Bind images to all cameras in the scene',msgctxt)
		return''
	def draw(self:Operator,context:Context):0
	def invoke(self,context:Context,_event:Event):
		scene_props:SceneProps=context.scene.cpp
		if scene_props.source_dir and os.path.isdir(scene_props.source_dir):self.directory=scene_props.source_dir
		wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		A=True;cls=self.__class__;dt=time.time();msgctxt=cls.__qualname__;do_directory_search=self.directory and os.path.isdir(self.directory);flags=common.UnifiedNameOptions.from_string_set(self.un_flags)
		if not self.use_existing_caches:
			common.UnifiedNameCache.update_eval_images_cache(flags=flags);common.UnifiedNameCache.update_eval_cameras_cache(context,flags=flags)
			if do_directory_search:common.UnifiedNameCache.update_eval_directory_cache(directory=self.directory,file_format=common.FileFormat.IMAGE,flags=flags)
		match self.mode:
			case'ACTIVE':
				camera=main.Workflow.camera
				if not camera:reports.report_and_log(self,level=logging.WARNING,message='No active camera, operation skipped');return{'CANCELLED'}
				camera_names={common.UnifiedName().from_object(ob=camera,flags=flags)}
			case'ALL':camera_names=common.UnifiedNameCache.cached_camera_names
		image_names=list(common.UnifiedNameCache.cached_image_names)
		if do_directory_search:file_names=list(common.UnifiedNameCache.cached_file_names)
		num_cameras=len(camera_names);num_remains=0;num_changed=0;num_opened=0;num_opening_failed=0;un_camera:common.UnifiedName
		for un_camera in camera_names:
			is_found=_A
			for un_image in image_names:
				if un_camera==un_image:
					image_names.remove(un_image);cam_props:CameraProps=un_camera.item.data.cpp;image:Image=un_image.item
					if cam_props.image!=image:cam_props.image=image;num_changed+=1
					else:num_remains+=1
					is_found=A;break
			else:
				if do_directory_search:
					for un_fp in file_names:
						if un_camera==un_fp:
							file_names.remove(un_fp);image=bpy.data.images.load(un_fp.item,check_existing=_A)
							if image:
								num_opened+=1;cam_props:CameraProps=un_camera.item.data.cpp
								if cam_props.image!=image:cam_props.image=image;num_changed+=1
								else:num_remains+=1
								is_found=A;break
							else:num_opening_failed+=1;log.info(f'Camera "{un_camera.item.name}" skipped because of failed image open from path "{{un_fp.item}}"')
							break
			if not is_found:log.info(f"Can not find image for camera {un_camera.item.name} with given options")
		main.CheckPoint.image_arr_has_changes=A;num_done=num_changed+num_remains;time_done=time.time()-dt;fmt_failed_to_open=''
		if num_opening_failed:fmt_failed_to_open=pgettext(', failed to open %d',msgctxt)%num_opening_failed
		if num_done:
			if num_done==num_cameras:
				if num_done==1:
					if num_changed:
						if num_opened:reports.report_and_log(self,level=logging.INFO,message='The image is open and binded, the previous value has been changed. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
						else:reports.report_and_log(self,level=logging.INFO,message='Binded image, the previous value has been changed. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
					else:reports.report_and_log(self,level=logging.INFO,message='The appropriate image is already binded to the options selected. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
				elif num_changed:
					if num_opened:reports.report_and_log(self,level=logging.INFO,message='Binded all images, opened {num_opened:d} new, replaced {num_changed:d}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_opened=num_opened,num_changed=num_changed,elapsed=time_done)
					else:reports.report_and_log(self,level=logging.INFO,message='Binded all images, {num_changed:d} replaced. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_changed=num_changed,elapsed=time_done)
				else:reports.report_and_log(self,level=logging.INFO,message='For the selected options, all the necessary images are already binded. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,elapsed=time_done)
			elif num_changed:
				if num_opened:reports.report_and_log(self,level=logging.INFO,message='Binded {num_done:d}/{num_cameras:d} required images, opened {num_opened:d} new, replaced {num_changed:d}{fmt_failed_to_open:s}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=num_cameras,num_opened=num_opened,num_changed=num_changed,fmt_failed_to_open=fmt_failed_to_open,elapsed=time_done)
				else:reports.report_and_log(self,level=logging.INFO,message='Binded {num_done:d}/{num_cameras:d} required images, replaced {num_changed:d}. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=num_cameras,num_changed=num_changed,elapsed=time_done)
			else:reports.report_and_log(self,level=logging.INFO,message='{num_done:d}/{num_cameras:d} of the necessary images are binded for the selected options. Search time - {elapsed:.3f} second(s)',msgctxt=msgctxt,num_done=num_done,num_cameras=num_cameras,elapsed=time_done)
		elif do_directory_search:reports.report_and_log(self,level=logging.INFO,message='Could not bind image(s) of either available or "{directory:s}" directory with selected options{fmt_failed_to_open:s}',msgctxt=msgctxt,directory=self.directory,fmt_failed_to_open=fmt_failed_to_open)
		else:reports.report_and_log(self,level=logging.INFO,message='Could not bind image(s) with selected options{fmt_failed_to_open:s}',msgctxt=msgctxt,fmt_failed_to_open=fmt_failed_to_open)
		scene_props:SceneProps=context.scene.cpp;scene_props.source_dir=self.directory;return{'FINISHED'}