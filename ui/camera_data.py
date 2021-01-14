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
        layout.prop(camera, "lens")

    elif camera.type == 'ORTHO':
        layout.prop(camera, "ortho_scale")

    elif camera.type == 'PANO':
        layout.prop(camera, "lens")

    # Reality Capture sensor width is 36.0f as constant w.r.t 35mm camera format.
    # So here it is not displayed.

    if camera.type == 'PERSP':
        col = layout.column(align=True)
        col.prop(camera.cpp, "principal_x", text="Principal X")
        col.prop(camera.cpp, "principal_y", text="Y")

        layout.prop(camera.cpp, "skew")
        layout.prop(camera.cpp, "pixel_aspect")


def draw_reality_capture_distortion(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera.cpp, "distortion_model")
    distortion_model = camera.cpp.distortion_model

    if distortion_model != 'NONE':
        col = layout.column(align=True)

        if distortion_model == 'DIVISION':
            col.prop(camera.cpp, "division_k1")

        elif distortion_model == 'BROWN':
            col.prop(camera.cpp, "brown_k1")
            col.prop(camera.cpp, "brown_k2")
            col.prop(camera.cpp, "brown_k3")
            col.prop(camera.cpp, "brown_k4")
            col.separator()
            col.prop(camera.cpp, "brown_p1")
            col.prop(camera.cpp, "brown_p2")


# ------------------------ METASHAPE ------------------------ #
def draw_metashape_calibration(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera, "type")

    if camera.type == 'PERSP':
        layout.prop(camera, "lens")
        if camera.sensor_fit == 'VERTICAL':
            layout.prop(camera, "sensor_height", text="Sensor")
        else:
            layout.prop(camera, "sensor_width", text="Sensor")

    elif camera.type == 'ORTHO':
        layout.prop(camera, "ortho_scale")

    elif camera.type == 'PANO':
        layout.prop(camera, "lens")
        layout.prop(camera.cpp, "pano_type")

    if camera.type == 'PERSP' or (camera.type == 'PANO' and camera.cpp.pano_type == 'FISHEYE'):
        col = layout.column(align=True)
        col.prop(camera.cpp, "principal_x", text="Principal X")
        col.prop(camera.cpp, "principal_y", text="Y")

        layout.prop(camera.cpp, "skew")
        layout.prop(camera.cpp, "affinity")


def draw_metashape_distortion(layout: bpy.types.UILayout, camera: bpy.types.Camera) -> None:
    layout.prop(camera.cpp, "distortion_model")
    distortion_model = camera.cpp.distortion_model

    col = layout.column(align=True)
    if distortion_model == 'BROWN':
        col.prop(camera.cpp, "brown_k1")
        col.prop(camera.cpp, "brown_k2")
        col.prop(camera.cpp, "brown_k3")
        col.prop(camera.cpp, "brown_k4")
        col.separator()
        col.prop(camera.cpp, "brown_p1")
        col.prop(camera.cpp, "brown_p2")
        col.prop(camera.cpp, "brown_p3")
        col.prop(camera.cpp, "brown_p4")


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
