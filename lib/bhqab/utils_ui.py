from __future__ import annotations
_M='FINISHED'
_L='INTERNAL'
_K='version'
_J='SKIP_SAVE'
_I='EXEC_DEFAULT'
_H='doc_url'
_G='UNSIGNED'
_F='utf-8'
_E='CANCELLED'
_D=False
_C='HIDDEN'
_B=None
_A=True
import os,re,sys,logging
from datetime import datetime
from typing import Generator,Iterable
import importlib,random,string,bpy
from bpy.types import Context,Event,ID,ImagePreview,Menu,Operator,PropertyGroup,STATUSBAR_HT_header,Timer,UILayout,WindowManager
from bpy.props import BoolProperty,CollectionProperty,FloatProperty,IntProperty,StringProperty
from mathutils import Vector
import blf
from bl_ui import space_statusbar
from bpy.app.translations import pgettext
import bpy.utils.previews,addon_utils
from.import updater
__all__='get_addon_package_name','eval_unique_name','eval_text_pixel_dimensions','draw_wrapped_text','developer_extras_poll','template_developer_extras_warning','progress','copy_default_presets_from','template_preset','template_disclosure_enum_flag','update_localization','request_localization_from_file','safe_register','UPDATE_PROPS_ATTR_NAME','PreferencesUpdateProperties','BHQAB_OT_check_addon_updates','BHQAB_OT_install_addon_update','register_addon_update_operators','unregister_addon_update_operators','IconsCache'
_UI_TIME_FMT='%d-%m-%Y %H:%M:%S'
def get_addon_package_name()->str:return __package__.split('.')[0]
def eval_unique_name(*,arr:Iterable,prefix:str='',suffix:str='')->str:
	if arr is bpy.ops:
		ret=prefix+'.'+str().join(random.sample(string.ascii_lowercase,k=10))+suffix
		if isinstance(getattr(getattr(arr,ret,_B),'bl_idname',_B),str):return eval_unique_name(arr=arr,prefix=prefix,suffix=suffix)
		return ret
	else:
		ret=prefix+str().join(random.sample(string.ascii_letters,k=5))+suffix
		if hasattr(arr,ret)or isinstance(arr,Iterable)and ret in arr:return eval_unique_name(arr=arr,prefix=prefix,suffix=suffix)
		return ret
def eval_text_pixel_dimensions(*,fontid:int=0,text:str='')->Vector:
	ret=Vector((.0,.0))
	if not text:return ret
	is_single_char=bool(len(text)==1);SINGLE_CHARACTER_SAMPLES=100
	if is_single_char:text*=SINGLE_CHARACTER_SAMPLES
	ret.x,ret.y=blf.dimensions(fontid,text)
	if is_single_char:ret.x/=SINGLE_CHARACTER_SAMPLES
	return ret
def draw_wrapped_text(context:Context,layout:UILayout,*,text:str,text_ctxt:_B|str=_B)->_B:
	A=' ';col=layout.column(align=_A)
	if context.region.type=='WINDOW':win_padding=30
	elif context.region.type=='UI':win_padding=52
	else:win_padding=52
	wrap_width=context.region.width-win_padding;space_width=eval_text_pixel_dimensions(text=A).x;text=pgettext(text,text_ctxt)
	for line in text.split('\n'):
		num_characters=len(line)
		if not num_characters:col.separator();continue
		line_words=list((_,eval_text_pixel_dimensions(text=_).x)for _ in line.split(A));num_line_words=len(line_words);line_words_last=num_line_words-1;sublines=[''];subline_width=.0
		for i in range(num_line_words):
			word,word_width=line_words[i];sublines[-1]+=word;subline_width+=word_width;next_word_width=.0
			if i<line_words_last:next_word_width=line_words[i+1][1];sublines[-1]+=A;subline_width+=space_width
			if subline_width+next_word_width>wrap_width:
				subline_width=.0
				if i<line_words_last:sublines.append('')
		for subline in sublines:col.label(text=subline)
def developer_extras_poll(context:Context)->bool:return context.preferences.view.show_developer_ui
def template_developer_extras_warning(context:Context,layout:UILayout)->_B:
	if developer_extras_poll(context):col=layout.column(align=_A);scol=col.column(align=_A);scol.alert=_A;scol.label(text='Warning',icon='INFO');text='This section is intended for developers. You see it because you have an active "Developers Extras" option in the Blender user preferences.';draw_wrapped_text(context,scol,text=text,text_ctxt='BHQAB_Preferences');col.prop(context.preferences.view,'show_developer_ui')
