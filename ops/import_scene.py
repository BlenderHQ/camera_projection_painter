from __future__ import annotations
_J='HIDDEN'
_I='FINISHED'
_H='CPP_OT_import_scene'
_G='EXEC_DEFAULT'
_F='CANCELLED'
_E='dae'
_D='obj'
_C='fbx'
_B=True
_A=False
import logging,os,re
from..import Reports
from.import common
from..import get_addon_pref
from..import main
from..lib import bhqab
import bpy
from bpy.types import Context,Event,Material,Operator
from bpy.props import BoolProperty,EnumProperty,StringProperty
import addon_utils
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props import Object;from..props.wm import WMProps
__all__=_H,
def check_additional_builtin_io_addons()->set:
	ret=set()
	if addon_utils.check('io_scene_fbx')[1]:ret.add(_C)
	if addon_utils.check('io_scene_obj')[1]:ret.add(_D)
	if bpy.app.build_options.collada:ret.add(_E)
	return ret
def get_prop_file_format_items(_self=None,_context=None):
	ret=[];additional_io_addons_set=check_additional_builtin_io_addons()
	if _C in additional_io_addons_set:ret.append((_C,'Autodesk (*.fbx)',''))
	if _D in additional_io_addons_set:ret.append((_D,'Wavefront (*.obj)',''))
	if _E in additional_io_addons_set:ret.append((_E,'Collada (*.dae)',''))
	return ret
def _get_file_fmt_enum_item_name_from_fp(fp:str)->str:
	if fp:
		_,ext=os.path.splitext(fp)
		if ext:
			for(enum_str,_enum_name,_enum_desc)in get_prop_file_format_items():
				if ext==f".{enum_str}":return enum_str
def _ot_result_to_bool(result:set)->bool:
	if result=={_I}:return _B
	elif result=={_F}:return _A
	else:raise AssertionError('Operator should be executed default, not running modal.')
def _cb_REALITY_CAPTURE_FBX(context:Context,abs_fp:str)->bool:ret=bpy.ops.import_scene.fbx(_G,filepath=abs_fp,use_manual_orientation=_A,global_scale=1.,bake_space_transform=_A,use_custom_normals=_B,use_image_search=_A,use_alpha_decals=_A,use_anim=_B,anim_offset=1.,use_subsurf=_A,use_custom_props=_B,use_custom_props_enum_as_string=_B,ignore_leaf_bones=_A,force_connect_children=_A,automatic_bone_orientation=_A,primary_bone_axis='Y',secondary_bone_axis='X',use_prepost_rot=_B,axis_forward='-Z',axis_up='Y');return _ot_result_to_bool(ret)
def _cb_REALITY_CAPTURE_OBJ(context:Context,abs_fp:str)->bool:ret=bpy.ops.wm.obj_import(_G,filepath=abs_fp,global_scale=1.,clamp_size=.0,forward_axis='NEGATIVE_Z',up_axis='Y',use_split_objects=_B,use_split_groups=_A,import_vertex_groups=_A,validate_meshes=_A);return _ot_result_to_bool(ret)
def _cb_REALITY_CAPTURE_DAE(context:Context,abs_fp:str)->bool:ret=bpy.ops.wm.collada_import(_G,filepath=abs_fp,import_units=_A,fix_orientation=_A,find_chains=_A,auto_connect=_A,min_chain_length=0,keep_bind_info=_A);return _ot_result_to_bool(ret)
_CALLBACKS={'REALITY_CAPTURE':{_C:_cb_REALITY_CAPTURE_FBX,_D:_cb_REALITY_CAPTURE_OBJ,_E:_cb_REALITY_CAPTURE_DAE}}
def _apply_udim_materials_fix(context:Context,*,objects:set[Object]):
	for ob in objects:
		if main.Workflow.object_poll(ob):
			context.view_layer.objects.active=ob;ob_name=ob.name_full;materials:list[Material]=list()
			for slot in ob.material_slots:
				if slot.material:materials.append(slot.material)
			is_udim_fix_required=_A
			for mat in materials:
				if re.match(ob_name+'\\.\\d',mat.name_full):is_udim_fix_required=_B
				else:is_udim_fix_required=_A;break
			if is_udim_fix_required:
				bpy.ops.object.material_slot_remove_unused()
				while len(ob.material_slots)>1:bpy.ops.object.material_slot_remove()
				if ob.material_slots:mat=ob.material_slots[0].material;mat.name=ob_name+'.<UDIM>'
class CPP_OT_import_scene(common.IOFileBase_Params,metaclass=common.SetupContextOperator):
	bl_idname='cpp.import_scene';bl_label='Import Scene';bl_description='Import paint object';bl_translation_context=_H;bl_options={'REGISTER','UNDO'}
	def _get_file_fmt_filter_glob(self)->str:
		ret=''
		for(enum_str,_enum_name,_enum_desc)in get_prop_file_format_items():ret+=f"*.{enum_str};"
		return ret
	filter_glob:StringProperty(get=_get_file_fmt_filter_glob,options={_J});is_filepath_recognized:BoolProperty(options={_J});file_format:EnumProperty(items=get_prop_file_format_items,name='Type',description='File type to be imported')
	def draw(self:Operator,context:Context):
		layout=self.layout;layout.use_property_split=_B;addon_pref=get_addon_pref(context);layout.prop(addon_pref,'preferred_software_workflow')
		if self.is_filepath_recognized:text='Selected file recognized as\n'+layout.enum_item_name(self,'file_format',self.file_format)
		else:text='Please, select your reconstructed scene file.'
		bhqab.utils_ui.draw_wrapped_text(context,layout,text=text)
	def check(self,_context):
		file_fmt=_get_file_fmt_enum_item_name_from_fp(self.filepath);self.is_filepath_recognized=_A
		if file_fmt is not None:self.file_format=file_fmt;self.is_filepath_recognized=_B
		return file_fmt
	def invoke(self,context:Context,_event:Event):wm=context.window_manager;wm.fileselect_add(self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		cls=self.__class__;msgctxt=cls.bl_translation_context
		if not self.filename:return{_F}
		if self.is_filepath_recognized is _A:Reports.report_and_log(self,level=logging.WARNING,message='Unable to import file with unknown file extension',msgctxt=msgctxt);return{_F}
		addon_pref=get_addon_pref(context);wm=context.window_manager;wm_props:WMProps=wm.cpp;initial_objects=set(context.scene.objects);result=_CALLBACKS[addon_pref.preferred_software_workflow][self.file_format](context,self.filepath);imported_objects=set(context.scene.objects)-initial_objects
		if wm_props.configure_udim:_apply_udim_materials_fix(context,objects=imported_objects)
		if result is _B:Reports.report_and_log(self,level=logging.INFO,message='Imported "{filepath}"',msgctxt=msgctxt,filepath=os.path.basename(self.filepath));return{_I}
		else:Reports.report_and_log(self,level=logging.WARNING,message='Import Failed "{filepath}"',msgctxt=msgctxt,filepath=self.filepath);return{_F}