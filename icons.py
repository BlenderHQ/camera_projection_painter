from __future__ import annotations
_B='default'
_A=None
import os
from.import DATA_DIR,log
__all__='get_id','IconsCache'
import bpy
from bpy.types import ImagePreview
import bpy.utils.previews
_IMAGE_ICON_NAMES='cleanup','ensure_canvas'
_DATA_ICON_NAMES='aa','appearance','bind','calibration','credits','dataset','double_precision','export_cameras','export_reality_capture','export','facing_back','facing_front','github','image','import_cameras','import_image','import_images','import_scene','import','info','inspection','keymap','lens_distortion','license','links','location','outline_checker','outline_fill','outline_lines','patreon','preferences','prv_size_large','prv_size_normal','readme','reality_capture','rotation','setup_context','single_precision','tooltip_fixed','tooltip_floating','tooltip_static','transform','ui','unit_mm','unit_px','update','viewport','youtube'
class IconsCache:
	_package:str='';_cache:dict[str,int]=dict();_pcoll_cache:_A|bpy.utils.previews.ImagePreviewCollection=_A
	@classmethod
	def _intern_initialize_from_data_files(cls,*,directory:str,icons_names:tuple[str]):
		for identifier in icons_names:
			try:icon_value=bpy.app.icons.new_triangles_from_file(os.path.join(directory,f"{identifier}.dat"))
			except ValueError:log.warning(f'Unable to load icon "{identifier}"');icon_value=0
			cls._cache[identifier]=icon_value
	@classmethod
	def initialize(cls,*,package:str=_B):
		if cls._cache and cls._package==package:return
		cls.release()
		if package!='NONE':
			package_directory=os.path.join(os.path.join(DATA_DIR,'icons'),package);cls._intern_initialize_from_data_files(directory=package_directory,icons_names=_DATA_ICON_NAMES);pcoll=bpy.utils.previews.new()
			for identifier in _IMAGE_ICON_NAMES:prv:ImagePreview=pcoll.load(identifier,os.path.join(package_directory,f"{identifier}.png"),'IMAGE');cls._cache[identifier]=prv.icon_id
			cls._pcoll_cache=pcoll
		cls._package=package
	@classmethod
	def release(cls):
		if cls._pcoll_cache is not _A:bpy.utils.previews.remove(cls._pcoll_cache);cls._pcoll_cache=_A
		cls._cache.clear()
def get_id(identifier:str)->int:IconsCache.initialize(package=_B);return IconsCache._cache.get(identifier,0)