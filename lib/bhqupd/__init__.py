from __future__ import annotations
if'bpy'in locals():from importlib import reload;reload(_intern);reload(updater)
else:from.import _intern,updater
import bpy
__all__='updater','AddonInfo','has_updates','ui_draw_updates_section','register_addon_update_operators','unregister_addon_update_operators','check_addon_updates','install_addon_update'
has_updates=_intern.has_updates
ui_draw_updates_section=_intern.ui_draw_updates_section
AddonInfo=_intern.AddonInfo
register_addon_update_operators=_intern.register_addon_update_operators
unregister_addon_update_operators=_intern.unregister_addon_update_operators
check_addon_updates=_intern.check_addon_updates
install_addon_update=_intern.install_addon_update