def _update_statusbar():bpy.context.workspace.status_text_set(text=_B)
class _progress_meta(type):
	@property
	def PROGRESS_BAR_UI_UNITS(cls):return cls._PROGRESS_BAR_UI_UNITS
	@PROGRESS_BAR_UI_UNITS.setter
	def PROGRESS_BAR_UI_UNITS(cls,value):cls._PROGRESS_BAR_UI_UNITS=max(cls._PROGRESS_BAR_UI_UNITS_MIN,min(value,cls._PROGRESS_BAR_UI_UNITS_MAX))
class progress(metaclass=_progress_meta):
	_PROGRESS_BAR_UI_UNITS=6;_PROGRESS_BAR_UI_UNITS_MIN=4;_PROGRESS_BAR_UI_UNITS_MAX=12;_is_drawn=_D;_attrname=''
	class ProgressPropertyItem(PropertyGroup):
		identifier:StringProperty(maxlen=64,options={_C})
		def _common_value_update(self,_context):_update_statusbar()
		valid:BoolProperty(default=_A,update=_common_value_update);num_steps:IntProperty(min=1,default=1,subtype=_G,options={_C},update=_common_value_update);step:IntProperty(min=0,default=0,subtype=_G,options={_C},update=_common_value_update)
		def _get_progress(self):return self.step/self.num_steps*100
		def _set_progress(self,_value):0
		value:FloatProperty(min=.0,max=1e2,precision=1,get=_get_progress,subtype='PERCENTAGE',options={_C});icon:StringProperty(default='NONE',maxlen=64,options={_C},update=_common_value_update);icon_value:IntProperty(min=0,default=0,subtype=_G,options={_C},update=_common_value_update);label:StringProperty(default='Progress',options={_C},update=_common_value_update);cancellable:BoolProperty(default=_D,options={_C},update=_common_value_update)
	def _func_draw_progress(self,context:Context):
		layout:UILayout=self.layout;layout.use_property_split=_A;layout.use_property_decorate=_D;layout.template_input_status();layout.separator_spacer();layout.template_reports_banner()
		if hasattr(WindowManager,progress._attrname):
			layout.separator_spacer()
			for item in progress.valid_progress_items():
				row=layout.row(align=_A);row.label(text=item.label,icon=item.icon,icon_value=item.icon_value);srow=row.row(align=_A);srow.ui_units_x=progress.PROGRESS_BAR_UI_UNITS;srow.prop(item,'value',text='')
				if item.cancellable:row.prop(item,'valid',text='',icon='X',toggle=_A,invert_checkbox=_A)
		layout.separator_spacer();row=layout.row();row.alignment='RIGHT';row.label(text=context.screen.statusbar_info())
	@classmethod
	def progress_items(cls)->tuple[ProgressPropertyItem]:return tuple(getattr(bpy.context.window_manager,cls._attrname,tuple()))
	@classmethod
	def valid_progress_items(cls)->Generator[ProgressPropertyItem]:return(_ for _ in cls.progress_items()if _.valid)
	@classmethod
	def _get(cls,*,identifier:str)->_B|ProgressPropertyItem:
		for item in cls.progress_items():
			if item.identifier==identifier:return item
	@classmethod
	def get(cls,*,identifier:str='')->ProgressPropertyItem:
		ret=cls._get(identifier=identifier)
		if ret:ret.valid=_A;return ret
		if not cls._is_drawn:bpy.utils.register_class(progress.ProgressPropertyItem);cls._attrname=eval_unique_name(arr=WindowManager,prefix='bhq_',suffix='_progress');setattr(WindowManager,cls._attrname,CollectionProperty(type=progress.ProgressPropertyItem,options={_C}));STATUSBAR_HT_header.draw=cls._func_draw_progress;_update_statusbar()
		cls._is_drawn=_A;ret:progress.ProgressPropertyItem=getattr(bpy.context.window_manager,cls._attrname).add();ret.identifier=identifier;return ret
	@classmethod
	def complete(cls,*,identifier:str):
		item=cls._get(identifier=identifier)
		if item:
			item.valid=_D
			for _ in cls.valid_progress_items():return
			cls.release_all()
	@classmethod
	def release_all(cls):
		if not cls._is_drawn:return
		delattr(WindowManager,cls._attrname);bpy.utils.unregister_class(progress.ProgressPropertyItem);importlib.reload(space_statusbar);STATUSBAR_HT_header.draw=space_statusbar.STATUSBAR_HT_header.draw;_update_statusbar();cls._is_drawn=_D
