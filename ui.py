from __future__ import annotations
_J='reality_capture'
_I='CPP_OT_export_cameras'
_H='EXEC_DEFAULT'
_G='INVOKE_DEFAULT'
_F='image'
_E=None
_D='DEFAULT_CLOSED'
_C=False
_B='SceneProps'
_A=True
from enum import auto,IntFlag
from.lib import bhqupd
from.import constants
from.import icons
from.import main
from.import ops
from bpy.types import Context,Operator,Panel,SpaceFileBrowser,UILayout,UIList
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
if TYPE_CHECKING:from.props import Scene;from.props.camera import BindImageHistoryItem;from.props.camera import CameraProps;from.props.scene import SceneProps;from.props.wm import WMProps
__all__='PanelPoll','CPP_PT_dev_runtime_info','CPP_PT_dataset','CPP_PT_image','CPP_PT_calibration','CPP_PT_lens_distortion','CPP_PT_inspection','CPP_PT_inspection_image_orientation','CPP_PT_inspection_highlight_border','CPP_PT_unified_name_props','CPP_PT_io_cameras_transform','CPP_PT_export_cameras_rc_csv','CPP_PT_export_cameras_rc_metadata_xmp'
class PanelPoll(IntFlag):NONE=auto();OBJECT_MODE=auto();PAINT_MODE=auto();TOOL_POLL=auto();CAMERA=auto();IMAGE=auto();BRUSH=auto()
class PanelMembers:bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Camera Painter';bl_options=set();bl_translation_context='CPP'
class IOPanelMembers:bl_space_type='FILE_BROWSER';bl_region_type='TOOL_PROPS';bl_parent_id='FILE_PT_operator';bl_options=set()
class PanelHeaderIcon:
	header_icon:str
	def draw_header(self,_context:Context):
		icon_value=icons.get_id(self.header_icon)
		if icon_value:self.layout.label(icon_value=icon_value)
class PanelBase(PanelMembers,PanelHeaderIcon):
	requirements:PanelPoll
	@classmethod
	def poll(cls,context:Context):
		ret=_A
		if PanelPoll.CAMERA&cls.requirements:ret=ret and main.Workflow.get_cam()is not _E
		if PanelPoll.IMAGE&cls.requirements:ret=ret and main.Workflow.get_image()is not _E
		if PanelPoll.BRUSH&cls.requirements:ret=ret and main.Workflow.get_brush()is not _E
		if PanelPoll.TOOL_POLL&cls.requirements:ret=ret and main.Workflow.ImagePaint.tool_poll(context)
		required_modes=set()
		if PanelPoll.OBJECT_MODE&cls.requirements:required_modes.add('OBJECT')
		if PanelPoll.PAINT_MODE&cls.requirements:required_modes.add('PAINT_TEXTURE')
		if required_modes:ret=ret and context.mode in required_modes
		return ret
class CPP_PT_dataset(Panel,PanelBase):
	bl_label='Dataset';bl_order=0;header_icon='dataset';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE
	def draw_header(self,context:Context):
		layout=self.layout;has_updates=bhqupd.has_updates()
		if has_updates:keywords=dict(icon_value=icons.get_id('update'),text=pgettext('Update Available','Preferences'))
		else:keywords=dict(icon_value=icons.get_id('preferences'),text='')
		props:ops.pref_show.CPP_OT_pref_show=layout.operator(operator=ops.pref_show.CPP_OT_pref_show.bl_idname,emboss=_C,**keywords)
		if has_updates:props.shortcut='UPDATES'
	def draw(self,context:Context):A='ALL';layout=self.layout;layout.use_property_split=_A;wm_props:WMProps=context.window_manager.cpp;is_setup_context=wm_props.setup_context_stage==constants.SetupStage.PASS_THROUGH.name;col=layout.column();col.enabled=is_setup_context;col.scale_y=1.5;col.operator(operator=ops.setup_context.CPP_OT_setup_context.bl_idname,icon_value=icons.get_id('setup_context'));col=layout.column(align=_A);col.operator(operator=ops.import_scene.CPP_OT_import_scene.bl_idname,icon_value=icons.get_id('import_scene'));col=layout.column(align=_A);col.operator_context=_G;col.operator(operator=ops.import_cameras.CPP_OT_import_cameras.bl_idname,icon_value=icons.get_id('import_cameras'));col.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id('export_cameras'));col=layout.column(align=_A);col.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Import Camera Images',text_ctxt=ops.bind_images.CPP_OT_bind_images.bl_translation_context,icon_value=icons.get_id('import_images')).mode=A;scol=col.column(align=_A);scol.operator_context=_H;props:ops.bind_images.CPP_OT_bind_images=scol.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Bind Camera Images',text_ctxt=ops.bind_images.CPP_OT_bind_images.bl_translation_context,icon_value=icons.get_id('bind'));props.mode=A
