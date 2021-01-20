from typing import Iterator

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
    PointerProperty
)


class SceneProperties(PropertyGroup):
    """
    Contains properties and methods related to the Scene
    """

    @property
    def has_camera_objects(self) -> bool:
        """
        True if there are camera objects in the scene
        @return: bool
        """
        for ob in self.id_data.objects:
            if ob.type == 'CAMERA':
                return True
        return False

    @property
    def camera_objects(self) -> Iterator[bpy.types.Object]:
        """
        Generator of sequence of camera objects
        @return: generator
        """
        return (ob for ob in self.id_data.objects if ob.type == 'CAMERA')

    def update_lens_distortions_from_camera_objects(self):
        for camera_ob in self.camera_objects:
            camera = camera_ob.data

            camera.cpp.update_from_camera_data()

    @property
    def has_initial_visible_camera_objects(self) -> bool:
        """
        True if there are initial visible camera objects in the scene
        @return: bool
        """
        for _ in self.initial_visible_camera_objects:
            return True
        return False

    @property
    def initial_visible_camera_objects(self) -> Iterator[bpy.types.Object]:
        """
        Generator of sequence of initial visible camera objects
        @return: generator
        """
        return (ob for ob in self.camera_objects if ob.initial_visible)

    @property
    def has_camera_objects_selected(self) -> bool:
        """
        True if there are selected cameras in the scene
        @return: bool
        """
        for _ in self.selected_camera_objects:
            return True
        return False

    @property
    def selected_camera_objects(self):
        """
        Generator of sequence of selected camera objects
        @return: generator
        """
        return (ob for ob in self.id_data.cpp.camera_objects if ob.select_get())

    @property
    def used_images(self):
        """
        Generator of sequence of images used by `initial_visible_camera_objects`
        None values are skipped. So length may be not equal.
        """
        return (_.data.cpp.image for _ in self.initial_visible_camera_objects if _.data.cpp.image)

    # Utility methods
    def evaluate_initial_visible_camera_objects(self, context) -> None:
        """
        Set `initial_visible` attribute to True of object in
        context.visible_objects for each object in a scene.
        """
        for camera_ob in self.camera_objects:
            state = camera_ob in context.visible_objects
            camera_ob.initial_visible = state

    def update_initial_visible_cameras_sensors(self) -> None:
        """
        Update `sensor_fit` for each initial visible camera in the scene
        """
        for camera_ob in self.initial_visible_camera_objects:
            camera = camera_ob.data
            image = camera.cpp.image
            if image and image.cpp.valid:
                width, height = image.cpp.static_size
                if width > height:
                    camera.sensor_fit = 'VERTICAL'
                else:
                    camera.sensor_fit = 'HORIZONTAL'

    # Update methods
    def _get_camera_index(self):
        camob = None
        if bpy.context.mode == 'OBJECT':
            camob = bpy.context.active_object
        if not (camob and camob.type == 'CAMERA'):
            camob = self.id_data.camera
        if camob and camob.type == 'CAMERA':
            return self.id_data.objects.find(camob.name)
        return -1

    def _set_camera_index(self, value):
        self.id_data.camera = self.id_data.objects[value]
        camera_object = self.id_data.camera
        camera_object.initial_visible = True
        image = camera_object.data.cpp.image
        # if image and image.cpp.valid:
        #     self.id_data.tool_settings.image_paint.clone_image = image
        if bpy.context.mode == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
            camera_object.select_set(True)
            bpy.context.view_layer.objects.active = camera_object

    def _get_used_all_cameras(self):
        for ob in self.camera_objects:
            if ob == self.id_data.camera:
                continue
            if ob.initial_visible:
                return True
        return False

    def _set_used_all_cameras(self, value):
        for ob in self.camera_objects:
            if ob == self.id_data.camera:
                continue
            ob.initial_visible = value

    active_camera_index: IntProperty(
        name="Active Camera", get=_get_camera_index, set=_set_camera_index)

    used_all_cameras: BoolProperty(
        name="Use All", get=_get_used_all_cameras, set=_set_used_all_cameras)

    # Properties
    source_dir: StringProperty(
        name="Source Images Directory",
        subtype='DIR_PATH',
        description="The path to the directory of the images used. "
                    "Used to automate image search for cameras by name"
    )

    cameras_viewport_size: FloatProperty(
        name="Viewport Display Size",
        default=1.0, soft_min=0.5, soft_max=5.0, min=0.1, step=0.1,
        subtype='DISTANCE',
        options={'HIDDEN'},
        description="The size of the cameras to display in the viewport. Does not affect camera settings"
    )

    # Viewport draw
    use_projection_preview: BoolProperty(
        name="Brush Preview", default=True,
        options={'HIDDEN'},
        description="Display preview overlay projection clone image in brush"
    )

    use_normal_highlight: BoolProperty(
        name="Normal Highlight", default=True,
        options={'HIDDEN'},
        description="Visualization of the angle between "
        "the direction of the projector and the normal of the mesh in the current fragment"
    )

    camera_axes_size: FloatProperty(
        name="Axes Size",
        default=0.0, soft_min=0.0, soft_max=1.0, step=0.1,
        subtype='DISTANCE',
        options={'HIDDEN'},
        description="Axis display length in viewport"
    )

    # Current image preview
    current_image_size: IntProperty(
        name="Scale",
        default=250, min=200, soft_max=1000,
        subtype='PIXEL',
        options={'HIDDEN'},
        description="The size of the displayed image on the longest side in pixels"
    )

    current_image_alpha: FloatProperty(
        name="Alpha",
        default=0.25, soft_min=0.0, soft_max=1.0, step=1,
        subtype='FACTOR',
        options={'HIDDEN'},
        description="The transparency of the displayed gizmo. "
        "If the cursor is over the gizmo, an opaque image is displayed"
    )

    current_image_position: FloatVectorProperty(
        name="Pos", size=2,
        options={'HIDDEN'},
        default=(0.0, 0.0), min=0.0, max=1.0
    )

    # Warnings
    use_warnings: BoolProperty(
        name="Use warnings", default=True,
        options={'HIDDEN'},
        description="Use warnings if drawing can potentially become lagging"
    )

    use_warning_action_draw: BoolProperty(
        name="Brush Preview", default=True,
        options={'HIDDEN'},
        description="Displays a warning in the brush preview. Doesn't depend on Use Brush Preview"
    )

    use_warning_action_popup: BoolProperty(
        name="Info popup", default=False,
        options={'HIDDEN'},
        description="Open popup warning if current context is out of recommended"
    )

    use_warning_action_lock: BoolProperty(
        name="Lock Paint", default=True,
        options={'HIDDEN'},
        description="Lock paint if current context is out of recommended"
    )

    distance_warning: FloatProperty(
        name="Safe Radius",
        default=5.0, soft_min=1.0, soft_max=15.0,
        subtype='DISTANCE',
        options={'HIDDEN'},
        description="User recommended radius projected onto the plane brush"
    )

    max_loaded_images: IntProperty(
        name="Max Loaded Images",
        default=5,
        min=2,
        soft_max=10,
        description="The number of images simultaneously loaded into memory.\n"
                    "If this limit is exceeded, the first of the loaded images is freed from memory"
    )
