from math import radians

from bpy_extras import view3d_utils
from mathutils import Vector, Matrix


def ray_cast(context, mpos):
    ob = context.active_object
    region = context.region
    rv3d = context.region_data

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mpos)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mpos)

    ray_target = ray_origin + view_vector

    # get the ray relative to the object
    matrix_inv = ob.matrix_world.inverted()
    ray_origin_obj = matrix_inv @ ray_origin
    ray_target_obj = matrix_inv @ ray_target
    ray_direction_obj = ray_target_obj - ray_origin_obj

    # cast the ray
    success, location, normal, face_index = ob.ray_cast(
        ray_origin_obj, ray_direction_obj)

    if success:
        location = ob.matrix_world @ location
        distance = (ray_origin - location).length
        return distance
    return -1


def _get_check_pattern():
    pattern = []
    rays_rows = 16  # 128 rays
    rays_cols = 8
    for i in range(rays_rows):
        angle = radians(360.0 / rays_rows * i)
        for j in range(rays_cols):
            mat_rotation = Matrix.Rotation(angle, 3, 'Z')
            p1 = Vector((1.0, 0.0, 0.0))
            p1.rotate(mat_rotation)
            pattern.append(p1.to_2d() * (1.0 / rays_cols * j))
    pattern.append(Vector((0.0, 0.0)))
    return pattern


CHECK_PATTERN = _get_check_pattern()  # do it at stage of import, it's constant


def get_warning_status(context, mpos) -> bool:
    mpos = Vector(mpos)
    brush_radius = context.scene.tool_settings.unified_paint_settings.size

    p0 = view3d_utils.region_2d_to_vector_3d(
        context.region, context.region_data, mpos)
    p1 = view3d_utils.region_2d_to_vector_3d(
        context.region, context.region_data, (mpos.x + brush_radius, mpos.y))
    scr_radius = (p0 - p1).length
    lens = context.space_data.lens * 0.01

    distances = []
    for p in CHECK_PATTERN:
        ppos = mpos + \
            (p * context.scene.tool_settings.unified_paint_settings.size)
        dist = ray_cast(context, ppos)
        if dist != -1:
            distances.append(dist)

    distance = 0.0
    if distances:
        distance = sum(distances) / len(distances)

    if (distance != -1) and ((scr_radius / lens * distance) > context.scene.cpp.distance_warning):
        return True
    return False
