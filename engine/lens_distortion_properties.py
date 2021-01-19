# Copyright (C) 2018 Ivan Perevala (ivpe), Vlad Kuzmin (ssh4)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import FloatProperty, EnumProperty

from . import _engine as engine
from ._engine import icons

__all__ = (
    "camera_calibration_helper",
)

_double_property_additional_description = "\u2022 The current value is displayed in single precision.\n" \
    "Actual value may be different.\n"\
    "Double precision value can be showed in popup (dot right).\n"\
    "For more information, see the documentation."


class NG_OT_ng_prop_info(bpy.types.Operator):
    bl_idname = "ng.prop_info"
    bl_label = "Property Information"
    bl_options = {'INTERNAL'}

    desk: bpy.props.StringProperty()

    @classmethod
    def description(cls, _context, properties):
        return properties.desk

    def execute(self, _context):
        return {'CANCELLED'}


def get_double_pointer_property(name: str, **kwargs):
    """Generate and register dynamic property type which contains float, double as string and exact double as
    string representation of floating point value. "Exact" value means imported 16 digits value from third-party
    software.

    Registered property group contains additional API:
        prec_icon_id (property): integer icon id to be used to show precision info in the UI.
        draw (method): Should be used to draw property in the UI with given text.
        draw_info (method): Should be used to draw double precision representation in the UI.

    Args:
        name (str): Regular property name.
        **kwargs: Keyword arguments should be the same as for `bpy.props.FloatProperty`.
    Returns:
        bpy.props.PointerProperty: Registered property.
    """
    # Set display precision to IEEE-754 standard.
    kwargs["precision"] = engine.types.FLT_DIG

    # `update` keyword argument handling.
    # First should be called passed by `**kwargs` update function or method,
    # than delta value will be computed.
    kwargs_update_func = None
    if "update" in kwargs:
        kwargs_update_func = kwargs["update"]
        del kwargs["update"]

    kwargs_default = 0.0
    if "default" in kwargs:
        kwargs_default = kwargs["default"]

    def _float_value_update(self, context):
        if kwargs_update_func is not None:
            kwargs_update_func(self, context)
        engine.types.evaluate_ng_cpp_prop_as_string(self)
        self.prev_float_value = self.float_value

    def _exact_double_value_update(self, _context):
        self.float_value = engine.types.str_to_floating_point(self.exact_double_as_str)
        self.double_as_str = self.exact_double_as_str

    # Add information about floating point precision to property description.
    if "description" in kwargs:
        kwargs["description"] += ".\n\n" + _double_property_additional_description
    else:
        kwargs["description"] = _double_property_additional_description

    # UI draw methods:
    def _prec_icon_id_getter(self) -> None:
        """
        Precision icon id:
            White - no exact double precision value.
            Green - current double precision value equals to exact double precision value.
            Yellow - current double precision value is different from exact double precision value.
        """
        if not self.exact_double_as_str:
            return icons.get_icon_id("white_dot")
        elif self.double_as_str == self.exact_double_as_str:
            return icons.get_icon_id("green_dot")
        else:
            return icons.get_icon_id("yellow_dot")

    def _draw_method(self, layout: bpy.types.UILayout, text="") -> None:
        """Draw single precision value in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """
        row = layout.row(align=True)
        if text:
            row.prop(self, "float_value", text=text)
        else:
            row.prop(self, "float_value")

        dbl_text = "Missing"
        if self.double_as_str:
            dbl_text = self.double_as_str

        exact_text = "Missing"
        if self.exact_double_as_str:
            exact_text = self.exact_double_as_str

        props = row.operator(operator=NG_OT_ng_prop_info.bl_idname, icon_value=self.prec_icon_id, text="", emboss=False)
        props.desk = f"\nDouble precision:                {dbl_text}\n" \
            f"Imported double precision: {exact_text}"

    def _draw_info_method(self, layout: bpy.types.UILayout) -> None:
        """Draw double precision value info in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """

        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text=f"{self.double_as_str}")
        row.label(icon_value=self.prec_icon_id)

    # Create dynamic class to store property.
    double_property_group = type(
        "ng_prop_" + name.replace(" ", "_").lower(),
        (
            bpy.types.PropertyGroup,
        ),
        {
            "__slots__": tuple(),

            "__annotations__": {
                "prev_float_value": bpy.props.FloatProperty(
                    **kwargs
                ),
                "float_value": bpy.props.FloatProperty(
                    name=name,
                    update=_float_value_update,
                    **kwargs
                ),
                "double_as_str": bpy.props.StringProperty(
                    maxlen=engine.types.DBL_DIG,
                    default=engine.types.floating_point_to_str(kwargs_default),
                    options={'HIDDEN'},
                ),
                "exact_double_as_str": bpy.props.StringProperty(
                    maxlen=engine.types.DBL_DIG,
                    update=_exact_double_value_update,
                    options={'HIDDEN'},
                )
            },
            "prec_icon_id": property(fget=_prec_icon_id_getter),
            "draw": _draw_method,
            "draw_info": _draw_info_method,
        }
    )

    bpy.utils.register_class(double_property_group)

    return bpy.props.PointerProperty(type=double_property_group)


