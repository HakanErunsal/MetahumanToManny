import bpy
import json
import os

from .utils import ensure_object_mode, get_mesh_and_armature


def load_bone_keep_list():
    """Load the bone keep list from bone_keep_list.json"""
    addon_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    json_path = os.path.join(addon_dir, "bone_keep_list.json")

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return set(data.get("bones_to_keep", []))
    except FileNotFoundError:
        print(f"Warning: bone_keep_list.json not found at {json_path}")
        return {"head", "spine_01", "spine_02", "spine_03"}
    except json.JSONDecodeError:
        print(f"Error: Could not parse bone_keep_list.json")
        return {"head", "spine_01", "spine_02", "spine_03"}


class InPlaceConversionOperator(bpy.types.Operator):
    bl_idname = "object.in_place_conversion"
    bl_label = "Convert Skeleton To Manny"
    bl_description = "One-click conversion: runs all cleanup operations and removes unused bones from armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh, armature = get_mesh_and_armature(context)

        if not mesh or not armature:
            self.report({'ERROR'}, "Please select both a mesh and an armature.")
            return {'CANCELLED'}

        ensure_object_mode(context)

        print("\n=== Starting In Place Conversion ===")

        # Step 1: Run cleanup_bone_weights (requires both mesh and armature selected)
        print("\n[1/4] Running Clean Up Face Bone Weights...")
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        armature.select_set(True)
        context.view_layer.objects.active = mesh
        bpy.ops.object.cleanup_bone_weights()

        # Step 2: Run cleanup_all_vertex_groups (mesh only)
        print("\n[2/4] Running Cleanup All Vertex Groups...")
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        context.view_layer.objects.active = mesh
        bpy.ops.object.cleanup_all_vertex_groups()

        # Step 3: Run fix_seams (mesh only)
        print("\n[3/4] Running Fix Seams...")
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        context.view_layer.objects.active = mesh
        bpy.ops.object.fix_seams()

        # Step 4: Delete bones not in keep list
        print("\n[4/4] Cleaning up armature bones...")
        bones_to_keep = load_bone_keep_list()
        print(f"Keeping {len(bones_to_keep)} bones: {sorted(bones_to_keep)}")

        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature

        deleted_count = self.delete_unwanted_bones(armature, bones_to_keep)
        print(f"Deleted {deleted_count} bones from armature")

        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True)
        armature.select_set(True)
        context.view_layer.objects.active = mesh

        self.report({'INFO'}, f"Conversion complete. Removed {deleted_count} bones.")
        print("\n=== In Place Conversion Complete ===")
        return {'FINISHED'}

    def delete_unwanted_bones(self, armature, bones_to_keep):
        """Delete all bones from armature that are not in the keep list"""
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            edit_bones = armature.data.edit_bones

            bones_to_delete = [bone.name for bone in edit_bones
                               if bone.name not in bones_to_keep]

            deleted_count = 0
            for bone_name in bones_to_delete:
                bone = edit_bones.get(bone_name)
                if bone:
                    edit_bones.remove(bone)
                    deleted_count += 1
        finally:
            # Never leave the armature stuck in Edit mode if removal raised.
            bpy.ops.object.mode_set(mode='OBJECT')

        return deleted_count


def register():
    bpy.utils.register_class(InPlaceConversionOperator)


def unregister():
    bpy.utils.unregister_class(InPlaceConversionOperator)


if __name__ == "__main__":
    register()
