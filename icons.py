from __future__ import annotations
import os
from.import DATA_DIR
from.lib import bhqab
__all__='ICONS_DIRECTORY','IMAGE_ICON_NAMES','DATA_ICON_NAMES','CameraPainterIcons','get_id'
ICONS_DIRECTORY=os.path.join(DATA_DIR,'icons')
IMAGE_ICON_NAMES='cleanup','ensure_canvas'
DATA_ICON_NAMES='aa','appearance','bind','calibration','cleanup_small','credits','dataset','export_cameras','export_reality_capture','export','facing_back','facing_front','github','ignore_extension','ignore_letter_case','image','import_cameras','import_image','import_images','import_scene','import','info','inspection','keymap','lens_distortion','license','links','metashape','outline_checker','outline_fill','outline_lines','patreon','preferences','prv_size_large','prv_size_normal','readme','reality_capture','setup_context','tooltip_fixed','tooltip_floating','tooltip_static','transform','ui','unit_mm','unit_px','update','use_cam_name','use_camera_name','use_image_filepath','viewport','youtube'
class CameraPainterIcons(bhqab.utils_ui.IconsCache):0
def get_id(identifier:str)->int:CameraPainterIcons.initialize(directory=ICONS_DIRECTORY,data_identifiers=DATA_ICON_NAMES,image_identifiers=IMAGE_ICON_NAMES);return CameraPainterIcons.get_id(identifier)