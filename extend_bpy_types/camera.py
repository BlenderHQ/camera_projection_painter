from .. import engine
from .. import __package__ as addon_pkg

import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty,
    PointerProperty
)


class BindImageHistoryItem(bpy.types.PropertyGroup):
    """Used to store a palette of previously used images.
    """
    image: PointerProperty(
        type=bpy.types.Image, name="Image",
        options={'HIDDEN'})

    favorite: BoolProperty(
        name="Favorite",
        default=False,
        description="Mark image as favorite"
    )


@engine.camera_data_intrinsics_properties.camera_calibration_helper()
class CameraProperties(bpy.types.PropertyGroup):
    """Serves for storing the properties associated with the data of each individual camera,
    the main here is the image binded to the camera.
    """
    # Update methods

    def _image_update(self, context):
        if self.image and self.image.cpp.valid:
            camera = self.id_data
            bind_history = camera.cpp_bind_history
            bind_history_images = []
            for item in bind_history:
                if item.image and item.image.cpp.valid:
                    bind_history_images.append(item.image)

            if self.image in bind_history_images:
                check_index = bind_history_images.index(self.image)
            else:
                item = camera.cpp_bind_history.add()
                item.image = self.image
                check_index = len(camera.cpp_bind_history) - 1

            if self.active_bind_index <= len(bind_history) - 1:
                item = bind_history[self.active_bind_index]
                if item.image != self.image:
                    self.active_bind_index = check_index

    def _image_poll(self, value):
        if value.source == 'FILE':
            return True
        return False

    def _active_bind_index_update(self, context):
        camera = self.id_data
        bind_history = camera.cpp_bind_history
        item = bind_history[self.active_bind_index]
        if item.image and item.image.cpp.valid and (item.image != self.image):
            self.image = item.image

    # Properties
    active_bind_index: IntProperty(
        name="Active Bind History Index",
        default=0,
        update=_active_bind_index_update)

    image: PointerProperty(
        type=bpy.types.Image, name="Image",
        options={'HIDDEN'},
        description="An image binded to a camera for use as a Clone Image in Texture Paint mode",
        update=_image_update,
        poll=_image_poll)
