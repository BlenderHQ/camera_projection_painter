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


def get_double_pointer_property(name: str, indices=(-1, -1), **kwargs):
    """Generate and register dynamic property type which contains float, double as string and exact double as
    string representation of floating point value. "Exact" value means imported 16 digits value from third-party
    software.

    Registered property group contains additional API:
        prec_icon_id (property): integer icon id to be used to show precision info in the UI.
        draw (method): Should be used to draw property in the UI with given text.
        draw_info (method): Should be used to draw double precision representation in the UI.

    Args:
        name (str): Regular property name.
        indices (tuple): Optional indices [i, j] for matrix element values.
        **kwargs: Keyword arguments should be the same as for `bpy.props.FloatProperty`.
    Returns:
        bpy.props.PointerProperty: Registered property.
    """

    # Set display precision to IEEE-754 standard.
    kwargs["precision"] = engine.intern.FLT_DIG

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
        engine.types.ng_prop_float_value_update(self)

    def _exact_double_value_update(self, _context):
        setattr(
            self,
            engine.types.NG_PROP_ATTR_FLOAT_VALUE,
            engine.intern.str_to_floating_point(
                getattr(
                    self,
                    engine.types.NG_PROP_ATTR_EXACT_DOUBLE_AS_STR
                )
            )
        )
        setattr(
            self,
            engine.types.NG_PROP_ATTR_DOUBLE_AS_STR,
            getattr(
                self,
                engine.types.NG_PROP_ATTR_EXACT_DOUBLE_AS_STR
            )
        )

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
        double_as_str = getattr(self, engine.types.NG_PROP_ATTR_DOUBLE_AS_STR)
        exact_double_as_str = getattr(self, engine.types.NG_PROP_ATTR_EXACT_DOUBLE_AS_STR)
        if not exact_double_as_str:
            return icons.get_icon_id("white_dot")
        elif double_as_str == exact_double_as_str:
            return icons.get_icon_id("green_dot")
        else:
            return icons.get_icon_id("yellow_dot")

    def _get_double_values_text(self):
        dbl_text = "Missing"
        double_as_str = getattr(self, engine.types.NG_PROP_ATTR_DOUBLE_AS_STR)
        if double_as_str:
            dbl_text = double_as_str

        exact_text = "Missing"
        exact_double_as_str = getattr(self, engine.types.NG_PROP_ATTR_EXACT_DOUBLE_AS_STR)
        if exact_double_as_str:
            exact_text = exact_double_as_str

        return dbl_text, exact_text

    def _draw_method(self, layout: bpy.types.UILayout, text=None) -> None:
        """Draw single precision value in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """
        row = layout.row(align=True)
        if text is not None:
            row.prop(self, engine.types.NG_PROP_ATTR_FLOAT_VALUE, text=text)
        else:
            row.prop(self, engine.types.NG_PROP_ATTR_FLOAT_VALUE)

        row.separator()

        dbl_text, exact_text = _get_double_values_text(self)
        props = row.operator(operator=NG_OT_ng_prop_info.bl_idname, icon_value=self.prec_icon_id, text="", emboss=False)
        props.desk = f"\n\u2022 Double precision:                {dbl_text}\n" \
            f"\u2022 Imported double precision: {exact_text}"

    def _draw_info_method(self, layout: bpy.types.UILayout) -> None:
        """Draw double precision value info in the UI.

        Args:
            layout (bpy.types.UILayout): Current layout.
        """
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        dbl_text, exact_text = _get_double_values_text(self)
        props = row.operator(
            operator=NG_OT_ng_prop_info.bl_idname,
            icon_value=self.prec_icon_id,
            text=f"{dbl_text}",
            emboss=False
        )
        props.desk = f"\u2022 Imported double precision: {exact_text}"

    annotations_dict = {
        engine.types.NG_PROP_ATTR_PREV_FLOAT_VALUE: bpy.props.FloatProperty(
            **kwargs
        ),
        engine.types.NG_PROP_ATTR_FLOAT_VALUE: bpy.props.FloatProperty(
            name=name,
            update=_float_value_update,
            **kwargs
        ),
        engine.types.NG_PROP_ATTR_DOUBLE_AS_STR: bpy.props.StringProperty(
            maxlen=engine.intern.DBL_DIG * 2,
            default=engine.intern.floating_point_to_str(kwargs_default),
            options={'HIDDEN'},
        ),
        engine.types.NG_PROP_ATTR_EXACT_DOUBLE_AS_STR: bpy.props.StringProperty(
            maxlen=engine.intern.DBL_DIG * 2,
            update=_exact_double_value_update,
            options={'HIDDEN'},
        ),
    }

    if (indices[0] != -1 and indices[1] != -1):
        annotations_dict["indices"] = bpy.props.IntVectorProperty(
            default=indices,
            size=2,
            options={'HIDDEN', 'SKIP_SAVE'}
        )

    # Create dynamic class to store property.
    double_property_group = type(
        "ng_prop_" + name.replace(" ", "_").lower(),
        (
            bpy.types.PropertyGroup,
        ),
        {
            "__slots__": tuple(),
            "__annotations__": annotations_dict,
            "prec_icon_id": property(fget=_prec_icon_id_getter),
            "draw": _draw_method,
            "draw_info": _draw_info_method,
        }
    )

    _reg(double_property_group)
    _reg(NG_OT_ng_prop_info)

    return bpy.props.PointerProperty(type=double_property_group)
