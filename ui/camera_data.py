from . import common
from .. import __package__ as addon_pkg

if "bpy" in locals():
    import importlib
    importlib.reload(common)

import bpy


# ------------------------ REALITY_CAPTURE ------------------------ #
def draw_reality_capture_calibration(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera, "type")

    if camera.type == 'PERSP':
        camera.cpp.focal_length.draw(layout)

    elif camera.type == 'ORTHO':
        camera.cpp.ortho_scale.draw(layout)

    elif camera.type == 'PANO':
        camera.cpp.focal_length.draw(layout)

    # Reality Capture sensor width is 36.0f as constant w.r.t 35mm camera format.
    # So here it is not displayed.

    if camera.type == 'PERSP':
        col = layout.column(align=True)
        camera.cpp.principal_point_x.draw(col, text="Principal X")
        camera.cpp.principal_point_y.draw(col, text="Y")

        camera.cpp.skew.draw(layout)
        camera.cpp.pixel_aspect_ratio.draw(layout)


def draw_reality_capture_distortion(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera.cpp, "distortion_model")

    if camera.cpp.distortion_model == 'BROWN':
        col = layout.column(align=True)
        camera.cpp.brown_k1.draw(col)
        camera.cpp.brown_k2.draw(col)
        camera.cpp.brown_k3.draw(col)
        camera.cpp.brown_k4.draw(col)
        col.separator()
        camera.cpp.brown_p1.draw(col, text="T1")
        camera.cpp.brown_p2.draw(col, text="T2")

    elif camera.cpp.distortion_model == 'DIVISION':
        col = layout.column(align=True)
        camera.cpp.division_k1.draw(col)


# ------------------------ METASHAPE ------------------------ #
def draw_metashape_calibration(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera, "type")

    if camera.type == 'PERSP':
        camera.cpp.focal_length.draw(layout)
        if camera.sensor_fit == 'VERTICAL':
            layout.prop(camera, "sensor_height", text="Sensor")
        else:
            layout.prop(camera, "sensor_width", text="Sensor")

    elif camera.type == 'ORTHO':
        camera.cpp.focal_length.draw(layout)

    elif camera.type == 'PANO':
        camera.cpp.focal_length.draw(layout)
        layout.prop(camera.cpp, "pano_type")

    if camera.type == 'PERSP' or (camera.type == 'PANO' and camera.cpp.pano_type == 'FISHEYE'):
        col = layout.column(align=True)
        camera.cpp.principal_point_x.draw(col, text="Principal X")
        camera.cpp.principal_point_y.draw(col, text="Y")

        camera.cpp.affinity.draw(layout)
        camera.cpp.pixel_aspect_ratio.draw(layout)


def draw_metashape_distortion(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera.cpp, "distortion_model")

    if camera.cpp.distortion_model == 'BROWN':
        col = layout.column(align=True)
        camera.cpp.brown_k1.draw(col)
        camera.cpp.brown_k2.draw(col)
        camera.cpp.brown_k3.draw(col)
        camera.cpp.brown_k4.draw(col)
        col.separator()
        camera.cpp.brown_p1.draw(col)
        camera.cpp.brown_p2.draw(col)
        camera.cpp.brown_p3.draw(col)
        camera.cpp.brown_p4.draw(col)


# ------------------------ Panels ------------------------ #
class CPP_PT_camera_extrinsics(bpy.types.Panel):
    bl_label = "Transform"
    bl_parent_id = "CPP_PT_workflow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return common.get_camera_object(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        camera_object = common.get_camera_object(context)

        layout.prop(camera_object, "location")
        layout.prop(camera_object, "rotation_euler")


class CameraIntrinsicsPanelBase:
    bl_parent_id = "CPP_PT_workflow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Camera Painter"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        addon_preferences = context.preferences.addons[addon_pkg].preferences
        preferred_workflow = addon_preferences.preferred_workflow

        camera_ob = common.get_camera_object(context)
        if camera_ob is None:
            return False
        camera = camera_ob.data

        # REALITY_CAPTURE
        if preferred_workflow == 'REALITY_CAPTURE':
            if camera.type == 'PERSP':
                return True

        # METASHAPE
        elif preferred_workflow == 'METASHAPE':
            if camera.type == 'PERSP':
                return True
            elif camera.type == 'PANO' and camera.cpp.pano_type == 'FISHEYE':
                return True

        return False


class CPP_PT_calibration(bpy.types.Panel, CameraIntrinsicsPanelBase):
    bl_label = "Calibration"

    @classmethod
    def poll(cls, context):
        return common.get_camera_object(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        addon_preferences = context.preferences.addons[addon_pkg].preferences
        preferred_workflow = addon_preferences.preferred_workflow

        camera_ob = common.get_camera_object(context)
        camera = camera_ob.data

        if preferred_workflow == 'REALITY_CAPTURE':
            draw_reality_capture_calibration(layout, camera)
        elif preferred_workflow == 'METASHAPE':
            draw_metashape_calibration(layout, camera)


class CPP_PT_lens_distortion(bpy.types.Panel, CameraIntrinsicsPanelBase):
    bl_label = "Lens Distortion"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        addon_preferences = context.preferences.addons[addon_pkg].preferences
        preferred_workflow = addon_preferences.preferred_workflow

        camera_ob = common.get_camera_object(context)
        camera = camera_ob.data

        if preferred_workflow == 'REALITY_CAPTURE':
            draw_reality_capture_distortion(layout, camera)
        elif preferred_workflow == 'METASHAPE':
            draw_metashape_distortion(layout, camera)
