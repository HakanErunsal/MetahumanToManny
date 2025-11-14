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

class FixTwistBoneNamesOperator(bpy.types.Operator):
    bl_idname = "object.fix_twist_bone_names"
    bl_label = "Fix Twist Bone Names"
    bl_description = "Renames 'twistCor' vertex groups to 'twist' and removes corresponding 'twist' groups if they exist"

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        
        # Ensure there is a mesh object selected
        if not context.object or context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        mesh = context.object
        
        # Find all LOD meshes if enabled
        meshes_to_process = []
        if settings.bAutoLookForLOD:
            meshes_to_process = find_all_lod_meshes(mesh)
            if len(meshes_to_process) > 1:
                self.report({'INFO'}, f"Found {len(meshes_to_process)} LOD meshes to process")
        else:
            meshes_to_process = [mesh]
        
        # Process each mesh
        total = len(meshes_to_process)
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            self.process_twist_bones(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def process_twist_bones(self, mesh):
        """Process twist bone names for a single mesh"""
        print(f"Processing vertex groups for object: {mesh.name}")
        
        # Get all the vertex groups
        vertex_groups = mesh.vertex_groups
        twist_cor_groups = [vg for vg in vertex_groups if "twistCor" in vg.name]

        if not twist_cor_groups:
            print("No 'twistCor' vertex groups found.")
            return

        print(f"Found twistCor groups: {[vg.name for vg in twist_cor_groups]}")

        # Loop through each "twistCor" vertex group
        for twist_cor_group in twist_cor_groups:
            # Find the name of the corresponding group without "Cor"
            corresponding_group_name = twist_cor_group.name.replace("twistCor", "twist")
            corresponding_group = vertex_groups.get(corresponding_group_name)

            # If the corresponding group exists, delete it
            if corresponding_group:
                print(f"Found corresponding group: {corresponding_group_name}, removing it.")
                vertex_groups.remove(corresponding_group)
            else:
                print(f"No corresponding group found for: {twist_cor_group.name}")

            # Rename the "twistCor" group by removing "Cor"
            new_group_name = twist_cor_group.name.replace("twistCor", "twist")
            print(f"Renaming group {twist_cor_group.name} to {new_group_name}")
            twist_cor_group.name = new_group_name

        print("Finished processing 'twistCor' vertex groups.")

def register():
    bpy.utils.register_class(FixTwistBoneNamesOperator)

def unregister():
    bpy.utils.unregister_class(FixTwistBoneNamesOperator)

if __name__ == "__main__":
    register()