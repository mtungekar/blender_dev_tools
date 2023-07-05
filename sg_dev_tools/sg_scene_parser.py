import bpy
from simplygon10 import Simplygon
from simplygon10 import simplygon_loader
from .sg_mesh_handler import BlenderMeshHelper


class BlenderSceneParser:

    def __init__(self, sg, scene, material_lookup, root_collection):
        self.root_collection = root_collection
        self.all_objects = self.root_collection.all_objects
        self.iter_object = self.object_iter()
        self.sg = sg
        self.scene = scene
        self.material_lookup = material_lookup

    def object_iter(self):
        for x in self.all_objects:
            yield x

    def next_object(self):
        retVal = None
        try:
            retVal = next(self.iter_object)
        except StopIteration:
            retVal = None
        return retVal

    def accept(self, visitor):
        while visitor.visit(self):
            continue

    def meshes(self, obj):
        if obj is None:
            return False
        if obj.type == 'MESH':
            result = BlenderMeshHelper.get_sg_mesh(
                self.sg, bpy.types.Mesh(obj.data))
            self.scene.GetRootNode().AddChild(result[0])
            for mat in result[1]:
                self.material_lookup[mat.name] = mat
        return True

    def empties(self, obj):
        if obj is None:
            return False
        if obj.type == 'EMPTY':
            print("visiting empties")
        return True

    def armtures(self, obj):
        if obj is None:
            return False
        if obj.type == 'ARMTURE':
            print("visiting armtures")
        return True

    def surfaces(self, obj):
        if obj is None:
            return False
        if obj.type == 'SURFACE':
            print("visiting surfaces")
        return True


class BlenderSceneObjectVisitor:
    def __str__(self):
        return self.__class__.__name__


class BlenderMeshVisitor(BlenderSceneObjectVisitor):
    def visit(self, parser):
        return parser.meshes(parser.next_object())


class BlenderEmptyVisitor(BlenderSceneObjectVisitor):
    def visit(self, parser):
        return parser.empties(parser.next_object())


class BlenderSurfaceVisitor(BlenderSceneObjectVisitor):
    def visit(self, parser):
        return parser.surfaces(parser.next_object())


class BlenderArmtureVisitor(BlenderSceneObjectVisitor):
    def visit(self, parser):
        parser.armtures(parser.next_object())
