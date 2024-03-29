from __future__ import annotations
_C='LEFTMOUSE'
_B='PRESS'
_A=None
bl_info={'name':'Camera Projection Painter 4.0.0','author':'Vladlen Kuzmin (ssh4), Ivan Perevala (ivpe)','version':(4,0,0),'blender':(4,0,0),'description':'Photogrammetry textures refinement','location':'Tool Settings > Camera Painter','support':'COMMUNITY','category':'Paint','doc_url':'https://github.com/BlenderHQ/camera_projection_painter'}
import os,time
from importlib import reload
dt=time.time()
from.lib import bhqab
ADDON_PKG=bhqab.utils_ui.get_addon_package_name()
DATA_DIR=os.path.join(os.path.dirname(__file__),'data')
DOCS_BRANCH='latest'
def get_addon_pref(context:Context)->props.pref.Preferences:return context.preferences.addons[ADDON_PKG].preferences
class Reports(bhqab.reports.AddonLogger):0
def register_class(cls):bpy.utils.register_class(cls);_classes_registered.append(cls)
def unregister_class(cls):bpy.utils.unregister_class(cls);_classes_registered.remove(cls)
if'bpy'in locals():reload(bhqab);reload(bhqglsl);reload(bhqdbl);reload(bhqupd);reload(constants);reload(icons);reload(props);reload(shaders);reload(main);reload(ops);reload(langs);reload(ui);reload(manual_map)
else:_classes_registered=list();from.lib import bhqglsl,bhqdbl,bhqupd;from.import constants;from.import icons;from.import props;from.import shaders;from.import main;from.import ops;from.import langs;from.import ui;from.import manual_map
HAS_BPY=False
try:import bpy
except ImportError:pass
else:HAS_BPY=bpy.app.version is not _A
from bpy.types import Context,KeyMap,KeyMapItem
from bpy.app.handlers import persistent
_addon_keymaps:dict[str,tuple[tuple[dict[str,str|bool|int],dict[str|any]]]]
if HAS_BPY and not bpy.app.background:_addon_keymaps={main.CPP_OT_draw.bl_idname:((dict(type=_C,value=_B,head=True),_A),),main.CPP_OT_select.bl_idname:((dict(type=_C,value=_B,head=True),_A),),main.CPP_OT_view_camera.bl_idname:((dict(type='MIDDLEMOUSE',value=_B,head=True),_A),)}
else:_addon_keymaps=dict()
_keymap_registry:list[tuple[KeyMap,KeyMapItem]]=[]
def register_keymap():
	if HAS_BPY and not bpy.app.background:
		wm=bpy.context.window_manager;kc=wm.keyconfigs.addon;km=kc.keymaps.new('Image Paint')
		for(idname,data)in _addon_keymaps.items():
			for(key_data,key_props)in data:
				key_data['idname']=idname;kmi=km.keymap_items.new(**key_data)
				if key_props is not _A:
					for(attr,value)in key_props.items():
						if hasattr(kmi.properties,attr):setattr(kmi.properties,attr,value)
				_keymap_registry.append((km,kmi))
def unregister_keymap():
	if HAS_BPY and not bpy.app.background:
		for(km,kmi)in _keymap_registry:km.keymap_items.remove(kmi)
		_keymap_registry.clear()
def eval_manual_map():
	pref=bpy.context.preferences;curr_language_code=pref.view.language[0:2];docs_locale='en'
	if curr_language_code in langs.LANGS:docs_locale=curr_language_code;Reports.log.debug(f"Requested manual map with existing locale '{pref.view.language}'")
	else:Reports.log.warning(f"Requested manual map with missing locale '{pref.view.language}'")
	return f"https://bhqcpp.readthedocs.io/{docs_locale}/{DOCS_BRANCH}/",manual_map.MANUAL_MAP