class CPP_UL_bind_history_item(UIList):
	def draw_item(self,context:Context,layout:UILayout,data:CameraProps,item:BindImageHistoryItem,icon_id:int,active_data:CameraProps,active_propname:str,index:int):
		row=layout.row(align=_A);image=item.image
		if image:row.label(text=image.name)
		else:row.alignment='RIGHT'
		row.emboss='NONE';props:ops.bind_history_remove.CPP_OT_bind_history_remove=row.operator(operator=ops.bind_history_remove.CPP_OT_bind_history_remove.bl_idname,text='',icon='REMOVE');props.index=index
class CPP_PT_image(Panel,PanelBase):
	bl_label='Image';bl_order=1;header_icon=_F;requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA
	def draw(self,_context:Context):
		C='ACTIVE';B='image.open';A='image.new';layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;cam=main.Workflow.get_cam();cam_props:CameraProps=cam.cpp;image=cam_props.image
		if image:layout.template_ID_preview(cam_props,_F,new=A,open=B,rows=6,cols=5)
		else:layout.template_ID(cam_props,_F,new=A,open=B)
		col=layout.column(align=_A);col.operator_context=_G;props:ops.bind_images.CPP_OT_bind_images=col.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Import Image',text_ctxt=ops.bind_images.CPP_OT_bind_images.bl_translation_context,icon_value=icons.get_id('import_image'));props.mode=C;scol=col.column(align=_A);scol.operator_context=_H;props:ops.bind_images.CPP_OT_bind_images=scol.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Bind Image',text_ctxt=ops.bind_images.CPP_OT_bind_images.bl_translation_context,icon_value=icons.get_id('bind'));props.mode=C;col=layout.column(align=_A);col.use_property_split=_C;col.template_list(CPP_UL_bind_history_item.__qualname__,'',cam_props,'bind_history',cam_props,'active_bind_index',rows=1)
class CPP_PT_calibration(Panel,PanelBase):
	bl_label='Calibration';bl_options={_D};bl_order=3;header_icon='calibration';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA
	def draw(self,context:Context):
		C='Skew';B='Lens';A='CameraProps';layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;scene:Scene=context.scene;scene_props:SceneProps=scene.cpp;cam=main.Workflow.get_cam();cam_props:CameraProps=cam.cpp;col=layout.column(align=_A);col.prop(scene_props,'units',expand=_A)
		match scene_props.units:
			case'MILLIMETERS':layout.prop(cam_props,'s_lens',text=B,text_ctxt=A)
			case'PIXELS':layout.prop(cam_props,'px_lens',text=B,text_ctxt=A)
		col=layout.column(align=_A);col.prop(cam,'sensor_fit');col.prop(cam_props,'s_sensor',text='Sensor',text_ctxt=A);col=layout.column(align=_A);col.prop(cam,'clip_start');col.prop(cam,'clip_end');col=layout.column(align=_A)
		match scene_props.units:
			case'MILLIMETERS':col.prop(cam_props,'s_principal_x_mm',text='Principal X',text_ctxt=A);col.prop(cam_props,'s_principal_y_mm',text='Y',text_ctxt=A);layout.prop(cam_props,'s_skew',text=C,text_ctxt=A)
			case'PIXELS':col.prop(cam_props,'px_principal',text='Principal',text_ctxt=A);layout.prop(cam_props,'px_skew',text=C,text_ctxt=A)
		layout.prop(cam_props,'s_aspect',text='Aspect Ratio',text_ctxt=A)
class CPP_PT_lens_distortion(Panel,PanelBase):
	bl_label='Lens Distortion';bl_options={_D};bl_order=4;header_icon='lens_distortion';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA
	def draw(self,context:Context):
		D='s_k4';C='s_k3';B='s_k2';A='s_k1';layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;cam=main.Workflow.get_cam();cam_props:CameraProps=cam.cpp;layout.prop(cam_props,'distortion_model')
		match cam_props.distortion_model:
			case constants.DistortionModel.BROWN.name:col=layout.column();col.prop(cam_props,A);col.prop(cam_props,B);col.prop(cam_props,C);col.prop(cam_props,D);col.separator();col.prop(cam_props,'s_p1');col.prop(cam_props,'s_p2')
			case constants.DistortionModel.POLYNOMIAL.name:col=layout.column();col.prop(cam_props,A);col.prop(cam_props,B);col.prop(cam_props,C);col.prop(cam_props,D)
			case constants.DistortionModel.DIVISION.name:col=layout.column();col.prop(cam_props,A);col.prop(cam_props,B)
