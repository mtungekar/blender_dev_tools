from simplygon10 import Simplygon
from simplygon10 import simplygon_loader
from pathlib import Path
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
from .blender_debug import *
from .sg_scene_parser import *
from .sg_utils import SimplygonErrorHandler, sgErrorHandler, CheckLog, validate_sg_scene, setup_blender_pbr


@bpy_extras.io_utils.orientation_helper(axis_forward='X', axis_up='Y')
class SgExporter_OT_ExportSgScene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    # important since its how bpy.ops.import_test.some_data is constructed
    bl_idname = "export_scene.sgscene"
    bl_label = "Simplygon(.sgscene|.sg|.sb)"

    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = '.sgscene'
    filter_glob: bpy.props.StringProperty(
        default='*.sgscene;*.sb;*.sg',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    export_meshes: bpy.props.BoolProperty(
        name='Export Meshes:',
        description=(
            'Export Meshes.'
        ),
        default=True,
    )

    export_materials: bpy.props.BoolProperty(
        name='Export Materials:',
        description=(
            'Export Materials.'
        ),
        default=True,
    )

    export_textures: bpy.props.BoolProperty(
        name='Export Textures:',
        description=(
            'Export Textures.'
        ),
        default=True,
    )

    export_cameras: bpy.props.BoolProperty(
        name='Cameras',
        description=(
            'Cameras'
        ),
        default=False,
    )

    export_armture: bpy.props.BoolProperty(
        name='Exprot Armature',
        description=(
            'Exprot Armature'
        ),
        default=False,
    )

    def __init__(self) -> None:
        pass

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout.prop(self, 'export_meshes')

    def execute(self, context):

        return self.export_sg_scene(context)

    def export_sg_scene(self, context):
        # get scene
        # export meshes
        sg = simplygon_loader.init_simplygon()
        if sg is not None:
            sg.SetErrorHandler(sgErrorHandler)
            self.write_scene(context, sg)
        return {'FINISHED'}

    def write_scene(self, context, sg):
        material_lookup = {}
        sg_scene = sg.CreateScene()

        root_collection = bpy.context.scene.collection
        scene_parser = BlenderSceneParser(
            sg, sg_scene, material_lookup, root_collection)
        mesh_visitor = BlenderMeshVisitor()
        scene_parser.accept(mesh_visitor)

        for k, v in material_lookup.items():
            sg_mat = sg.CreateMaterial()
            # setup blender pbr
            sg_mat.SetName(k)
            setup_blender_pbr(sg, sg_mat)
            sg_scene.GetMaterialTable().AddMaterial(sg_mat)

        if sg_scene is None or sg_scene.IsNull():
            raise Exception("Failed to export")

        id = sg_scene.SelectNodes('SceneMesh')
        print(f'SelectionSet id{id}')

        # validate_sg_scene(sg, sg_scene)
        exporter = sg.CreateSceneExporter()
        exporter.SetScene(sg_scene)
        output_file_path = self.filepath + '.obj'
        exporter.SetExportFilePath(output_file_path)
        CheckLog(sg)
        result = exporter.Run()
        if Simplygon.Failed(result):
            raise Exception("Failed to export")
        CheckLog(sg)
        pass
