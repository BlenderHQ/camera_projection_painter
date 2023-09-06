from __future__ import annotations
_M='CPP_OT_export_cameras'
_L='transform'
_K='Transform'
_J='INVOKE_DEFAULT'
_I='EXEC_DEFAULT'
_H='image'
_G='export_reality_capture'
_F='reality_capture'
_E='SceneProps'
_D=False
_C=None
_B='DEFAULT_CLOSED'
_A=True
from enum import auto,IntFlag
from.import get_addon_pref
from.import constants
from.import icons
from.import main
from.import ops
from.import props
from bpy.types import Context,Operator,Panel,Scene,SpaceFileBrowser,UILayout,UIList
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
if TYPE_CHECKING:from.lib.bhqab.utils_ui import PreferencesUpdateProperties;from.props.camera import BindImageHistoryItem;from.props.camera import CameraProps;from.props.intern.rc_xmp import RC_MetadataXMP_Props;from.props.ob import ObjectProps;from.props.scene import SceneProps;from.props.wm import WMProps
__all__='PanelPoll','CPP_PT_dev_runtime_info','CPP_PT_dataset','CPP_PT_image','CPP_PT_transform','CPP_PT_transform_location_default','CPP_PT_transform_location_rc_xyalt','CPP_PT_transform_rotation','CPP_PT_transform_rotation_rc_hpr','CPP_PT_transform_rotation_rc_opk','CPP_PT_transform_rotation_rc_rotation','CPP_PT_rc_rc_xmp_params','CPP_PT_calibration','CPP_PT_lens_distortion','CPP_PT_inspection','CPP_PT_inspection_image_orientation','CPP_PT_inspection_highlight_border','CPP_PT_unified_name_props','CPP_PT_io_cameras_transform','CPP_PT_export_cameras_rc_csv','CPP_PT_export_cameras_rc_metadata_xmp'
class PanelPoll(IntFlag):NONE=auto();OBJECT_MODE=auto();PAINT_MODE=auto();TOOL_POLL=auto();CAMERA=auto();IMAGE=auto();BRUSH=auto()
class PanelMembers:bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Camera Painter';bl_options=set();bl_translation_context='CPP'
class IOPanelMembers:bl_space_type='FILE_BROWSER';bl_region_type='TOOL_PROPS';bl_parent_id='FILE_PT_operator';bl_options=set()
class PanelBase(PanelMembers):
	header_icon:str;requirements:PanelPoll
	def draw_header(self,_context:Context):
		icon_value=icons.get_id(self.header_icon)
		if icon_value:self.layout.label(icon_value=icon_value)
	@classmethod
	def poll(cls,context:Context):
		ret=_A
		if PanelPoll.CAMERA&cls.requirements:ret=ret and main.Workflow.cam is not _C
		if PanelPoll.IMAGE&cls.requirements:ret=ret and main.Workflow.image is not _C
		if PanelPoll.BRUSH&cls.requirements:ret=ret and main.Workflow.brush is not _C
		if PanelPoll.TOOL_POLL&cls.requirements:ret=ret and main.Workflow.ImagePaint.tool_poll(context)
		required_modes=set()
		if PanelPoll.OBJECT_MODE&cls.requirements:required_modes.add('OBJECT')
		if PanelPoll.PAINT_MODE&cls.requirements:required_modes.add('PAINT_TEXTURE')
		if required_modes:ret=ret and context.mode in required_modes
		return ret
