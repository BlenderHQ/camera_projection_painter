__all__ = (
    "camera_calibration_helper",
)

from . import _engine as engine

from . import ng_prop

if "bpy" in locals():
    import importlib

import bpy

_camera_data_intrinsics = {}

if engine.WITH_NG_LD_ANY:
    _polynomial_coeff = {}
    _division_coeff = {}
    _nuke_coeff = {}
    _brown_coeff = {}

    _separated_distortion_coeff_prop_dict = {}
    _unified_distortion_coeff_prop_dict = {}

    _internal_distortion_model_items = []
    _rc_distortion_model_items = []
    _ms_distortion_model_items = []

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
    if engine.WITH_NG_LD_POLYNOMIAL:
        _polynomial_coeff.update(
            {
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
        )

    # Division lens distortion model coefficients
    if engine.WITH_NG_LD_DIVISION:
        _division_coeff.update(
            {
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
        )

    # Nuke lens distortion model coefficients
    if engine.WITH_NG_LD_NUKE:
        _nuke_coeff.update(
            {
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
        )

    # Brown-Conrady lens distortion model coefficients
    if engine.WITH_NG_LD_BROWN:
        _brown_coeff.update(
            {
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
        )

    # Add default (No lens distortion items) to distortion model enum properties
    _internal_distortion_model_items.append(
        (str(engine.types.DistortionModel.NONE), "No Lens Distortion", "")
    )

    _rc_distortion_model_items.append(
        (str(engine.types.RC_DistortionModel.perspective), "Perspective", "No lens distortion")
    )

    _ms_distortion_model_items.append(
        (str(engine.types.MS_DistortionModel.NONE), "No lens distortion", "No lens distortion")
    )

    # Extend lens distortion coefficient dictionaries with correspondence to build options:

    if engine.WITH_NG_LD_POLYNOMIAL:
        _internal_distortion_model_items.append(
            (str(engine.types.DistortionModel.POLYNOMIAL), "Polynomial", "Polynomial lens distortion model")
        )
        _separated_distortion_coeff_prop_dict.update(_polynomial_coeff)

    if engine.WITH_NG_LD_DIVISION:
        _internal_distortion_model_items.append(
            (str(engine.types.DistortionModel.DIVISION), "Division", "Division lens distortion model with "
             "two radial lens distortion coefficients")
        )
        _rc_distortion_model_items.append(
            (str(engine.types.RC_DistortionModel.division), "Division", "Division lens distortion model with "
             "one radial lens distortion coefficient")
        )
        _separated_distortion_coeff_prop_dict.update(_division_coeff)

    if engine.WITH_NG_LD_NUKE:
        _internal_distortion_model_items.append(
            (str(engine.types.DistortionModel.NUKE), "Nuke", "Nuke lens distortion model")
        )
        _separated_distortion_coeff_prop_dict.update(_nuke_coeff)

    if engine.WITH_NG_LD_BROWN:
        _internal_distortion_model_items.append(
            (str(engine.types.DistortionModel.BROWN), "Brown", "Brown-Conrady lens distortion model")
        )
        _rc_distortion_model_items.extend(
            [
                (
                    str(engine.types.RC_DistortionModel.brown3),
                    "Brown3",
                    "Brown-Conrady lens distortion model with three radial lens distortion coefficients"
                ),
                (
                    str(engine.types.RC_DistortionModel.brown4),
                    "Brown4",
                    "Brown-Conrady lens distortion model with four radial lens distortion coefficients"
                ),
                (
                    str(engine.types.RC_DistortionModel.brown3t2),
                    "Brown3t2",
                    "Brown-Conrady lens distortion model with three radial and two tangential lens "
                    "distortion coefficients"
                ), (
                    str(engine.types.RC_DistortionModel.brown4t2),
                    "Brown4t2",
                    "Brown-Conrady lens distortion model with four radial and two tangential lens "
                    "distortion coefficients"
                ),
            ]
        )

        _ms_distortion_model_items.append(
            (str(engine.types.MS_DistortionModel.BROWN), "Brown",
             "Brown-Conrady lens distortion model with four radial and four tangential lens "
             "distortion coefficients")
        )

        _separated_distortion_coeff_prop_dict.update(_brown_coeff)

    # Update camera data intrinsics dictionary by separated lens distortion coefficients dictionary
    _camera_data_intrinsics.update(_separated_distortion_coeff_prop_dict)

    # Unified lens distortion coefficients as pure python properties

    def _unified_coeff_get(attr_name: str):

        def wrapper(self):
            dm = engine.types.DistortionModel(getattr(self, engine.types.ATTR_DISTORTION_MODEL))
            if dm == engine.types.DistortionModel.NONE:
                return None

            elif engine.WITH_NG_LD_POLYNOMIAL and dm == getattr(engine.types.DistortionModel, 'POLYNOMIAL'):
                if attr_name == engine.types.ATTR_K1:
                    return getattr(self, engine.types.ATTR_POLYNOMIAL_K1)
                elif attr_name == engine.types.ATTR_K2:
                    return getattr(self, engine.types.ATTR_POLYNOMIAL_K2)
                elif attr_name == engine.types.ATTR_K3:
                    return getattr(self, engine.types.ATTR_POLYNOMIAL_K3)
                else:
                    return None

            elif engine.WITH_NG_LD_DIVISION and dm == getattr(engine.types.DistortionModel, 'DIVISION'):
                if attr_name == engine.types.ATTR_K1:
                    return getattr(self, engine.types.ATTR_DIVISION_K1)
                elif attr_name == engine.types.ATTR_K2:
                    return getattr(self, engine.types.ATTR_DIVISION_K2)
                else:
                    return None

            elif engine.WITH_NG_LD_NUKE and dm == getattr(engine.types.DistortionModel, 'NUKE'):
                if attr_name == engine.types.ATTR_K1:
                    return getattr(self, engine.types.ATTR_NUKE_K1)
                elif attr_name == engine.types.ATTR_K2:
                    return getattr(self, engine.types.ATTR_NUKE_K2)
                else:
                    return None

            elif engine.WITH_NG_LD_BROWN and dm == getattr(engine.types.DistortionModel, 'BROWN'):
                if attr_name == engine.types.ATTR_K1:
                    return getattr(self, engine.types.ATTR_BROWN_K1)
                elif attr_name == engine.types.ATTR_K2:
                    return getattr(self, engine.types.ATTR_BROWN_K2)
                elif attr_name == engine.types.ATTR_K3:
                    return getattr(self, engine.types.ATTR_BROWN_K3)
                elif attr_name == engine.types.ATTR_K4:
                    return getattr(self, engine.types.ATTR_BROWN_K4)
                elif attr_name == engine.types.ATTR_P1:
                    return getattr(self, engine.types.ATTR_BROWN_P1)
                elif attr_name == engine.types.ATTR_P2:
                    return getattr(self, engine.types.ATTR_BROWN_P2)
                elif attr_name == engine.types.ATTR_P3:
                    return getattr(self, engine.types.ATTR_BROWN_P3)
                elif attr_name == engine.types.ATTR_P4:
                    return getattr(self, engine.types.ATTR_BROWN_P4)

            return None

        return wrapper

    _unified_distortion_coeff_prop_dict.update(
        {
            engine.types.ATTR_K1: property(fget=_unified_coeff_get(engine.types.ATTR_K1)),
            engine.types.ATTR_K2: property(fget=_unified_coeff_get(engine.types.ATTR_K2)),
            engine.types.ATTR_K3: property(fget=_unified_coeff_get(engine.types.ATTR_K3)),
            engine.types.ATTR_K4: property(fget=_unified_coeff_get(engine.types.ATTR_K4)),
            engine.types.ATTR_P1: property(fget=_unified_coeff_get(engine.types.ATTR_P1)),
            engine.types.ATTR_P2: property(fget=_unified_coeff_get(engine.types.ATTR_P2)),
            engine.types.ATTR_P3: property(fget=_unified_coeff_get(engine.types.ATTR_P3)),
            engine.types.ATTR_P4: property(fget=_unified_coeff_get(engine.types.ATTR_P4)),

        }
    )

    # Lens distortion model enumerators:

    def _eval_dm(self, required_enum_item: engine.types.DistortionModel) -> None:
        if engine.types.DistortionModel(getattr(self, engine.types.ATTR_DISTORTION_MODEL)) != required_enum_item:
            setattr(self, engine.types.ATTR_DISTORTION_MODEL, str(required_enum_item))

    def _eval_rc_dm(self, required_enum_item: engine.types.RC_DistortionModel, use_corrective_brown_dm: bool) -> None:
        rc_dm = engine.types.RC_DistortionModel(getattr(self, engine.types.ATTR_REALITY_CAPTURE_DISTORTION_MODEL))

        if rc_dm != required_enum_item:
            if use_corrective_brown_dm and rc_dm in (
                engine.types.RC_DistortionModel.brown3,
                engine.types.RC_DistortionModel.brown4,
                engine.types.RC_DistortionModel.brown3t2,
                engine.types.RC_DistortionModel.brown4t2
            ):
                required_enum_item = engine.types.RC_DistortionModel.brown3

                def _is_non_zero_coeff(attr_name: str) -> bool:
                    return (getattr(getattr(self, attr_name), engine.types.NG_PROP_ATTR_FLOAT_VALUE) != 0.0)

                if _is_non_zero_coeff(engine.types.ATTR_BROWN_K4):
                    required_enum_item = engine.types.RC_DistortionModel.brown4

                if _is_non_zero_coeff(engine.types.ATTR_BROWN_P1) or _is_non_zero_coeff(engine.types.ATTR_BROWN_P2):
                    if required_enum_item == engine.types.RC_DistortionModel.brown4:
                        required_enum_item = engine.types.RC_DistortionModel.brown4t2
                    else:
                        required_enum_item = engine.types.RC_DistortionModel.brown3t2
                
            setattr(self, engine.types.ATTR_REALITY_CAPTURE_DISTORTION_MODEL, str(required_enum_item))

    def _eval_ms_dm(self, required_enum_item: engine.types.MS_DistortionModel) -> None:
        ms_dm = engine.types.MS_DistortionModel(getattr(self, engine.types.ATTR_METASHAPE_DISTORTION_MODEL))

        if ms_dm != required_enum_item:
            setattr(self, engine.types.ATTR_METASHAPE_DISTORTION_MODEL, str(required_enum_item))

    _distortion_model_kwargs = {
        "items": _internal_distortion_model_items,
        "default": str(engine.types.DistortionModel(0)),
        "name": "Distortion Model",
        "description": "Internal use only lens distortion model",
    }

    def _rc_distortion_model_update(self, _context):
        rc_dm = engine.types.RC_DistortionModel(getattr(self, engine.types.ATTR_REALITY_CAPTURE_DISTORTION_MODEL))

        if rc_dm == engine.types.RC_DistortionModel.perspective:
            _eval_ms_dm(self, engine.types.MS_DistortionModel.NONE)
            _eval_dm(self, engine.types.DistortionModel.NONE)

        elif rc_dm == engine.types.RC_DistortionModel.division:
            _eval_ms_dm(self, engine.types.MS_DistortionModel.NONE)
            _eval_dm(self, engine.types.DistortionModel.DIVISION)

        elif rc_dm in (
            engine.types.RC_DistortionModel.brown3,
            engine.types.RC_DistortionModel.brown4,
            engine.types.RC_DistortionModel.brown3t2,
            engine.types.RC_DistortionModel.brown4t2
        ):
            _eval_ms_dm(self, engine.types.MS_DistortionModel.BROWN)
            _eval_dm(self, engine.types.DistortionModel.BROWN)

    _rc_distortion_model_kwargs = {
        "items": _rc_distortion_model_items,
        "default": str(engine.types.RC_DistortionModel(0)),
        "name": "Distortion Model",
        "description": "Lens distortion model to be used",
        "update": _rc_distortion_model_update,
    }

    def _ms_distortion_model_update(self, _context):
        dm = engine.types.MS_DistortionModel(getattr(self, engine.types.ATTR_METASHAPE_DISTORTION_MODEL))

        if dm == engine.types.MS_DistortionModel.NONE:
            _eval_rc_dm(self, engine.types.RC_DistortionModel.perspective, use_corrective_brown_dm=False)
            _eval_dm(self, engine.types.DistortionModel.NONE)

        elif dm == engine.types.MS_DistortionModel.BROWN:
            _eval_rc_dm(self, engine.types.RC_DistortionModel.brown3, use_corrective_brown_dm=True)
            _eval_dm(self, engine.types.DistortionModel.BROWN)

    _ms_distortion_model_kwargs = {
        "items": _ms_distortion_model_items,
        "default": str(engine.types.MS_DistortionModel(0)),
        "name": "Distortion Model",
        "description": "Lens distortion model to be used",
        "update": _ms_distortion_model_update,
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
    _camera_data_intrinsics.update(
        {
            # Lens distortion model enum property
            engine.types.ATTR_DISTORTION_MODEL: bpy.props.EnumProperty(
                **_distortion_model_kwargs
            ),
            # Lens distortion model enum property (Reality Capture)
            engine.types.ATTR_REALITY_CAPTURE_DISTORTION_MODEL: bpy.props.EnumProperty(
                **_rc_distortion_model_kwargs
            ),

            # Lens distortion model enum property (Metashape)
            engine.types.ATTR_METASHAPE_DISTORTION_MODEL: bpy.props.EnumProperty(
                **_ms_distortion_model_kwargs
            ),

            # Panoramic type
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
    )


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
    if not engine.WITH_NG_LD_ANY:
        raise AssertionError(
            "C++ module was compiled with configuration that do not support intrinsics data (lens distortions). "
            "Please, recompile module with any of \"WITH_NG_LD_...\" configuration options or request support "
            "from addon developers."
        )

    def wrapper(cls):
        if not hasattr(cls, "__annotations__"):
            setattr(cls, "__annotations__", {})

        cls.__annotations__.update(_camera_data_intrinsics)

        for attr_name, value in _unified_distortion_coeff_prop_dict.items():
            if not hasattr(cls, attr_name):
                setattr(cls, attr_name, value)

        if not hasattr(cls, "update_from_camera_data"):
            setattr(cls, "update_from_camera_data", _update_from_camera_data)

        return cls

    return wrapper