# Common properties for lens distortion coefficients.
_common_coeff_kwargs = {
    "subtype": 'NONE',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "soft_min": -5.0,
    "soft_max": 5.0,
    "options": {'HIDDEN'},
}

# Polynomial lens distortion model coefficients
_polynomial_coeff = {
    "polynomial_k1": get_double_pointer_property(
        name="K1",
        description="First coefficient of Polynomial radial distortion",
        **_common_coeff_kwargs
    ),
    "polynomial_k2": get_double_pointer_property(
        name="K2",
        description="Second coefficient of Polynomial radial distortion",
        **_common_coeff_kwargs
    ),
    "polynomial_k3": get_double_pointer_property(
        name="K3",
        description="Third coefficient of Polynomial radial distortion",
        **_common_coeff_kwargs
    ),
}

# Division lens distortion model coefficients
_division_coeff = {
    "division_k1": get_double_pointer_property(
        name="K1",
        description="First coefficient of Division radial distortion",
        **_common_coeff_kwargs
    ),
    "division_k2": get_double_pointer_property(
        name="K2",
        description="Second coefficient of Division radial distortion",
        **_common_coeff_kwargs
    ),
}


# Nuke lens distortion model coefficients
_nuke_coeff = {
    "nuke_k1": get_double_pointer_property(
        name="K1",
        description="First coefficient of Nuke radial distortion",
        **_common_coeff_kwargs
    ),
    "nuke_k2": get_double_pointer_property(
        name="K2",
        description="Second coefficient of Nuke radial distortion",
        **_common_coeff_kwargs
    ),
}

# Brown-Conrady lens distortion model coefficients
_brown_coeff = {
    "brown_k1": get_double_pointer_property(
        name="K1",
        description="First coefficient of Brown-Conrady radial distortion",
        **_common_coeff_kwargs
    ),
    "brown_k2": get_double_pointer_property(
        name="K2",
        description="Second coefficient of Brown-Conrady radial distortion",
        **_common_coeff_kwargs
    ),
    "brown_k3": get_double_pointer_property(
        name="K3",
        description="Third coefficient of Brown-Conrady radial distortion",
        **_common_coeff_kwargs
    ),
    "brown_k4": get_double_pointer_property(
        name="K4",
        description="Fourth coefficient of Brown-Conrady radial distortion",
        **_common_coeff_kwargs
    ),
    "brown_p1": get_double_pointer_property(
        name="P1",
        description="First coefficient of Brown-Conrady tangential distortion",
        **_common_coeff_kwargs
    ),
    "brown_p2": get_double_pointer_property(
        name="P2",
        description="Second coefficient of Brown-Conrady tangential distortion",
        **_common_coeff_kwargs
    ),
    "brown_p3": get_double_pointer_property(
        name="P3",
        description="Third coefficient of Brown-Conrady tangential distortion",
        **_common_coeff_kwargs
    ),
    "brown_p4": get_double_pointer_property(
        name="P4",
        description="Fourth coefficient of Brown-Conrady tangential distortion",
        **_common_coeff_kwargs
    ),
}