class CPP_PT_dataset(Panel,PanelBase):
	bl_label='Dataset';bl_order=0;header_icon='dataset';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE
	def draw_header(self,context:Context):
		layout=self.layout;addon_pref=get_addon_pref(context);update_props:PreferencesUpdateProperties=addon_pref.update_props
		if update_props.has_updates:keywords=dict(icon_value=icons.get_id('update'),text=pgettext('Update Available','PreferencesUpdate'))
		else:keywords=dict(icon_value=icons.get_id('preferences'),text='')
		props:ops.pref_show.CPP_OT_pref_show=layout.operator(operator=ops.pref_show.CPP_OT_pref_show.bl_idname,emboss=_D,**keywords)
		if update_props.has_updates:props.shortcut='UPDATES'
	def draw(self,context:Context):A='ALL';layout=self.layout;layout.use_property_split=_A;scene:Scene=context.scene;scene_props:SceneProps=scene.cpp;wm_props:WMProps=context.window_manager.cpp;is_setup_context=wm_props.setup_context_stage==constants.SetupStage.PASS_THROUGH.name;col=layout.column();col.enabled=is_setup_context;col.scale_y=1.5;col.operator(operator=ops.setup_context.CPP_OT_setup_context.bl_idname,icon_value=icons.get_id('setup_context'));col=layout.column(align=_A);col.operator(operator=ops.import_scene.CPP_OT_import_scene.bl_idname,icon_value=icons.get_id('import_scene'));col=layout.column(align=_A);col.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Import Camera Images',icon_value=icons.get_id('import_images')).mode=A;scol=col.column(align=_A);scol.operator_context=_I;props:ops.bind_images.CPP_OT_bind_images=scol.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Bind Camera Images',icon_value=icons.get_id('bind'));props.mode=A;col=layout.column(align=_A);scol.operator_context=_J;col.operator(operator=ops.import_cameras.CPP_OT_import_cameras.bl_idname,icon_value=icons.get_id('import_cameras'));col.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id('export_cameras'));col=layout.column(align=_A);col.prop(scene_props,'precision',expand=_A)
class CPP_UL_bind_history_item(UIList):
	def draw_item(self,context:Context,layout:UILayout,data:CameraProps,item:BindImageHistoryItem,icon_id:int,active_data:CameraProps,active_propname:str,index:int):
		row=layout.row(align=_A);image=item.image
		if image:row.label(text=image.name)
		else:row.alignment='RIGHT'
		row.emboss='NONE';props:ops.bind_history_remove.CPP_OT_bind_history_remove=row.operator(operator=ops.bind_history_remove.CPP_OT_bind_history_remove.bl_idname,text='',icon='REMOVE');props.index=index
class CPP_PT_image(Panel,PanelBase):
	bl_label='Image';bl_order=1;header_icon=_H;requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA
	def draw(self,_context:Context):
		C='ACTIVE';B='image.open';A='image.new';layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;cam=main.Workflow.cam;cam_props:CameraProps=cam.cpp;image=cam_props.image
		if image:layout.template_ID_preview(cam_props,_H,new=A,open=B,rows=6,cols=5)
		else:layout.template_ID(cam_props,_H,new=A,open=B)
		col=layout.column(align=_A);col.operator_context=_J;props:ops.bind_images.CPP_OT_bind_images=col.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Import Image',icon_value=icons.get_id('import_image'));props.mode=C;scol=col.column(align=_A);scol.operator_context=_I;props:ops.bind_images.CPP_OT_bind_images=scol.operator(operator=ops.bind_images.CPP_OT_bind_images.bl_idname,text='Bind Image',icon_value=icons.get_id('bind'));props.mode=C;col=layout.column(align=_A);col.use_property_split=_D;col.template_list(CPP_UL_bind_history_item.__qualname__,'',cam_props,'bind_history',cam_props,'active_bind_index',rows=1)
class CPP_PT_transform(Panel,PanelBase):
	bl_label=_K;bl_options={_B};bl_order=2;header_icon=_L;requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA
	def draw(self,_context:Context):0
class CPP_PT_transform_location_default(Panel,PanelBase):
	bl_label='Location';bl_options=set();bl_parent_id=CPP_PT_transform.__qualname__;header_icon='location';requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.location.draw(context,layout)
class CPP_PT_transform_location_rc_xyalt(Panel,PanelBase):
	bl_label='X, Y, Alt';bl_options={_B};bl_parent_id=CPP_PT_transform.__qualname__;header_icon=_F;requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.rc_xyalt.draw(context,layout);props:ops.export_cameras.CPP_OT_export_cameras=layout.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id(_G));props.fmt=ops.common.IOFormat.RC_NXYZ.name
