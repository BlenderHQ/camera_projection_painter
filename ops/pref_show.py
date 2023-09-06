from __future__ import annotations
_B='UPDATES'
_A='CPP_OT_pref_show'
from..import ADDON_PKG
from..import get_addon_pref
from..import reports
import bpy
from bpy.types import Context,Operator
from bpy.props import EnumProperty
__all__=_A,
class CPP_OT_pref_show(Operator):
	bl_idname='cpp.pref_show';bl_label='Show Preferences';bl_description='Camera Projection Painter user preferences';bl_translation_context=_A;bl_options={'INTERNAL'};shortcut:EnumProperty(items=(('NONE','',''),(_B,'','')),default='NONE',options={'HIDDEN','SKIP_SAVE'})
	@reports.log_execution_helper
	def execute(self,context:Context):
		addon_pref=get_addon_pref(context)
		match self.shortcut:
			case'UPDATES':addon_pref.tab='INFO';addon_pref.info_section={_B}
		return bpy.ops.preferences.addon_show('EXEC_DEFAULT',module=ADDON_PKG)