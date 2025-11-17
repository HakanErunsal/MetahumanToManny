import bpy
import re

def find_all_lod_meshes(base_mesh):
    """Find all LOD meshes related to the selected mesh (LOD0, LOD1, LOD2, etc.)"""
    all_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    lod_pattern = re.compile(r'_LOD\d+$')
    
    # Check if the base mesh itself has LOD suffix
    base_name = base_mesh.name
    match = lod_pattern.search(base_name)
    
    if match:
        # Remove the LOD suffix to get the base name (e.g., "FaceMesh_LOD0" -> "FaceMesh")
        prefix = base_name[:match.start()]
    else:
        # If no LOD suffix, use the full name as prefix
        prefix = base_name
    
    print(f"Looking for LOD meshes with prefix: '{prefix}'")
    
    # Find all meshes that match: prefix + "_LOD" + digit(s)
    lod_meshes = []
    for obj in all_meshes:
        match = lod_pattern.search(obj.name)
        if match:
            # Get the prefix of this object
            obj_prefix = obj.name[:match.start()]
            # Only include if the prefix matches exactly
            if obj_prefix == prefix:
                lod_meshes.append(obj)
                print(f"  Found matching LOD: {obj.name}")
    
    # If we found LOD meshes, return them sorted; otherwise just return the base mesh
    if lod_meshes:
        lod_meshes.sort(key=lambda x: x.name)  # Sort for consistent ordering
        return lod_meshes
    else:
        return [base_mesh]

class CleanUpUnusedVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_unused_vertex_groups"
    bl_label = "Clean Up Unused Vertex Groups"
    bl_description = "Deletes vertex groups in the mesh that do not have a corresponding bone in the armature"

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        
        # Ensure the correct objects are selected
        selected_objects = context.selected_objects
        
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
        
        # Find all LOD meshes if enabled
        meshes_to_process = []
        if settings.bAutoLookForLOD:
            meshes_to_process = find_all_lod_meshes(mesh)
            if len(meshes_to_process) > 1:
                self.report({'INFO'}, f"Found {len(meshes_to_process)} LOD meshes to process")
        else:
            meshes_to_process = [mesh]
        
        # Get the list of bones in the armature (once, used for all LODs)
        bones_in_armature = {bone.name for bone in armature.pose.bones}
        
        # Process each mesh
        total = len(meshes_to_process)
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            self.cleanup_unused_groups(target_mesh, bones_in_armature)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def cleanup_unused_groups(self, mesh, bones_in_armature):
        """Clean up unused vertex groups for a single mesh"""
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
        
        print(f"Unused vertex groups deleted: {len(vertex_groups_to_delete)}")

def register():
    bpy.utils.register_class(CleanUpUnusedVertexGroupsOperator)

def unregister():
    bpy.utils.unregister_class(CleanUpUnusedVertexGroupsOperator)

if __name__ == "__main__":
    register()
