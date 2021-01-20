__all__ = (
    "object_transform_matrix_helper",
)

from . import _engine as engine
from . import ng_prop

if "bpy" in locals():
    import importlib
    # importlib.reload(ng_prop)

import bpy

_element_kwargs = {
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
}

_object_transform_matrix_prop_dict = {}


def _get_elem_name_by_indices(i: int, j: int):
    return f"r_{i}{j}"


for i in range(4):
    for j in range(4):
        name = _get_elem_name_by_indices(i, j)
        _object_transform_matrix_prop_dict[name] = ng_prop.get_double_pointer_property(name=name)


def _update_transform_matrix_from_object(self):
    ob = self.id_data
    for i in range(4):
        for j in range(4):
            name = _get_elem_name_by_indices(i, j)
            elem = getattr(self, name)
            setattr(elem, "float_value", ob.matrix_world[i][j])


def _draw_rotation_matrix(self, layout: bpy.types.UILayout) -> None:
    layout.label(text="Rotation Matrix:")
    grid = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True)
    for i in range(3):
        for j in range(3):
            elem = getattr(self, _get_elem_name_by_indices(i, j))
            elem.draw_info(grid)


def _draw_location_elements(self, layout: bpy.types.UILayout) -> None:
    row = layout.row(align=True)
    row.alignment = 'EXPAND'

    col = row.column(align=True)
    col.alignment = 'RIGHT'
    col.label(text="Location:  X")
    col.label(text="Y")
    col.label(text="Z")

    col = row.column(align=True)
    row.alignment = 'CENTER'
    self.r_03.draw_info(col)
    self.r_13.draw_info(col)
    self.r_23.draw_info(col)


def object_transform_matrix_helper():
    """Class decorator function. Updates class annotations by double precision values of 4x4 transform matrix
    """
    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        cls.__annotations__.update(_object_transform_matrix_prop_dict)

        if not hasattr(cls, "update_transform_matrix_from_object"):
            setattr(cls, "update_transform_matrix_from_object", _update_transform_matrix_from_object)

        if not hasattr(cls, "draw_rotation_matrix"):
            setattr(cls, "draw_rotation_matrix", _draw_rotation_matrix)

        if not hasattr(cls, "draw_location_elements"):
            setattr(cls, "draw_location_elements", _draw_location_elements)

        return cls

    return wrapper
