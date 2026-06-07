import bpy

from .utils import (
    find_all_lod_meshes,
    merge_vertex_group_weights,
    ensure_object_mode,
    get_target_mesh,
)


class FixTwistBoneNamesOperator(bpy.types.Operator):
    bl_idname = "object.fix_twist_bone_names"
    bl_label = "Fix Twist Bone Names"
    bl_description = ("Renames 'twistCor' vertex groups to 'twist', merging the weights "
                      "into any existing 'twist' group")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings

        mesh = get_target_mesh(context)
        if not mesh:
            self.report({'ERROR'}, "Please select a mesh object.")
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
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            self.process_twist_bones(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")

        self.report({'INFO'}, f"Processed {total} mesh(es).")
        return {'FINISHED'}

    def process_twist_bones(self, mesh):
        """Process twist bone names for a single mesh"""
        print(f"Processing vertex groups for object: {mesh.name}")

        vertex_groups = mesh.vertex_groups
        twist_cor_groups = [vg for vg in vertex_groups if "twistCor" in vg.name]

        if not twist_cor_groups:
            print("No 'twistCor' vertex groups found.")
            return

        print(f"Found twistCor groups: {[vg.name for vg in twist_cor_groups]}")

        for twist_cor_group in twist_cor_groups:
            twist_cor_name = twist_cor_group.name
            target_name = twist_cor_name.replace("twistCor", "twist")

            if vertex_groups.get(target_name) is not None:
                # The 'twist' counterpart already exists (e.g. distinct Manny bones).
                # Merge the twistCor weights into it rather than destroying it.
                print(f"'{target_name}' already exists; merging '{twist_cor_name}' into it.")
                self.report({'WARNING'},
                            f"Merged '{twist_cor_name}' into existing '{target_name}'")
                merge_vertex_group_weights(mesh, twist_cor_name, target_name,
                                           create_target=False, remove_source=True)
            else:
                # No counterpart: simply rename twistCor -> twist.
                print(f"Renaming group {twist_cor_name} to {target_name}")
                twist_cor_group.name = target_name

        print("Finished processing 'twistCor' vertex groups.")


def register():
    bpy.utils.register_class(FixTwistBoneNamesOperator)


def unregister():
    bpy.utils.unregister_class(FixTwistBoneNamesOperator)


if __name__ == "__main__":
    register()
