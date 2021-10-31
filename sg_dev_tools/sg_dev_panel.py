import bpy

class SgDev_PT_MultiFileImport(bpy.types.Panel):
    """Creates a Panel for Internal Simplygon Development Tools"""
    bl_label = "Multi File"
    bl_idname = 'SgDev_PT_MultifileOBJ'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SimplygonDevTools"
     
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene,'import_folder_path')
        col.operator('simplygon.sg_obj_multifile_import_operator')

        col = layout.column(align=True)
        if(context.object):
            col.prop(context.object,'import_file_path')
            col.operator('simplygon.sg_obj_multifile_reload_operator')
        else:
            col.label(text='no object present')

class SgDev_PT_SgSceneImport(bpy.types.Panel):
    """Creates a Panel for Internal Simplygon Development Tools"""
    bl_label = "SgScene"
    bl_idname = 'SgDev_PT_SgScene'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SimplygonDevTools"
     
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator('simplygon.sg_scene_import_operator')

