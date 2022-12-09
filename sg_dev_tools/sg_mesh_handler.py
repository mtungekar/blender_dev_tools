import bpy
from simplygon10 import Simplygon
import numpy as np
from .sg_utils import get_unique_ids
from .sg_utils import get_material_name
from .sg_utils import get_polygons_with_material_id
class BlenderMeshHelper:
    
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    def create(context,sg_geom,mesh_name, material_lookup):
        
        num_triangles = sg_geom.GetTriangleCount()
        num_corners = num_triangles * 3
        num_vertices = sg_geom.GetVertexCount()
        coords = sg_geom.GetCoords()
        normals = sg_geom.GetNormals()
        bitangents = sg_geom.GetBitangents(0)
        vertex_ids = sg_geom.GetVertexIds()
        material_ids = sg_geom.GetMaterialIds()
        unique_ids = get_unique_ids(material_ids.GetData())
        new_mesh = bpy.data.meshes.new(mesh_name)
        group_ids = sg_geom.GetGroupIds()

        #for id in unique_ids:
        #    triCount = get_polygons_with_material_id(material_ids.GetData(),id)
        #    print(f'Material:{id} Tris:{triCount} ')
        
        #vertex data
        new_mesh.vertices.add(num_vertices)
        new_mesh.vertices.foreach_set('co', coords.GetData())

        #corner data
        new_mesh.loops.add(num_corners)
        new_mesh.loops.foreach_set('vertex_index',  vertex_ids.GetData())
        new_mesh.loops.foreach_set('normal', normals.GetData())
        
        
        if bitangents is not None:
            new_mesh.loops.foreach_set('bitangent', bitangents.GetData())

        for uv_index in range(0,255):
            if sg_geom.GetTexCoords(uv_index) is not None:
                uv_coord_name = 'Texcoord%03d'%uv_index
                new_uv_layer = new_mesh.uv_layers.new(name=uv_coord_name)
                if new_uv_layer is None:
                    print("UV limit reached")
                    break
                
                new_uv_layer.data.foreach_set('uv',sg_geom.GetTexCoords(uv_index).GetData())

        for color_index in range(0,255):
            if sg_geom.GetColors(color_index) is not None:
                color_set_name = 'Color%03d'%color_index
                new_vc_layer = new_mesh.vertex_colors.new(name=color_set_name)
                if new_vc_layer is None:
                    print("Color limit reached")
                    break
                
                new_vc_layer.data.foreach_set('color',sg_geom.GetColors(color_index).GetData())
        
        new_mesh.polygons.add(num_triangles)
        
        #setup starting corner index for each polygon.
        #loop total is number of corners in the polygon (three for our case)
        loop_starts = np.arange(0, num_corners, step=3)
        loop_totals = np.full(num_triangles, 3)
        
        #setup polygon data loops(corners) and material ids
        new_mesh.polygons.foreach_set('loop_start', loop_starts)
        new_mesh.polygons.foreach_set('loop_total', loop_totals)

        #faces_use_smooth = tuple(bool(context_smooth_group) for (_, _, _, _, context_smooth_group, _, _) in faces)
        #new_mesh.polygons.foreach_set("use_smooth", faces_use_smooth)
        new_mesh.polygons.foreach_set('use_smooth',  [True] * num_triangles)
        
        #hookup materials
        local_to_global = {}
        for matId in unique_ids:
            if matId not in material_lookup:
                blender_material_name = get_material_name(None, matId)
                index = bpy.data.materials.new(blender_material_name)
                local_to_global[index] = matId
                material_lookup[matId] = blender_material_name
                new_mesh.materials.append(bpy.data.materials[blender_material_name])
            else:
                blender_material_name = material_lookup[matId]
                new_mesh.materials.append(bpy.data.materials[blender_material_name])

        #for k,v in local_to_global:

        if not material_ids.IsNull():
            new_mesh.polygons.foreach_set('material_index',material_ids.GetData())
        
        new_mesh.validate(verbose=False)
        new_mesh.update()    
        return new_mesh