_persistent_classes=ops.bind_history_remove.CPP_OT_bind_history_remove,ops.bind_images.CPP_OT_bind_images,ops.data_cleanup.CPP_OT_data_cleanup,ops.ensure_canvas.CPP_OT_canvas_new,ops.ensure_canvas.CPP_OT_quick_select_canvas,ops.ensure_canvas.CPP_OT_ensure_canvas,ops.ensure_tool_settings.CPP_OT_ensure_tool_settings,ops.export_cameras.CPP_OT_export_cameras,ops.import_cameras.CPP_OT_import_cameras,ops.import_scene.CPP_OT_import_scene,ops.calc_scene_cage.CPP_OT_calc_scene_cage
_gpu_require_classes=main.CPP_OT_main,main.CPP_OT_draw,main.CPP_OT_select,main.CPP_OT_view_camera,main.CPP_GGT_editing_cage,ops.pref_show.CPP_OT_pref_show,ops.setup_context.CPP_OT_setup_context,ui.CPP_PT_dataset,ui.CPP_UL_bind_history_item,ui.CPP_PT_image,ui.CPP_PT_calibration,ui.CPP_PT_lens_distortion,ui.CPP_PT_inspection,ui.CPP_PT_inspection_image_orientation,ui.CPP_PT_inspection_highlight_border,ui.CPP_PT_io_cameras_transform,ui.CPP_PT_unified_name_props,ui.CPP_PT_export_cameras_rc_csv,ui.CPP_PT_export_cameras_rc_metadata_xmp,ui.CPP_PT_io_import_scene,ui.CPP_PT_inspection_cage
_classes=_persistent_classes
if HAS_BPY and not bpy.app.background:_classes=_persistent_classes+_gpu_require_classes
def _register_classes():
	props.register()
	for cls in _classes:register_class(cls)
	if not bpy.app.background:bpy.app.translations.register(ADDON_PKG,langs.LANGS);bpy.utils.register_manual_map(eval_manual_map);register_keymap()
	bhqupd.register_addon_update_operators()
def _unregister_classes():
	if not bpy.app.background:unregister_keymap();bpy.utils.unregister_manual_map(eval_manual_map);bpy.app.translations.unregister(ADDON_PKG)
	for cls in reversed(_classes_registered):unregister_class(cls)
	props.unregister();bhqupd.unregister_addon_update_operators()
def _log_settings(_=_A):log=Reports.log;log.debug('Loaded with settings:').push_indent();context=bpy.context;log.debug('Preferences:').push_indent();addon_pref=get_addon_pref(context);Reports.log_settings(item=addon_pref);log.pop_indent();log.debug('Scene:').push_indent();scene_props:props.scene.SceneProps=context.scene.cpp;Reports.log_settings(item=scene_props);log.pop_indent();log.pop_indent()
@persistent
def _handler_load_post(_=_A):
	if not _classes_registered:_register_classes();addon_pref=get_addon_pref(bpy.context);addon_pref.log_level=addon_pref.log_level
	bhqupd.check_addon_updates();_log_settings()
	if not main.WindowInstances.instances:main.WindowInstances.modal_ensure_operator_invoked_in_all_windows(context=bpy.context)
	if bpy.app.timers.is_registered(_handler_load_post):bpy.app.timers.unregister(_handler_load_post)
@persistent
def _handler_save_pre(_=_A):scene_props:props.scene.SceneProps=bpy.context.scene.cpp;scene_props.version=bpy.app.version[0]*100+bpy.app.version[1]%100;main.Workflow.Mesh.remove_temp_data()
_application_handlers=(bpy.app.handlers.load_post,_handler_load_post),(bpy.app.handlers.save_pre,_handler_save_pre)
def register():
	dt=time.time();Reports.initialize(logger_name=bl_info['name'],directory=os.path.join(os.path.dirname(__file__),'logs'),max_num_logs=30)
	if bpy.app.background:_register_classes()
	else:
		for(handle,func)in _application_handlers:handle.append(func)
		bpy.app.timers.register(_handler_load_post,first_interval=.1)
	Reports.log.debug('Register finished in {:.6f} second(s)'.format(time.time()-dt))
def unregister():
	dt=time.time()
	if not bpy.app.background:
		icons.CameraPainterIcons.release();main.WindowInstances.cancel_all()
		for(handle,func)in reversed(_application_handlers):
			if func in handle:handle.remove(func)
	_unregister_classes();Reports.log.debug('Un-registering finished in {:.6f} second(s)'.format(time.time()-dt));Reports.shutdown()