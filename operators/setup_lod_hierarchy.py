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
        return lod_meshes, prefix
    else:
        return [base_mesh], prefix

class SetupLodHierarchyOperator(bpy.types.Operator):
    bl_idname = "object.setup_lod_hierarchy"
    bl_label = "Setup LOD Hierarchy"
    bl_description = "Parents all LOD meshes to their LodGroup object and sets up Unreal Engine LOD recognition"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure a mesh object is selected
        if not context.object or context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        mesh = context.object
        
        # Find all LOD meshes
        lod_meshes, prefix = find_all_lod_meshes(mesh)
        
        if not lod_meshes:
            self.report({'ERROR'}, "No LOD meshes found.")
            return {'CANCELLED'}
        
        # Look for or create the LodGroup object
        lod_group_name = f"{prefix}_LodGroup"

        # Always delete existing LodGroup object if it exists
        lod_group = bpy.data.objects.get(lod_group_name)
        if lod_group:
            # Unlink from all collections
            for coll in lod_group.users_collection:
                coll.objects.unlink(lod_group)
            # Remove from bpy.data.objects
            bpy.data.objects.remove(lod_group)
            print(f"Deleted existing LodGroup object: {lod_group_name}")

        # Create a new empty object with the required name
        lod_group = bpy.data.objects.new(lod_group_name, None)
        lod_group.empty_display_type = 'PLAIN_AXES'
        lod_group.scale = (0.01, 0.01, 0.01)
        context.collection.objects.link(lod_group)
        print(f"Created new LodGroup object: {lod_group_name} (Empty, scale 0.01)")

        print(f"\n=== Setting up LOD hierarchy ===")
        print(f"LodGroup: {lod_group_name}")
        print(f"LOD meshes to parent: {[obj.name for obj in lod_meshes]}")

        # IMPORTANT: Sort LOD meshes by their LOD number to ensure correct order in FBX export
        def get_lod_number(obj):
            match = re.search(r'_LOD(\d+)$', obj.name)
            return int(match.group(1)) if match else 999

        lod_meshes.sort(key=get_lod_number)
        print(f"Sorted order: {[obj.name for obj in lod_meshes]}")


        # Parent all LOD meshes to the LodGroup with keep transform
        for lod_mesh in lod_meshes:
            # Store current world matrix
            # old_matrix = lod_mesh.matrix_world.copy()

            # Set parent with keep transform
            # lod_mesh.parent = lod_group
            # lod_mesh.matrix_parent_inverse.identity()
            # lod_mesh.matrix_world = old_matrix

            bpy.ops.object.select_all(action='DESELECT')
            lod_group.select_set(True)
            lod_mesh.select_set(True)
            context.view_layer.objects.active = lod_group

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

            print(f"Parented {lod_mesh.name} to {lod_group_name} (keep transform)")

        # Add custom property to LodGroup for Unreal Engine
        lod_group["fbx_type"] = "LodGroup"

        # Set the property metadata (description)
        id_props = lod_group.id_properties_ui("fbx_type")
        id_props.update(description="This object is for unreal to recognize lods")

        print(f"Added custom property 'fbx_type' = 'LodGroup' to {lod_group_name}")

        self.report({'INFO'}, f"LOD hierarchy setup complete! Parented {len(lod_meshes)} mesh(es) to {lod_group_name}")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SetupLodHierarchyOperator)

def unregister():
    bpy.utils.unregister_class(SetupLodHierarchyOperator)

if __name__ == "__main__":
    register()