def copy_default_presets_from(*,src_root:str):
	for(root,_dir,files)in os.walk(src_root):
		for filename in files:
			rel_dir=os.path.relpath(root,src_root);src_fp=os.path.join(root,filename);tar_dir=bpy.utils.user_resource('SCRIPTS',path=os.path.join('presets',rel_dir),create=_A)
			if not tar_dir:print('Failed to create presets path');return
			tar_fp=os.path.join(tar_dir,filename)
			with open(src_fp,'r',encoding=_F)as src_file,open(tar_fp,'w',encoding=_F)as tar_file:tar_file.write(src_file.read())
def template_preset(layout:UILayout,*,menu:Menu,operator:str)->_B:row=layout.row(align=_A);row.use_property_split=_D;row.menu(menu=menu.__name__,text=menu.bl_label);row.operator(operator=operator,text='',icon='ADD');row.operator(operator=operator,text='',icon='REMOVE').remove_active=_A
def template_disclosure_enum_flag(layout:UILayout,*,item:ID,prop_enum_flag:str,flag:str)->bool:
	row=layout.row(align=_A);row.use_property_split=_D;row.emboss='NONE_OR_STATUS';row.alignment='LEFT';icon='DISCLOSURE_TRI_RIGHT';ret=_D
	if flag in getattr(item,prop_enum_flag):icon='DISCLOSURE_TRI_DOWN';ret=_A
	icon_value=UILayout.enum_item_icon(item,prop_enum_flag,flag)
	if icon_value:row.label(icon_value=icon_value)
	row.prop_enum(item,prop_enum_flag,flag,icon=icon);return ret
def update_localization(*,module:str,langs:dict):
	try:bpy.app.translations.unregister(module)
	except RuntimeError:pass
	else:bpy.app.translations.register(module,langs)
def request_localization_from_file(*,module:str,langs:dict,msgctxt:str,src:str,dst:dict[str,str]):
	for(lang,translations)in langs.items():
		if lang in dst:
			for item in translations.keys():
				if item[0]==msgctxt:return item[1]
	src_data=''
	with open(src,'r',encoding=_F)as src_file:
		src_data=src_file.read()
		for(dst_locale,dst_filename)in dst.items():
			with open(dst_filename,'r',encoding=_F)as dst_file:
				if dst_locale not in langs:langs[dst_locale]=dict()
				langs[dst_locale][msgctxt,src_data]=dst_file.read()
	update_localization(module=module,langs=langs);return src_data
def safe_register(cls):
	try:bpy.utils.unregister_class(cls)
	except RuntimeError:pass
	bpy.utils.register_class(cls)
