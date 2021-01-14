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

__all__ = (
    "LD_CalibrationProperties",
    "LD_PolynomialCoefficients",
    "LD_DivisionCoefficients",
    "LD_NukeCoefficients",
    "LD_BrownConradyCoefficients",
    "LD_FULL_camera_properties",
)

from bpy.props import FloatProperty, EnumProperty


PROP_PREC = 4
PROP_STEP = 6


# Camera calibration properties
class LD_CalibrationProperties:
    __slots__ = ()

    # --- Internal acessors ---
    distortion_model: EnumProperty(
        items=[
            ('NONE', "No Lens Distortion", ""),
            #('POLYNOMIAL', "Polynomial", ""),
            ('DIVISION', "Division", ""),
            #('NUKE', "Nuke", ""),
            ('BROWN', "Brown", ""),
        ],
        default='NONE',
        name="Distortion Model"
    )

    def _get_coefficient_eval(self, attr_name: str) -> float:
        if self.distortion_model == 'NONE':
            return 0.0
        return getattr(self, self.distortion_model.lower() + "_" + attr_name, 0.0)

    def _set_coefficient_eval(self, attr_name: str, value: float):
        if self.distortion_model != 'NONE':
            setattr(self, self.distortion_model.lower() + "_" + attr_name, value)

    # Radial coefficients
    @property
    def k1(self):
        return self._get_coefficient_eval("k1")

    @k1.setter
    def k1(self, value):
        self._set_coefficient_eval("k1", value)

    @property
    def k2(self):
        return self._get_coefficient_eval("k2")

    @k2.setter
    def k2(self, value):
        self._set_coefficient_eval("k2", value)

    @property
    def k3(self):
        return self._get_coefficient_eval("k3")

    @k3.setter
    def k3(self, value):
        self._set_coefficient_eval("k3", value)

    @property
    def k4(self):
        return self._get_coefficient_eval("k4")

    @k4.setter
    def k4(self, value):
        self._set_coefficient_eval("k4", value)

    # Tangential coefficients
    @property
    def p1(self):
        return self._get_coefficient_eval("p1")

    @p1.setter
    def p1(self, value):
        self._set_coefficient_eval("p1", value)

    @property
    def p2(self):
        return self._get_coefficient_eval("p2")

    @p2.setter
    def p2(self, value):
        self._set_coefficient_eval("p2", value)

    @property
    def p3(self):
        return self._get_coefficient_eval("p3")

    @p3.setter
    def p3(self, value):
        self._set_coefficient_eval("p3", value)

    @property
    def p4(self):
        return self._get_coefficient_eval("p4")

    @p4.setter
    def p4(self, value):
        self._set_coefficient_eval("p4", value)

    # --- / ---

    # Panoramic camera type
    pano_type: EnumProperty(
        items=[
            ('FISHEYE', "Fisheye", "Fisheye panoramic camera"),
            ('EQUIRECTANGULAR', "Equirectangular", "Equirectangular panoramic camera"),
            ('CYLINDRICAL', "Cylindrical", "Cylindrical panoramic camera"),
        ],
        default='FISHEYE',
        name="Panoramic Type",
        description="Panoramic type used for projection. Lens distortions are supported only by Fisheye cameras."
    )

    # Optical center
    principal_x: FloatProperty(
        name="Principal X", default=0.0, soft_min=-1.0, soft_max=1.0,
        unit='CAMERA',
        precision=PROP_PREC,
        step=PROP_STEP,
        options={'HIDDEN'},
        description="Deviation of the camera principal point in millimeters by X axis"
    )

    principal_y: FloatProperty(
        name="Principal Y", default=0.0, soft_min=-1.0, soft_max=1.0,
        unit='CAMERA',
        precision=PROP_PREC,
        step=PROP_STEP,
        options={'HIDDEN'},
        description="Deviation of the camera principal point in millimeters by Y axis"
    )

    # Skew
    skew: FloatProperty(
        name="Skew", default=0.0, soft_min=-1.0, soft_max=1.0,
        subtype='FACTOR',
        precision=PROP_PREC,
        step=PROP_STEP,
        options={'HIDDEN'},
        description="Skew correction factor"
    )

    # Affinity
    affinity: FloatProperty(
        name="Affinity", default=0.0, soft_min=-1.0, soft_max=1.0,
        subtype='FACTOR',
        precision=PROP_PREC,
        step=PROP_STEP,
        options={'HIDDEN'},
        description="Affinity correction factor"
    )

    # Pixel aspect
    # NOTE: always clamped in ~0.0f...~2.0f in `engine` module, higher or lower values are ignored to support
    # 'Distort' / `Undistort` mode.
    pixel_aspect: FloatProperty(
        name="Pixel Aspect", default=1.0, min=0.01, max=1.99,
        subtype='FACTOR',
        precision=PROP_PREC,
        step=PROP_STEP,
        options={'HIDDEN'},
        description="Camera pixel aspect ratio correction factor"
    )


