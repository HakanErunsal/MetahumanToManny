import bpy

from .utils import (
    find_all_lod_meshes,
    merge_vertex_group_weights,
    ensure_object_mode,
    get_mesh_and_armature,
)


class CleanUpBoneWeightsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_bone_weights"
    bl_label = "Clean Up Face Bone Weights"
    bl_description = "Merges child-bone weights into head, neck_02 and neck_01"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings
        mesh, armature = get_mesh_and_armature(context)

        if not mesh or not armature:
            self.report({'ERROR'}, "Please select both a mesh and an armature.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Find all LOD meshes if enabled
        if settings.bAutoLookForLOD:
            meshes_to_process = find_all_lod_meshes(mesh)
            if len(meshes_to_process) > 1:
                self.report({'INFO'}, f"Found {len(meshes_to_process)} LOD meshes to process")
        else:
            meshes_to_process = [mesh]

        # Process each mesh
        total = len(meshes_to_process)
        wm = context.window_manager
        wm.progress_begin(0, total)
        try:
            for idx, target_mesh in enumerate(meshes_to_process):
                wm.progress_update(idx)
                print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
                cleanup_vertex_groups(target_mesh, armature)
                self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
            wm.progress_update(total)
        finally:
            wm.progress_end()

        self.report({'INFO'}, f"Processed {total} mesh(es).")
        return {'FINISHED'}


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
            merge_vertex_group_weights(obj, child_bone_name, target_group_name, create_target=True)

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
