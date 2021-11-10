import pathlib
import bpy
import bpy_extras
import math
import os
import sys
import glob
import gc
import threading
import numpy as np

from pathlib import Path
from simplygon import simplygon_loader
from simplygon import Simplygon
from . import sg_utils
from .sg_texture_handler import SGTextureHandler
from .sg_material_handler import SGMaterialHandler

from .sg_mesh_handler import BlenderMeshHelper

#global variable
mappings_json = object()

@bpy_extras.io_utils.orientation_helper(axis_forward='X', axis_up='Y')
class SgImporter_OT_ImportSgScene(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "import_scene.sgscene"
    bl_label = "Simplygon(.sgscene)"
    filename_ext = ".sgscene"
    bl_options = {'REGISTER', 'UNDO'}
    

    filter_glob: bpy.props.StringProperty(
        default="*.sgscene",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    import_meshes: bpy.props.BoolProperty(
        name='Import Meshes:',
        description=(
            'Import Meshes.'
        ),
        default=True,
    )

    import_materials: bpy.props.BoolProperty(
        name='Import Materials:',
        description=(
            'Import Materials.'
        ),
        default=True,
    )

    import_textures: bpy.props.BoolProperty(
        name='Import Textures:',
        description=(
            'Import Textures.'
        ),
        default=True,
    )

    import_cameras: bpy.props.BoolProperty(
        name='Cameras',
        description=(
            'Cameras'
        ),
        default=False,
    )

    
    def get_mappings(self,context):
        global mappings_json
        return sg_utils.create_mapping_list(mappings_json)

    material_mapping: bpy.props.EnumProperty(
        name='Material Mapping:',
        items=get_mappings,
        options={'ANIMATABLE'},
        description=(
            'Import Materials.'
        ),
    )

    def __init__(self) -> None:
        global mappings_json
        mappings_json = sg_utils.import_material_mappings('material_mappings.json')
        

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout.prop(self, 'import_meshes')
        layout.prop(self, 'import_materials')
        layout.prop(self, 'import_textures')
        layout.prop(self, 'import_cameras')
        layout.prop(self, 'material_mapping')
        
    def execute(self, context):
        
        import_settings = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "filter_glob",
            ),
        )

        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4()
        import_settings["global_matrix"] = global_matrix
        return self.import_sg_scene(context)

    
   
    def import_sg_scene(self, 
        context, 
        *,
        import_meshes = True,
        import_materials = False, 
        import_textures = False, 
        import_cameras = False):
        
        sg = simplygon_loader.init_simplygon()
        if sg is not None:
            self.read_scene(context,sg)
        return {'FINISHED'}
        
        
    def read_scene(self, context, sg):
        importer = sg.CreateSceneImporter()
        importer.SetImportFilePath( self.filepath )
        if not importer.RunImport():
            raise Exception('Failed to load import')
        sg_scene = importer.GetScene()
        if sg_scene is None:
            raise Exception('No valid scene')
            
        #scene = bpy.context.scene
        bpy.ops.scene.new(type='EMPTY')

        sg_collection = bpy.data.collections.new('simplygon')
        bpy.context.scene.collection.children.link(sg_collection)

        global mappings_json
        #texture lookup
        texture_lookup = {}
        material_lookup = {}
        mapping = sg_utils.get_material_mapping(mappings_json, self.material_mapping)

        if self.import_textures:
            texture_table = sg_scene.GetTextureTable()
            for texture_index in range(texture_table.GetTexturesCount()):
                #print('Texture%d' % texture_index)
                texture = texture_table.GetTexture(texture_index)
                texture_name = texture.GetName();
                blender_texture = SGTextureHandler.create(sg,texture)
                texture_lookup[texture_name] = blender_texture
        
        if self.import_materials:
            material_table = sg_scene.GetMaterialTable()
            for material_index in range(material_table.GetMaterialsCount()):
                #print('Material%d' % material_index)
                material = material_table.GetMaterial(material_index)
                material_name = sg_utils.get_material_name(material, material_index)

                blender_material = SGMaterialHandler.create(sg,material_name,material, texture_lookup,mapping)
                material_lookup[material_index] = material_name
        
        if self.import_meshes:
            selected_set_id = sg_scene.SelectNodes('ISceneMesh')
            selection_set = sg_scene.GetSelectionSetTable().GetSelectionSet(selected_set_id)

            if selection_set.GetItemCount() == 0:
                print("no meshes")
                
            for set_index in range(selection_set.GetItemCount()):
                node_guid = selection_set.GetItem(set_index)
                sg_meshnode = Simplygon.spSceneMesh.SafeCast(sg_scene.GetNodeByGUID(node_guid))
                if sg_meshnode is None:
                    raise Exception('Failed to fetch node')
                    
                sg_geom = sg_meshnode.GetGeometry()
                name = sg_meshnode.GetName()
                if name is None:
                    name = 'Default'
                new_mesh = BlenderMeshHelper.create(context,sg_geom,name,material_lookup)
                new_object = bpy.data.objects.new(name + '_node', new_mesh)
                new_object.scale = (0.001, 0.001, 0.001)
                sg_collection.objects.link(new_object)
                
                
        if self.import_cameras:
            selection_set_id2 = sg_scene.SelectNodes('ISceneCamera')
            selection_set = sg_scene.GetSelectionSetTable().GetSelectionSet(selection_set_id2)
            print("SelectionSetMeshes:%d "%selection_set_id2)
            for set_index in range(selection_set.GetItemCount()):
                node_guid = selection_set.GetItem(set_index)
                print(node_guid)
                temp_node = sg_scene.GetNodeByGUID(node_guid)
                if temp_node is None:
                    raise Exception('Failed to fetch node')
                
                sg_cameranode = Simplygon.spSceneCamera.SafeCast(temp_node)
                if sg_cameranode is None:
                    raise Exception('Failed to cast to camera')
                    
                camera_pos = sg_cameranode.GetCameraPositions()
                for i in range(camera_pos.GetTupleCount()):
                    temp_pos = camera_pos.GetTuple(i)  
                    # curr_obj = bpy.ops.object.empty_add(type='SPHERE', align='WORLD', location=(temp_pos[0],temp_pos[1],temp_pos[2]), scale=(1, 1, 1))
                    vis_camera_obj = bpy.data.objects.new( "VisibilityCamera", None)
                    vis_camera_obj.location=(temp_pos[0]*0.001,temp_pos[1]*0.001,temp_pos[2]*0.001)
                    vis_camera_obj.empty_display_type = 'SPHERE'
                    vis_camera_obj.empty_display_size = 0.01
                    # vis_camera_obj.scale = (0.001, 0.001, 0.001)
                    sg_collection.objects.link(vis_camera_obj)
                    
        
