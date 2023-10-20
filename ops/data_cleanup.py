from __future__ import annotations
_A='CPP_OT_data_cleanup'
import logging
from..import Reports
from.import common
from..import icons
import bpy
from bpy.types import bpy_prop_collection,Context,Event,Operator
from bpy.props import BoolProperty
__all__=_A,
def is_possibly_default_blenddata()->bool:C='Light';B='Camera';A='Cube';return bool((bpy.data.objects and bpy.data.meshes and bpy.data.cameras and bpy.data.lights and bpy.data.materials)and(len(bpy.data.objects)==3 and len(bpy.data.meshes)==len(bpy.data.cameras)==len(bpy.data.lights)==1)and(A in bpy.data.objects and bpy.data.objects[A].data.name==A and B in bpy.data.objects and bpy.data.objects[B].data.name==B and C in bpy.data.objects and bpy.data.objects[C].data.name==C and'Material'in bpy.data.materials))
def is_possibly_only_default_image_blenddata()->bool:return bool(bpy.data.images and len(bpy.data.images)==1 and bpy.data.images[0].name=='Render Result')
class CPP_OT_data_cleanup(metaclass=common.SetupContextOperator):
	bl_idname='cpp.data_cleanup';bl_label='Data Cleanup';bl_translation_context=_A;options={'REGISTER'};cleanup_data:BoolProperty(translation_context=_A,name='Cleanup Data',description='Delete object, mesh, material, texture, light and camera data-blocks');cleanup_images:BoolProperty(translation_context=_A,name='Cleanup Images',description='Delete all image data-blocks')
	def draw(self:Operator,context:Context):layout=self.layout;layout.use_property_split=False;row=layout.row();col=row.column();col.template_icon(icon_value=icons.get_id('cleanup'),scale=common.CENTERED_DIALOG_ICON_SCALE);col=row.column();col.ui_units_x=common.CENTERED_DIALOG_PROPS_UI_UNITS_X;col.prop(self,'cleanup_data');col.prop(self,'cleanup_images')
	def invoke(self,context:Context,event:Event):self.cleanup_data=is_possibly_default_blenddata();self.cleanup_images=is_possibly_only_default_image_blenddata();common.invoke_props_dialog_centered(context,event,operator=self);return{'RUNNING_MODAL'}
	def execute(self,context:Context):
		msgctxt=self.bl_translation_context
		def _do_cleanup(coll:bpy_prop_collection):
			for _ in coll:coll.remove(_)
		if self.cleanup_data or self.cleanup_images:
			if self.cleanup_data:
				for _ in(bpy.data.objects,bpy.data.meshes,bpy.data.textures,bpy.data.cameras,bpy.data.lights,bpy.data.materials):_do_cleanup(_)
			if self.cleanup_images:_do_cleanup(bpy.data.images)
			Reports.report_and_log(self,level=logging.INFO,message='Data cleanup complete',msgctxt=msgctxt);return{'FINISHED'}
		elif is_possibly_default_blenddata()or is_possibly_only_default_image_blenddata():Reports.report_and_log(self,level=logging.INFO,message='Recommended data cleanup skipped',msgctxt=msgctxt)
		else:Reports.report_and_log(self,level=logging.INFO,message='Data cleanup skipped',msgctxt=msgctxt)
		return{'CANCELLED'}