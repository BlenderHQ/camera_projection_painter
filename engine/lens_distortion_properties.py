__all__ = (
    "camera_calibration_helper",
)

from . import _engine as engine

from . import ng_prop

if "bpy" in locals():
    import importlib

import bpy

# Common properties for lens distortion coefficients.
_common_coeff_kwargs = {
    "subtype": 'NONE',
    "precision": engine.intern.FLT_DIG,
    "step": 2,
    "soft_min": -5.0,
    "soft_max": 5.0,
    "options": {'HIDDEN'},
}

# Polynomial lens distortion model coefficients
_polynomial_coeff = {}
if engine.WITH_NG_LD_POLYNOMIAL:
    _polynomial_coeff = {
        engine.types.ATTR_POLYNOMIAL_K1: ng_prop.get_double_pointer_property(
            name="K1",
            description="First coefficient of Polynomial radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_POLYNOMIAL_K2: ng_prop.get_double_pointer_property(
            name="K2",
            description="Second coefficient of Polynomial radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_POLYNOMIAL_K3: ng_prop.get_double_pointer_property(
            name="K3",
            description="Third coefficient of Polynomial radial distortion",
            **_common_coeff_kwargs
        ),
    }

# Division lens distortion model coefficients
_division_coeff = {}
if engine.WITH_NG_LD_DIVISION:
    _division_coeff = {
        engine.types.ATTR_DIVISION_K1: ng_prop.get_double_pointer_property(
            name="K1",
            description="First coefficient of Division radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_DIVISION_K2: ng_prop.get_double_pointer_property(
            name="K2",
            description="Second coefficient of Division radial distortion",
            **_common_coeff_kwargs
        ),
    }


# Nuke lens distortion model coefficients
_nuke_coeff = {}
if engine.WITH_NG_LD_NUKE:
    _nuke_coeff = {
        engine.types.ATTR_NUKE_K1: ng_prop.get_double_pointer_property(
            name="K1",
            description="First coefficient of Nuke radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_NUKE_K2: ng_prop.get_double_pointer_property(
            name="K2",
            description="Second coefficient of Nuke radial distortion",
            **_common_coeff_kwargs
        ),
    }

