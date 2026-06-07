import bpy

from .utils import find_all_lod_meshes, ensure_object_mode, get_target_mesh


class FixSeamsOperator(bpy.types.Operator):
    bl_idname = "object.fix_seams"
    bl_label = "Fix Seams"
    bl_description = "Fix seams by selecting non-manifold geometry and merging by distance"
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

        # Remember the active object so we can restore it afterwards.
        original_active = context.view_layer.objects.active

        total = len(meshes_to_process)
        try:
            for idx, target_mesh in enumerate(meshes_to_process):
                print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
                self.process_seams(context, target_mesh)
                self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")
        finally:
            # Always leave Object mode and restore the user's active object,
            # even if a mesh op raised mid-run.
            if context.object and context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            if original_active:
                context.view_layer.objects.active = original_active

        self.report({'INFO'}, f"Processed {total} mesh(es).")
        return {'FINISHED'}

    def process_seams(self, context, obj):
        """Process seams for a single mesh"""
        context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')

        # Work in vertex select mode for deterministic behaviour.
        bpy.ops.mesh.select_mode(type='VERT')

        # Select non-manifold vertices and merge any within the threshold.
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        bpy.ops.object.mode_set(mode='OBJECT')

        print("Seams fixed successfully!")


def register():
    bpy.utils.register_class(FixSeamsOperator)


def unregister():
    bpy.utils.unregister_class(FixSeamsOperator)


if __name__ == "__main__":
    register()
