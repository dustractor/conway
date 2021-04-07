bl_info = {
    "name":"Conway",
    "category":"Mesh",
    "version":(0,2),
    "blender":(2,80,0)
}
import bpy,bmesh
cachedata = dict()
tkkey = None

class CONWAY_OT_conway(bpy.types.Operator):
    bl_idname = "conway.conway"
    bl_label = "Conway"
    bl_options = {"REGISTER","UNDO"}
    birth_rule: bpy.props.IntProperty(default=3,min=1)
    survival_rule: bpy.props.IntProperty(default=2,min=1)
    def execute(self,context):
        global cachedata,tkkey
        bpy.ops.object.mode_set(mode="OBJECT")
        obj = context.active_object
        mesh = obj.data
        meshkey = (len(mesh.vertices),len(mesh.edges),len(mesh.polygons),id(self))
        if (meshkey == tkkey) and (meshkey in cachedata):
            vert_to_face_map = cachedata[meshkey]
        else:
            vert_to_face_map = {i:set() for i in range(meshkey[0])}
            for f in mesh.polygons:
                for v in f.vertices:
                    vert_to_face_map[v].add(f.index)
            tkkey = meshkey
        sel = set()
        uns = set()
        F = {i:set() for i in range(meshkey[2])}
        for f in range(meshkey[2]):
            for v in mesh.polygons[f].vertices:
                for n in filter(lambda _: mesh.polygons[_].select and (_ != f),vert_to_face_map[v]):
                    F[f].add(n)
        born,survived = self.birth_rule,self.survival_rule
        for f in F:
            if len(F[f]) == born:
                sel.add(f)
            elif len(F[f]) != survived:
                uns.add(f)
        for e in range(meshkey[1]):
            mesh.edges[e].select = False
        for f in range(meshkey[2]):
            if f in sel:
                mesh.polygons[f].select = True
            if f in uns:
                mesh.polygons[f].select = False
        cachedata[meshkey] = vert_to_face_map
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}

def handler(scene):
    bpy.ops.conway.conway()

def deal_with_handlers(self,context):
    if self.conway_post:
        if handler not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(handler)
    else:
        if handler in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(handler)

def menuitem(self,context):
    self.layout.operator("conway.conway")
    self.layout.prop(context.window_manager,"conway_post")


def register():
    bpy.utils.register_class(CONWAY_OT_conway)
    bpy.types.VIEW3D_MT_select_edit_mesh.append(menuitem)
    bpy.types.WindowManager.conway_post = bpy.props.BoolProperty(update=deal_with_handlers)


def unregister():
    bpy.utils.unregister_class(CONWAY_OT_conway)
    del bpy.types.WindowManager.conway_post

