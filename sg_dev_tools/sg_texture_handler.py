import pathlib
import bpy
import tempfile
import os
from os.path import dirname, join, isfile, basename, normpath
from simplygon10 import Simplygon


class SGTextureHandler:
    """Texture handler"""
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)
    
    
    def create_temporary_image(name, path) -> bpy.types.Image:
        image = bpy.data.images.new(name,128,128)
        image.filepath = path
        image.source = 'FILE'
        return image

    def create(sg,texture) -> bpy.types.Image:
        image_data = texture.GetImageData()
        image_name = texture.GetName()
        texture_path = texture.GetFilePath()
        temp_dir = None
        is_temp_image = False
        if image_name is None:
            raise RuntimeError("No valid texture name found on Simplygon Texture Object.")

        if image_data is not None:
            texture.ExportImageData()
            texture_path = texture.GetFilePath()
        
        fileExt = pathlib.Path(texture_path).suffix

        if fileExt == '':
            texture_path = texture_path+'.png'

        num_images = len(bpy.data.images)

        try:
            blender_image = bpy.data.images.load(os.path.abspath(texture_path), check_existing=temp_dir is None)
        except RuntimeError:
            print('failed to load image creating temporary')
            blender_image = create_temporary_image(image_name,texture_path)
            is_temp_image = True
        
        blender_image.alpha_mode = 'NONE'

        # If created a new image
        if len(bpy.data.images) != num_images:
            blender_image.name = image_name

        return blender_image   