class CPP_PT_inspection(Panel,PanelBase):
	bl_label='Inspection';bl_options={_D};bl_order=5;header_icon='inspection';requirements=PanelPoll.PAINT_MODE|PanelPoll.TOOL_POLL
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'cameras_viewport_size',text='Camera Size',text_ctxt=_B);layout.prop(scene_props,'current_image_alpha',text='Image Alpha',text_ctxt=_B)
class CPP_PT_inspection_image_orientation(Panel,PanelMembers):
	bl_label='Orientation';bl_options={_D};bl_parent_id=CPP_PT_inspection.__name__
	def draw_header(self,context:Context):layout=self.layout;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'highlight_orientation',text='')
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.enabled=scene_props.highlight_orientation;layout.prop(scene_props,'highlight_orientation_landscape_color',text='Landscape',text_ctxt=_B);layout.prop(scene_props,'highlight_orientation_portrait_color',text='Portrait',text_ctxt=_B)
class CPP_PT_inspection_highlight_border(Panel,PanelMembers):
	bl_label='Border';bl_options={_D};bl_parent_id=CPP_PT_inspection.__name__
	def draw_header(self,context:Context):layout=self.layout;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'highlight_border',text='')
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.enabled=scene_props.highlight_border;col=layout.column(align=_A);col.prop(scene_props,'highlight_border_color_0',text='Color',text_ctxt=_B);col.prop(scene_props,'highlight_border_color_1',text=' ',translate=_C);col=layout.column(align=_A);col.prop(scene_props,'highlight_border_type',expand=_A,text='Type',text_ctxt=_B);col=layout.column(align=_A);col.prop(scene_props,'highlight_border_facing',expand=_A,text='Facing',text_ctxt=_B)
class CPP_PT_inspection_cage(Panel,PanelMembers):
	bl_label='Cage';bl_options={_D};bl_parent_id=CPP_PT_inspection.__name__
	def draw_header(self,context:Context):layout=self.layout;scene:Scene=context.scene;scene_props:SceneProps=scene.cpp;layout.prop(scene_props,'use_cage',text='')
	def draw(self,context):layout=self.layout;layout.use_property_split=_A;scene:Scene=context.scene;scene_props:SceneProps=scene.cpp;layout.enabled=scene_props.use_cage;layout.operator(operator=ops.calc_scene_cage.CPP_OT_calc_scene_cage.bl_idname);col=layout.column();col.prop(scene_props,'cage_flags',expand=_A)
class CPP_PT_unified_name_props(Panel,IOPanelMembers):
	bl_label='Names Comparison';bl_translation_context='PROP_UN_FLAGS'
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname in{ops.bind_images.CPP_OT_bind_images.__qualname__,ops.import_cameras.CPP_OT_import_cameras.__qualname__}
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_C;sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;col=layout.column();col.props_enum(operator,'name_flags')
class CPP_PT_io_cameras_transform(Panel,IOPanelMembers):
	bl_label='Transform'
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname in{ops.import_cameras.CPP_OT_import_cameras.__qualname__,ops.export_cameras.CPP_OT_export_cameras.__qualname__}
	def draw_header(self,context:Context):layout=self.layout;layout.label(icon_value=icons.get_id('transform'))
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;layout.prop(operator,'global_scale');layout.prop(operator,'up_axis');layout.prop(operator,'forward_axis')
class CPP_PT_export_cameras_rc_csv(Panel,IOPanelMembers,PanelHeaderIcon):
	bl_label='Character Separated Values';bl_translation_context=_I;header_icon=_J
	@classmethod
	def poll(cls,context:Context):
		sfile:SpaceFileBrowser=context.space_data;operator:_E|Operator|ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator
		if operator.bl_idname==ops.export_cameras.CPP_OT_export_cameras.__qualname__:operator:ops.export_cameras.CPP_OT_export_cameras;return operator.fmt in{ops.common.IOFileFormat.RC_IECP.name,ops.common.IOFileFormat.RC_NXYZ.name,ops.common.IOFileFormat.RC_NXYZHPR.name,ops.common.IOFileFormat.RC_NXYZOPK.name}
		return _C
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator:ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator;layout.prop(operator,'rc_csv_write_num_cameras')
class CPP_PT_export_cameras_rc_metadata_xmp(Panel,IOPanelMembers,PanelHeaderIcon):
	bl_label='Metadata (XMP)';bl_translation_context=_I;header_icon=_J
	@classmethod
	def poll(cls,context:Context):
		sfile:SpaceFileBrowser=context.space_data;operator:_E|Operator|ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator
		if operator.bl_idname==ops.export_cameras.CPP_OT_export_cameras.__qualname__:operator:ops.export_cameras.CPP_OT_export_cameras;return operator.fmt==ops.common.IOFileFormat.RC_METADATA_XMP.name
		return _C
	def draw(self,context:Context):
		layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator:ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator;layout.prop(operator,'rc_metadata_xmp_export_mode');layout.prop(operator,'rc_metadata_xmp_use_calibration_groups')
		if operator.rc_metadata_xmp_use_calibration_groups:box=layout.box();box.prop(operator,'rc_metadata_xmp_calibration_group');box.prop(operator,'rc_metadata_xmp_distortion_group')
		layout.prop(operator,'rc_metadata_xmp_include_editor_options')
		if operator.rc_metadata_xmp_include_editor_options:box=layout.box();box.prop(operator,'rc_metadata_xmp_in_texturing');box.prop(operator,'rc_metadata_xmp_in_meshing')
class CPP_PT_io_import_scene(Panel,IOPanelMembers):
	bl_label='Options'
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname==ops.import_scene.CPP_OT_import_scene.__qualname__
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;wm_props:WMProps=context.window_manager.cpp;layout.prop(wm_props,'configure_udim')