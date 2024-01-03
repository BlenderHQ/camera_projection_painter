from __future__ import annotations
_B='WINDOW'
_A='VIEW_3D'
from typing import TYPE_CHECKING
if TYPE_CHECKING:from typing import Iterator;from bpy.types import Area,Context,Region,Space
__all__='iter_areas','iter_area_regions','iter_area_spaces','tag_redraw_all_regions'
def iter_areas(context:Context,*,area_type:str=_A)->Iterator[Area]:
	for window in context.window_manager.windows:
		for area in window.screen.areas:
			area:Area
			if area.type==area_type:yield area
def iter_regions(context:Context,*,area_type:str=_A,region_type:str=_B)->Iterator[Region]:
	for window in context.window_manager.windows:
		for area in window.screen.areas:
			area:Area
			if area.type==area_type:
				for region in area.regions:
					if region.type==region_type:yield region
def iter_area_regions(*,area:Area,region_type:str=_B)->Iterator[Region]:
	for region in area.regions:
		region:Region
		if region.type==region_type:yield region
def iter_area_spaces(*,area:Area,space_type:str=_A)->Iterator[Space]:
	for space in area.spaces:
		space:Space
		if space.type==space_type:yield space
def tag_redraw_all_regions(context:Context,*,area_type:str=_A,region_type:str=_B):
	for area in iter_areas(context,area_type=area_type):
		for region in iter_area_regions(area=area,region_type=region_type):region.tag_redraw()