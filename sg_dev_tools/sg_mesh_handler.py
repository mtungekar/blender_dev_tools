import bpy
from simplygon10 import Simplygon
import numpy as np
from .sg_utils import get_unique_ids, get_unique_materials, get_material_name
from .blender_debug import *


class BlenderMeshHelper:

    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    def create(context, sg_geom, mesh_name, material_lookup):

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

        # for id in unique_ids:
        #    triCount = get_polygons_with_material_id(material_ids.GetData(),id)
        #    print(f'Material:{id} Tris:{triCount} ')

        # vertex data
        new_mesh.vertices.add(num_vertices)
        new_mesh.vertices.foreach_set('co', coords.GetData())

        # corner data
        new_mesh.loops.add(num_corners)
        new_mesh.loops.foreach_set('vertex_index',  vertex_ids.GetData())
        new_mesh.loops.foreach_set('normal', normals.GetData())

        if bitangents is not None:
            new_mesh.loops.foreach_set('bitangent', bitangents.GetData())

        for uv_index in range(0, 255):
            if sg_geom.GetTexCoords(uv_index) is not None:
                uv_coord_name = 'Texcoord%03d' % uv_index
                new_uv_layer = new_mesh.uv_layers.new(name=uv_coord_name)
                if new_uv_layer is None:
                    print("UV limit reached")
                    break

                new_uv_layer.data.foreach_set(
                    'uv', sg_geom.GetTexCoords(uv_index).GetData())

        for color_index in range(0, 255):
            if sg_geom.GetColors(color_index) is not None:
                color_set_name = 'Color%03d' % color_index
                new_vc_layer = new_mesh.vertex_colors.new(name=color_set_name)
                if new_vc_layer is None:
                    print("Color limit reached")
                    break

                new_vc_layer.data.foreach_set(
                    'color', sg_geom.GetColors(color_index).GetData())

        new_mesh.polygons.add(num_triangles)

        # setup starting corner index for each polygon.
        # loop total is number of corners in the polygon (three for our case)
        loop_starts = np.arange(0, num_corners, step=3)
        loop_totals = np.full(num_triangles, 3)

        # setup polygon data loops(corners) and material ids
        new_mesh.polygons.foreach_set('loop_start', loop_starts)
        new_mesh.polygons.foreach_set('loop_total', loop_totals)

        # faces_use_smooth = tuple(bool(context_smooth_group) for (_, _, _, _, context_smooth_group, _, _) in faces)
        # new_mesh.polygons.foreach_set("use_smooth", faces_use_smooth)
        new_mesh.polygons.foreach_set('use_smooth',  [True] * num_triangles)

        # hookup materials
        local_to_global = {}
        for matId in unique_ids:
            if matId not in material_lookup:
                blender_material_name = get_material_name(None, matId)
                index = bpy.data.materials.new(blender_material_name)
                local_to_global[index] = matId
                material_lookup[matId] = blender_material_name
                new_mesh.materials.append(
                    bpy.data.materials[blender_material_name])
            else:
                blender_material_name = material_lookup[matId]
                new_mesh.materials.append(
                    bpy.data.materials[blender_material_name])

        # for k,v in local_to_global:

        if not material_ids.IsNull():
            new_mesh.polygons.foreach_set(
                'material_index', material_ids.GetData())

        new_mesh.validate(verbose=False)
        new_mesh.update()
        return new_mesh

    def get_sg_mesh(sg, obj):
        blender_mesh = bpy.data.meshes[obj.name]
        if blender_mesh is None:
            print(f'Mesh is none')

        num_vertices = len(blender_mesh.vertices)
        num_polygons = len(blender_mesh.polygons)
        num_loops = len(blender_mesh.loops)
        loops_per_polygon = num_loops / num_polygons
        is_quad = True if loops_per_polygon > 3 else False

        if is_quad:
            blender_mesh.create_normals_split()
            blender_mesh.calc_normals_split()
            blender_mesh.calc_loop_triangles()

        num_triangles = len(blender_mesh.loop_triangles)
        num_triangle_corners = num_triangles * 3

        print(
            f'MeshName={blender_mesh.name} Vertices={num_vertices} Polygons={num_polygons} TotalLoops={num_loops} LoopsPerPolygon={loops_per_polygon} Triangle={num_triangles} ')

        sg_mesh = sg.CreateSceneMesh()
        sg_mesh.SetName(blender_mesh.name)

        sg_geom = sg.CreateGeometryData()
        sg_geom.SetVertexCount(num_vertices)
        sg_geom.SetTriangleCount(num_triangles)

        has_normals = True  # blender_mesh.loops.find('normal')
        has_uvs = True
        has_tangents = False

        # print_mesh_info(blender_mesh)

        # vertex data
        sg_coords = sg_geom.GetCoords()
        vertices_data = np.empty(num_vertices*3, dtype=np.float32)
        blender_mesh.vertices.foreach_get('co', vertices_data)
        sg_coords.SetData(vertices_data.tolist(), num_vertices*3)

        # corner data
        sg_vertex_ids = sg_geom.GetVertexIds()
        vertex_ids = np.empty(num_triangle_corners, dtype=np.int32)
        blender_mesh.loop_triangles.foreach_get('vertices', vertex_ids)
        sg_vertex_ids.SetData(vertex_ids.tolist(), num_triangle_corners)

        polyg_index = np.empty(num_triangle_corners, dtype=np.int32)
        blender_mesh.loop_triangles.foreach_get('polygon_index', polyg_index)

        mesh_loops = np.empty(num_triangle_corners, dtype=np.int32)
        blender_mesh.loop_triangles.foreach_get('loops', mesh_loops)
        # sg_vertex_ids.SetData(mesh_loops.tolist(), num_triangle_corners)

        if has_normals:
            sg_geom.AddNormals()
            normals = sg_geom.GetNormals()
            print(f'tc {num_triangle_corners} tc {normals.GetTupleCount()}')
            split_normals = np.empty(num_triangle_corners*3, dtype=np.float32)
            blender_mesh.loop_triangles.foreach_get(
                'split_normals', split_normals)
            normals.SetData(split_normals.tolist(), num_triangles*3*3)

        uv_level = 0
        uv_names = get_uv_map_names(blender_mesh)
        if has_uvs:
            for uv_name in uv_names:
                sg_geom.AddNamedTexCoords(uv_name)
                uv_data = np.zeros(num_triangle_corners*2, dtype=np.float32)
                sg_texcoord = sg_geom.GetTexCoords(uv_level)
                blender_mesh.calc_tangents(uvmap=uv_name)
                # uvs
                uv_index = 0
                for corner_index in mesh_loops:
                    uv_layer = blender_mesh.uv_layers[uv_name].uv[corner_index]
                    uv_data[uv_index] = uv_layer.vector[0]
                    uv_data[uv_index+1] = uv_layer.vector[1]
                    uv_index += 2
                # blender_mesh.uv_layers[uv_name].uv.foreach_get(
                    # 'vector', uv_data)
                sg_texcoord.SetData(uv_data.tolist(), num_triangle_corners*2)
                # tangents
                if has_tangents:
                    sg_geom.AddTangents(uv_level)
                    sg_tangents = sg_geom.GetTangents(uv_level)
                    sg_bitangents = sg_geom.GetBitangents(uv_level)
                    tangents_data = np.zeros(
                        num_triangle_corners*3, dtype=np.float32)
                    bitangents_data = np.zeros(
                        num_triangle_corners*3, dtype=np.float32)
                    data_index = 0
                    for corner_index in mesh_loops:
                        tangent = blender_mesh.loops[corner_index].tangent
                        bitangent = blender_mesh.loops[corner_index].bitangent
                        tangents_data[data_index] = tangent[0]
                        tangents_data[data_index+1] = tangent[1]
                        tangents_data[data_index+2] = tangent[2]
                        bitangents_data[data_index] = bitangent[0]
                        bitangents_data[data_index+1] = bitangent[1]
                        bitangents_data[data_index+2] = bitangent[2]
                        uv_index += 3
                    # blender_mesh.loops.foreach_get('tangent', tangents_data)
                    sg_tangents.SetData(tangents_data.tolist(),
                                        num_triangle_corners*3)
                    # bitangents
                    # blender_mesh.loops.foreach_get('bitangent', tangents_data)
                    sg_bitangents.SetData(bitangents_data.tolist(),
                                          num_triangle_corners*3)
                uv_level += 1

        # triangle data
        sg_geom.AddMaterialIds()
        sg_material_ids = sg_geom.GetMaterialIds()
        material_ids = np.zeros(num_triangles, dtype=np.int32)
        material_ids_temp = np.zeros(2, dtype=np.int32)

        blender_mesh.loop_triangles.foreach_set(
            'material_index', material_ids)
        sg_material_ids.SetData(material_ids.tolist(), num_triangles)

        # quad data
        sg_geom.AddQuadFlags()
        sg_quad_flags = sg_geom.GetQuadFlags()
        quad_data = np.empty(num_triangles, dtype=np.int32)
        # blender_mesh.loop_triangle_polygons.foreach_set('value', quad_data)
        tri_index = 0
        while tri_index < num_triangles:
            quad_indexA = blender_mesh.loop_triangle_polygons[tri_index].value
            if tri_index+1 < num_triangles:
                quad_indexB = blender_mesh.loop_triangle_polygons[tri_index+1].value
                if quad_indexA == quad_indexB:
                    sg_quad_flags.SetItem(
                        tri_index, Simplygon.SG_QUADFLAG_FIRST)
                    sg_quad_flags.SetItem(
                        tri_index+1, Simplygon.SG_QUADFLAG_SECOND)
                    tri_index += 2
                else:
                    sg_quad_flags.SetItem(
                        tri_index, Simplygon.SG_QUADFLAG_TRIANGLE)
                    tri_index += 1
            else:
                sg_quad_flags.SetItem(
                    tri_index, Simplygon.SG_QUADFLAG_TRIANGLE)
                tri_index += 1

        if not sg_geom.ValidateQuadFlags() and is_quad:
            sg_geom.RepairQuadFlags()

        unique_mats = get_unique_materials(blender_mesh.materials)
        sg_mesh.SetGeometry(sg_geom)

        return sg_mesh, unique_mats