class CPP_PT_transform_rotation(Panel,PanelBase):
	bl_label='Rotation';bl_options=set();bl_parent_id=CPP_PT_transform.__qualname__;header_icon='rotation';requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.rotation_matrix.draw(context,layout)
class CPP_PT_transform_rotation_rc_hpr(Panel,PanelBase):
	bl_label='Heading, Pitch, Roll';bl_options={_B};bl_parent_id=CPP_PT_transform.__qualname__;header_icon=_F;requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.rc_hpr.draw(context,layout);props:ops.export_cameras.CPP_OT_export_cameras=layout.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id(_G));props.fmt=ops.common.IOFormat.RC_NXYZHPR.name
class CPP_PT_transform_rotation_rc_opk(Panel,PanelBase):
	bl_label='Omega, Phi, Kappa';bl_options={_B};bl_parent_id=CPP_PT_transform.__qualname__;header_icon=_F;requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.rc_opk.draw(context,layout);props:ops.export_cameras.CPP_OT_export_cameras=layout.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id(_G));props.fmt=ops.common.IOFormat.RC_NXYZOPK.name
class CPP_PT_rc_rc_xmp_params(Panel,PanelBase):
	bl_label='XMP Parameters';bl_options={_B};bl_parent_id=CPP_PT_transform.__qualname__;header_icon=_F;requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;cam=main.Workflow.cam;cam_props:CameraProps=cam.cpp;rc_xmp_props:RC_MetadataXMP_Props=cam_props.rc_metadata_xmp_props;rc_xmp_props.ui_draw_rc_metadata_xmp_params(context,layout);props:ops.export_cameras.CPP_OT_export_cameras=layout.operator(operator=ops.export_cameras.CPP_OT_export_cameras.bl_idname,icon_value=icons.get_id(_G));props.fmt=ops.common.IOFormat.RC_METADATA_XMP.name
class CPP_PT_transform_rotation_rc_rotation(Panel,PanelBase):
	bl_label='Rotation Component';bl_options={_B};bl_parent_id=CPP_PT_rc_rc_xmp_params.__qualname__;header_icon=_C;requirements=PanelPoll.NONE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;camera=main.Workflow.camera;camera_props:ObjectProps=camera.cpp;camera_props.rc_rotation.draw(context,layout)
class CPP_PT_calibration(Panel,PanelBase):
	bl_label='Calibration';bl_options={_B};bl_order=3;header_icon='calibration';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA|PanelPoll.IMAGE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;cam=main.Workflow.cam;cam_props:CameraProps=cam.cpp;col=layout.column(align=_A);col.prop(scene_props,'units',expand=_A);cam_props.ui_draw_calibration(context,layout)
class CPP_PT_lens_distortion(Panel,PanelBase):
	bl_label='Lens Distortion';bl_options={_B};bl_order=4;header_icon='lens_distortion';requirements=PanelPoll.OBJECT_MODE|PanelPoll.PAINT_MODE|PanelPoll.CAMERA|PanelPoll.IMAGE
	def draw(self,context:Context):layout=self.layout;layout.use_property_decorate=_A;layout.use_property_split=_A;cam=main.Workflow.cam;cam_props:CameraProps=cam.cpp;cam_props.ui_draw_lens_distortion(context,layout)