def _intern_update_post_restart_blender(module_name:str):import subprocess;startupinfo=subprocess.STARTUPINFO();startupinfo.dwFlags=subprocess.DETACHED_PROCESS;subprocess.Popen([bpy.app.binary_path,'-con','--python-expr','import bpy; bpy.ops.wm.recover_last_session(); '],startupinfo=startupinfo);bpy.ops.wm.quit_blender()
UPDATE_PROPS_ATTR_NAME='update_props'
class PreferencesUpdateProperties(PropertyGroup):
	auto_check:BoolProperty(default=_A,options={_C,_J},translation_context=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT,name='Check for Updates',description='Automatically check for updates when you open Blender');auth_token:StringProperty(maxlen=256,subtype='PASSWORD',options={_C},translation_context=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT,name='Authorization Token',description='Authorization token to increase the limit of responses during development');has_updates:BoolProperty(options={_C});url:StringProperty(options={_C},maxlen=256)
	@classmethod
	def _get_addon_module_name(cls)->str:return __package__.split('.')[0]
	@classmethod
	def _get_addon_clean_module_name(cls)->str:
		module_name=cls._get_addon_module_name();match=re.match('^(.*?)(?:-.*)?$',module_name)
		if match and match.groups:return match.group(1)
		return module_name
	@classmethod
	def _get_addon_module(cls)->dict:return sys.modules[cls._get_addon_module_name()]
	@classmethod
	def _get_addon_int_version(cls)->int:return updater.eval_int_version(ver=cls._get_addon_module().bl_info.get(_K,(0,0,0)))
	@classmethod
	def _get_addon_update_cache_directory(cls)->str:root=os.path.dirname(os.path.dirname(cls._get_addon_module().__file__));return os.path.join(root,f"{cls._get_addon_clean_module_name()}_update_cache")
	@classmethod
	def _get_addon_latest_release_url(cls)->str:import urllib.parse;doc_url=cls._get_addon_module().bl_info[_H];parsed=urllib.parse.urlparse(doc_url);owner,repo_name=parsed.path[1:].split('/');api_path=f"/repos/{owner}/{repo_name}/releases/latest";api_url=urllib.parse.urlunparse((parsed.scheme,'api.github.com',api_path,'','',''));return api_url
	@classmethod
	def check_poll(cls)->bool:
		if BHQAB_OT_check_addon_updates.proc:return _D
		cache=updater.UpdateCache.get(directory=cls._get_addon_update_cache_directory())
		if cache.checked_at:
			if cache.remaining>0:return _A
			elif datetime.now()>datetime.fromtimestamp(cache.reset_at):return _A
		else:return _A
		return _D
	@staticmethod
	def _format_timestamp(value:int|float):return datetime.fromtimestamp(value).strftime(_UI_TIME_FMT)
	def draw(self,context:Context,layout:UILayout):
		A='wm.path_open';cls=self.__class__;msgctxt=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT;cache_directory=cls._get_addon_update_cache_directory();cache=updater.UpdateCache.get(directory=cache_directory);checked_at_fmt=''
		if cache.checked_at:checked_at_fmt=self._format_timestamp(cache.checked_at)
		if cache.has_updates:prerelease_fmt=pgettext('Pre-release',msgctxt)if cache.tag_is_prerelease else'';text=pgettext('Released version {tag_name} {prerelease_fmt}({published_at}), last checked at {checked_at}\nRelease Notes:\n\n{body}',msgctxt).format(tag_name=cache.tag_name,prerelease_fmt=prerelease_fmt,published_at=self._format_timestamp(cache.tag_published_at),checked_at=checked_at_fmt,body=pgettext(cache.tag_body,msgctxt));draw_wrapped_text(context,layout,text=text);layout.operator(operator=BHQAB_OT_install_addon_update.bl_idname,text=pgettext('Update to {tag_name}',msgctxt).format(tag_name=cache.tag_name))
		elif checked_at_fmt:draw_wrapped_text(context,layout,text=pgettext('You are using the latest version, checked at {checked_at}',msgctxt).format(checked_at=checked_at_fmt))
		else:draw_wrapped_text(context,layout,text='There is no information about available updates',text_ctxt=msgctxt)
		col=layout.column(align=_A);col.use_property_split=_A;col.operator(BHQAB_OT_check_addon_updates.bl_idname);col.prop(self,'auto_check')
		if developer_extras_poll(context):box=layout.box();template_developer_extras_warning(context,box);layout.prop(self,'auth_token');scol=box.column();scol.enabled=os.path.exists(cache_directory);scol.operator(operator=A,text=cache_directory).filepath=cache_directory;cache_filepath=os.path.join(cache_directory,updater.UPDATE_INFO_FILENAME);scol=box.column();scol.enabled=os.path.exists(cache_filepath);scol.operator(operator=A,text=updater.UPDATE_INFO_FILENAME).filepath=cache_filepath;text=pgettext('Cache File: {fp}\nRate Limit: {rate_limit}\nRemaining: {remaining}\nReset Time: {reset_at}',msgctxt).format(fp=cache_directory,rate_limit=cache.rate_limit,remaining=cache.remaining,reset_at=self._format_timestamp(cache.reset_at));draw_wrapped_text(context,box,text=text)
class format_dict(dict):
	def __missing__(self,key):return'...'
