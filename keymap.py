from .engine import icons
from . import operators

if "bpy" in locals():
    import importlib
    importlib.reload(operators)

import bpy
import rna_keymap_ui

_keymaps = []

ADDON_KEYMAP = {
    "Image Paint": {
        operators.CPP_OT_image_paint.bl_idname: (
            (
                {"type": 'LEFTMOUSE', "value": 'PRESS', "head": True},
                None
            ),
        ),

        operators.CPP_OT_enable_all_cameras.bl_idname: (
            (
                {"type": 'H', "value": 'PRESS', "alt": True},
                None
            ),
        ),

        "view3d.view_center_pick": (
            (
                {"type": 'SPACE', "value": 'PRESS'},
                None
            ),
        ),
    },
    "Window": {
        operators.CPPDEV_OT_reload.bl_idname: (
            (
                {"type": "F5", "value": 'PRESS', "shift": True, "ctrl": True},
                None
            ),
        ),
    },
}


def get_hotkey_entry_item(
        km: bpy.types.KeyMap,
        kmi_name: str,
        kmi_value: str,
        properties: set) -> bpy.types.KeyMapItem:
    """Hotkey entry item.

    Args:
        km (bpy.types.KeyMap): Current keymap.
        kmi_name (str): Name of searched keymap item.
        kmi_value (str): Value of searched keymap item.
        properties (set): Set of OperatorProperties-like strings.

    Returns:
        bpy.types.KeyMapItem: Found keymap item.
    """
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if properties:
                value = getattr(km.keymap_items[i].properties, properties, None)
                if value == kmi_value:
                    return km_item
            else:
                return km_item


def draw_kmi(
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        km_name: str,
        bl_idname: str
) -> None:
    kc = context.window_manager.keyconfigs.user
    km = kc.keymaps[km_name]
    kmi = get_hotkey_entry_item(km, bl_idname, None, None)
    if kmi:
        layout.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, layout, 0)
    else:
        layout.label(text="Keymap item not registered", icon_value=icons.get_icon_id("warning"))


def register():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    for km_name, km_items in ADDON_KEYMAP.items():
        km = kc.keymaps.new(km_name)

        for idname, data in km_items.items():
            for variance in data:
                key_data, properties = variance

                key_data["idname"] = idname

                kmi = km.keymap_items.new(**key_data)

                if properties:
                    for attr, value in properties.items():
                        if hasattr(kmi.properties, attr):
                            setattr(kmi.properties, attr, value)
                        else:
                            print(attr, value)
                            print(kmi.properties.bl_rna)

                _keymaps.append((km, kmi))


def unregister():
    for km, kmi in _keymaps:
        km.keymap_items.remove(kmi)
    _keymaps.clear()
