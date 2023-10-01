from __future__ import annotations
_A='CPP_OT_bind_history_remove'
from..import main
from..import reports
from bpy.types import Context,Operator
from bpy.props import IntProperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:from..props.camera import CameraProps
__all__=_A,
class CPP_OT_bind_history_remove(Operator):
	bl_idname='cpp.bind_history_remove';bl_options={'REGISTER'};bl_translation_context=_A;bl_label='Remove Image from Bind History';bl_description='Remove item from image bind history';index:IntProperty(default=0,options={'HIDDEN','SKIP_SAVE'})
	@classmethod
	def poll(cls,_context:Context):
		cam=main.Workflow.cam
		if cam:
			cam_props:CameraProps=cam.cpp
			if cam_props.bind_history:return True
		return False
	@reports.log_execution_helper
	def execute(self,_context:Context):
		cam=main.Workflow.cam;cam_props:CameraProps=cam.cpp;cam_props.bind_history.remove(self.index);len_history=len(cam_props.bind_history)
		if len_history:cam_props.active_bind_index=min(max(self.index-1,0),len_history-1)
		return{'FINISHED'}