class CPP_PT_inspection(Panel,PanelBase):
	bl_label='Inspection';bl_options={_B};bl_order=5;header_icon='inspection';requirements=PanelPoll.PAINT_MODE|PanelPoll.TOOL_POLL
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'cameras_viewport_size',text='Camera Size',text_ctxt=_E);layout.prop(scene_props,'current_image_alpha',text='Image Alpha',text_ctxt=_E)
class CPP_PT_inspection_image_orientation(Panel,PanelMembers):
	bl_label='Orientation';bl_options={_B};bl_parent_id=CPP_PT_inspection.__name__
	def draw_header(self,context:Context):layout=self.layout;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'highlight_orientation',text='')
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.enabled=scene_props.highlight_orientation;layout.prop(scene_props,'highlight_orientation_landscape_color',text='Landscape',text_ctxt=_E);layout.prop(scene_props,'highlight_orientation_portrait_color',text='Portrait',text_ctxt=_E)
class CPP_PT_inspection_highlight_border(Panel,PanelMembers):
	bl_label='Border';bl_options={_B};bl_parent_id=CPP_PT_inspection.__name__
	def draw_header(self,context:Context):layout=self.layout;scene_props:SceneProps=context.scene.cpp;layout.prop(scene_props,'highlight_border',text='')
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;scene_props:SceneProps=context.scene.cpp;layout.enabled=scene_props.highlight_border;col=layout.column(align=_A);col.prop(scene_props,'highlight_border_color_0',text='Color',text_ctxt=_E);col.prop(scene_props,'highlight_border_color_1',text=' ',translate=_D);col=layout.column(align=_A);col.prop(scene_props,'highlight_border_type',expand=_A,text='Type',text_ctxt=_E)
class CPP_PT_unified_name_props(Panel,IOPanelMembers):
	bl_label='Names Comparison';bl_translation_context='PROP_UN_FLAGS'
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname in{ops.bind_images.CPP_OT_bind_images.__qualname__,ops.import_cameras.CPP_OT_import_cameras.__qualname__}
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_D;sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;col=layout.column();col.props_enum(operator,'un_flags')
class CPP_PT_io_cameras_transform(Panel,IOPanelMembers):
	bl_label=_K
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname in{ops.import_cameras.CPP_OT_import_cameras.__qualname__,ops.export_cameras.CPP_OT_export_cameras.__qualname__}
	def draw_header(self,context:Context):layout=self.layout;layout.label(icon_value=icons.get_id(_L))
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;props.intern.double.properties_draw(operator,'global_scale',context,layout);layout.prop(operator,'axis_up');layout.prop(operator,'axis_forward')
class CPP_PT_export_cameras_rc_csv(Panel,IOPanelMembers):
	bl_label='Character Separated Values';bl_translation_context=_M
	@classmethod
	def poll(cls,context:Context):
		sfile:SpaceFileBrowser=context.space_data;operator:_C|Operator|ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator
		if operator.bl_idname==ops.export_cameras.CPP_OT_export_cameras.__qualname__:operator:ops.export_cameras.CPP_OT_export_cameras;return operator.fmt in{ops.common.IOFormat.RC_IECP.name,ops.common.IOFormat.RC_NXYZ.name,ops.common.IOFormat.RC_NXYZHPR.name,ops.common.IOFormat.RC_NXYZOPK.name}
		return _D
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator:ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator;layout.prop(operator,'rc_csv_write_num_cameras')
class CPP_PT_export_cameras_rc_metadata_xmp(Panel,IOPanelMembers):
	bl_label='Metadata (XMP)';bl_translation_context=_M
	@classmethod
	def poll(cls,context:Context):
		sfile:SpaceFileBrowser=context.space_data;operator:_C|Operator|ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator
		if operator.bl_idname==ops.export_cameras.CPP_OT_export_cameras.__qualname__:operator:ops.export_cameras.CPP_OT_export_cameras;return operator.fmt==ops.common.IOFormat.RC_METADATA_XMP.name
		return _D
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;sfile:SpaceFileBrowser=context.space_data;operator:ops.export_cameras.CPP_OT_export_cameras=sfile.active_operator;operator.ui_draw_rc_metadata_xmp_overwrite_props(context,layout)
class CPP_PT_io_import_scene(Panel,IOPanelMembers):
	bl_label='Options'
	@classmethod
	def poll(cls,context:Context):sfile:SpaceFileBrowser=context.space_data;operator=sfile.active_operator;return operator.bl_idname==ops.import_scene.CPP_OT_import_scene.__qualname__
	def draw(self,context:Context):layout=self.layout;layout.use_property_split=_A;wm_props:WMProps=context.window_manager.cpp;layout.prop(wm_props,'apply_udim_materials_fix')