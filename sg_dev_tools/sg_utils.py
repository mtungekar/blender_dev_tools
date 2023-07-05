from __future__ import print_function
from os import path
import sys
import json
import bpy
from types import SimpleNamespace
from bpy.types import EnumPropertyItem
import pathlib
from simplygon10 import Simplygon
from simplygon10 import simplygon_loader


class SimplygonErrorHandler(Simplygon.ErrorHandler):
    def HandleError(self, object: Simplygon.spObject, interfaceName: str, methodName: str, errorType: int, errorText: str):
        print('Error (%s:%s): %s' % (interfaceName, methodName, errorText))


sgErrorHandler = SimplygonErrorHandler()


def CheckLog(sg: Simplygon.ISimplygon):
    # Check if any errors occurred.
    hasErrors = sg.ErrorOccurred()
    if hasErrors:
        errors = sg.CreateStringArray()
        sg.GetErrorMessages(errors)
        errorCount = errors.GetItemCount()
        if errorCount > 0:
            print('CheckLog: Errors:')
            for errorIndex in range(errorCount):
                errorString = errors.GetItem(errorIndex)
                print(errorString)
            sg.ClearErrorMessages()
    else:
        print('CheckLog: No errors.')

    # Check if any warnings occurred.
    hasWarnings = sg.WarningOccurred()
    if hasWarnings:
        warnings = sg.CreateStringArray()
        sg.GetWarningMessages(warnings)
        warningCount = warnings.GetItemCount()
        if warningCount > 0:
            print('CheckLog: Warnings:')
            for warningIndex in range(warningCount):
                warningString = warnings.GetItem(warningIndex)
                print(warningString)
            sg.ClearWarningMessages()
    else:
        print('CheckLog: No warnings.')

    sg.ClearErrorMessages()
    sg.ClearWarningMessages()


def get_import_path(scene) -> pathlib.Path:
    abs_path = bpy.path.abspath(scene.import_folder_path)
    return pathlib.Path(abs_path)


def get_texture_coord_name(uv_index) -> str:
    name = 'Texcoord%03d' % uv_index
    return name


def get_polygons_with_material_id(material_ids, id):
    result = 0
    for x in material_ids:
        if x == id:
            result += 1
    return result


def get_unique_ids(material_ids):
    used = set()
    unique_ids = [id for id in material_ids if id not in used and (
        used.add(id) or True)]
    return unique_ids


def get_material_name(sg_material, material_index):
    material_name = "Material_"+str(material_index)
    if sg_material is not None:
        material_name = sg_material.GetName()
    return material_name


def import_material_mappings(file_path):
    fullpath = pathlib.Path(__file__).parent / pathlib.Path(file_path)
    if not fullpath.is_file():
        raise RuntimeError(f'mappings json not found{fullpath}')
    with open(fullpath, 'r') as mapping_json:
        data = mapping_json.read()
    return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


def create_mapping_list(json_object):
    materail_mappings = []

    if json_object is None:
        materail_mappings.append(('NONE', 'None', 'None'))
        return materail_mappings

    for i in json_object.mappings:
        materail_mappings.append((i.name.upper(), i.name, i.name))

    return materail_mappings


def get_material_mapping(json_object, name):
    kvp = {}
    for i in json_object.mappings:
        if i.name.upper() == name:
            return i.map.__dict__


def get_unique_materials(materials):
    used = set()
    unique_mats = [mat for mat in materials if mat not in used and (
        used.add(mat) or True)]
    return unique_mats


def validate_sg_scene(sg, sg_scene):
    validator = sg.CreateSceneValidator()
    # validator.SetCheckDegenerateFaceIndices(True)
    # validator.SetCheckMaterials(True)
    # validator.SetCheckMeshes(True)
    # validator.SetCheckZeroAreaFaces(True)
    validator.ValidateScene(sg_scene)
    num_errors = validator.GetErrorCount()

    for i in range(num_errors):
        err_string = validator.GetErrorString(i)
        print(err_string)


def setup_blender_pbr(sg, sg_material):
    colorNode = sg.CreateShadingColorNode()
    colorNode.SetColor(0.18, 0.18, 0.18, 1.0)
    sg_material.AddMaterialChannel('Base Color')
    sg_material.AddMaterialChannel('Metallic')
    sg_material.AddMaterialChannel('Specular')
    sg_material.AddMaterialChannel('Roughness')
    sg_material.AddMaterialChannel('Normal')
    sg_material.AddMaterialChannel('Alpha')
    sg_material.AddMaterialChannel('Emission')
    sg_material.SetOpacityChannel('Alpha')

    sg_material.SetShadingNetwork('Base Color', colorNode)
    sg_material.SetShadingNetwork('Metallic', colorNode)
    sg_material.SetShadingNetwork('Specular', colorNode)
    sg_material.SetShadingNetwork('Roughness', colorNode)
    sg_material.SetShadingNetwork('Normal', colorNode)
    sg_material.SetShadingNetwork('Alpha', colorNode)
    sg_material.SetShadingNetwork('Emission', colorNode)
