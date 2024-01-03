from __future__ import annotations
_b='select_framebuffer_scale'
_a='REALITY_CAPTURE'
_Z='tooltip_position'
_Y='FOLLOW'
_X='tooltip_preview_size'
_W='NORMAL'
_V='cameras_transparency'
_U='use_smooth_previews'
_T='dithering_mix_factor'
_S='FACTOR'
_R='use_previews'
_Q='use_mesh_preview'
_P='info_section'
_O='LICENSE'
_N='CREDITS'
_M='UPDATES'
_L='ENUM_FLAG'
_K='keymap'
_J='README'
_I='appearance_section'
_H='VIEWPORT'
_G='HIDDEN'
_F='info'
_E='tab'
_D=None
_C='SKIP_SAVE'
_B=True
_A='Preferences'
import os
from..import ADDON_PKG,DATA_DIR,Reports
from..lib import bhqab
from..lib import bhqupd
from..import icons
from..import langs
from..import main
import bpy
from bpy.types import AddonPreferences,Context,KeyMap,UILayout
from bpy.props import BoolProperty,EnumProperty,FloatProperty,IntProperty
import rna_keymap_ui
__all__=_A,
class Preferences(AddonPreferences):
	bl_idname=ADDON_PKG
	def get_tab(self)->int:
		num_items=3
		if bhqab.utils_ui.developer_extras_poll(bpy.context):num_items+=1
		index=self.get(_E,num_items);return min(index,num_items-1)
	def set_tab(self,value):self[_E]=value
	def get_tab_items(self,context:Context)->tuple:
		_tab_items=('APPEARANCE','Appearance','Appearance settings',icons.get_id('appearance'),0),('KEYMAP','Keymap','Keymap settings',icons.get_id(_K),1),('INFO','Info','Information and links',icons.get_id(_F),2);ret=_tab_items
		if bhqab.utils_ui.developer_extras_poll(context):ret+=('DEV','Developer Extras','Settings used for debugging and development purposes',0,3),
		return ret
	tab:EnumProperty(items=get_tab_items,get=get_tab,set=set_tab,update=Reports.update_log_setting_changed(identifier=_E),default=-1,options={_G,_C},translation_context=_A,name='Tab',description='Active tab for viewing user preferences');appearance_section:EnumProperty(items=((_H,'Viewport','Common viewport settings',icons.get_id('viewport'),1<<0),('AA','Anti-Aliasing','Anti-aliasing settings',icons.get_id('aa'),1<<1)),default={_H},options={_G,_C,_L},update=Reports.update_log_setting_changed(identifier=_I),translation_context=_A,name='Appearance Section',description='Active appearance section');info_section:EnumProperty(items=((_M,'Updates','Information about available updates. Here you can check for a new release, review the release notes, and update the addon',icons.get_id('update'),1<<0),(_J,'Readme','Notes that can help you start using the addon, for example, if there is no internet connection',icons.get_id('readme'),1<<1),(_N,'Credits','Thanks to those involved in creating the addon',icons.get_id('credits'),1<<2),('LINKS','Links','Useful links to online resources that can help you use the addon',icons.get_id('links'),1<<3),(_O,'License','Addon license information',icons.get_id('license'),1<<4)),default={_J},options={_G,_C,_L},update=Reports.update_log_setting_changed(identifier=_P),translation_context=_A,name='Info Section',description='Active information section');aa_method:bhqab.utils_gpu.DrawFramework.get_prop_aa_method();fxaa_preset:bhqab.utils_gpu.FXAA.get_prop_preset();fxaa_value:bhqab.utils_gpu.FXAA.get_prop_value();smaa_preset:bhqab.utils_gpu.SMAA.get_prop_preset();use_mesh_preview:BoolProperty(default=_B,options={_C},update=Reports.update_log_setting_changed(identifier=_Q),translation_context=_A,name='Use Mesh Preview',description="Use mesh preview for brush and inspection. This option can be useful to significantly reduce the use of video memory, for example, if the purpose of using the addon is only to import and export cameras. The current implementation of Blender forces the display to save the object's data and re-render it, just to show the brush preview. Of course, this is convenient, but it significantly increases the load on the system. Therefore, if it is not critical for you to see a preview of the brush you are drawing with, you can disable the preview");use_previews:BoolProperty(default=_B,options={_C},update=Reports.update_log_setting_changed(identifier=_R),translation_context=_A,name='Use Previews',description="Use image previews. Whether to generate and display image previews in the viewport. This does not significantly increase the amount of video memory, but it can cause small friezes in the viewport. The generation system works according to the principle of displaying the necessary previews. That is, all camera frames in the observer's field of view will be added to the render queue. Of course, the faster you read data from the disk, the faster it will be generated. The camera on which the cursor is hovered on is always added to render queue first");dithering_mix_factor:FloatProperty(default=.3,min=.0,max=1.,soft_min=.1,subtype=_S,options={_C},update=Reports.update_log_setting_changed(identifier=_T),translation_context=_A,name='Dithering Strength',description='8x8 Bayer dithering strength. The resolution of the previews is rather small - 128x128 pixels. Of course, this add-on performs smoothing of the generated previews, but for a clearer understanding of what is shown, you can use dithering and mix it with the original preview');use_smooth_previews:BoolProperty(default=_B,options={_C},update=Reports.update_log_setting_changed(identifier=_U),translation_context=_A,name='Smooth Previews',description='Use fast approximated anti-aliasing for preview images. Blender generates previews as Nearest, so readability is lost. This option does not add more data from the original image but performs smoothing and thus makes it more readable');cameras_transparency:FloatProperty(min=.0,soft_min=.1,max=1.,default=1.,subtype=_S,options={_C},update=Reports.update_log_setting_changed(identifier=_V),translation_context=_A,name='Cameras Transparency',description='Transparency of cameras in the viewport.');tooltip_preview_size:EnumProperty(items=((_W,'Normal','Standard size, 128x128 pixels',icons.get_id('prv_size_normal'),0),('LARGE','Large','Stretched to double size',icons.get_id('prv_size_large'),1)),default=_W,options={_C},update=Reports.update_log_setting_changed(identifier=_X),translation_context=_A,name='Tooltip Preview Size',description='The size of the preview image in the tooltip. Does not affect the quality of the displayed preview, only its size');tooltip_position:EnumProperty(items=(('REMAIN','Static','Appears near the brush and remains in the place where it appeared',icons.get_id('tooltip_static'),0),(_Y,'Floating','Appears and follows the brush',icons.get_id('tooltip_floating'),1),('FIXED','Fixed','Appears only at the bottom of the screen, in the middle',icons.get_id('tooltip_fixed'),2)),default=_Y,update=Reports.update_log_setting_changed(identifier=_Z),translation_context=_A,name='Tooltip Position',description='The location of the pop-up tooltip with information about the camera data on which the cursor is hovered');preferred_software_workflow:EnumProperty(items=((_a,'Reality Capture','Use presets for Reality Capture'),),default=_a,update=Reports.update_log_setting_changed(identifier='preferred_software_workflow'),translation_context=_A,name='Software',description='Preset for software for which the operation will be performed');select_framebuffer_scale:IntProperty(min=10,max=100,default=10,subtype='PERCENTAGE',options={_C},update=Reports.update_log_setting_changed(identifier=_b),translation_context=_A,name='Select Framebuffer Scale',description='Select framebuffer scale percentage, available in "Developer Extras" section. This exists mostly for optimization purposes, since the smaller size of framebuffer significantly reduces the use of both memory and CPU. The point is that the data from framebuffer will be read not only in one particular place, but also to determine which cameras in the field of view of the observer and require rendering of preview. Changing this option requires restarting the active main operator');log_level:Reports.get_prop_log_level()
	@staticmethod
	def _get_hotkey_entry_item(km:KeyMap,kmi_name:str,kmi_value:str,properties):
		for(i,km_item)in enumerate(km.keymap_items):
			if km.keymap_items.keys()[i]==kmi_name:
				if properties:
					value=getattr(km.keymap_items[i].properties,properties,_D)
					if value==kmi_value:return km_item
				else:return km_item
	def draw(self,context:Context):
		layout:UILayout=self.layout;layout.use_property_split=_B;layout.use_property_decorate=_B;row_tab=layout.row(align=_B);row_tab.use_property_decorate=_B;row_tab.use_property_split=False;row_tab.prop(self,_E,expand=_B)
		match self.tab:
			case'APPEARANCE':
				if bhqab.utils_ui.template_disclosure_enum_flag(layout,item=self,prop_enum_flag=_I,flag=_H):col=layout.column();col.prop(self,_Q);col.prop(self,_V);col.prop(self,_Z,expand=_B);col.prop(self,_R);scol=col.column();scol.enabled=self.use_previews;scol.prop(self,_U);scol.prop(self,_T);scol.prop(self,_X,expand=_B)
				if bhqab.utils_ui.template_disclosure_enum_flag(layout,item=self,prop_enum_flag=_I,flag='AA'):col=layout.column(align=_B);bhqab.utils_gpu.DrawFramework.ui_preferences(layout,pref=self,attr_aa_method='aa_method',attr_smaa_preset='smaa_preset',attr_fxaa_preset='fxaa_preset',attr_fxaa_value='fxaa_value')
			case'KEYMAP':
				col=layout.column();kc=context.window_manager.keyconfigs.addon;km:_D|KeyMap=kc.keymaps.get('Image Paint')
				if km:
					col.context_pointer_set(_K,km);kmi=self._get_hotkey_entry_item(km,main.CPP_OT_select.bl_idname,_D,_D)
					if kmi:rna_keymap_ui.draw_kmi([],kc,km,kmi,col,0)
					kmi=self._get_hotkey_entry_item(km,main.CPP_OT_draw.bl_idname,_D,_D)
					if kmi:rna_keymap_ui.draw_kmi([],kc,km,kmi,col,0)
					kmi=self._get_hotkey_entry_item(km,main.CPP_OT_view_camera.bl_idname,_D,_D)
					if kmi:rna_keymap_ui.draw_kmi([],kc,km,kmi,col,0)
			case'INFO':
				def _intern_show_info_section(*,flag:str)->bool:return bhqab.utils_ui.template_disclosure_enum_flag(layout,item=self,prop_enum_flag=_P,flag=flag)
				for flag in(_J,_N,_O):
					if _intern_show_info_section(flag=flag):text=bhqab.utils_ui.request_localization_from_file(module=ADDON_PKG,langs=langs.LANGS,msgctxt=flag,src=os.path.join(DATA_DIR,_F,f"{flag}.txt"),dst={'uk':os.path.join(DATA_DIR,_F,f"{flag}_uk.txt")});bhqab.utils_ui.draw_wrapped_text(context,layout,text=text,text_ctxt=flag)
				if _intern_show_info_section(flag=_M):bhqupd.ui_draw_updates_section(context,layout,cb_draw_wrapped_text=bhqab.utils_ui.draw_wrapped_text)
				if _intern_show_info_section(flag='LINKS'):
					col_flow=layout.column_flow(columns=3,align=_B)
					def _intern_draw_large_url(icon:str,text:str,url:str):col=col_flow.column(align=_B);box=col.box();box.template_icon(icons.get_id(identifier=icon),scale=3.);scol=box.column();scol.emboss='NONE';scol.operator('wm.url_open',text=text,text_ctxt=_A).url=url
					_intern_draw_large_url(icon='patreon',text='Support Project on Patreon',url='https://www.patreon.com/BlenderHQ');_intern_draw_large_url(icon='github',text='Project on GitHub',url='https://github.com/BlenderHQ/camera_projection_painter');_intern_draw_large_url(icon='youtube',text='BlenderHQ on YouTube',url='https://www.youtube.com/@BlenderHQ');col=layout.column();bhqab.utils_ui.draw_wrapped_text(context,col,text='In case of issues, please submit log file alongside with issue.');Reports.template_ui_draw_paths(col)
			case'DEV':bhqab.utils_ui.template_developer_extras_warning(context,layout);layout.prop(self,'log_level');layout.prop(self,_b)