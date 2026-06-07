import bpy

from .utils import (
    find_all_lod_meshes,
    merge_vertex_group_weights,
    ensure_object_mode,
    get_target_mesh,
)


class FixToesOperator(bpy.types.Operator):
    bl_idname = "object.fix_toes"
    bl_label = "Fix Toes"
    bl_description = "Merges toe vertex groups into ball_l and ball_r and deletes the originals"
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
            self.process_toes(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")

        self.report({'INFO'}, f"Processed {total} mesh(es).")
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

        # Split sides by the side suffix, case-insensitively (matching the toe filter).
        # endswith keeps the lists disjoint, so a group is never merged twice.
        left_groups = [vg for vg in toe_groups if vg.name.lower().endswith("_l")]
        right_groups = [vg for vg in toe_groups if vg.name.lower().endswith("_r")]

        # Surface, rather than silently drop, any toe group with no _l/_r side suffix.
        unmatched = [vg for vg in toe_groups if vg not in left_groups and vg not in right_groups]
        if unmatched:
            names = [vg.name for vg in unmatched]
            print(f"Warning: toe groups with no _l/_r side suffix, skipped: {names}")
            self.report({'WARNING'}, f"Skipped unsided toe group(s): {', '.join(names)}")

        # Process left and right groups
        self.merge_and_clean(mesh, left_groups, "ball_l")
        self.merge_and_clean(mesh, right_groups, "ball_r")

        print("Vertex groups merged and cleaned.")

    def merge_and_clean(self, mesh, groups, target_group_name):
        """Merge the weights from the given groups into the target and delete the originals."""
        for group in groups:
            group_name = group.name
            print(f"Merging weights of group '{group_name}' into '{target_group_name}'")
            merge_vertex_group_weights(mesh, group_name, target_group_name,
                                       create_target=False, remove_source=True)


def register():
    bpy.utils.register_class(FixToesOperator)


def unregister():
    bpy.utils.unregister_class(FixToesOperator)


if __name__ == "__main__":
    register()
