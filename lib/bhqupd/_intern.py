from __future__ import annotations
_G='INVOKE_DEFAULT'
_F='FINISHED'
_E='PREFERENCES'
_D='INTERNAL'
_C=False
_B=True
_A=None
import logging,os,random,string,subprocess,sys,textwrap
from importlib import reload
if'bpy'in locals():reload(updater)
else:import bpy;from.import updater
from bpy.types import Area,Context,Operator,ScriptDirectory,Timer,UILayout,Window
import addon_utils
from bpy.app.translations import pgettext
from typing import TYPE_CHECKING
from typing import Callable
if TYPE_CHECKING:from types import ModuleType
MSGCTXT='BHQUPD'
RELEASE_NOTES_MSGCTXT='BHQUPD_RELEASE_NOTES'
def _draw_wrapped_text(context:Context,layout:UILayout,*,text:str,text_ctxt:_A|str=_A)->_A:
	text=pgettext(text,text_ctxt);col=layout.column(align=_B)
	for line in text.splitlines():
		for sub_line in textwrap.wrap(line,width=80):col.label(text=sub_line)
def has_updates()->bool:
	if AddonInfo.valid:info=updater.UpdateInfo.get(module_name=AddonInfo.module.__name__);return tuple(info.version)>AddonInfo.version
	return _C
def ui_draw_updates_section(context:Context,layout:UILayout,cb_draw_wrapped_text:Callable[[Context,UILayout,str,_A|str],_A]=_draw_wrapped_text):
	col=layout.column();col.use_property_split=_B
	if not AddonInfo.valid:col.alert=_B;col.label(icon='ERROR');cb_draw_wrapped_text(context,col,text='Unable to evaluate information about current addon',text_ctxt=MSGCTXT);return
	info=updater.UpdateInfo.get(module_name=AddonInfo.module.__name__)
	if BHQUPD_check_addon_updates.proc:row=col.row();row.progress(text='Checking',text_ctxt=MSGCTXT,factor=BHQUPD_check_addon_updates.progress_value,type='RING')
	else:col.operator(operator=BHQUPD_check_addon_updates.bl_idname)
	is_compatible=tuple(info.blender)<=bpy.app.version;text_last_checked=updater.format_timestamp(timestamp=info.checked_at)
	if has_updates():
		text_published_at=updater.format_timestamp(timestamp=info.release_published_at);text_body=pgettext(info.release_description,RELEASE_NOTES_MSGCTXT)
		if is_compatible:col.operator(operator=BHQUPD_install_addon_update.bl_idname);cb_draw_wrapped_text(context,col,text=pgettext('Version {version} released at {published_at}, last checked {last_checked}.\nRelease Notes:\n{body}',MSGCTXT).format(version='.'.join(str(_)for _ in info.version),published_at=text_published_at,last_checked=text_last_checked,body=text_body))
		else:scol=col.column(align=_B);scol.alert=_B;cb_draw_wrapped_text(context,scol,text=pgettext('Latest release requires at least Blender {blender}, last checked {last_checked}.',MSGCTXT).format(blender='.'.join(str(_)for _ in info.blender),last_checked=text_last_checked));cb_draw_wrapped_text(context,col,text=pgettext('Release Notes:\n{body}',MSGCTXT).format(body=text_body))
	elif info.checked_at:cb_draw_wrapped_text(context,col,text=pgettext('You are using latest version, last checked {last_checked}',MSGCTXT).format(last_checked=text_last_checked))
	else:cb_draw_wrapped_text(context,col,text='There is no information about available updates',text_ctxt=MSGCTXT)
	if context.preferences.view.show_developer_ui:
		box=col.box();box.label(text='Developer Extras:',icon='INFO',text_ctxt=MSGCTXT);scol=box.column(align=_B)
		if info.remaining<10:col.alert=_B
		cb_draw_wrapped_text(context,scol,text=pgettext('Rate limit: {rate_limit}\nRemaining: {remaining}\nReset at: {reset_at}\n',MSGCTXT).format(rate_limit=info.rate_limit,remaining=info.remaining,reset_at=updater.format_timestamp(timestamp=info.reset_at)if info.reset_at else'-'))
class AddonInfo:
	__slots__=();valid:bool=_C;module:_A|ModuleType=_A;directory:_A|str=_A;version:_A|tuple[str|int]=_A;repo_url:_A|str=_A
	@classmethod
	def evaluate(cls):
		cls.valid=_C;cls.module=_A;cls.directory=_A;cls.version=_A;cls.repo_url=_A;module=sys.modules.get(__package__.split('.')[0],_A)
		if module is _A:return
		filepath=module.__file__
		if filepath and os.path.isfile(filepath):filepath=os.path.dirname(filepath)
		else:filepath=_A
		version=module.bl_info.get('version',_A);repo_url=module.bl_info.get('doc_url',_A)
		if all(_ is not _A for _ in(filepath,version,repo_url)):cls.module=module;cls.directory=filepath;cls.version=version;cls.repo_url=repo_url;cls.valid=_B
	@classmethod
	def eval_arguments(cls)->updater.CheckAddonUpdatesArguments:args=updater.CheckAddonUpdatesArguments();args.directory=cls.directory;args.repo_url=cls.repo_url;return args