class BHQAB_OT_check_addon_updates(Operator):
	bl_idname='bhqab.check_addon_updates';bl_label='Check Now';bl_translation_context=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT;bl_options={_L};proc=_B;timers:Timer;force:BoolProperty(options={_C,_J})
	@classmethod
	def description(cls,_context:Context,_properties:BHQAB_OT_check_addon_updates):
		msgctxt=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT
		if PreferencesUpdateProperties.check_poll():return pgettext('Check for updates now',msgctxt)
		else:
			cache_filepath=PreferencesUpdateProperties._get_addon_update_cache_directory();cache=updater.UpdateCache.get(directory=cache_filepath)
			if not cache.remaining:return pgettext('Unable check for updates before {reset_at}, exceeded rate limit',msgctxt).format(reset_at=PreferencesUpdateProperties._format_timestamp(cache.reset_at))
		return pgettext('Can not check for updates now',msgctxt)
	@classmethod
	def poll(cls,_context:Context):return PreferencesUpdateProperties.check_poll()
	def cancel(self,context:Context):
		cls=self.__class__;proc=cls.proc;cls.proc=_B
		if proc:proc.kill()
		if self.timers:
			wm=context.window_manager
			for timer in self.timers:wm.event_timer_remove(timer)
		self.timers=_B
	def invoke(self,context:Context,event:Event):
		cls=self.__class__;module_name=PreferencesUpdateProperties._get_addon_module_name();addon_pref=context.preferences.addons[module_name].preferences;update_props:PreferencesUpdateProperties=getattr(addon_pref,UPDATE_PROPS_ATTR_NAME);cache=updater.UpdateCache.get(directory=update_props._get_addon_update_cache_directory());self.has_updates=cache.has_updates;update_localization(module=__package__,langs=cache.eval_tag_body_localization())
		if not(self.force or update_props.auto_check):return{_E}
		if not update_props.check_poll():return{_E}
		updater.setup_logger(module_name=module_name);import subprocess;proc=subprocess.Popen([sys.executable,updater.__file__,module_name,update_props._get_addon_update_cache_directory(),update_props._get_addon_latest_release_url(),str(update_props._get_addon_int_version()),update_props.auth_token],shell=_A,stdin=_B,stdout=subprocess.PIPE,universal_newlines=_A);cls.proc=proc;wm=context.window_manager;self.timers=list()
		for window in wm.windows:self.timers.append(wm.event_timer_add(.1,window=window))
		wm.modal_handler_add(self);return{'RUNNING_MODAL'}
	def modal(self,context:Context,event:Event):
		cls=self.__class__;msgctxt=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT;cache_filepath=PreferencesUpdateProperties._get_addon_update_cache_directory();cache=updater.UpdateCache.get(directory=cache_filepath)
		if cls.proc is _B:self.cancel(context);return{_E}
		if cls.proc.poll()is _B:return{'PASS_THROUGH'}
		module_name=PreferencesUpdateProperties._get_addon_module_name();addon_pref=context.preferences.addons[module_name].preferences;update_props:PreferencesUpdateProperties=getattr(addon_pref,UPDATE_PROPS_ATTR_NAME);update_props.has_updates=cache.has_updates;update_localization(module=__package__,langs=cache.eval_tag_body_localization())
		if cls.proc.stdout and cls.proc.stdout.readable():
			lines=cls.proc.stdout.readlines()
			for line in reversed(lines):
				if line:report_type,text=updater.parse_log(module_name=module_name,string=line);self.report(type={report_type},message=pgettext(text,msgctxt).format_map(format_dict(tag_name=cache.tag_name)));break
			print(''.join(lines))
		if context.area:context.area.tag_redraw()
		self.cancel(context);return{_M}
