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

class FixSeamsOperator(bpy.types.Operator):
    bl_idname = "object.fix_seams"
    bl_label = "Fix Seams"
    bl_description = "Fix seams by selecting non-manifold geometry and merging by distance"

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        
        # Ensure there is a mesh object selected
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
            self.process_seams(context, target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def process_seams(self, context, obj):
        """Process seams for a single mesh"""
        # Set the object as active
        context.view_layer.objects.active = obj
        
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
        
        print("Seams fixed successfully!")


def register():
    bpy.utils.register_class(FixSeamsOperator)

def unregister():
    bpy.utils.unregister_class(FixSeamsOperator)

if __name__ == "__main__":
    register()
