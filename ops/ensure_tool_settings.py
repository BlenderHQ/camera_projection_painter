from __future__ import annotations
_A='CPP_OT_ensure_tool_settings'
import logging
from.import common
from..import main
from..import reports
import bpy
from bpy.types import Context
__all__=_A,
class CPP_OT_ensure_tool_settings(metaclass=common.SetupContextOperator):
	bl_idname='cpp.ensure_tool_settings';bl_label='Ensure Tool Settings';bl_translation_context=_A;options={'INTERNAL'}
	def execute(self,context:Context):
		E='IMAGE';D='VIEW_3D';C='builtin_brush.Clone';B=False;A='TEXTURE_PAINT';cls=self.__class__;msgctxt=cls.bl_translation_context;ob=main.Workflow.object
		if not main.Workflow.object_poll(ob):
			for ob in context.visible_objects:
				if main.Workflow.object_poll(ob):context.view_layer.objects.active=ob;break
		ob=main.Workflow.object
		if not main.Workflow.object_poll(ob):reports.report_and_log(self,level=logging.WARNING,message='Scene is missing paint object',msgctxt=msgctxt);return{'CANCELLED'}
		scene=context.scene;imapaint=scene.tool_settings.image_paint
		if ob.mode!=A:bpy.ops.object.mode_set(mode=A)
		tool=context.workspace.tools.from_space_view3d_mode(context.mode,create=B)
		if tool.idname!=C:bpy.ops.wm.tool_set_by_id(name=C,cycle=B,space_type=D)
		if imapaint.mode!=E:imapaint.mode=E
		if not imapaint.use_clone_layer:imapaint.use_clone_layer=True
		for area in context.screen.areas:
			if area.type==D:area.spaces.active.shading.light='FLAT'
		return{'FINISHED'}