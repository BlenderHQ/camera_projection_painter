from __future__ import annotations
_B='BHQAB_Preferences'
_A=None
from datetime import datetime
import inspect,logging,logging.handlers,os,pprint,re,textwrap,time,bpy
from bpy.types import bpy_prop_array,Context,Operator,UILayout
from bpy.props import EnumProperty
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import Any;from types import FunctionType;from bpy.types import bpy_struct
__all__='CONSOLE_ESC_SEQ','AddonLogger'
class CONSOLE_ESC_SEQ:RESET='\x1b[0m';BLUE='\x1b[1;34m';CYAN='\x1b[1;36m';PURPLE='\x1b[1;35m';GRAY='\x1b[38;20m';YELLOW='\x1b[33;20m';RED='\x1b[31;20m';BOLD_RED='\x1b[31;1m';GREEN='\x1b[1;32m'
class AddonLogger:
	log:_A|__IndentLogger=_A;directory:str='';filename:str=''
	class __IndentLogger(logging.Logger):
		def __init__(self,name):super().__init__(name);self.indent=0
		def push_indent(self):self.indent+=1;return self
		def pop_indent(self):self.indent=max(0,self.indent-1);return self
		def _indented(self,level,msg):indent=' '*self.indent*4;indented_message='{caller:25}'.format(caller=inspect.stack()[2].function)+'|'+indent+' '+msg;super().log(level,indented_message);return self
		def debug(self,msg):return self._indented(logging.DEBUG,msg)
		def info(self,msg):return self._indented(logging.INFO,msg)
		def warning(self,msg):return self._indented(logging.WARNING,msg)
		def error(self,msg):return self._indented(logging.ERROR,msg)
		def critical(self,msg):return self._indented(logging.CRITICAL,msg)
		def log(self,level,msg):self._indented(level,msg);return self
	class __ColoredFormatter(logging.Formatter):
		msg='%(message)s';format='%(name)s (%(levelname)s): ';FORMATS={logging.DEBUG:CONSOLE_ESC_SEQ.BLUE+format+CONSOLE_ESC_SEQ.RESET+msg,logging.INFO:CONSOLE_ESC_SEQ.CYAN+format+CONSOLE_ESC_SEQ.RESET+msg,logging.WARNING:CONSOLE_ESC_SEQ.YELLOW+format+CONSOLE_ESC_SEQ.RESET+msg,logging.ERROR:CONSOLE_ESC_SEQ.RED+format+CONSOLE_ESC_SEQ.RESET+msg,logging.CRITICAL:CONSOLE_ESC_SEQ.BOLD_RED+format+CONSOLE_ESC_SEQ.RESET+msg}
		def format(self,record):log_fmt=self.FORMATS.get(record.levelno);formatter=logging.Formatter(log_fmt);return formatter.format(record)
	@classmethod
	def initialize(cls,*,logger_name:str,directory:str,max_num_logs:int=-1):
		cls.directory=directory;cls.filename=datetime.now().strftime('log %d-%m-%Y %H-%M-%S.%f.txt');log_filepath=os.path.join(directory,cls.filename);cls.log=cls.__IndentLogger(logger_name);cls.log.setLevel(logging.DEBUG)
		if not cls.log.handlers:__fh=logging.FileHandler(filename=log_filepath,mode='w',encoding='utf-8');__fh.setLevel(logging.DEBUG);__ch=logging.StreamHandler();__ch.setLevel(logging.WARNING);__fh.setFormatter(logging.Formatter('%(levelname)10s: %(message)s'));__ch.setFormatter(cls.__ColoredFormatter());cls.log.addHandler(__fh);cls.log.addHandler(__ch)
		if max_num_logs>0:
			pattern=re.compile('log (\\d{2}-\\d{2}-\\d{4} \\d{2}-\\d{2}-\\d{2}\\.\\d{6})\\.txt')
			def extract_datetime(filename):
				match=re.search(pattern,filename)
				if match:datetime_str=match.group(1);return datetime.strptime(datetime_str,'%d-%m-%Y %H-%M-%S.%f')
				return datetime.min
			sorted_files=sorted(os.listdir(cls.directory),key=extract_datetime,reverse=True);log_ext=os.path.splitext(log_filepath)[1];_logs_to_remove=set();i=0
			for filename in sorted_files:
				if os.path.splitext(filename)[1]==log_ext:
					if i>max_num_logs:_logs_to_remove.add(filename)
					else:i+=1
			for filename in _logs_to_remove:
				try:os.remove(os.path.join(cls.directory,filename))
				except OSError:break
	@classmethod
	def shutdown(cls):
		for handler in cls.log.handlers:handler.close()
		cls.log.handlers.clear();cls.log=_A;cls.directory='';cls.filename=''
	@staticmethod
	def _filter_paths_from_keywords(*,keywords:dict[str,Any])->dict[str,Any]:
		C='filename';B='directory';A='filepath';_str_hidden='(hidden for security reasons)';arg_filepath=keywords.get(A,_A);arg_directory=keywords.get(B,_A);arg_filename=keywords.get(C,_A)
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
	@classmethod
	def report_and_log(cls,operator:Operator,*,level:int,message:str,msgctxt:str,**msg_kwargs:_A|dict[str,Any]):
		cls.log.log(level=level,msg=message.format(**msg_kwargs));report_message=pgettext(msgid=message,msgctxt=msgctxt).format(**msg_kwargs)
		match level:
			case logging.DEBUG|logging.INFO:operator.report(type={'INFO'},message=report_message)
			case logging.WARNING:operator.report(type={'WARNING'},message=report_message)
			case logging.ERROR|logging.CRITICAL:operator.report(type={'ERROR'},message=report_message)
	@classmethod
	def log_execution_helper(cls,ot_execute_method:FunctionType[Operator,Context])->FunctionType[Operator,Context]:
		def execute(operator:Operator,context:Context):
			props=operator.as_keywords()
			if props:props_fmt=textwrap.indent(pprint.pformat(AddonLogger._filter_paths_from_keywords(keywords=props),indent=4,compact=False),prefix=' '*40);cls.log.debug('"{label}" execution begin with properties:\n{props}'.format(label=operator.bl_label,props=props_fmt)).push_indent()
			else:cls.log.debug('"{label}" execution begin'.format(label=operator.bl_label)).push_indent()
			dt=time.time();ret=ot_execute_method(operator,context);cls.log.pop_indent().debug('"{label}" execution ended as {flag} in {elapsed:.6f} second(s)'.format(label=operator.bl_label,flag=ret,elapsed=time.time()-dt));return ret
		return execute
	@staticmethod
	def _get_value(*,item:object,identifier:str):return getattr(item,identifier,'(readonly)')
	@staticmethod
	def _format_setting_value(*,value:object)->str:
		if isinstance(value,float):value:float;return'%.6f'%value
		elif isinstance(value,str):
			value:str
			if'\n'in value:return value.split('\n')[0][:-1]+' ... (multi-lined string skipped)'
			elif len(value)>50:return value[:51]+' ... (long string skipped)'
		elif isinstance(value,bpy_prop_array):return', '.join(AddonLogger._format_setting_value(value=_)for _ in value)
		return value
	@classmethod
	def log_settings(cls,*,item:bpy_struct):
		for prop in item.bl_rna.properties:
			identifier=prop.identifier
			if identifier!='rna_type':
				value=cls._get_value(item=item,identifier=identifier);value_fmt=cls._format_setting_value(value=value);cls.log.debug('{identifier}: {value_fmt}'.format(identifier=identifier,value_fmt=value_fmt))
				if type(prop.rna_type)==bpy.types.PointerProperty:cls.log.push_indent();cls.log_settings(item=getattr(item,prop.identifier));cls.log.pop_indent()
	@classmethod
	def update_log_setting_changed(cls,identifier:str)->FunctionType[bpy_struct,Context]:
		log=cls.log
		def _log_setting_changed(self,_context:Context):value=AddonLogger._get_value(item=self,identifier=identifier);value_fmt=AddonLogger._format_setting_value(value=value);log.debug(f"Setting updated '{self.bl_rna.name}.{identifier}': {value_fmt}")
		return _log_setting_changed
	@classmethod
	def get_prop_log_level(cls):
		log=cls.log;_update_log_log_level=cls.update_log_setting_changed(identifier='log_level')
		def _update_log_level(self,context:Context):
			for handle in log.handlers:
				if type(handle)==logging.StreamHandler:handle.setLevel(self.log_level)
			_update_log_log_level(self,context)
		return EnumProperty(items=((logging.getLevelName(logging.DEBUG),'Debug','Debug messages (low priority)',0,logging.DEBUG),(logging.getLevelName(logging.INFO),'Info','Informational messages',0,logging.INFO),(logging.getLevelName(logging.WARNING),'Warning','Warning messages (medium priority)',0,logging.WARNING),(logging.getLevelName(logging.ERROR),'Error','Error messages (high priority)',0,logging.ERROR),(logging.getLevelName(logging.CRITICAL),'Critical','Critical error messages',0,logging.CRITICAL)),default=logging.getLevelName(logging.WARNING),update=_update_log_level,options={'SKIP_SAVE'},translation_context=_B,name='Log Level',description='The level of the log that will be output to the console. For log to file, this level value will not change')
	@classmethod
	def template_ui_draw_paths(cls,layout:UILayout):A='wm.path_open';layout.operator(operator=A,text='Open Log Files Directory',text_ctxt=_B).filepath=cls.directory;layout.operator(operator=A,text=pgettext('Open Log: "{filename}"',msgctxt=_B).format(filename=cls.filename)).filepath=os.path.join(cls.directory,cls.filename)