# Brown-Conrady lens distortion model coefficients
_brown_coeff = {}
if engine.WITH_NG_LD_BROWN:
    _brown_coeff = {
        engine.types.ATTR_BROWN_K1: ng_prop.get_double_pointer_property(
            name="K1",
            description="First coefficient of Brown-Conrady radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_K2: ng_prop.get_double_pointer_property(
            name="K2",
            description="Second coefficient of Brown-Conrady radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_K3: ng_prop.get_double_pointer_property(
            name="K3",
            description="Third coefficient of Brown-Conrady radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_K4: ng_prop.get_double_pointer_property(
            name="K4",
            description="Fourth coefficient of Brown-Conrady radial distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_P1: ng_prop.get_double_pointer_property(
            name="P1",
            description="First coefficient of Brown-Conrady tangential distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_P2: ng_prop.get_double_pointer_property(
            name="P2",
            description="Second coefficient of Brown-Conrady tangential distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_P3: ng_prop.get_double_pointer_property(
            name="P3",
            description="Third coefficient of Brown-Conrady tangential distortion",
            **_common_coeff_kwargs
        ),
        engine.types.ATTR_BROWN_P4: ng_prop.get_double_pointer_property(
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


def _focal_length_update(self, _context):
    self.id_data.lens = self.float_value


_focal_length_kwargs = {
    "name": "Focal Length",
    "default": 50.0,
    "min": 1.0,
    "step": 2,
    "unit": 'CAMERA',
    "description": "Camera focal length",
    "update": _focal_length_update,
}


def _ortho_scale_update(self, _context):
    self.id_data.ortho_scale = self.float_value


_ortho_scale_kwargs = {
    "name": "Ortho Scale",
    "default": 6.0,
    "min": 0.001,
    "step": 2,
    "description": "Camera orthographic scale",
    "update": _ortho_scale_update,
}


def _sensor_x_update(self, _context):
    self.id_data.sensor_width = self.float_value


_sensor_x_kwargs = {
    "name": "Sensor",
    "default": 36.0,
    "min": 1.0,
    "max": 100.0,
    "step": 2,
    "description": "CCD sensor width",
    "update": _sensor_x_update
}


def _sensor_y_update(self, _context):
    self.id_data.sensor_height = self.float_value


_sensor_y_kwargs = {
    "name": "Sensor",
    "default": 24.0,
    "min": 1.0,
    "max": 100.0,
    "step": 2,
    "description": "CCD sensor width",
    "update": _sensor_y_update,
}

# Optical center
_principal_point_x_kwargs = {
    "name": "Principal X",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "step": 2,
    "unit": 'CAMERA',
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Deviation of the camera principal point in millimeters by X axis",
}

_principal_point_y_kwargs = {
    "name": "Principal Y",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "step": 2,
    "unit": 'CAMERA',
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Deviation of the camera principal point in millimeters by Y axis",
}

# Skew
_skew_kwargs = {
    "name": "Skew",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "step": 2,
    "subtype": 'FACTOR',
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Skew correction factor",
}

# Affinity
_affinity_kwargs = {
    "name": "Affinity",
    "default": 0.0,
    "soft_min": -1.0,
    "soft_max": 1.0,
    "step": 2,
    "subtype": 'FACTOR',
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
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
    "step": 2,
    "subtype": 'FACTOR',
    "precision": engine.intern.FLT_DIG,
    "step": engine.intern.FLT_DIG,
    "options": {'HIDDEN'},
    "description": "Camera pixel aspect ratio correction factor"
}


# Camera calibration properties
_lens_distortion_prop_dict = {
    engine.types.ATTR_DISTORTION_MODEL: bpy.props.EnumProperty(
        **_distortion_model_kwargs
    ),
    engine.types.ATTR_PANO_TYPE: bpy.props.EnumProperty(
        **_pano_type_kwargs
    ),
    engine.types.ATTR_FOCAL_LENGTH: ng_prop.get_double_pointer_property(
        **_focal_length_kwargs
    ),
    engine.types.ATTR_SENSOR_X: ng_prop.get_double_pointer_property(
        **_sensor_x_kwargs
    ),
    engine.types.ATTR_SENSOR_Y: ng_prop.get_double_pointer_property(
        **_sensor_y_kwargs
    ),
    engine.types.ATTR_ORTHO_SCALE: ng_prop.get_double_pointer_property(
        **_ortho_scale_kwargs
    ),
    engine.types.ATTR_PRINCIPAL_POINT_X: ng_prop.get_double_pointer_property(
        **_principal_point_x_kwargs
    ),
    engine.types.ATTR_PRINCIPAL_POINT_Y: ng_prop.get_double_pointer_property(
        **_principal_point_y_kwargs
    ),
    engine.types.ATTR_SKEW: ng_prop.get_double_pointer_property(
        **_skew_kwargs
    ),
    engine.types.ATTR_AFFINITY: ng_prop.get_double_pointer_property(
        **_affinity_kwargs
    ),
    engine.types.ATTR_PIXEL_ASPECT_RATIO: ng_prop.get_double_pointer_property(
        **_pixel_aspect_ratio
    ),
}


def _update_from_camera_data(self):
    camera = self.id_data

    for attr, value in (
        (engine.types.ATTR_FOCAL_LENGTH, camera.lens),
        (engine.types.ATTR_ORTHO_SCALE, camera.ortho_scale),
        (engine.types.ATTR_SENSOR_X, camera.sensor_width),
        (engine.types.ATTR_SENSOR_Y, camera.sensor_height),
    ):
        setattr(getattr(self, attr), engine.types.NG_PROP_ATTR_FLOAT_VALUE, value)


def camera_calibration_helper():
    """Class decorator function. Updates class annotations by double precision values relative to camera data.
    """

    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        cls.__annotations__.update(_lens_distortion_prop_dict)
        cls.__annotations__.update(_distortion_coefficients_prop_dict)

        if not hasattr(cls, "update_from_camera_data"):
            setattr(cls, "update_from_camera_data", _update_from_camera_data)

        return cls

    return wrapper
