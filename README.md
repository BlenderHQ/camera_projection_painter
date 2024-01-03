# Camera Projection Painter

View in
[🇺🇸](./README.md),
[🇺🇦](./README_uk.md)
.

- [Camera Projection Painter](#camera-projection-painter)
  - [About](#about)
  - [How To Use the Addon](#how-to-use-the-addon)
  - [Release Notes](#release-notes)
  - [License](#license)


## About

Add-on for Blender for working with photo scans and photogrammetry. It allows you to paint over the texture of the reconstructed object with a clone brush from the original photo.

![qs-complete](https://github.com/BlenderHQ/camera_projection_painter/assets/3924000/e8fc7191-04cb-4e9c-86f2-f8d309873ed9)

## How To Use the Addon

To get started, you need to export data from your photogrammetry software. Next, run the "Setup Context" operator and follow a few simple steps to import data. After completing the setup, you can adjust the texture and camera data. That's in short. More detailed information can be found in the tooltips for operators and properties, and even more detailed information can be found on the [project documentation page](https://docs.camera-painter.com).

If there are any issues with the add-on, or if you have suggestions for the development of the project, we will be happy to [read them on GitHub](https://github.com/BlenderHQ/camera_projection_painter/issues). The project was created and maintained with the support of patrons on our [Patreon](https://patreon.com/BlenderHQ).


## Release Notes

<details open><summary>
Version 4.0.0.
</summary>

* Fixed updates system. A separate repository and a separate testing system have been created for the new one.

* Fixed the logging system to the file that held the logging file open while removing the addon (thank you Vlad, noticed it on stream)

* A system is added to separate a particular region for work. It allows you to highlight the area of the large scene, for which the preview of the images will be generated, the cameras and the mesh projection will be visible. By default after the context is configured, the region will be set to the bounds of the current scene, taking into account the boundaries of the object and the position of the cameras. The appropriate operator to update the region has also been added.

------------------------------------------------------------------------------------------------------------------------

> This update breaks backward compatibility with `*.blend` files that have been saved using previous versions of the addon.Therefore, please test the addon with new files only.

* The method of storing double precision values has been changed - this accelerates the operation of import/export operations and transformation of the scene. A separate library was created for this purpose [bhqdbl](https://github.com/ivan-perevala/bhqdbl).

  * The precision display option was removed. Now the properties can only be edited with single precision. This does not affect the accuracy of the data that has been imported and which remained unchanged - they can be exported as is.

  * Camera transformation converters have been removed. This is a necessary change, because as it turned out, they are not used in practice and only create unnecessary ballast to maintain the addon.

  * Imports of the properties of cameras that do not relate to the addon work itself have been removed. They are now only available as export options. In the current version, this applies to exports of Reality Capture XMP: export overwrite flags also have been removed, since there is nothing more to overwrite.Please take this change as necessary, as it is an important step for implementing the import/export of other file formats that contain much more third-party data.

  * The unit and functional tests system supplemented with functional tests of `bhqdbl` library. 

* Updated import and export of camera data:
  * Import of cameras now first imports all the data, and only if the import has been successful, transferred data to the Blender data-blocks.
  * Import-export system is unified. First, the input parameters (directory, the file list, their names, etc.) are evaluated, then import itself and then reports. This is an important step for building functional tests.

* Updated image bind system: now search finds all the files supported by OpenImageIO.

* Updated user interface.
  * Now the operators in the Dataset panel are placed in the same order in which they are called during [setting up the context](https://docs.camera-painter.com/en/double-precision-library/ops/setup-context.html).
  * The calibration and lens distortion panels are now visible in the absence of the image binded to the camera. Obviously in this case in pixel values will be displayed zeros.
  * The documentation opening system has been updated. Documentation for a particular branch of the addon, not just a specific language will now be opened.
  * When importing images, the filter is turned on to show images by default.

* Maintenance: The incompatibility with the following versions of Python is eliminated. This applies to [changes in Python language syntax](https://docs.python.org/3/whatsnew/3.11.html#language-builtins).

</details>

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue)](https://www.gnu.org/licenses/gpl-3.0)

Copyright © 2020 Vladlen Kuzmin (ssh4), Ivan Perevala (ivpe).

<details><summary>
GNU GPL v3 License.
</summary>

```
Camera Projection Painter addon.
Copyright (C) 2020 Vladlen Kuzmin (ssh4), Ivan Perevala (ivpe)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

</details>