class BHQAB_OT_install_addon_update(Operator):
	bl_idname='bhqab.install_addon_update';bl_label='Install Update';bl_description='Install addon update';bl_translation_context=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT;bl_options={_L}
	@classmethod
	def poll(cls,_context:Context):return PreferencesUpdateProperties.check_poll()
	@staticmethod
	def switch_to_manual_installation():doc_url=PreferencesUpdateProperties._get_addon_module().bl_info[_H];bpy.ops.wm.url_open(_I,url=doc_url)
	def execute(self,context:Context):
		A='WARNING';msgctxt=updater.BHQAB_PREFERENCES_UPDATES_MSGCTXT;doc_url=PreferencesUpdateProperties._get_addon_module().bl_info[_H];module_name=PreferencesUpdateProperties._get_addon_module_name();clean_module_name=PreferencesUpdateProperties._get_addon_clean_module_name();updater.setup_logger(module_name=module_name);log=logging.getLogger(module_name);module_directory=os.path.dirname(PreferencesUpdateProperties._get_addon_module().__file__);root_directory=os.path.dirname(module_directory);cache_directory=PreferencesUpdateProperties._get_addon_update_cache_directory();cache=updater.UpdateCache.get(directory=cache_directory);local_filename=cache.retrieved_filepath;data_root_dirname=updater.get_zipfile_base_dir(module_name=module_name,local_filename=local_filename)
		if data_root_dirname is _B:self.report('Downloaded file can not be used for installation');return{_E}
		backup_directory=os.path.join(cache_directory,'backup');result=updater.create_directory(module_name=module_name,directory=backup_directory,ensure_empty=_A)
		if not result:self.report(type={A},message='Failed to create backup directory');return{_E}
		result=updater.copy_directory(module_name=module_name,src=module_directory,dst=backup_directory)
		if not result:self.report(type={A},message='Failed to make backup');return{_E}
		self.report(type={'INFO'},message='Installing update');addon_utils.disable(module_name,default_set=_D);result=updater.remove_directory(module_name=module_name,directory=module_directory)
		if not result:addon_utils.enable(module_name,persistent=_A);self.report(type={A},message='Unable to remove local installation files, please, check directory permissions');return{_E}
		def _intern_critical():print('\n\nA critical error occurred while installing "{module_name:s}" the update, unable to restore the installation from backup. Use the link {doc_url:s} to visit the repository and download the latest update. If you do not have access to the Internet, "{backup_directory:s}" contains a backup files\n\n'.format(module_name=module_name,doc_url=doc_url,backup_directory=backup_directory));bpy.ops.wm.url_open(_I,url=doc_url);bpy.ops.wm.path_open(_I,filepath=backup_directory);return{_E}
		def _intern_restore_backup():
			result=updater.copy_directory(module_name=module_name,src=backup_directory,dst=module_directory)
			if result:addon_utils.enable(module_name,persistent=_A);self.report(type={A},message='Update failed, installation restored from backup. Please install the update manually');return{_E}
			else:return _intern_critical()
		result=updater.extract_archive_data(module_name=module_name,local_filename=local_filename,dst=module_directory)
		if not result:return _intern_restore_backup()
		log.info(f'Removing backup files from "{backup_directory}"');result=updater.remove_directory(module_name=module_name,directory=backup_directory)
		if result:log.info('Backup files removed')
		else:log.warning('Unable to remove backup files')
		log.info(f'Removing update zip archive from "{local_filename}"');result=updater.remove_file(module_name=module_name,filepath=local_filename)
		if result:log.info('Update zip archive removed')
		else:log.warning('Unable to remove update zip archive')
		cache.has_updates=_D;cache.write(module_name=module_name);log.info('Restarting Blender');_intern_update_post_restart_blender(module_name=clean_module_name);return{_M}
def check_addon_updates(*,force:bool=_D):cb=eval(f"bpy.ops.{BHQAB_OT_check_addon_updates.bl_idname}");cb('INVOKE_DEFAULT',force=force)
_classes=BHQAB_OT_check_addon_updates,BHQAB_OT_install_addon_update
def register_addon_update_operators()->list[Operator]:...
def unregister_addon_update_operators():...
if getattr(bpy.app,_K):
	def register_addon_update_operators()->list[Operator]:
		_registered=[]
		for cls in _classes:prefix,suffix=cls.__qualname__.split('_OT_');cls.bl_idname=eval_unique_name(arr=bpy.ops,prefix=prefix.lower(),suffix=f"_{suffix}");bpy.utils.register_class(cls);_registered.append(cls)
		return _registered
	def unregister_addon_update_operators():
		for cls in reversed(_classes):bpy.utils.unregister_class(cls)
class IconsCache:
	_directory:str='';_cache:dict[str,int]=dict();_pcoll_cache:_B|bpy.utils.previews.ImagePreviewCollection=_B
	@classmethod
	def _intern_initialize_from_data_files(cls,*,directory:str,ids:Iterable[str]):
		for identifier in ids:
			try:icon_value=bpy.app.icons.new_triangles_from_file(os.path.join(directory,f"{identifier}.dat"))
			except ValueError:log.warning(f'Unable to load icon "{identifier}"');icon_value=0
			cls._cache[identifier]=icon_value
	@classmethod
	def _intern_initialize_from_image_files(cls,*,directory:str,ids:Iterable[str]):
		pcoll=bpy.utils.previews.new()
		for identifier in ids:prv:ImagePreview=pcoll.load(identifier,os.path.join(directory,f"{identifier}.png"),'IMAGE');cls._cache[identifier]=prv.icon_id
		cls._pcoll_cache=pcoll
	@classmethod
	def initialize(cls,*,directory:str,data_identifiers:Iterable[str],image_identifiers:Iterable[str]):
		if cls._cache and cls._directory==directory:return
		cls.release()
		if directory:cls._intern_initialize_from_data_files(directory=directory,ids=data_identifiers);cls._intern_initialize_from_image_files(directory=directory,ids=image_identifiers)
		cls._directory=directory
	@classmethod
	def release(cls):
		if cls._pcoll_cache is not _B:bpy.utils.previews.remove(cls._pcoll_cache);cls._pcoll_cache=_B
		cls._cache.clear()
	@classmethod
	def get_id(cls,identifier:str)->int:return cls._cache.get(identifier,0)