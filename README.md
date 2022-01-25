# Debugging tools

Blender tools to debug issues with Simplygon API Scene.
This is small set of blender utilities that I wrote to 
debug Simplygon issues.

## Requirements
[Simplygon 9.0+](https://www.simplygon.com) (Free Version) 
[Blender 2.8+](https://www.blender.com)

## Development
VStudio Code IDE
Python 3.7+ (Need to match with Blender's python)
VSCode Extension Blender Development (by Jacques Lucke)
Flake8

### Change Log

2021-10-31 (version 0.2.0)
*Added multi file import and reload for OBJ files
*Added panel for importing files
*Initial push to remote

2021-04-15 (version 0.1.2)
*Added handling of opacity/opacity mask
*Bug fixes

2020-09-23 (version 0.1.1)
*Minor adjustments to how mesh is setup
*Bug fixes

2020-08-13 (version 0.1.0)
*Moved to blender add-on
*Implemented SgScene import operator
*Added optional importing of texture, materials, meshes, cameras
*Added material and texture handlers

2020-06-23 (version 0.0.1)
*Added simple script to import visibility camera points into blender as empties