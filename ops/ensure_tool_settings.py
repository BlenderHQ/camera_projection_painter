from __future__ import annotations
_A='CPP_OT_ensure_tool_settings'
import logging
from..import Reports
from.import common
from..import main
import bpy
from bpy.types import Context,Mesh
__all__=_A,
class CPP_OT_ensure_tool_settings(metaclass=common.SetupContextOperator):
	bl_idname='cpp.ensure_tool_settings';bl_label='Ensure Tool Settings';bl_translation_context=_A;options={'REGISTER'}
	def execute(self,context:Context):
		F='IMAGE';E='VIEW_3D';D='builtin_brush.Clone';C='TEXTURE_PAINT';B=False;A=True;cls=self.__class__;msgctxt=cls.bl_translation_context;ob=main.Workflow.get_object()
		if not main.Workflow.object_poll(ob):
			for ob in context.visible_objects:
				if main.Workflow.object_poll(ob):context.view_layer.objects.active=ob;break
		is_ob_ok=A;ob=main.Workflow.get_object()
		if not main.Workflow.object_poll(ob):
			is_ob_ok=B
			if ob:
				me:Mesh=ob.data
				if me.polygons:
					uv_layer=me.uv_layers.active
					if not uv_layer:is_ob_ok=A;Reports.report_and_log(self,level=logging.WARNING,message='Active UV map is missing, continue with limited capabilities',msgctxt=msgctxt)
				else:Reports.report_and_log(self,level=logging.WARNING,message='Canvas object has no polygons',msgctxt=msgctxt)
			else:Reports.report_and_log(self,level=logging.WARNING,message='Scene is missing canvas object',msgctxt=msgctxt)
		if not is_ob_ok:return{'CANCELLED'}
		scene=context.scene;imapaint=scene.tool_settings.image_paint
		if ob.mode!=C:bpy.ops.object.mode_set(mode=C)
		tool=context.workspace.tools.from_space_view3d_mode(context.mode,create=B)
		if tool.idname!=D:bpy.ops.wm.tool_set_by_id(name=D,cycle=B,space_type=E)
		if imapaint.mode!=F:imapaint.mode=F
		if not imapaint.use_clone_layer:imapaint.use_clone_layer=A
		common.update_scene_editing_cage(context)
		for area in context.screen.areas:
			if area.type==E:area.spaces.active.shading.light='FLAT'
		return{'FINISHED'}