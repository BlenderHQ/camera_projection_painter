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
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
}

_object_location_vector_prop_dict = {}
_object_rotation_matrix_prop_dict = {}


def _get_location_vector_elem_name_by_index(i: int):
    return f"{engine.types.ATTR_LOCATION_VECTOR_PREFIX}{i}"


def _location_vector_elem_update(self, _context):
    self.id_data.matrix_world[self.index][3] = getattr(
        self,
        engine.types.NG_PROP_ATTR_FLOAT_VALUE
    )


def _get_rotation_matrix_elem_name_by_indices(i: int, j: int):
    return f"{engine.types.ATTR_ROTATION_MATRIX_PREFIX}{i}{j}"


def _rotation_matrix_elem_update(self, _context):
    self.id_data.matrix_world[self.indices[0]][self.indices[1]] = getattr(
        self,
        engine.types.NG_PROP_ATTR_FLOAT_VALUE
    )


for i in range(3):
    name = _get_location_vector_elem_name_by_index(i)
    _object_location_vector_prop_dict[name] = ng_prop.get_double_pointer_property(
        name=name,
        index=i,
        update=_location_vector_elem_update,
        options={'HIDDEN'}
    )

    for j in range(3):
        name = _get_rotation_matrix_elem_name_by_indices(i, j)
        _object_rotation_matrix_prop_dict[name] = ng_prop.get_double_pointer_property(
            name=name,
            indices=(i, j),
            update=_rotation_matrix_elem_update,
            options={'HIDDEN'}
        )


def _update_location_vector_from_object(self):
    ob = self.id_data
    for i in range(3):
        setattr(
            getattr(self, _get_location_vector_elem_name_by_index(i)),
            engine.types.NG_PROP_ATTR_FLOAT_VALUE,
            ob.matrix_world[i][3]
        )


def _update_rotation_matrix_from_object(self):
    ob = self.id_data
    for i in range(3):
        for j in range(3):
            setattr(
                getattr(self, _get_rotation_matrix_elem_name_by_indices(i, j)),
                engine.types.NG_PROP_ATTR_FLOAT_VALUE,
                ob.matrix_world[i][j]
            )


def _draw_rotation_matrix(self, layout: bpy.types.UILayout) -> None:
    layout.label(text="Rotation Matrix:")
    grid = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True)
    for i in range(3):
        for j in range(3):
            elem = getattr(self, _get_rotation_matrix_elem_name_by_indices(i, j))
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

    for i in range(3):
        getattr(self, _get_location_vector_elem_name_by_index(i)).draw_info(col)


def object_transform_matrix_helper():
    """Class decorator function. Updates class annotations by double precision values of 4x4 transform matrix
    """
    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        cls.__annotations__.update(_object_location_vector_prop_dict)
        cls.__annotations__.update(_object_rotation_matrix_prop_dict)

        if not hasattr(cls, "update_location_vector_from_object"):
            setattr(cls, "update_location_vector_from_object", _update_location_vector_from_object)

        if not hasattr(cls, "update_rotation_matrix_from_object"):
            setattr(cls, "update_rotation_matrix_from_object", _update_rotation_matrix_from_object)

        if not hasattr(cls, "draw_rotation_matrix"):
            setattr(cls, "draw_rotation_matrix", _draw_rotation_matrix)

        if not hasattr(cls, "draw_location_elements"):
            setattr(cls, "draw_location_elements", _draw_location_elements)

        return cls

    return wrapper
