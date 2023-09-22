from __future__ import annotations
_C='LEFTMOUSE'
_B='PRESS'
_A=None
bl_info={'name':'Camera Projection Painter','author':'Vlad Kuzmin (ssh4), Ivan Perevala (ivpe)','version':(3,6,0),'blender':(3,6,0),'description':'Expanding the capabilities of clone brush for working with photo scans','location':'Tool settings > Camera Painter','support':'COMMUNITY','category':'Paint','doc_url':'https://github.com/BlenderHQ/camera_projection_painter'}
ADDON_PKG=__package__.split('.')[0]
import os,time
from importlib import reload
dt=time.time()
DATA_DIR=os.path.join(os.path.dirname(__file__),'data')
if'_log'in locals():reload(_log)
else:from.import _log
log=_log.LOG
LOG_DIR=_log.LOG_DIR
LOG_FILE=_log.LOG_FILE
def register_class(cls):bpy.utils.register_class(cls);_classes_registered.append(cls)
def unregister_class(cls):bpy.utils.unregister_class(cls);_classes_registered.remove(cls)
def get_addon_pref(context)->props.pref.Preferences:return context.preferences.addons[ADDON_PKG].preferences
if'bpy'in locals():reload(_log);reload(reports);reload(constants);reload(bhqab);reload(bhqglsl);reload(icons);reload(props);reload(shaders);reload(main);reload(ops);reload(langs);reload(ui);reload(manual_map)
else:_classes_registered=list();from.import reports,constants;from.lib import bhqab;from.lib import bhqglsl;from.import icons,props,shaders,main,ops,langs,ui,manual_map
HAS_BPY=False
try:import bpy
except ImportError:pass
else:HAS_BPY=bpy.app.version is not _A
from bpy.types import KeyMap,KeyMapItem
from bpy.app.handlers import persistent
log.debug('Sub-modules import time: {:.6f} second(s)'.format(time.time()-dt))
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
def eval_manual_map():return'https://bhqcpp.readthedocs.io/en/latest/',manual_map.MANUAL_MAP
_persistent_classes=ops.bind_history_remove.CPP_OT_bind_history_remove,ops.bind_images.CPP_OT_bind_images,ops.data_cleanup.CPP_OT_data_cleanup,ops.ensure_canvas.CPP_OT_canvas_new,ops.ensure_canvas.CPP_OT_canvas_quick_select,ops.ensure_canvas.CPP_OT_ensure_canvas,ops.ensure_tool_settings.CPP_OT_ensure_tool_settings,ops.export_cameras.CPP_OT_export_cameras,ops.import_cameras.CPP_OT_import_cameras,ops.import_scene.CPP_OT_import_scene
_gpu_require_classes=main.CPP_OT_main,main.CPP_OT_draw,main.CPP_OT_select,main.CPP_OT_view_camera,ops.pref_show.CPP_OT_pref_show,ops.setup_context.CPP_OT_setup_context,ui.CPP_PT_dataset,ui.CPP_UL_bind_history_item,ui.CPP_PT_image,ui.CPP_PT_transform,ui.CPP_PT_transform_location_default,ui.CPP_PT_transform_location_rc_xyalt,ui.CPP_PT_transform_rotation,ui.CPP_PT_transform_rotation_rc_hpr,ui.CPP_PT_transform_rotation_rc_opk,ui.CPP_PT_rc_rc_xmp_params,ui.CPP_PT_transform_rotation_rc_rotation,ui.CPP_PT_calibration,ui.CPP_PT_lens_distortion,ui.CPP_PT_inspection,ui.CPP_PT_inspection_image_orientation,ui.CPP_PT_inspection_highlight_border,ui.CPP_PT_io_cameras_transform,ui.CPP_PT_unified_name_props,ui.CPP_PT_export_cameras_rc_csv,ui.CPP_PT_export_cameras_rc_metadata_xmp,ui.CPP_PT_io_import_scene
_classes=_persistent_classes
if HAS_BPY and not bpy.app.background:_classes=_persistent_classes+_gpu_require_classes
def _register_classes():
	props.register()
	for cls in _classes:register_class(cls)
	if not bpy.app.background:bhqab.utils_ui.register_addon_update_operators();bpy.app.translations.register(ADDON_PKG,langs.LANGS);bpy.utils.register_manual_map(eval_manual_map);register_keymap()
def _unregister_classes():
	if not bpy.app.background:unregister_keymap();bpy.utils.unregister_manual_map(eval_manual_map);bpy.app.translations.unregister(ADDON_PKG);bhqab.utils_ui.unregister_addon_update_operators()
	for cls in reversed(_classes_registered):unregister_class(cls)
	props.unregister()
@persistent
def _handler_load_post(_=_A):
	if not _classes_registered:_register_classes();bhqab.utils_ui.check_addon_updates(force=False);addon_pref=get_addon_pref(bpy.context);addon_pref.log_level=addon_pref.log_level
	if not main.WindowInstances.instances:main.WindowInstances.modal_ensure_operator_invoked_in_all_windows(context=bpy.context,idname=main.CPP_OT_main.bl_idname)
	if bpy.app.timers.is_registered(_handler_load_post):bpy.app.timers.unregister(_handler_load_post)
@persistent
def _handler_save_pre(_=_A):scene_props:props.scene.SceneProps=bpy.context.scene.cpp;scene_props.version=bpy.app.version[0]*100+bpy.app.version[1]%100;main.Workflow.Mesh.remove_temp_data()
_application_handlers=(bpy.app.handlers.load_post,_handler_load_post),(bpy.app.handlers.save_pre,_handler_save_pre)
def register():
	dt=time.time()
	if bpy.app.background:_register_classes()
	else:
		for(handle,func)in _application_handlers:handle.append(func)
		bpy.app.timers.register(_handler_load_post,first_interval=.1)
	bpy.app.handlers.load_post.append(reports.load_post_log_settings);log.debug('Register finished in {:.6f} second(s)'.format(time.time()-dt))
def unregister():
	dt=time.time();bpy.app.handlers.load_post.remove(reports.load_post_log_settings)
	if not bpy.app.background:
		icons.IconsCache.release();main.WindowInstances.cancel_all()
		for(handle,func)in reversed(_application_handlers):
			if func in handle:handle.remove(func)
	_unregister_classes();log.debug('Un-registering finished in {:.6f} second(s)'.format(time.time()-dt))