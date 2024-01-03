from __future__ import annotations
from enum import auto,IntEnum,IntFlag
TEMPORARY_DATA_NAME:str='cpp_data'
UI_COMPATIBILITY_MODES:set[str]={'OBJECT','PAINT_TEXTURE'}
MAX_FRAGMENT_SAMPLER_UNIFORMS=25
class BorderType(IntEnum):NONE=auto();FILL=auto();CHECKER=auto();LINES=auto()
class Facing(IntFlag):FRONT=auto();BACK=auto()
class Cage(IntFlag):USE=auto();USE_CAMERAS=auto();USE_PREVIEWS=auto();USE_MESH_PREVIEW=auto()
class SetupStage(IntEnum):PASS_THROUGH=auto();INVOKED=auto();PRE_CLEANUP=auto();IMPORT_SCENE=auto();CHECK_CANVAS=auto();CHECK_CAMERAS=auto();CHECK_IMAGES=auto();CHECK_TOOL=auto();FINISHED=auto()
class DistortionModel(IntEnum):NONE=auto();DIVISION=auto();POLYNOMIAL=auto();BROWN=auto()
class IEEE754:FLT_DIG:int=6;FLT_EXP:float=float(f"1e-{FLT_DIG}");FLT_MAX:float=3.402823e38;INT_MAX:int=2147483647
class PROPERTY:
	OPTIONS:set[str]={'ANIMATABLE'}
	class FLOAT:STEP:float=float(f"1e-3");PRECISION:int=9
class CAMERA:
	class LENS:MIN:float=.1;SOFT_MAX:float=5e3;DEFAULT:float=5e1
	class SENSOR:DEFAULT_FIT:str='AUTO';DEFAULT_WIDTH:float=36.;DEFAULT_HEIGHT:float=24.;MIN:float=.1;SOFT_MAX:float=1e2
	class SELECT:OFFSET:int=-1
	class ASPECT:DEFAULT:float=1.
class TIME_STEP:IDLE:float=1/5;ACTIVE:float=1/60
class UI:
	class TOOLTIP:BORDER_PX_UNIT_SCALE:float=7.;PRV_SIZE_NORMAL:int=128;PRV_SIZE_LARGE:int=256;OFFSET_FROM_BORDER:int=50;FILEPATH_MAX_LENGTH:int=40
	class PRV:RESOLUTION=128*64;SIDE=int(RESOLUTION/128);NUM_TILES=SIDE**2;COLOR_FORMAT='RGBA8'
	if __debug__:
		class BLF:BOLD=1<<11;ITALIC=1<<12