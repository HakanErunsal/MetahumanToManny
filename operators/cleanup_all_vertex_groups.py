import bpy

from .utils import ensure_object_mode, get_target_mesh


class CleanupAllVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_all_vertex_groups"
    bl_label = "Cleanup All"
    bl_description = "Runs all vertex group cleanup operations: Fix Twist Bones, Fix Finger Bulges, Fix Toes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = get_target_mesh(context)
        if not mesh:
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Set mesh as active so the sub-operators (which resolve the target mesh
        # from the selection/active object) all act on it.
        context.view_layer.objects.active = mesh

        print("\n=== Running All Vertex Group Cleanups ===")

        print("\n[1/3] Running Fix Twist Bone Names...")
        bpy.ops.object.fix_twist_bone_names()

        print("\n[2/3] Running Fix Finger Bulges...")
        bpy.ops.object.fix_finger_bulges()

        print("\n[3/3] Running Fix Toes...")
        bpy.ops.object.fix_toes()

        self.report({'INFO'}, "Vertex group cleanups done.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(CleanupAllVertexGroupsOperator)


def unregister():
    bpy.utils.unregister_class(CleanupAllVertexGroupsOperator)


if __name__ == "__main__":
    register()
