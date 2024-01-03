from __future__ import annotations
_F='UNSIGNED'
_E='utf-8'
_D=False
_C='HIDDEN'
_B=None
_A=True
import os
from typing import Generator,Iterable
import importlib,random,string,bpy
from bpy.types import Context,ID,ImagePreview,Menu,PropertyGroup,STATUSBAR_HT_header,UILayout,WindowManager
from bpy.props import BoolProperty,CollectionProperty,FloatProperty,IntProperty,StringProperty
from mathutils import Vector
import blf
from bl_ui import space_statusbar
from bpy.app.translations import pgettext
import bpy.utils.previews
__all__='get_addon_package_name','eval_unique_name','eval_text_pixel_dimensions','draw_wrapped_text','developer_extras_poll','template_developer_extras_warning','progress','copy_default_presets_from','template_preset','template_disclosure_enum_flag','update_localization','request_localization_from_file','IconsCache'
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
		valid:BoolProperty(default=_A,update=_common_value_update);num_steps:IntProperty(min=1,default=1,subtype=_F,options={_C},update=_common_value_update);step:IntProperty(min=0,default=0,subtype=_F,options={_C},update=_common_value_update)
		def _get_progress(self):return self.step/self.num_steps*100
		def _set_progress(self,_value):0
		value:FloatProperty(min=.0,max=1e2,precision=1,get=_get_progress,subtype='PERCENTAGE',options={_C});icon:StringProperty(default='NONE',maxlen=64,options={_C},update=_common_value_update);icon_value:IntProperty(min=0,default=0,subtype=_F,options={_C},update=_common_value_update);label:StringProperty(default='Progress',options={_C},update=_common_value_update);cancellable:BoolProperty(default=_D,options={_C},update=_common_value_update)
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
			with open(src_fp,'r',encoding=_E)as src_file,open(tar_fp,'w',encoding=_E)as tar_file:tar_file.write(src_file.read())
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
	with open(src,'r',encoding=_E)as src_file:
		src_data=src_file.read()
		for(dst_locale,dst_filename)in dst.items():
			with open(dst_filename,'r',encoding=_E)as dst_file:
				if dst_locale not in langs:langs[dst_locale]=dict()
				langs[dst_locale][msgctxt,src_data]=dst_file.read()
	update_localization(module=module,langs=langs);return src_data
def safe_register(cls):
	try:bpy.utils.unregister_class(cls)
	except RuntimeError:pass
	bpy.utils.register_class(cls)
class IconsCache:
	_directory:str='';_cache:dict[str,int]=dict();_pcoll_cache:_B|bpy.utils.previews.ImagePreviewCollection=_B
	@classmethod
	def _intern_initialize_from_data_files(cls,*,directory:str,ids:Iterable[str]):
		for identifier in ids:
			try:icon_value=bpy.app.icons.new_triangles_from_file(os.path.join(directory,f"{identifier}.dat"))
			except ValueError:icon_value=0
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