from . import _engine as engine
from ._engine import icons

__all__ = (
    "get_double_pointer_property",
)

if "bpy" in locals():
    for _ in range(len(_registered_classes)):
        bpy.utils.unregister_class(_registered_classes.pop())

import bpy

_registered_classes = []


def _reg(cls) -> None:
    if cls not in _registered_classes:
        bpy.utils.register_class(cls)
        _registered_classes.append(cls)


_double_property_additional_description = "\u2022 The current value is displayed in single precision.\n" \
    "Actual value may be different.\n" \
    "Double precision value can be showed in popup (dot right).\n" \
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
    # `get` and `set` keyword arguments will raise an error.
    kwargs_update_func = None
    if "update" in kwargs:
        kwargs_update_func = kwargs["update"]
        del kwargs["update"]

    if "set" in kwargs or "set" in kwargs:
        engine.intern.err_log("`ng_prop_` do not support `get` and `set` arguments, use `update` instead.\n")
        raise AttributeError()

    def _float_value_update(self, context):
        if kwargs_update_func is not None:
            kwargs_update_func(self, context)
        engine.types.evaluate_ng_cpp_prop_as_string(self)
        self.prev_float_value = self.float_value

    def _exact_double_value_update(self, _context):
        self.float_value = engine.types.str_to_floating_point(self.exact_double_as_str)
        self.double_as_str = self.exact_double_as_str

    # Default value
    kwargs_default = 0.0
    if "default" in kwargs:
        kwargs_default = kwargs["default"]

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

    def _draw_method(self, layout: bpy.types.UILayout, text=None) -> None:
        """Draw single precision value in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """
        row = layout.row(align=True)
        if text is not None:
            row.prop(self, "float_value", text=text)
        else:
            row.prop(self, "float_value")

        dbl_text = "Missing"
        if self.double_as_str:
            dbl_text = self.double_as_str

        exact_text = "Missing"
        if self.exact_double_as_str:
            exact_text = self.exact_double_as_str

        row.separator()
        props = row.operator(operator=NG_OT_ng_prop_info.bl_idname, icon_value=self.prec_icon_id, text="", emboss=False)
        props.desk = f"\n\u2022 Double precision:                {dbl_text}\n" \
            f"\u2022 Imported double precision: {exact_text}"

    def _draw_info_method(self, layout: bpy.types.UILayout) -> None:
        """Draw double precision value info in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """
        layout.label(text=f"{self.double_as_str}", icon_value=self.prec_icon_id)

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

    _reg(double_property_group)
    _reg(NG_OT_ng_prop_info)

    return bpy.props.PointerProperty(type=double_property_group)
