import bpy

from .utils import (
    find_all_lod_meshes,
    merge_vertex_group_weights,
    ensure_object_mode,
    get_target_mesh,
)

_BULGE_SUFFIX = "_bulge"


class FixFingerBulgesOperator(bpy.types.Operator):
    bl_idname = "object.fix_finger_bulges"
    bl_label = "Fix Finger Bulges"
    bl_description = "Merges each '*_bulge' group into its base group and deletes the bulge"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings

        obj = get_target_mesh(context)
        if not obj:
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Find all LOD meshes if enabled
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

        self.report({'INFO'}, f"Processed {total} mesh(es).")
        return {'FINISHED'}

    def process_bulges(self, obj):
        """Process bulge vertex groups for a single mesh"""
        print(f"Processing bulge vertex groups for object: {obj.name}")

        # Only treat groups whose name ends in '_bulge' as bulge groups, so the
        # stripped target name is always a real, different group.
        bulge_groups = [vg for vg in obj.vertex_groups if vg.name.endswith(_BULGE_SUFFIX)]
        for bulge_group in bulge_groups:
            bulge_name = bulge_group.name
            target_name = bulge_name[:-len(_BULGE_SUFFIX)]

            print(f"Merging '{bulge_name}' into '{target_name}'...")
            merge_vertex_group_weights(obj, bulge_name, target_name,
                                       create_target=False, remove_source=True)

        print("Finished processing bulge vertex groups.")


def register():
    bpy.utils.register_class(FixFingerBulgesOperator)


def unregister():
    bpy.utils.unregister_class(FixFingerBulgesOperator)


if __name__ == "__main__":
    register()
