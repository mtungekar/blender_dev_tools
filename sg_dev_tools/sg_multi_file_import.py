import bpy
from .sg_utils import get_import_path


class SgImporter_OT_MultiImporter(bpy.types.Operator):
    bl_idname='simplygon.sg_obj_multifile_import_operator'
    bl_label="Multiple OBJ Importer"

    def execute(self,context):
        #Find obj
        import_path = get_import_path(context.scene)
        import_extensions = ('*.obj','*.sgscene','*.sg','*.glb','*.gltf')
        files_to_load_map = {}
        for ext in import_extensions:
            files_to_load_map[ext.lstrip('*.')] = list(import_path.glob('*.obj'))
        # Improt and link files
        for key,value in files_to_load_map.items():
            for import_file_path in value:
                if key == 'obj':
                    bpy.ops.import_scene.obj(filepath=str(import_file_path),axis_forward='X', axis_up='Y')
                elif key == 'sg' or key == 'sgscene':
                    bpy.ops.import_scene.sgscene(filepath=str(import_file_path),axis_forward='X', axis_up='Y')
                elif key == 'glb' or key == "gltf":
                    bpy.ops.import_scene.gltf(filepath=str(import_file_path))
                elif key == 'fbx':
                    bpy.ops.import_scene.fbx(filepath=str(import_file_path))

            for importe_obj in context.selected_objects:
                importe_obj.import_file_path = import_file_path.name

        self.report(
            {'ERROR'},
            f'no code to load from{import_path}')
        return{'CANCELLED'}

class SgImporter_OT_MultiReload(bpy.types.Operator):
    bl_idname='simplygon.sg_obj_multifile_reload_operator'
    bl_label="Mass OBJ"

    def execute(self,context):
        current_obj = context.object

        import_file_name = current_obj.import_file_path
        mtx_transform = current_obj.matrix_world.copy()

        for collection in list(current_obj.users_collection):
            collection.objects.unlink(current_obj)

        if current_obj.users == 0:
            bpy.data.objects.remove(current_obj)
        del current_obj

        import_path = get_import_path(context.scene)
        import_file_path = import_path / import_file_name
        bpy.ops.import_scene.obj(filepath=str(import_file_path),axis_forward='X', axis_up='Y')

        for imported_obj in context.selected_objects:
                imported_obj.import_file_path = import_file_path.name
                imported_obj.matrix_world = mtx_transform

        return {'FINISHED'}
