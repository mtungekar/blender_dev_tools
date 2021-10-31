# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Simplygon Development Tools",
    "author" : "Mustafa Tungekar",
    "description" : "Development Tools for Simplygon",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "Development > UI",
    "warning" : "",
    "category" : "Development(Simplygon)"
}

import bpy

from .sg_scene_importer import SgImporter_OT_ImportSgScene
from .sg_dev_panel import SgDev_PT_MultiFileImport, SgDev_PT_SgSceneImport
from .sg_multi_file_import import SgImporter_OT_MultiImporter, SgImporter_OT_MultiReload

#list of classes to use
blender_classes = [
    SgImporter_OT_ImportSgScene,
    SgImporter_OT_MultiImporter,
    SgDev_PT_MultiFileImport,
    SgImporter_OT_MultiReload,
    SgDev_PT_SgSceneImport,
]

def initialize():

    #register custom properties on the scene
    bpy.types.Scene.import_folder_path = bpy.props.StringProperty(
        name='Root Folder',
        subtype='DIR_PATH'
    )

    #register custom properties on object
    bpy.types.Object.import_file_path = bpy.props.StringProperty(
        name='Import Filepath',
    )

    #register all classes
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)


def deinitialize():

    #clean up custom properties
    del bpy.types.Scene.import_folder_path
    del bpy.types.Object.import_file_path

    #unregister all classes
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(SgImporter_OT_ImportSgScene.bl_idname, text="Simplygon(.sgscene)")

#helper method to add importer to File>Import> <importer>
def add_importer_to_menu(menu_fn):
    bpy.types.TOPBAR_MT_file_import.append(menu_fn)

#helper method to remove importer from File>Import> <importer>
def remove_importer_to_menu(menu_fn):
    bpy.types.TOPBAR_MT_file_import.remove(menu_fn)

def register():
    initialize()

def unregister():
    deinitialize()
