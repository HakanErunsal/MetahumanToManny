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

class FixFingerBulgesOperator(bpy.types.Operator):
    bl_idname = "object.fix_finger_bulges"
    bl_label = "Fix Finger Bulges"
    bl_description = "Merge bulge vertex groups into their corresponding original groups and delete the bulge groups."

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        
        # Ensure a mesh object is selected
        obj = context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        # Find all LOD meshes if enabled
        meshes_to_process = []
        if settings.bAutoLookForLOD:
            meshes_to_process = find_all_lod_meshes(obj)
            if len(meshes_to_process) > 1:
                self.report({'INFO'}, f"Found {len(meshes_to_process)} LOD meshes to process")
        else:
            meshes_to_process = [obj]
        
        # Process each mesh
        total = len(meshes_to_process)
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            self.process_bulges(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def process_bulges(self, obj):
        """Process bulge vertex groups for a single mesh"""
        print(f"Processing bulge vertex groups for object: {obj.name}")
        
        # Find and process all bulge vertex groups
        bulge_groups = [vg for vg in obj.vertex_groups if "bulge" in vg.name]
        for bulge_group in bulge_groups:
            bulge_name = bulge_group.name
            target_name = bulge_name.replace("_bulge", "")
            
            print(f"Merging '{bulge_name}' into '{target_name}'...")
            self.merge_vertex_groups(obj, bulge_name, target_name)

        print("Finished processing bulge vertex groups.")

    def merge_vertex_groups(self, obj, src_group_name, target_group_name):
        """Merge weights from src_group_name into target_group_name and remove src_group_name."""
        if target_group_name not in obj.vertex_groups:
            print(f"Warning: Target vertex group '{target_group_name}' not found.")
            return

        if src_group_name not in obj.vertex_groups:
            print(f"Warning: Source vertex group '{src_group_name}' not found.")
            return

        # Get the source and target groups
        src_group = obj.vertex_groups[src_group_name]
        target_group = obj.vertex_groups[target_group_name]

        # Add weights from the source group to the target group
        for v in obj.data.vertices:
            try:
                src_weight = src_group.weight(v.index)
            except RuntimeError:
                src_weight = 0

            try:
                target_weight = target_group.weight(v.index)
            except RuntimeError:
                target_weight = 0

            merged_weight = src_weight + target_weight
            target_group.add([v.index], merged_weight, 'REPLACE')

        # Remove the source group
        obj.vertex_groups.remove(src_group)

def register():
    bpy.utils.register_class(FixFingerBulgesOperator)

def unregister():
    bpy.utils.unregister_class(FixFingerBulgesOperator)

if __name__ == "__main__":
    register()
