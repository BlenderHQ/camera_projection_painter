![Logo](https://user-images.githubusercontent.com/16822993/88917283-2f4d8100-d270-11ea-9f2e-d546d6f3d0b0.png)
### TODO(ivpe): current file contains todo's (search(TODO))
# Camera Projection Painter

-------------
## Preamble

This is a community project aimed at improving Blender's functionality for working with photo scans. The main idea is to correct photoscan textures in areas that cannot be processed in the photoscan software. For example, very small details like eyelashes, eyes. It is not recommended to consider an add-on for full manual texturing of objects. Although possible, it will take much longer.

In terms of workflow, the main feature of the add-on is that there is no need to export a un-distorted image from the software supported by the add-on. The addon is able to make un-distortion directly while drawing. All that is needed is to import the camera data file. More details can be found in the section dedicated to working with specific software.

-------------
## Workfow Automation

 - ### Setup Context

 TODO(ivpe): update current section to current implementation

  The operator allows you to carry out all the preparatory steps "in one click". Its description is quite extensive and will be considered for more specific situations.
  
  First of all, it is checked that there is a mesh object in the scene that can be used for drawing. The only requirements for it are that it must be visible (hidden objects will be skipped by the search), must have at least one polygon and at least one UV map. The first 2 requirements are simple, but in the case of a UV map, it makes no sense to automate its creation - it is assumed that the user is using the scene after reconstruction in photogrammetric software, which makes the absence of at least one UV map unacceptable. The object does not have to be selected - if a camera is selected or no object is selected, then the object with the largest number of polygons will be automatically selected.

  If a suitable object is not found, the Autodesk © FBX (*.fbx) file will be imported. This stage involves more than just import. If the path to the dataset is not specified in the dataset settings or the specified path does not exist, then the directory from which the import is made will be set as the dataset directory. The import operator itself uses the standard Blender importer for compatibility purposes, so it may take some time in terms of speed. One of the limitations is also the inability to track the incremental progress of imports. It is also important to mention that the importer will work even if you disabled the standard FBH import addon.
  > For users of the Metashape © software. Previously there was a problem with the orientation of the cameras after importing the FBX file, now the addon takes care of this and after importing the cameras of your scene will be automatically rotated.

  The next step is to bind images to cameras by name and previews generation. For more details see the section on this operator.

  The final stage is tool settings setup. The object mode will be set to "Texture Paint" mode. The tool will set to "Clone Brush". The texture mode will be set to "Single Image". If the scene does not have an active camera, will be set. The brush "Clone Image" will be set equal to the one binded to the active scene camera. The viewport display mode will be set to "Flat".

 - ### Name comparison algorithm
This topic is directly related to all IO operators ("Bind Camera Images", "Import/Export Camera Data").

The main goal is to compare different item names. These can be camera object names, their data names, image data block names, image file path file names, camera / image names in camera data files of third-party software, actual file names. The current implementation is unified for all of these items. It can be tricky to understand how this works, but it's important to read it if you run into any problems. A more detailed explanation is described in the section of the respective operator.

In short, each of these names is reduced to a single form for comparison. In any case, the comparison will take place without regard to the registry (uppercase or lowercase characters). The situation with file extensions is a little more complicated. The fact is that the names can contain periods not only before the actual file extension. Therefore, to compare names, only the file extension of the required type will be removed from the actual file name:

### Supported image formats

Is equal to [Blender supported image formats][1]:

  - `*.bmp`
  - `*.sgi`, `*.rgb`, `*.bw`
  - `*.png`
  - `*.jpg`, `*.jpeg`
  - `*.jp2`, `*.j2c`
  - `*.tga`
  - `*.cin`, `*.dpx`
  - `*.exr`
  - `*.hdr`
  - `*.tif`, `*.tiff`
  - `*.psd`: (does not exist in the official documentation, but does exist)

### Supported camera data IO file formats

 - `*.csv`: Reality Capture "Internal/External camera parameters", "Comma-separated Name, X, Y, Z", "Comma-separated Name, X, Y, Z, Heading, Pitch, Roll", "Comma-separated Name, X, Y, Z, Omega, Phi, Kappa"
 - `*.txt`: Metashape "Omega Phi Kappa (\*.txt)"
 - `*.xmp` - (TODO(ivpe): explain this)
 - `*.xml` - (TODO(ivpe): explain this)

So, for example, there is an image named "DSC09941.JPG". Since we compare only lowercase, dsc09941.jpg will be used for comparison, and since ".jpg" is in the list of supported image formats, the file extension will not be used in the comparison. As a result, the name "dsc09941" will be used for comparison. It should be understood that the image file cannot have an extension, for example ".csv". In this case, the name for comparison will remain "dsc09941.csv". At the same time, if we have a camera data file "dsc09941.xmp" (not image file), then its name for comparison will be "dsc09941".

As a result, we can compare the names of the camera data files with the names of the images, and with any other names.


- ### Bind Camera Images 

Since the purpose and implementation of cameras in Blender differs from photogrammetric software, it is necessary to automate the search for appropriate images for specific cameras.

The search is performed among image files in the selected dataset directory as well as images already open in the \*.blend file. The second is useful if the scene is imported immediately along with images. For files already open in a \*.blend file, the search is also performed by the filename in the image path. That is, the name of the image can be "Image", and the file path contains "C:\DSC09941.jpg" - this will also be a searched.

The search algorithm evaluates: the name of the camera object, the name of the data of the camera object and the image name and image file name of the file path. They are all evaluated for comparison as image names. What does it mean? It is undesirable for the names of objects and their data to contain slashes, backslashes - it is obvious that in such a situation they cannot be regarded as names of images. More detailed examples can be found in the table.
 
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
C/DSC09941.AAA | DSC09941.AAA   | No            |

Also, for convenience, there is an option "Refresh Image Previews" - if you select it, higher quality previews will be generated, but for large datasets this may take some time.

-------------
## Preferred Workflow
Preferred workflow refers to a change in the user interface as well as automation, according to the software used to reconstruct the scenes. Currently supported third-party software products are:
- Capturing Reality © Reality Capture ©
- Agisoft © Metashape ©


-------------
## Known limitations when working with the add-on

 - [Blender's packed files][3]: Their use is contrary to the purpose of the add-on - it is assumed that you are using the same image dataset that was used to reconstruct the scene, without unnecessary copying of files.

[Support on Patreon][2]



[1]: https://docs.blender.org/manual/en/latest/files/media/image_formats.html#image-formats
[2]: https://www.patreon.com/BlenderHQ
[3]: https://docs.blender.org/manual/en/latest/files/blend/packed_data.html