from .. import engine

import bpy

from bpy.props import BoolProperty


@engine.camera_data_extrinsics_properties.object_transform_matrix_helper()
class ObjectProperties(bpy.types.PropertyGroup):
    used: BoolProperty(name="Used", default=True)

    def update_ng_prop(self) -> None:
        """Updates object data translation vector and rotation matrix elements and (optionally, only for cameras),
        camera data intrinsics data.
        """
        camera_ob = self.id_data

        # Update object data
        camera_ob.cpp.update_location_vector_from_object()
        camera_ob.cpp.update_rotation_matrix_from_object()

        # Update camera data intrinsics obly for 'CAMERA' type.
        if camera_ob.type == 'CAMERA':
            camera_ob.data.cpp.update_from_camera_data()