_distortion_coefficients_prop_dict = {}

_distortion_model_items = [
    ('NONE', "No Lens Distortion", ""),
]

if engine.WITH_NG_LD_POLYNOMIAL:
    _distortion_model_items.append(
        ('POLYNOMIAL', "Polynomial", "Polynomial lens distortion model")
    )
    _distortion_coefficients_prop_dict.update(_polynomial_coeff)

if engine.WITH_NG_LD_DIVISION:
    _distortion_model_items.append(
        ('DIVISION', "Division", "Division lens distortion model")
    )
    _distortion_coefficients_prop_dict.update(_division_coeff)

if engine.WITH_NG_LD_NUKE:
    _distortion_model_items.append(
        ('NUKE', "Nuke", "Nuke lens distortion model")
    )
    _distortion_coefficients_prop_dict.update(_nuke_coeff)

if engine.WITH_NG_LD_BROWN:
    _distortion_model_items.append(
        ('BROWN', "Brown", "Brown-Conrady lens distortion model")
    )
    _distortion_coefficients_prop_dict.update(_brown_coeff)

_distortion_model_kwargs = {
    "items": _distortion_model_items,
    "default": 'NONE',
    "name": "Distortion Model",
    "description": "Lens distortion model to be used"
}

# Panoramic camera type
_pano_type_kwargs = {
    "items": [
        ('FISHEYE', "Fisheye", "Fisheye panoramic camera"),
        ('EQUIRECTANGULAR', "Equirectangular", "Equirectangular panoramic camera"),
        ('CYLINDRICAL', "Cylindrical", "Cylindrical panoramic camera"),
    ],
    "default": 'FISHEYE',
    "name": "Panoramic Type",
    "description": "Panoramic type used for projection. Lens distortions are supported only by Fisheye cameras.",
}

# Optical center
_principal_point_x_kwargs = {
    "name": "Principal X",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "unit": 'CAMERA',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Deviation of the camera principal point in millimeters by X axis",
}

_principal_point_y_kwargs = {
    "name": "Principal Y",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "unit": 'CAMERA',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Deviation of the camera principal point in millimeters by Y axis",
}

# Skew
_skew_kwargs = {
    "name": "Skew",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "subtype": 'FACTOR',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Skew correction factor",
}

# Affinity
_affinity_kwargs = {
    "name": "Affinity",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "subtype": 'FACTOR',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Affinity correction factor",
}

# Pixel aspect
# NOTE: always clamped in ~0.0f...~2.0f in `engine` module, higher or lower values are ignored to support
# 'Distort' / `Undistort` mode.
_pixel_aspect_ratio = {
    "name": "Pixel Aspect",
    "default": 1.0,
    "min": 0.01,
    "max": 1.99,
    "subtype": 'FACTOR',
    "precision": engine.types.FLT_DIG,
    "step": engine.types.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Camera pixel aspect ratio correction factor"
}


# Camera calibration properties
_lens_distortion_prop_dict = {
    "distortion_model": bpy.props.EnumProperty(**_distortion_model_kwargs),
    "pano_type": bpy.props.EnumProperty(**_pano_type_kwargs),
    "principal_point_x": get_double_pointer_property(**_principal_point_x_kwargs),
    "principal_point_y": get_double_pointer_property(**_principal_point_y_kwargs),
    "skew": get_double_pointer_property(**_skew_kwargs),
    "affinity": get_double_pointer_property(**_affinity_kwargs),
    "pixel_aspect_ratio": get_double_pointer_property(**_pixel_aspect_ratio),
}


def camera_calibration_helper():
    """Class decorator function. Updates class annotations by double precision values relative to camera data.
    """
    bpy.utils.register_class(NG_OT_ng_prop_info)

    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        cls.__annotations__.update(_lens_distortion_prop_dict)
        cls.__annotations__.update(_distortion_coefficients_prop_dict)

        return cls

    return wrapper
