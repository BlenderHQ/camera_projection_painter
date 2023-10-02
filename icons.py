from __future__ import annotations
import os
from.import DATA_DIR
from.lib import bhqab
__all__='get_id',
_ICONS_DIRECTORY=os.path.join(DATA_DIR,'icons','default')
_IMAGE_ICON_NAMES='cleanup','ensure_canvas'
_DATA_ICON_NAMES='aa','appearance','bind','calibration','credits','dataset','double_precision','export_cameras','export_reality_capture','export','facing_back','facing_front','github','image','import_cameras','import_image','import_images','import_scene','import','info','inspection','keymap','lens_distortion','license','links','location','outline_checker','outline_fill','outline_lines','patreon','preferences','prv_size_large','prv_size_normal','readme','reality_capture','rotation','setup_context','single_precision','tooltip_fixed','tooltip_floating','tooltip_static','transform','ui','unit_mm','unit_px','update','viewport','youtube'
class CameraPainterIcons(bhqab.utils_ui.IconsCache):0
def get_id(identifier:str)->int:CameraPainterIcons.initialize(directory=_ICONS_DIRECTORY,data_identifiers=_DATA_ICON_NAMES,image_identifiers=_IMAGE_ICON_NAMES);return CameraPainterIcons.get_id(identifier)