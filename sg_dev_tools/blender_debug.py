import bpy
import numpy as np


def print_blender_objects():
    for obj in bpy.data.objects:
        print(f'Debug ObjectName:{obj.name}')


def print_blender_meshes():
    for obj in bpy.data.meshes:
        print(f'Debug MeshName:{obj.name}')


def print_blender_materials():
    for obj in bpy.data.materials:
        print(f'Debug MaterialName:{obj.name}')


def print_blender_node_groups():
    for obj in bpy.data.node_groups:
        print(f'Debug NodeGroupName:{obj.name}')


def print_blender_scenes():
    for obj in bpy.data.scenes:
        print(f'Debug SceneName:{obj.name}')


def print_blender_textures():
    for obj in bpy.data.textures:
        print(f'Debug TextureName:{obj.name}')


def print_collection_info(collection):
    for obj in collection.objects:
        print(f'Object name:{obj.name} -----> {obj.type}')

    for coll in collection.children:
        print_collection_info(coll)


def print_context_scene_info():
    ctx_scene = bpy.context.scene
    root_collection = ctx_scene.collection
    print_collection_info(root_collection)


def print_polygon_info(blender_mesh):
    for poly in blender_mesh.polygons:
        print("Polygon index: %d, length: %d" %
              (poly.index, poly.loop_total))


def print_mesh_vertex_attributes(blender_mesh):
    print("Vertex Attribute Info\n")
    for meshloop in blender_mesh.loops:
        print(f'Vertex Attribute:{meshloop}')


def get_uv_map_names(blender_mesh):
    uv_maps = []
    for attrib in blender_mesh.attributes:
        if attrib.data_type == 'FLOAT2' and attrib.domain == 'CORNER':
            uv_maps.append(attrib.name)

    return uv_maps


def print_mesh_info(blender_mesh):
    num_vertices = len(blender_mesh.vertices)
    num_polygons = len(blender_mesh.polygons)
    num_loops = len(blender_mesh.loops)
    loops_per_polygon = num_loops / num_polygons
    is_quad = True if loops_per_polygon == 4 else False
    num_triangles = num_polygons * 2 if is_quad else num_polygons

    if is_quad:
        blender_mesh.create_normals_split()
        blender_mesh.calc_normals_split()
        blender_mesh.calc_loop_triangles()

    print(f'Mesh {blender_mesh.name} Verts:{num_vertices} Polys:{num_polygons} Loops:{num_loops} CornersPerPoly:{loops_per_polygon} Quad:{is_quad} Tris:{num_triangles}')

    for attrib in blender_mesh.attributes:
        print(f'MeshAttrib {attrib}')

    for i in blender_mesh.loop_triangle_polygons:
        print(f'LoopsTris {i.value}')
    for t in blender_mesh.loop_triangles:
        print(
            f'LoopTri Index:{t.index} {t. material_index} {t.vertices} {t.split_normals}')

    split_normals = np.empty(num_triangles*3*3, dtype=np.float32)
    vertex_ids = np.empty(num_triangles*3, dtype=np.int32)
    blender_mesh.loop_triangles.foreach_get('split_normals', split_normals)
    blender_mesh.loop_triangles.foreach_get('vertices', vertex_ids)

    print(split_normals)
    print(vertex_ids)
    # print(f'LoopsTris {}')
