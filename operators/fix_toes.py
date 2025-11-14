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

class FixToesOperator(bpy.types.Operator):
    bl_idname = "object.fix_toes"
    bl_label = "Fix Toes Vertex Groups"
    bl_description = "Merge toe vertex groups into ball_l and ball_r, then delete the original groups"

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        
        # Ensure a mesh object is selected
        if not bpy.context.object or bpy.context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        mesh = bpy.context.object
        
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
            self.process_toes(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def process_toes(self, mesh):
        """Process toe vertex groups for a single mesh"""
        print(f"Processing vertex groups for object: {mesh.name}")

        # Ensure the target groups ball_l and ball_r exist
        if "ball_l" not in mesh.vertex_groups:
            mesh.vertex_groups.new(name="ball_l")
        if "ball_r" not in mesh.vertex_groups:
            mesh.vertex_groups.new(name="ball_r")
        
        # Get all the vertex groups that contain "toe"
        toe_groups = [vg for vg in mesh.vertex_groups if "toe" in vg.name.lower()]

        if not toe_groups:
            print("No 'toe' vertex groups found.")
            return

        print(f"Found vertex groups to merge: {[vg.name for vg in toe_groups]}")

        # Separate into left and right toe groups based on the suffix (_l or _r)
        left_groups = [vg for vg in toe_groups if "_l" in vg.name]
        right_groups = [vg for vg in toe_groups if "_r" in vg.name]

        # Process left and right groups
        self.merge_and_clean(mesh, left_groups, "ball_l")
        self.merge_and_clean(mesh, right_groups, "ball_r")

        print("Vertex groups merged and cleaned.")

    def merge_and_clean(self, mesh, groups, target_group_name):
        """Merges the weights from the specified groups into the target group and deletes the original groups."""
        target_group = mesh.vertex_groups.get(target_group_name)

        for group in groups:
            group_name = group.name
            print(f"Merging weights of group '{group_name}' into '{target_group_name}'")

            # Merge the weights into the target group
            self.merge_vertex_group_weights(mesh, group_name, target_group_name)

            # Remove the original group after merging
            mesh.vertex_groups.remove(group)
            print(f"Deleted vertex group: {group_name}")

    def merge_vertex_group_weights(self, obj, src_group_name, target_group_name):
        """Merges the weights from the source vertex group into the target vertex group."""
        src_group = obj.vertex_groups.get(src_group_name)
        target_group = obj.vertex_groups.get(target_group_name)

        if not src_group or not target_group:
            return
        
        # Merge the weights from the source to the target group
        for v in obj.data.vertices:
            try:
                src_weight = src_group.weight(v.index)
            except RuntimeError:
                src_weight = 0

            try:
                target_weight = target_group.weight(v.index)
            except RuntimeError:
                target_weight = 0

            # Add the merged weight to the target group
            merged_weight = src_weight + target_weight
            target_group.add([v.index], merged_weight, 'REPLACE')

def register():
    bpy.utils.register_class(FixToesOperator)

def unregister():
    bpy.utils.unregister_class(FixToesOperator)

if __name__ == "__main__":
    register()
