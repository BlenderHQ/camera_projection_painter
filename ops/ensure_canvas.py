from __future__ import annotations
_E='CANCELLED'
_D='CPP_OT_ensure_canvas'
_C='CPP_OT_canvas_new'
_B='REGISTER'
_A='FINISHED'
import logging,re
from..import Reports
from.import common
from..import icons
import bpy
from bpy.types import Context,Event,ImagePaint,Material,Operator,ShaderNode,ShaderNodeTree
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props import Image,WindowManager;from..props.wm import WMProps
__all__=_C,_D
_PATTERN='[^.]+\\.\\d+\\.[^.]+'
class CPP_OT_canvas_new(Operator):
	bl_idname='cpp.canvas_new';bl_label='Create New Canvas';bl_translation_context=_C;bl_options={_B}
	@Reports.log_execution_helper
	def execute(self,context:Context):imapaint:ImagePaint=context.tool_settings.image_paint;new_image=bpy.data.images.new(name='Canvas',width=2048,height=2048,alpha=True,float_buffer=True);imapaint.canvas=new_image;return{_A}
def _eval_image_by_object_name(context:Context)->None|Image:
	ob=context.active_object
	if ob:
		ob_name=ob.name_full
		if'MESH'==ob.type:
			for slot in ob.material_slots:
				mat:Material=slot.material
				if mat and mat.use_nodes:
					ntree:ShaderNodeTree=mat.node_tree
					for node in ntree.nodes:
						node:ShaderNode
						if'ShaderNodeTexImage'==node.bl_idname:return node.image
		for image in bpy.data.images:
			if re.match(ob_name+_PATTERN,image.name_full):return image
class CPP_OT_canvas_quick_select(Operator):
	bl_idname='cpp.canvas_quick_select';bl_label='Image Quick Select';bl_description='Select image';bl_translation_context='CPP_OT_canvas_quick_select';bl_options={_B}
	def execute(self,context:Context):
		cls=self.__class__;msgctxt=cls.__qualname__;image=_eval_image_by_object_name(context)
		if image:
			imapaint:ImagePaint=context.tool_settings.image_paint
			if imapaint.canvas!=image:imapaint.canvas=image
			Reports.report_and_log(self,level=logging.INFO,message='Selected image "{filename}"',msgctxt=msgctxt,filename=image.name);return{_A}
		Reports.report_and_log(self,level=logging.WARNING,message='Unable to evaluate image for quick select',msgctxt=msgctxt);return{_E}
class CPP_OT_ensure_canvas(metaclass=common.SetupContextOperator):
	bl_idname='cpp.ensure_canvas';bl_label='Ensure Canvas';bl_translation_context=_D;bl_options={_B}
	def draw(self:Operator,context:Context):
		A='canvas';layout=self.layout;layout.use_property_split=False;imapaint:ImagePaint=context.tool_settings.image_paint;wm:WindowManager=context.window_manager;wm_props:WMProps=wm.cpp;row=layout.row();col=row.column();col.template_icon(icon_value=icons.get_id('ensure_canvas'),scale=common.CENTERED_DIALOG_ICON_SCALE);col=row.column();col.ui_units_x=common.CENTERED_DIALOG_PROPS_UI_UNITS_X
		if imapaint.canvas and imapaint.canvas.preview_ensure():col.template_ID_preview(imapaint,A,new=CPP_OT_canvas_new.bl_idname)
		else:col.template_ID(imapaint,A,new=CPP_OT_canvas_new.bl_idname)
		if imapaint.canvas:col.prop(wm_props,'configure_udim')
		image=_eval_image_by_object_name(context)
		if image:
			if image!=imapaint.canvas:prv=image.preview_ensure();col.operator(operator=CPP_OT_canvas_quick_select.bl_idname,icon_value=prv.icon_id,text=image.name_full)
	def invoke(self,context:Context,event:Event):common.invoke_props_dialog_centered(context,event,operator=self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		cls=self.__class__;msgctxt=cls.__qualname__;wm_props:WMProps=context.window_manager.cpp;imapaint:ImagePaint=context.tool_settings.image_paint
		if wm_props.configure_udim:
			ob=context.object
			if ob and imapaint.canvas:
				pattern=ob.name_full+_PATTERN;match=re.match(pattern,imapaint.canvas.name_full)
				if match:imapaint.canvas.source='TILED';Reports.report_and_log(self,level=logging.INFO,message='Selected "{filename}" as UDIM paint canvas',msgctxt=msgctxt,filename=imapaint.canvas.name_full);return{_A}
		if imapaint.canvas:Reports.report_and_log(self,level=logging.INFO,message='Selected "{filename}" as paint canvas',msgctxt=msgctxt,filename=imapaint.canvas.name_full);return{_A}
		else:Reports.report_and_log(self,level=logging.WARNING,message='Paint canvas is missing',msgctxt=msgctxt);return{_E}