# Common properties for lens distortion coefficients.
_kwargs_coeff = {
    "subtype": 'NONE',
    "precision": PROP_PREC,
    "step": PROP_STEP,
    "soft_min": -5.0,
    "soft_max": 5.0,
    "options": {'HIDDEN'},
}


# Polynomial
class LD_PolynomialCoefficients:
    __slots__ = ()

    polynomial_k1: FloatProperty(
        name="K1",
        description="First coefficiend of Polynomial radial distortion",
        **_kwargs_coeff
    )

    polynomial_k2: FloatProperty(
        name="K2",
        description="Second coefficiend of Polynomial radial distortion",
        **_kwargs_coeff
    )

    polynomial_k3: FloatProperty(
        name="K3",
        description="Third coefficiend of Polynomial radial distortion",
        **_kwargs_coeff
    )


# Division
class LD_DivisionCoefficients:
    __slots__ = ()

    division_k1: FloatProperty(
        name="K1",
        description="First coefficiend of Division distortion",
        **_kwargs_coeff
    )

    division_k2: FloatProperty(
        name="K2",
        description="Second coefficiend of Division distortion",
        **_kwargs_coeff
    )


# Nuke
class LD_NukeCoefficients:
    __slots__ = ()

    nuke_k1: FloatProperty(
        name="K1",
        description="First coefficiend of Nuke distortion",
        **_kwargs_coeff
    )

    nuke_k2: FloatProperty(
        name="K2",
        description="Second coefficiend of Nuke distortion",
        **_kwargs_coeff
    )


# Brown-Conrady
class LD_BrownConradyCoefficients:
    __slots__ = ()

    brown_k1: FloatProperty(
        name="K1",
        description="First coefficiend of Brown-Conrady radial distortion",
        **_kwargs_coeff
    )

    brown_k2: FloatProperty(
        name="K2",
        description="Second coefficiend of Brown-Conrady radial distortion",
        **_kwargs_coeff
    )

    brown_k3: FloatProperty(
        name="K3",
        description="Third coefficiend of Brown-Conrady radial distortion",
        **_kwargs_coeff
    )

    brown_k4: FloatProperty(
        name="K4",
        description="Fourth coefficiend of Brown-Conrady radial distortion",
        **_kwargs_coeff
    )

    brown_p1: FloatProperty(
        name="P1",
        description="First coefficiend of Brown-Conrady tangential distortion",
        **_kwargs_coeff
    )

    brown_p2: FloatProperty(
        name="P2",
        description="Second coefficiend of Brown-Conrady tangential distortion",
        **_kwargs_coeff
    )

    brown_p3: FloatProperty(
        name="P3",
        description="Third coefficiend of Brown-Conrady tangential distortion",
        **_kwargs_coeff
    )

    brown_p4: FloatProperty(
        name="P4",
        description="Fourth coefficiend of Brown-Conrady tangential distortion",
        **_kwargs_coeff
    )


class LD_FULL_camera_properties(
        LD_CalibrationProperties,
        LD_PolynomialCoefficients,
        LD_DivisionCoefficients,
        LD_NukeCoefficients,
        LD_BrownConradyCoefficients
):
    """
    This class should be used as second base class after `bpy.types.PropertyGroup`
    """
    pass
