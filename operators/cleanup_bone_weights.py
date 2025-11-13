import bpy

class CleanUpBoneWeightsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_bone_weights"
    bl_label = "Clean Up Bone Weights"
    bl_description = "Cleans up vertex groups by merging child bones into head, neck_02, and neck_01"

    def execute(self, context):
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
        
        cleanup_vertex_groups(mesh, armature)
        self.report({'INFO'}, "Bone weights cleanup completed!")
        return {'FINISHED'}

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
