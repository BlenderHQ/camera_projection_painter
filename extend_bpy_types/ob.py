from .. import engine

import bpy

from bpy.props import BoolProperty


@engine.object_transform_properties.object_transform_matrix_helper()
class ObjectProperties(bpy.types.PropertyGroup):
    used: BoolProperty(name="Used", default=True)
