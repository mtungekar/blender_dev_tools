from __future__ import print_function
from os import path
import sys
import json
import bpy
from types import SimpleNamespace
from bpy.types import EnumPropertyItem
import pathlib


def get_import_path(scene) -> pathlib.Path:
    abs_path = bpy.path.abspath(scene.import_folder_path)
    return pathlib.Path(abs_path)

def get_texture_coord_name(uv_index) -> str:
    name = 'Texcoord%03d'%uv_index
    return name

def get_unique_ids(material_ids):
    used = set()
    unique_ids = [id for id in material_ids if id not in used and (used.add(id) or True)]
    return unique_ids

def get_material_name(sg_material, material_index):
    material_name = sg_material.GetName()
    if material_name is None:
        material_name = "Material_"+str(material_index)

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
        materail_mappings.append(('NONE','None','None'))
        return materail_mappings
    
    for i in json_object.mappings:
        materail_mappings.append((i.name.upper(),i.name,i.name))

    return materail_mappings

def get_material_mapping(json_object, name):
     kvp = {}
     for i in json_object.mappings:
         if i.name.upper() == name:
            return i.map.__dict__