AddonInfo.evaluate()
def _update_eval_translations():
	if bpy.app.background or not AddonInfo.valid:return{}
	try:bpy.app.translations.unregister(__package__)
	except RuntimeError:pass
	from.import langs;translations_dict=langs.LANGS;info=updater.UpdateInfo.get(module_name=AddonInfo.module.__name__);desc=info.release_description;translations=info.release_description_translations
	for(language,block)in translations.items():
		if language not in translations_dict:translations_dict[language]=dict()
		translations_dict[language][RELEASE_NOTES_MSGCTXT,desc]=block
	bpy.app.translations.register(module_name=__package__,translations_dict=translations_dict)
def _unregister_translations():
	if not bpy.app.background:bpy.app.translations.unregister(__package__)
class BHQUPD_check_addon_updates(Operator):
	bl_idname='bhqupd.check_addon_updates';bl_label='Check Now';bl_description='Check for addon updates from remote repository';bl_translation_context='BHQUPD_check_addon_updates';bl_options={_D};proc:_A|subprocess.Popen=_A;timers:list[Timer]=list();finish_cb=_A;progress_value:float=.0;area_type:str=_E
	@classmethod
	def poll(cls,context):return AddonInfo.valid and cls.proc is _A
	@classmethod
	def _update_preferences_areas(cls,context:Context):
		if bpy.app.background:return
		for window in context.window_manager.windows:
			window:Window
			for area in window.screen.areas:
				area:Area
				if area.type==cls.area_type:area.tag_redraw()
	def cancel(self,context):
		cls=self.__class__;cls.area_type=_E
		if cls.finish_cb:cls.finish_cb()
		running_proc=cls.proc;cls.proc=_A
		if running_proc:running_proc.kill()
		if cls.timers:
			wm=context.window_manager
			for timer in cls.timers:wm.event_timer_remove(timer)
			cls.timers.clear()
		cls.progress_value=.0;cls._update_preferences_areas(context)
	def invoke(self,context,event):
		cls=self.__class__;updater.setup_logger(module_name=AddonInfo.module.__name__);cls.proc=subprocess.Popen([sys.executable,updater.__file__,*AddonInfo.eval_arguments().as_arguments()],shell=_B,stdin=_A,stdout=subprocess.PIPE,universal_newlines=_B)
		if context.area:cls.area_type=context.area.type
		wm=context.window_manager
		for window in wm.windows:cls.timers.append(wm.event_timer_add(1./6e1,window=window))
		wm.modal_handler_add(self);return{'RUNNING_MODAL'}
	def modal(self,context,event):
		cls=self.__class__;log=logging.getLogger(AddonInfo.module.__name__)
		if cls.proc is _A:self.cancel(context);return{'CANCELLED'}
		if cls.proc.poll()is _A:cls.progress_value=.0 if cls.progress_value>=1. else cls.progress_value+1./3e1;cls._update_preferences_areas(context);return{'PASS_THROUGH'}
		out=cls.proc.stdout
		if out and out.readable():lines=out.readlines();log.info(''.join(lines))
		updater.UpdateInfo.reset();_update_eval_translations();cls._update_preferences_areas(context);self.cancel(context);return{_F}
class BHQUPD_install_addon_update(Operator):
	bl_idname='bhqupd.install_addon_update';bl_label='Install Update';bl_description='Install updated addon version. Current version would be kept';bl_translation_context='BHQUPD_install_addon_update';bl_options={_D}
	@classmethod
	def poll(cls,context):info=updater.UpdateInfo.get(module_name=AddonInfo.module.__name__);return AddonInfo.valid and os.path.exists(info.retrieved_filepath)
	def execute(self,context):
		A='EXEC_DEFAULT';info=updater.UpdateInfo.get(module_name=AddonInfo.module.__name__);target='DEFAULT';pref_filepaths=bpy.context.preferences.filepaths
		for item in pref_filepaths.script_directories:
			item:ScriptDirectory
			if os.path.samefile(os.path.dirname(os.path.dirname(AddonInfo.directory)),item.directory):target=item.name
		addons_old={mod.__name__ for mod in addon_utils.modules()};bpy.ops.preferences.addon_install(A,overwrite=_C,target=target,filepath=info.retrieved_filepath);addons_new={mod.__name__ for mod in addon_utils.modules()}-addons_old
		for module_name in addons_new:bpy.ops.preferences.addon_enable(A,module=module_name)
		self.report(type={'INFO'},message=pgettext('Installed version {version}',MSGCTXT).format(version=info.version));bpy.ops.preferences.addon_disable(A,module=AddonInfo.module.__name__);return{_F}
_operators=BHQUPD_check_addon_updates,BHQUPD_install_addon_update
def register_addon_update_operators():
	def update_eval_unique_operator_idname(*,cls:Operator)->Operator:
		category_name,id_name=cls.bl_idname.split('.');category=getattr(bpy.ops,category_name,_A)
		if category is _A:return cls
		id_name_eval=id_name
		while id_name_eval in dir(category):id_name_eval=f"{str().join(random.sample(string.ascii_lowercase,k=5))}_{id_name}"
		cls.bl_idname=f"{category_name}.{id_name_eval}";return cls
	for cls in _operators:cls=update_eval_unique_operator_idname(cls=cls);bpy.utils.register_class(cls)
	_update_eval_translations()
def unregister_addon_update_operators():
	for cls in _operators:bpy.utils.unregister_class(cls)
	_unregister_translations()
def check_addon_updates(*,finish_cb=_A):BHQUPD_check_addon_updates.finish_cb=finish_cb;operator_callback=eval(f"bpy.ops.{BHQUPD_check_addon_updates.bl_idname}");operator_callback(_G)
def install_addon_update():operator_callback=eval(f"bpy.ops.{BHQUPD_install_addon_update.bl_idname}");operator_callback(_G)