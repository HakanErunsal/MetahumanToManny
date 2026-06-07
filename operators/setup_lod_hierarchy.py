import bpy
import re

from .utils import find_all_lod_meshes, ensure_object_mode, get_target_mesh


class SetupLodHierarchyOperator(bpy.types.Operator):
    bl_idname = "object.setup_lod_hierarchy"
    bl_label = "Setup LOD Hierarchy"
    bl_description = "Parents all LOD meshes to their LodGroup object and sets up Unreal Engine LOD recognition"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = get_target_mesh(context)
        if not mesh:
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        # Find all LOD meshes (and the shared prefix).
        lod_meshes, prefix = find_all_lod_meshes(mesh, return_prefix=True)

        # Warn when the mesh has no LOD siblings, so inconsistent naming
        # (e.g. "Body_LOD_0" which the _LOD\d+ pattern rejects) is visible.
        if len(lod_meshes) == 1:
            self.report({'WARNING'},
                        f"No LOD siblings found for '{mesh.name}'. "
                        f"Expected names like '{prefix}_LOD0', '{prefix}_LOD1'. "
                        "Creating a single-mesh LodGroup.")

        # Look for or create the LodGroup object
        lod_group_name = f"{prefix}_LodGroup"

        # Always delete existing LodGroup object if it exists
        lod_group = bpy.data.objects.get(lod_group_name)
        if lod_group:
            for coll in lod_group.users_collection:
                coll.objects.unlink(lod_group)
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

        # Parent all LOD meshes to the LodGroup, keeping their transforms.
        for lod_mesh in lod_meshes:
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

        self.report({'INFO'}, f"Parented {len(lod_meshes)} mesh(es) to {lod_group_name}.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SetupLodHierarchyOperator)


def unregister():
    bpy.utils.unregister_class(SetupLodHierarchyOperator)


if __name__ == "__main__":
    register()
