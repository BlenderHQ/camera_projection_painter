# Camera Projection Painter

![Logo](https://user-images.githubusercontent.com/16822993/88917283-2f4d8100-d270-11ea-9f2e-d546d6f3d0b0.png)

-------------
## Preamble

This is a community project aimed at improving Blender's functionality for working with photo scans. The main idea is to correct photoscan textures in areas that cannot be processed in the photoscan software. For example, very small details like eyelashes, eyes. It is not recommended to consider an add-on for full manual texturing of objects. Although possible, it will take much longer.

In terms of workflow, the main feature of the add-on is that there is no need to export a un-distorted image from the software supported by the add-on. The addon is able to make un-distortion directly while drawing. All that is needed is to import the camera data file. More details can be found in the section dedicated to working with specific software.

-------------
## Workfow Automation

 - ### Setup Context
  The operator allows you to carry out all the preparatory steps "in one click". Its description is quite extensive and will be considered for more specific situations.
  
  First of all, it is checked that there is a mesh object in the scene that can be used for drawing. The only requirements for it are that it must be visible (hidden objects will be skipped by the search), must have at least one polygon and at least one UV map. The first 2 requirements are simple, but in the case of a UV map, it makes no sense to automate its creation - it is assumed that the user is using the scene after reconstruction in photogrammetric software, which makes the absence of at least one UV map unacceptable. The object does not have to be selected - if a camera is selected or no object is selected, then the object with the largest number of polygons will be automatically selected.

  If a suitable object is not found, the Autodesk © FBX (*.fbx) file will be imported. This stage involves more than just import. If the path to the dataset is not specified in the dataset settings or the specified path does not exist, then the directory from which the import is made will be set as the dataset directory. The import operator itself uses the standard Blender importer for compatibility purposes, so it may take some time in terms of speed. One of the limitations is also the inability to track the incremental progress of imports. It is also important to mention that the importer will work even if you disabled the standard FBH import addon.
  > For users of the Metashape © software. Previously there was a problem with the orientation of the cameras after importing the FBX file, now the addon takes care of this and after importing the cameras of your scene will be automatically rotated.

  The next step is to bind images to cameras by name and previews generation. For more details see the section on this operator.

  The final stage is tool settings setup. The object mode will be set to "Texture Paint" mode. The tool will set to "Clone Brush". The texture mode will be set to "Single Image". If the scene does not have an active camera, will be set. The brush "Clone Image" will be set equal to the one binded to the active scene camera. The viewport display mode will be set to "Flat".

 - ### Bind Camera Images
 It is necessary to automate the search for the corresponding images for specific cameras.

 The search is performed among image files in the selected dataset directory and also (if the appropriate option is selected) - among images already open in the blend file. The second is useful if the scene is imported immediately along with the images. For files already open in the blend file, the search is also performed by the file name in the image path. That is, the image name can "Image" and the file path contains "C:\DSC0001.jpg" - this will also be searched for.

The search algorithm is quite simple - according to the name of the camera object, camera object data name and the image name and file path image file name. Comparison of names is done without file extension and case insensitivity. The search will skip items whose name contains a slash at the end - they cannot be considered as a file name (that is, the slash should not be in the names of objects, cameras and images, these situations are not supported in terms of performance). More clearly in the table:
 
| Camera name  | Image name     | Сonjunction   |
-------------- | -------------- | ------------- |
DSC09941.JPG   | DSC09941.JPG   | Yes           |
DSC09941.JPG   | DSC09941.jpg   | Yes           |
DSC09941.JPG   | DSC09941.JPEG  | Yes           |
DSC09941.JPG   | DSC09941       | Yes           |
DSC.09941.JPG  | DSC.09941.JPG  | Yes           |
DSC.09941.JPG  | DSC.09941.png  | Yes           |
DSC.099.41.aaa | DSC.099.41.aaa | Yes           |
DSC09941       | DSC09941       | Yes           |
DSC09941       | dsc09941       | Yes           |
DSC09941.JPG   | CSF68851.JPG   | No            |
DSC.JPG        | DSC.09941      | No            |
DSC09941.JPG   | DSC09941.AAA   | No            |
DSC09941.AAA/  | DSC09941.AAA/  | No            |

File extensions are not considered when comparing names, but they do matter. To support names that are separated by a period, files with the following extensions are taken into account:

Is equal to [Blender supported image formats][1]:

  - *.bmp
  - *.sgi, *.rgb, *.bw
  - *.png
  - *.jpg, *.jpeg
  - *.jp2, *.j2c
  - *.tga
  - *.cin, *.dpx
  - *.exr
  - *.hdr
  - *.tif, *.tiff

For user convenience, there is an option "Rename" with which the name of the image, camera object and its data will be set equal to the name of the camera object without the file extension (keeping original case).

Also, for convenience, there is an option "Refresh image previews" - if you select it, higher quality previews will be generated, but for large datasets this may take some time.

-------------
## Preferred Workflow
Preferred workflow refers to a change in the user interface as well as automation, according to the software used to reconstruct the scenes. Currently supported third-party software products are:
- Capturing Reality © Reality Capture ©
- Agisoft © Metashape ©

### Reality Capture

#### Import Camera Data

-------------
## Known limitations when working with the add-on

Supported image file types:
  - jpeg
  - png
  - targa
  - tiff
  - bmp

Supported means that the workflow with them will be the fastest. Working with other types is also possible, however, in this case, high-resolution previews will not be generated and a large number of images must be loaded into memory to determine their size.

[Support on Patreon][2]



[1]: https://docs.blender.org/manual/en/latest/files/media/image_formats.html#image-formats
[2]: https://www.patreon.com/BlenderHQ
