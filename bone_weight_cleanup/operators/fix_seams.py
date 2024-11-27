import bpy

class FixSeamsOperator(bpy.types.Operator):
    bl_idname = "object.fix_seams"
    bl_label = "Fix Seams"
    bl_description = "Fix seams by selecting non-manifold geometry and merging by distance"

    def execute(self, context):
        # Ensure there is a mesh object selected
        if not bpy.context.object or bpy.context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        # Get the active mesh object
        obj = bpy.context.object

        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Deselect all vertices
        bpy.ops.mesh.select_all(action='DESELECT')

        # Select non-manifold vertices
        bpy.ops.mesh.select_non_manifold()

        # Merge by distance with a threshold of 0.0001m
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Seams fixed successfully!")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FixSeamsOperator)

def unregister():
    bpy.utils.unregister_class(FixSeamsOperator)

if __name__ == "__main__":
    register()
