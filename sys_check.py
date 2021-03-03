from .engine import icons
from . import engine

import bpy
import sys


readable_platforms = {
    'aix': "AIX",
    'linux': "Linux",
    'win32': "Windows",
    'cygwin': "Windows/Cygwin",
    'darwin': "macOS"
}

SUPPORTED_PLATFORMS = ("win32",)
SUPPORTED_BLENDER_VERSION = (0, 0, 0)  # bl_info["version"]


def check_blender_version() -> bool:
    """Check Blender version.

    Returns:
        bool: True if Blender version is greater or equal than in `bl_info` .
    """
    bver = bpy.app.version
    for i, sver in enumerate(SUPPORTED_BLENDER_VERSION):
        if bver[i] < sver:
            return False
    return True


def check_sys_platform() -> bool:
    """Check system platform.

    Returns:
        bool: True if current sys.platform in `SUPPORTED_PLATFORMS`.
    """
    return sys.platform in SUPPORTED_PLATFORMS


def check_module_configuration() -> bool:
    """Check C++ module attribute names.

    Returns:
        bool: True if engine.MODULE_ATTR is 'cpp' and has all required build flags.
    """
    return (
        engine.MODULE_ATTR == "cpp"

        and engine.WITH_NG_LD_DIVISION
        and engine.WITH_NG_LD_BROWN

        and engine.WITH_NG_IO
        and engine.WITH_NG_IO_BIND_IMAGES
        and engine.WITH_NG_IO_CSV
        and engine.WITH_NG_IO_XML

        and engine.WITH_NG_IMAGES
        and engine.WITH_NG_SHADERS
        and engine.WITH_NG_ICONS
    )


def draw_check_supported(layout: bpy.types.UILayout) -> bool:
    """Draw information about system platform and Blender version.

    Args:
        layout (bpy.types.UILayout): Current layout.

    Returns:
        bool: True if all checked sucessfull.
    """
    result = True
    if not check_blender_version():
        sbver = SUPPORTED_BLENDER_VERSION
        sbver_str = f"{sbver[0]}.{sbver[1]}.{sbver[2]}"
        layout.label(
            text=f"Minimum required Blender version is {sbver_str}",
            icon_value=icons.get_icon_id("unsupported_bv"))

        result = False

    if not check_sys_platform():
        sp = readable_platforms[sys.platform]

        sp_str = ""
        for i, p in enumerate(SUPPORTED_PLATFORMS):
            if i > 0:
                sp_str += ", "
            sp_str += f"\"{readable_platforms[p]}\""

        system_word = "system is"
        if len(SUPPORTED_PLATFORMS) > 1:
            system_word = "systems are"

        layout.label(
            text=f"OS \"{sp} currently is unsupported. Supported operating "
            f"{system_word} {sp_str}\"",
            icon_value=icons.get_icon_id("unsupported_os")
        )

        result = False

    if not check_module_configuration():
        layout.label(
            text="Internal error: C++ module compiled with wrong flags.",
            icon=icons.get_icon_id("warning")
        )

    return result
