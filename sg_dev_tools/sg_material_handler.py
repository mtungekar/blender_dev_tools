import bpy
from simplygon import Simplygon
from .sg_utils import get_texture_coord_name

class BlenderMaterialHelper:

    sg_channel_to_blender_node = {
        'BaseColor':'Base Color',
        'Opacity':'Alpha',
        'OpacityMask':'Alpha',
        'Metallic':'Metallic', 
        'Roughness':'Roughness', 
        'Normal':'Normal',
        'OpacityMask':'Alpha',
        'Emissive':'Emission'}

    def is_rgba_node(socket):
        return socket.type == 'RGBA'

    def is_value_node(socket):
        return socket.type == 'VALUE'

    def is_vector_node(socket):
        return socket.type == 'VECTOR'


    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    def create_blender_texture_image(blender_material, texture_lookup, location, label, tex_coord_level,socket):
        x,y = location
        #basic setup
        blender_texture_image = blender_material.node_tree.nodes.new('ShaderNodeTexImage')
        blender_texture_image.location = x-240,y
        blender_texture_image.label = label
        
        #filtering //todo
        
        #image
        blender_texture_image.image = bpy.data.images[label]
        #texture_lookup[]

        #outputs
        blender_material.node_tree.links.new(socket,blender_texture_image.outputs['Color'])
        #blender_material.node_tree.nodes.new(alpha_socket,blender_texture_image.outputs['Alpha'])

        #inputs
        uv_socket = blender_texture_image.inputs[0]

        #uv mapping
        uv_map = blender_material.node_tree.nodes.new('ShaderNodeUVMap')
        uv_map.location = x - 160, y - 70
        uv_map.uv_map = get_texture_coord_name(tex_coord_level)
        blender_material.node_tree.links.new(uv_socket, uv_map.outputs[0])

    def setup_blender_pbr_material(sg,blender_material,sg_material, texture_lookup):
        pbr_node = blender_material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        pbr_node.location = 10, 300
        channels = sg.CreateStringArray()
        sg_material.GetMaterialChannels(channels)
        x = -200
        y = 0
        i = 0
        
        for i in range(0,channels.GetItemCount()):
            channel = channels.GetItem(i)

            if channel not in BlenderMaterialHelper.sg_channel_to_blender_node:
                continue

            sg_shading_node = sg_material.GetShadingNetwork(channel)
            sg_texture_node = Simplygon.spShadingTextureNode.SafeCast(sg_shading_node)
            sg_color_node = Simplygon.spShadingColorNode.SafeCast(sg_shading_node)
            if sg_texture_node is not None:
                print(f'{channel} has TextureNode')
                texture_name = sg_texture_node.GetTextureName()
                tex_coord_level = sg_texture_node.GetTexCoordLevel()
                
                BlenderMaterialHelper.create_blender_texture_image(
                    blender_material,
                    texture_lookup,
                    (x,y),
                    texture_name,
                    tex_coord_level,
                    pbr_node.inputs[BlenderMaterialHelper.sg_channel_to_blender_node[channel]])

            elif sg_color_node is not None:
                print(f'{channel} has ColorNode')
                r = sg_color_node.GetDefaultParameterRed(0)
                g = sg_color_node.GetDefaultParameterGreen(0)
                b = sg_color_node.GetDefaultParameterBlue(0)
                a = sg_color_node.GetDefaultParameterAlpha(0)
                current_socket =  pbr_node.inputs[BlenderMaterialHelper.sg_channel_to_blender_node[channel]]
                print(f'{channel} SocketType {current_socket.type}')
                color_value = [r,g,b,a]
                if BlenderMaterialHelper.is_vector_node(current_socket):
                    pbr_node.inputs[BlenderMaterialHelper.sg_channel_to_blender_node[channel]].default_value = color_value[:3]
                elif BlenderMaterialHelper.is_value_node(current_socket):
                    pbr_node.inputs[BlenderMaterialHelper.sg_channel_to_blender_node[channel]].default_value = color_value[0]
                else:
                    pbr_node.inputs[BlenderMaterialHelper.sg_channel_to_blender_node[channel]].default_value = color_value

            y -= 20

        # Material output
        sg_blend_mode = sg_material.GetBlendMode();
        if sg_blend_mode == Simplygon.EMaterialBlendMode_Mask:
            blender_material.blend_method = 'CLIP'
        elif sg_blend_mode == Simplygon.EMaterialBlendMode_Blend:
            blender_material.blend_method = 'BLEND'
        else:
            blender_material.blend_method = 'OPAQUE'
        shader_ouput_node = blender_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        shader_ouput_node.location = x + 70, y + 10
        blender_material.node_tree.links.new(shader_ouput_node.inputs[0], pbr_node.outputs[0])



class SGMaterialHandler:
    """material handler"""
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    def create(sg,material_name,sg_material, texture_lookup, material_mapping):
        print(material_name)
        blender_material = bpy.data.materials.new(material_name)
        blender_material.use_backface_culling = True
        blender_material.use_nodes = True
        BlenderMaterialHelper.sg_channel_to_blender_node = material_mapping

        #clear material nodes
        while blender_material.node_tree.nodes:
            blender_material.node_tree.nodes.remove(blender_material.node_tree.nodes[0])

        BlenderMaterialHelper.setup_blender_pbr_material(sg,blender_material,sg_material,texture_lookup)

        return blender_material