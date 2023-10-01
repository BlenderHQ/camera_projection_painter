from __future__ import annotations
_A='CPP_OT_setup_context'
import logging
from.import common
from..import constants
from..import main
from..import reports
from..lib import bhqab
import bpy
from bpy.types import Context,Event,Operator,UILayout
from bpy.props import EnumProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props import WindowManager;from..props.wm import WMProps
__all__=_A,
def _do_data_cleanup(context:Context)->bool:return True
def _do_import_scene(context:Context)->bool:return not main.Workflow.object_poll(main.Workflow.object)
def _do_ensure_canvas(context:Context)->bool:return True
def _do_import_cameras(context:Context)->bool:return not main.Workflow.camera
def _do_bind_images(context:Context)->bool:return not main.Workflow.image
def _do_ensure_tool_settings(context:Context)->bool:return True
_STAGE_CALLBACKS={constants.SetupStage.PRE_CLEANUP:(_do_data_cleanup,bpy.ops.cpp.data_cleanup,{}),constants.SetupStage.IMPORT_SCENE:(_do_import_scene,bpy.ops.cpp.import_scene,{}),constants.SetupStage.CHECK_CANVAS:(_do_ensure_canvas,bpy.ops.cpp.ensure_canvas,{}),constants.SetupStage.CHECK_CAMERAS:(_do_import_cameras,bpy.ops.cpp.import_cameras,{}),constants.SetupStage.CHECK_IMAGES:(_do_bind_images,bpy.ops.cpp.bind_images,dict(mode='ALL')),constants.SetupStage.CHECK_TOOL:(_do_ensure_tool_settings,bpy.ops.cpp.ensure_tool_settings,{})}
PROGRESS_IDENTIFIER='setup_context'
class CPP_OT_setup_context(Operator):
	bl_idname='cpp.setup_context';bl_label='Setup Context';bl_options={'REGISTER'};bl_translation_context=_A;status:EnumProperty(items=((common.StageStatus.FINISHED.name,'Finished','',0,common.StageStatus.FINISHED.value),(common.StageStatus.CANCELLED.name,'Cancelled','',0,common.StageStatus.CANCELLED.value),(common.StageStatus.ABORTED.name,'Aborted','',0,common.StageStatus.ABORTED.value)),options={'HIDDEN','SKIP_SAVE'})
	def invoke(self,context:Context,event:Event):wm=context.window_manager;wm_props:WMProps=wm.cpp;wm_props.setup_context_stage=constants.SetupStage.INVOKED.name;progress=bhqab.utils_ui.progress.get(identifier=PROGRESS_IDENTIFIER);progress.num_steps=constants.SetupStage.FINISHED-constants.SetupStage.INVOKED;return self.execute(context)
	@reports.log_execution_helper
	def execute(self,context:Context):
		A='FINISHED';cls=self.__class__;msgctxt=cls.bl_translation_context;wm:WindowManager=context.window_manager;wm_props:WMProps=wm.cpp;status=common.StageStatus[self.status];stage=constants.SetupStage[wm_props.setup_context_stage]
		if status==common.StageStatus.ABORTED:bhqab.utils_ui.progress.complete(identifier=PROGRESS_IDENTIFIER);reports.report_and_log(self,level=logging.INFO,message='Context setup aborted',msgctxt=msgctxt);return{'CANCELLED'}
		else:
			next_stage=constants.SetupStage(stage+1)
			while next_stage!=constants.SetupStage.FINISHED:
				do_stage_cb,operator_cb,keywords=_STAGE_CALLBACKS[next_stage]
				if do_stage_cb(context):wm_props.setup_context_stage=next_stage.name;enum_keywords=dict(data=wm_props,property='setup_context_stage',identifier=wm_props.setup_context_stage);progress=bhqab.utils_ui.progress.get(identifier=PROGRESS_IDENTIFIER);progress.label=UILayout.enum_item_name(**enum_keywords);progress.icon_value=UILayout.enum_item_icon(**enum_keywords);progress.step=int(next_stage-constants.SetupStage.INVOKED)-1;operator_cb('INVOKE_DEFAULT',**keywords);return{A}
				next_stage=constants.SetupStage(next_stage+1)
		bhqab.utils_ui.progress.complete(identifier=PROGRESS_IDENTIFIER);wm_props.setup_context_stage=constants.SetupStage.PASS_THROUGH.name;reports.report_and_log(self,level=logging.INFO,message='Context setup completed',msgctxt=msgctxt);return{A}