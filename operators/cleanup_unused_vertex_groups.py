import bpy

from .utils import find_all_lod_meshes, ensure_object_mode, get_mesh_and_armature


class CleanUpUnusedVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_unused_vertex_groups"
    bl_label = "Cleanup Unused Groups"
    bl_description = "Deletes mesh vertex groups with no matching bone in the armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings

        mesh, armature = get_mesh_and_armature(context)

        # Check if both armature and mesh are selected
        if not armature or not mesh:
            self.report({'ERROR'}, "Please select both an armature and a mesh.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Find all LOD meshes if enabled
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

        self.report({'INFO'}, f"Processed {total} mesh(es).")
        return {'FINISHED'}

    def cleanup_unused_groups(self, mesh, bones_in_armature):
        """Clean up unused vertex groups for a single mesh"""
        # Collect groups whose name has no corresponding bone, then delete them.
        groups_to_delete = [vg.name for vg in mesh.vertex_groups
                            if vg.name not in bones_in_armature]

        for group_name in groups_to_delete:
            vg = mesh.vertex_groups.get(group_name)
            if vg:
                mesh.vertex_groups.remove(vg)
                print(f"Deleted vertex group: {group_name}")

        print(f"Unused vertex groups deleted: {len(groups_to_delete)}")


def register():
    bpy.utils.register_class(CleanUpUnusedVertexGroupsOperator)


def unregister():
    bpy.utils.unregister_class(CleanUpUnusedVertexGroupsOperator)


if __name__ == "__main__":
    register()
