from __future__ import annotations
import logging
from..import Reports
from.import common
from bpy.types import Operator
class CPP_OT_calc_scene_cage(Operator):
	bl_idname='cpp.calc_scene_cage';bl_label='Update Cage';bl_description='Updates the region for work, taking into account the size of the paint object and the position of all scene cameras';bl_options={'REGISTER','UNDO'};bl_translation_context='CPP_OT_calc_scene_cage'
	@Reports.log_execution_helper
	def execute(self,context):cls=self.__class__;msgctxt=cls.bl_translation_context;common.update_scene_editing_cage(context);context.area.tag_redraw();Reports.report_and_log(self,level=logging.INFO,message='Scene editing cage updated',msgctxt=msgctxt);return{'FINISHED'}