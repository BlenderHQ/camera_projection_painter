from __future__ import annotations
_A=None
import os,pprint,textwrap,time
from typing import Any
import logging,bpy
from bpy.types import Context,Operator,bpy_prop_array
from bpy.app.translations import pgettext
from bpy.app.handlers import persistent
from.import log,get_addon_pref
from typing import TYPE_CHECKING
if TYPE_CHECKING:from.props.scene import SceneProps
__all__='report_and_log','log_execution_helper'
_str_hidden='(hidden for security reasons)'
def _filter_paths_from_keywords(*,keywords:dict[str,Any])->dict[str,Any]:
	C='filename';B='directory';A='filepath';arg_filepath=keywords.get(A,_A);arg_directory=keywords.get(B,_A);arg_filename=keywords.get(C,_A)
	if arg_filepath is not _A and arg_filepath:
		if os.path.exists(bpy.path.abspath(arg_filepath)):filepath_fmt=f"Existing File Path {_str_hidden}"
		else:filepath_fmt=f"Missing File Path {_str_hidden}"
		keywords[A]=filepath_fmt
	if arg_directory is not _A and arg_directory:
		if os.path.isdir(bpy.path.abspath(arg_directory)):directory_fmt=f"Existing Directory Path {_str_hidden}"
		else:directory_fmt=f"Missing Directory Path {_str_hidden}"
		keywords[B]=directory_fmt
	if arg_filename is not _A and arg_filename:keywords[C]=f"Some Filename {_str_hidden}"
	return keywords
def report_and_log(operator:Operator,*,level:int,message:str,msgctxt:str,**msg_kwargs:_A|dict[str,Any]):
	log.log(level=level,msg=message.format(**msg_kwargs));report_message=pgettext(msgid=message,msgctxt=msgctxt).format(**msg_kwargs)
	match level:
		case logging.DEBUG|logging.INFO:operator.report(type={'INFO'},message=report_message)
		case logging.WARNING:operator.report(type={'WARNING'},message=report_message)
		case logging.ERROR|logging.CRITICAL:operator.report(type={'ERROR'},message=report_message)
def log_execution_helper(ot_execute_method):
	def execute(operator:Operator,context:Context):
		cls=operator.__class__;props=operator.as_keywords()
		if props:props_fmt=textwrap.indent(pprint.pformat(_filter_paths_from_keywords(keywords=props),indent=4,compact=False),prefix=' '*40);log.debug('"{label}" execution begin with properties:\n{props}'.format(label=cls.bl_label,props=props_fmt)).push_indent()
		else:log.debug('"{label}" execution begin'.format(label=cls.bl_label)).push_indent()
		dt=time.time();ret=ot_execute_method(operator,context);log.pop_indent().debug('"{label}" execution ended as {flag} in {elapsed:.6f} second(s)'.format(label=cls.bl_label,flag=ret,elapsed=time.time()-dt));return ret
	return execute
def _get_value(*,item:object,identifier:str):return getattr(item,identifier,'(readonly)')
def _format_setting_value(*,value:object)->str:
	if isinstance(value,float):value:float;return'%.6f'%value
	elif isinstance(value,str):
		value:str
		if'\n'in value:return value.split('\n')[0][:-1]+' ... (multi-lined string skipped)'
		elif len(value)>50:return value[:51]+' ... (long string skipped)'
	elif isinstance(value,bpy_prop_array):return', '.join(_format_setting_value(value=_)for _ in value)
	return value
def _log_settings(item):
	for prop in item.bl_rna.properties:
		identifier=prop.identifier
		if identifier!='rna_type':
			value=_get_value(item=item,identifier=identifier);value_fmt=_format_setting_value(value=value);log.debug('{identifier}: {value_fmt}'.format(identifier=identifier,value_fmt=value_fmt))
			if type(prop.rna_type)==bpy.types.PointerProperty:log.push_indent();_log_settings(getattr(item,prop.identifier));log.pop_indent()
@persistent
def load_post_log_settings(_=_A):log.debug('Loaded with settings:').push_indent();context=bpy.context;log.debug('Preferences:').push_indent();addon_pref=get_addon_pref(context);_log_settings(addon_pref);log.pop_indent();log.debug('Scene:').push_indent();scene_props:SceneProps=context.scene.cpp;_log_settings(scene_props);log.pop_indent();log.pop_indent()
def update_log_setting_changed(identifier):
	def _log_setting_changed(self,_context:Context):value=_get_value(item=self,identifier=identifier);value_fmt=_format_setting_value(value=value);log.debug(f"Setting updated '{self.bl_rna.name}.{identifier}': {value_fmt}")
	return _log_setting_changed