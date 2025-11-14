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

class CleanUpBoneWeightsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_bone_weights"
    bl_label = "Clean Up Bone Weights"
    bl_description = "Cleans up vertex groups by merging child bones into head, neck_02, and neck_01"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        selected_objects = bpy.context.selected_objects
        mesh = None
        armature = None

        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj
            elif obj.type == 'ARMATURE':
                armature = obj

        if not mesh or not armature:
            self.report({'ERROR'}, "Please select both a mesh and an armature.")
            return {'CANCELLED'}
        
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
            context.window_manager.progress_update(idx)
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            cleanup_vertex_groups(target_mesh, armature)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        
        context.window_manager.progress_end()
        self.report({'INFO'}, f"All done! Processed {total} mesh(es) total")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.progress_begin(0, 100)
        return self.execute(context)

def merge_vertex_group_weights(obj, src_group_name, target_group_name):
    if target_group_name not in obj.vertex_groups:
        print(f"Creating target vertex group: {target_group_name}")
        obj.vertex_groups.new(name=target_group_name)
    
    if src_group_name not in obj.vertex_groups:
        print(f"Skipping merge: Source vertex group '{src_group_name}' not found.")
        return

    src_group = obj.vertex_groups[src_group_name]
    target_group = obj.vertex_groups[target_group_name]
    
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
    
    print(f"Deleting vertex group: {src_group_name}")
    obj.vertex_groups.remove(src_group)

def process_bones_recursive(obj, armature, parent_bone_name, target_group_name, excluded_groups):
    bone = armature.pose.bones.get(parent_bone_name)
    if not bone:
        print(f"Bone '{parent_bone_name}' not found in armature.")
        return

    for child_bone in bone.children:
        child_bone_name = child_bone.name
        
        if child_bone_name in excluded_groups or child_bone_name == target_group_name:
            continue
        
        if child_bone_name in obj.vertex_groups:
            merge_vertex_group_weights(obj, child_bone_name, target_group_name)
        
        process_bones_recursive(obj, armature, child_bone_name, target_group_name, excluded_groups)

def cleanup_vertex_groups(obj, armature):
    if obj.type != 'MESH' or armature.type != 'ARMATURE':
        print("Error: Please select a mesh and an armature.")
        return

    excluded_groups = ['head', 'neck_02', 'neck_01']
    
    for target_group in excluded_groups:
        if target_group not in obj.vertex_groups:
            print(f"Creating missing vertex group: {target_group}")
            obj.vertex_groups.new(name=target_group)
    
    process_bones_recursive(obj, armature, 'head', 'head', excluded_groups)
    process_bones_recursive(obj, armature, 'neck_02', 'neck_02', excluded_groups)
    process_bones_recursive(obj, armature, 'neck_01', 'neck_01', excluded_groups)

    print("\nWeight paint cleanup completed!")

def register():
    bpy.utils.register_class(CleanUpBoneWeightsOperator)

def unregister():
    bpy.utils.unregister_class(CleanUpBoneWeightsOperator)

if __name__ == "__main__":
    register()
