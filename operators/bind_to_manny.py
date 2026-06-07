import bpy

from .utils import find_all_lod_meshes, ensure_object_mode, get_mesh_and_armature


class BindToMannyOperator(bpy.types.Operator):
    bl_idname = "object.bind_to_manny"
    bl_label = "Bind to Manny"
    bl_description = "Binds selected mesh (and its LODs) to Manny skeleton with empty groups and scales to 0.01"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.metahuman_to_manny_settings

        mesh, armature = get_mesh_and_armature(context)
        if not mesh or not armature:
            self.report({'ERROR'}, "Please select both a mesh and an armature (Manny skeleton).")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Find all LOD meshes if enabled
        if settings.bAutoLookForLOD:
            meshes_to_process = find_all_lod_meshes(mesh)
            if len(meshes_to_process) > 1:
                self.report({'INFO'}, f"Found {len(meshes_to_process)} LOD meshes to process")
        else:
            meshes_to_process = [mesh]

        print(f"\n=== Binding to Manny skeleton ===")
        print(f"Target armature: {armature.name}")
        print(f"Meshes to bind: {[obj.name for obj in meshes_to_process]}")

        # Process each mesh
        total = len(meshes_to_process)
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")

            # Clear selection and select only the current mesh
            bpy.ops.object.select_all(action='DESELECT')
            target_mesh.select_set(True)
            context.view_layer.objects.active = target_mesh

            # Clear any existing parent with keep transform
            if target_mesh.parent:
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                print(f"Cleared parent from {target_mesh.name} (kept transform)")

            # Remove existing armature modifiers
            for mod in list(target_mesh.modifiers):
                if mod.type == 'ARMATURE':
                    target_mesh.modifiers.remove(mod)

            # Select armature as well for parenting operation
            armature.select_set(True)
            context.view_layer.objects.active = armature

            # Set armature as parent with empty groups (using operator)
            bpy.ops.object.parent_set(type='ARMATURE_NAME')

            print(f"Bound {target_mesh.name} to {armature.name} with empty groups")

            # Scale mesh to 0.01 (100 times smaller for Unreal to Blender conversion)
            target_mesh.scale = (0.01, 0.01, 0.01)

            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")

        self.report({'INFO'}, f"Bound and scaled {total} mesh(es) to {armature.name}.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BindToMannyOperator)


def unregister():
    bpy.utils.unregister_class(BindToMannyOperator)


if __name__ == "__main__":
    register()
