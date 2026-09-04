import bpy
import re

from .utils import (
    find_all_lod_meshes,
    find_deform_armature,
    merge_vertex_group_weights,
    ensure_object_mode,
    get_target_mesh,
)

# MetaHuman hands carry helper joints in addition to the three segments Manny
# has per finger: bulge/half correctives, the mcp/pip/dip knuckles, the palm
# and side spreads, and the metacarpal slide. None of them exist on Manny, so
# every one has to fold back into the segment it belongs to or its vertices
# end up with no deforming bone at all.
_HELPER_SUFFIXES = (
    "palmMid", "side_inn", "side_out", "bulge", "half",
    "slide", "palm", "pip", "mcp", "dip", "in",
)

# Names look like "pinky_03_bulge_r" or "index_metacarpal_slide_l": the side
# suffix trails the helper name, which is why matching on a plain "_bulge"
# ending never fired. Anchoring the base to a finger segment keeps the pattern
# from touching body vertex groups that happen to end in "_in_l" and friends.
_HELPER_PATTERN = re.compile(
    r"^(?P<base>(?:thumb|index|middle|ring|pinky)_(?:[0-9]{2}|metacarpal))"
    r"_(?:" + "|".join(_HELPER_SUFFIXES) + r")"
    r"_(?P<side>[lr])$"
)


class FixFingerBulgesOperator(bpy.types.Operator):
    bl_idname = "object.fix_finger_bulges"
    bl_label = "Fix Finger Helpers"
    bl_description = ("Merges MetaHuman finger helper groups (bulge, half, mcp, pip, dip, "
                      "palm, side, slide) into their Manny finger bone and deletes them")
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
        merged_total = 0
        for idx, target_mesh in enumerate(meshes_to_process):
            print(f"\n=== Processing {target_mesh.name} ({idx + 1}/{total}) ===")
            merged_total += self.process_helpers(target_mesh)
            self.report({'INFO'}, f"Completed {target_mesh.name} ({idx + 1}/{total})")

        self.report({'INFO'}, f"Merged {merged_total} helper group(s) across {total} mesh(es).")
        return {'FINISHED'}

    def process_helpers(self, obj):
        """Merge every finger helper vertex group on a single mesh into its segment."""
        print(f"Processing finger helper vertex groups for object: {obj.name}")

        # The helper's target is always a real Manny finger bone, so the group can
        # be created when the mesh happens not to have it yet. Without an armature
        # to confirm that, stay conservative and only merge into existing groups.
        armature = find_deform_armature(obj)
        bone_names = set(armature.data.bones.keys()) if armature else None
        if bone_names is None:
            print("  No deforming armature found; merging only into existing groups.")

        merged = 0
        for vertex_group in list(obj.vertex_groups):
            match = _HELPER_PATTERN.match(vertex_group.name)
            if not match:
                continue

            source_name = vertex_group.name
            target_name = f"{match.group('base')}_{match.group('side')}"

            if bone_names is not None and target_name not in bone_names:
                print(f"Skipping '{source_name}': '{target_name}' is not a bone on {armature.name}")
                continue

            print(f"Merging '{source_name}' into '{target_name}'...")
            if merge_vertex_group_weights(obj, source_name, target_name,
                                          create_target=bone_names is not None,
                                          remove_source=True):
                merged += 1

        print(f"Finished processing finger helper vertex groups ({merged} merged).")
        return merged


def register():
    bpy.utils.register_class(FixFingerBulgesOperator)


def unregister():
    bpy.utils.unregister_class(FixFingerBulgesOperator)


if __name__ == "__main__":
    register()
