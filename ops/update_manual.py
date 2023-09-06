from __future__ import annotations
_B='INTERNAL'
_A='CPP_OT_update_manual'
import os
from..import props
from..import reports
import bpy
from bpy.types import Context,Operator
__all__=_A,
TAB=' '*4
GENERATED_MESSAGE='# This file is auto-generated, do not edit manually.'
def write_properties_manual_map():
	I='ops';H='\n    ';G='toctrees.inc';F='props';E='-';D='source';C='docs';B='utf-8';A='w';out_dir=os.path.abspath(f"{os.path.dirname(__file__)}/../")
	def _process_prop(prop,write_cb):
		if not prop.is_hidden:
			write_cb(f"{prop.name}\n{'*'*len(prop.name)}\n\n{prop.description}.\n")
			if prop.bl_rna.identifier=='EnumProperty':
				for item in prop.enum_items_static_ui:
					if item.identifier:write_cb(f"\n{item.name}\n {item.description}.\n")
					else:write_cb('\n\n')
			write_cb('\n')
	with open(os.path.join(out_dir,'manual_map.py'),A,encoding=B)as file:
		mm_w=file.write;mm_w(f"""{GENERATED_MESSAGE}

MANUAL_MAP = (
{TAB}# Properties:

""");toctrees=[]
		for(category,cls)in(('Camera',props.camera.CameraProps),('Object',props.ob.ObjectProps),('Scene',props.scene.SceneProps),('RC Metadata XMP',props.camera.RC_MetadataXMP_Params)):
			mm_w(f"{TAB}# {cls.bl_rna.name} ({category})\n");rna=cls.bl_rna;type_word=rna.name.lower();toctrees.append(f"props/{type_word}")
			with open(os.path.join(os.path.abspath(f"{os.path.dirname(__file__)}/../../"),C,D,F,f"{type_word}.rst"),A,encoding=B)as doc_file:
				dw=doc_file.write;dw(f"{category}\n{'#'*len(category)}\n\n")
				for prop in rna.properties:
					if not(prop.is_hidden or prop.identifier=='name'):mm_w(f'{TAB}("bpy.types.{type_word}.{prop.identifier}", "props/{type_word}.html#{prop.name.replace(" ",E).lower()}"),\n');_process_prop(prop,dw)
		with open(os.path.join(os.path.abspath(f"{os.path.dirname(__file__)}/../../"),C,D,F,G),A,encoding=B)as toctree_file:tw=toctree_file.write;tw('.. toctree::\n    :maxdepth: 4\n    :caption: Properties\n\n    '+H.join(toctrees))
		mm_w(f"""
{TAB}# {E*80}

{TAB}# Operators:

""");toctrees=[]
		for idname in dir(bpy.ops.cpp):
			op=getattr(bpy.ops.cpp,idname)
			if _B in op.bl_options:continue
			cls=op.get_rna_type();type_word=cls.name.replace(' ',E).lower();toctrees.append(f"ops/{type_word}");mm_w(f'{TAB}("bpy.ops.cpp.{idname}", "ops/{type_word}.html"),\n')
			with open(os.path.join(os.path.abspath(f"{os.path.dirname(__file__)}/../../"),C,D,I,f"{type_word}.rst"),A,encoding=B)as doc_file:
				dw=doc_file.write;dw(f"""{cls.name}
{"#"*len(cls.name)}

{op._get_doc()}

""")
				for prop in cls.properties:_process_prop(prop,dw)
		mm_w(')\n')
		with open(os.path.join(os.path.abspath(f"{os.path.dirname(__file__)}/../../"),C,D,I,G),A,encoding=B)as toctree_file:tw=toctree_file.write;tw('.. toctree::\n    :maxdepth: 4\n    :caption: Operators\n\n    '+H.join(toctrees))
class CPP_OT_update_manual(Operator):
	bl_idname='cpp.update_manual';bl_label='Update Manual';bl_translation_context=_A;bl_options={_B}
	@reports.log_execution_helper
	def execute(self,context:Context):write_properties_manual_map();return{'FINISHED'}