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

if "bpy" in locals():
    import importlib

    # Set debug info printing to true in case of package reloading
    intern.set_debug_info(True)

    importlib.reload(ng_prop)

    if WITH_NG_IO:
        importlib.reload(camera_data_io_properties)

    if WITH_NG_LD_ANY:
        importlib.reload(camera_data_extrinsics_properties)

    importlib.reload(camera_data_intrinsics_properties)

try:
    import bpy
except ImportError as err:
    raise ImportError("This module should be imported only from inside Blender.")

from ._engine import *

from . import ng_prop

if WITH_NG_IO:
    from . import camera_data_io_properties

if WITH_NG_LD_ANY:
    from . import camera_data_intrinsics_properties

from . import camera_data_extrinsics_properties
