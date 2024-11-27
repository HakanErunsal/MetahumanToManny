import bpy

class CleanUpUnusedVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_unused_vertex_groups"
    bl_label = "Clean Up Unused Vertex Groups"
    bl_description = "Deletes vertex groups in the mesh that do not have a corresponding bone in the armature"

    def execute(self, context):
        # Ensure the correct objects are selected
        selected_objects = bpy.context.selected_objects
        
        armature = None
        mesh = None
        
        # Identify the armature and the mesh from the selected objects
        for obj in selected_objects:
            if obj.type == 'ARMATURE':
                armature = obj
            elif obj.type == 'MESH':
                mesh = obj
        
        # Check if both armature and mesh are selected
        if not armature or not mesh:
            self.report({'ERROR'}, "Please select both an armature and a mesh.")
            return {'CANCELLED'}
        
        # Get the list of bones in the armature
        bones_in_armature = {bone.name for bone in armature.pose.bones}
        
        # Go through each vertex group in the mesh and collect the ones to delete
        vertex_groups_to_delete = []
        for vg in mesh.vertex_groups:
            if vg.name not in bones_in_armature:
                vertex_groups_to_delete.append(vg.name)
        
        # Delete vertex groups that don't have a corresponding bone
        for group_name in vertex_groups_to_delete:
            vg = mesh.vertex_groups.get(group_name)  # Get the vertex group by name
            if vg:
                mesh.vertex_groups.remove(vg)  # Remove the vertex group
                print(f"Deleted vertex group: {group_name}")
        
        self.report({'INFO'}, "Unused vertex groups deleted.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CleanUpUnusedVertexGroupsOperator)

def unregister():
    bpy.utils.unregister_class(CleanUpUnusedVertexGroupsOperator)

if __name__ == "__main__":
    register()
