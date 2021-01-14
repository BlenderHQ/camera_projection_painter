from . import ui_lists
from . import pie_menus
# Panels
from . import panel_camera_painter
from . import panel_dataset
from . import panel_canvas_texture
from . import panel_brush
from . import panel_workflow
from . import panel_image_preview
from . import panel_bind_history
from . import panels_view
# Camera data (extrinsics, intrinsics per preferred software workflow)
from . import camera_data

if "bpy" in locals():
    import importlib

    importlib.reload(ui_lists)
    # Reload panels
    importlib.reload(panel_camera_painter)
    importlib.reload(panel_dataset)
    importlib.reload(panel_canvas_texture)
    importlib.reload(panel_workflow)
    importlib.reload(panel_image_preview)
    importlib.reload(panel_bind_history)
    importlib.reload(panel_brush)
    importlib.reload(panels_view)
    # Camera data sub-module
    importlib.reload(camera_data)

import bpy


_classes = [
    # UI list items
    ui_lists.DATA_UL_scene_camera_item,
    ui_lists.DATA_UL_bind_history_item,
    ui_lists.DATA_UL_node_image_item,

    # Pie-menus
    pie_menus.CPP_MT_camera_pie,

    # Camera projection painter base panel
    panel_camera_painter.CPP_PT_camera_painter,
    # Dataset panel
    panel_dataset.CPP_PT_dataset,
    # Canvas / Texture panel
    panel_canvas_texture.CPP_PT_canvas_texture,
    # Workflow panel
    panel_workflow.CPP_PT_workflow,
    # Brush panel
    panel_brush.CPP_PT_brush,

    # View options panels
    panels_view.CPP_PT_view,
    panels_view.CPP_PT_texture_preview,
    panels_view.CPP_PT_cameras_viewport,
    panels_view.CPP_PT_brush_preview,
    panels_view.CPP_PT_warnings,

    # Image icon preview
    panel_image_preview.CPP_PT_image_preview,
    # Bind history
    panel_bind_history.CPP_PT_bind_history,
    # Camera data
    camera_data.CPP_PT_camera_extrinsics,
    camera_data.CPP_PT_calibration,
    camera_data.CPP_PT_lens_distortion,
]

register, unregister = bpy.utils.register_classes_factory(_classes)
