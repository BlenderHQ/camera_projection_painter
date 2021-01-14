from .. import poll
from .. import __package__ as addon_pkg

if "bpy" in locals():
    import importlib
    importlib.reload(poll)

import bpy
import gpu
import bgl


# Coordinates.
custom_shape_verts = (
    (0.0, 0.0, 0.0), )


class CPP_GT_camera_gizmo(bpy.types.Gizmo):
    bl_idname = "CPP_GT_camera_gizmo"

    __slots__ = (
        "shape",
        "camera_ob"
    )

    def _camera_ob_poll(self, value):
        return (isinstance(value, bpy.types.Object) and value.type == 'CAMERA')

    camera_ob: bpy.props.PointerProperty(type=bpy.types.Object)

    def draw(self, context):
        with gpu.matrix.push_pop():
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glEnable(bgl.GL_DEPTH_TEST)
            self.draw_custom_shape(self.shape)
            bgl.glDisable(bgl.GL_BLEND)
            bgl.glDisable(bgl.GL_DEPTH_TEST)

    def draw_select(self, context, select_id):
        self.draw_custom_shape(self.shape, select_id=select_id)

    def setup(self):
        if not hasattr(self, "shape"):
            self.shape = self.new_custom_shape(
                'POINTS', custom_shape_verts)

    def invoke(self, context, event):
        wm = context.window_manager
        wm.cpp.current_selected_camera_ob = self.camera_ob
        bpy.ops.wm.call_menu_pie(name="CPP_MT_camera_pie")
        return {'RUNNING_MODAL'}

    def exit(self, context, cancel):
        pass

    def modal(self, context, event, tweak):
        return {'FINISHED'}


class CPP_GGT_camera_gizmo_group(bpy.types.GizmoGroup):
    bl_idname = "CPP_GGT_camera_gizmo_group"
    bl_label = "Camera Painter Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'DEPTH_3D', 'SCALE'}

    _camera_gizmos: dict

    __slots__ = ("_camera_gizmos",)

    @classmethod
    def poll(cls, context):
        return poll.tool_setup_poll(context)

    def _create_gizmo(self, camera_ob):
        """Add one gizmo and sets its properties"""
        mpr = self.gizmos.new(CPP_GT_camera_gizmo.bl_idname)

        mpr.camera_ob = camera_ob

        mpr.matrix_basis = camera_ob.matrix_world

        mpr.use_select_background = False
        mpr.use_event_handle_all = False

        mpr.matrix_basis = camera_ob.matrix_world

        mpr.use_draw_modal = True

        self._camera_gizmos[camera_ob] = mpr

        return mpr

    def setup(self, context):
        self._camera_gizmos = {}

        # Gizmo created for every camera in the scene.
        for camera_ob in context.scene.cpp.camera_objects:
            self._create_gizmo(camera_ob)

    def refresh(self, context):
        _invalid_camera_gizmos = {}
        # Fill the dictionary with links to cameras that are deleted
        for camera_ob, mpr in self._camera_gizmos.items():
            try:
                _ = camera_ob.name
            except ReferenceError:
                _invalid_camera_gizmos[camera_ob] = mpr

        # Remove the gizmo of these cameras and from the dictionary
        for camera_ob, mpr in _invalid_camera_gizmos.items():
            self._camera_gizmos.pop(camera_ob)
            self.gizmos.remove(mpr)

        # Update the parameters of the gizmo of the existing cameras
        # and also add new ones if necessary
        for camera_ob in context.scene.cpp.camera_objects:
            if camera_ob in self._camera_gizmos.keys():
                mpr = self._camera_gizmos[camera_ob]
                mpr.matrix_basis = camera_ob.matrix_world
            else:
                mpr = self._create_gizmo(camera_ob)

    def draw_prepare(self, context):
        preferences = context.preferences.addons[addon_pkg].preferences
        # Properties concerning only rendering are changed when possible
        for mpr in self.gizmos:
            mpr.color = preferences.gizmo_color[0:3]
            mpr.alpha = preferences.gizmo_color[3]
            mpr.alpha_highlight = preferences.gizmo_color[3]

            mpr.scale_basis = preferences.gizmo_radius
