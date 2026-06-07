import bpy
from mathutils import Vector

# Canonical UE5 Manny / SKM_Manny IK + auxiliary bone layout.
# Each entry is (bone_name, parent_name, source_bone_to_copy_transform_from).
# A source of None means the bone is a static container placed at the origin
# (ik_foot_root, ik_hand_root, interaction, center_of_mass). A parent of "root"
# means the root bone if present, else top-level (see build_ik_bones).
# All generated bones are non-deforming and never connected to their parent.
IK_BONE_SPEC = [
    ("ik_foot_root",   "root",         None),
    ("ik_foot_l",      "ik_foot_root", "foot_l"),
    ("ik_foot_r",      "ik_foot_root", "foot_r"),
    ("ik_hand_root",   "root",         None),
    ("ik_hand_gun",    "ik_hand_root", "hand_r"),   # the weapon grip follows the right hand
    ("ik_hand_l",      "ik_hand_gun",  "hand_l"),   # off hand parented under the gun, not the root
    ("ik_hand_r",      "ik_hand_gun",  "hand_r"),
    ("interaction",    "root",         None),
    ("center_of_mass", "root",         None),
]

# Deform bones that must already exist for generation (the ones we copy transforms from).
# `root` is intentionally NOT required: many MetaHuman imports have no `root` bone
# (the FBX root node becomes the Armature object and `pelvis` is the top bone).
REQUIRED_SOURCE_BONES = ["foot_l", "foot_r", "hand_l", "hand_r"]


class GenerateIKBonesOperator(bpy.types.Operator):
    bl_idname = "object.generate_ik_bones"
    bl_label = "Generate IK Bones"
    bl_description = ("Generates the UE5 Manny IK/auxiliary bones (ik_foot_root, ik_foot_l/r, "
                      "ik_hand_root, ik_hand_gun, ik_hand_l/r, interaction, center_of_mass) on the "
                      "selected armature, rebuilding any that already exist")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Enabled whenever an armature is selected or active.
        if context.object and context.object.type == 'ARMATURE':
            return True
        return any(obj.type == 'ARMATURE' for obj in context.selected_objects)

    def execute(self, context):
        armature = self.find_armature(context)
        if not armature:
            self.report({'ERROR'}, "Please select an armature (the Manny skeleton).")
            return {'CANCELLED'}

        # Normalize to Object mode before changing selection / entering Edit mode,
        # so the operator works regardless of the mode the user started in.
        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        context.view_layer.objects.active = armature

        print("\n=== Generating Manny IK bones ===")
        print(f"Target armature: {armature.name}")

        bpy.ops.object.mode_set(mode='EDIT')
        try:
            created = self.build_ik_bones(armature)
        except Exception:
            # Never leave the user stranded in Edit mode if something goes wrong.
            bpy.ops.object.mode_set(mode='OBJECT')
            raise
        bpy.ops.object.mode_set(mode='OBJECT')

        if created is None:
            return {'CANCELLED'}

        self.report({'INFO'}, f"Generated {len(created)} IK bone(s) on {armature.name}.")
        print(f"Generated bones: {created}")
        print("=== IK bone generation complete ===")
        return {'FINISHED'}

    def find_armature(self, context):
        """Resolve the target armature, preferring the active object (mirrors poll() and the
        object whose mode execute() normalizes), then falling back to the first selected armature."""
        if context.object and context.object.type == 'ARMATURE':
            return context.object
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                return obj
        return None

    def build_ik_bones(self, armature):
        """Create the IK bone set in Edit mode. Returns the list of created names, or None on error."""
        edit_bones = armature.data.edit_bones

        # Validate the required source bones exist before touching anything.
        missing = [name for name in REQUIRED_SOURCE_BONES if name not in edit_bones]
        if missing:
            self.report({'ERROR'},
                        f"Armature is missing required Manny bone(s): {', '.join(missing)}. "
                        "Generate IK bones on a Manny-named skeleton.")
            return None

        # Capture source transforms up front (head/tail/roll) so later edits never
        # reference a half-built bone. Only the deform sources are needed.
        captured = {}
        for name in set(REQUIRED_SOURCE_BONES):
            src = edit_bones[name]
            captured[name] = (src.head.copy(), src.tail.copy(), src.roll)

        # The IK containers (ik_foot_root, ik_hand_root, interaction, center_of_mass) sit
        # under `root`. If a `root` bone exists, place them on it; otherwise place them at
        # the armature origin as top-level bones (siblings of pelvis) — which become
        # children of the root node again when the rig is exported back to FBX/UE.
        # A non-zero length is enforced so Blender never auto-deletes a zero-length bone.
        root_bone = edit_bones.get("root")
        if root_bone is not None:
            root_head, root_tail, root_roll = root_bone.head.copy(), root_bone.tail.copy(), root_bone.roll
            container_dir = root_tail - root_head
            if container_dir.length < 1e-5:
                container_dir = Vector((0.0, 0.0, 0.2))
            container_transform = (root_head, root_head + container_dir, root_roll)
            print("Parenting IK containers under the 'root' bone.")
        else:
            # Length taken from a deform bone so the markers are visible at the rig's scale.
            ref_head, ref_tail, _ = captured["foot_l"]
            ref_len = (ref_tail - ref_head).length or 0.1
            origin = Vector((0.0, 0.0, 0.0))
            container_transform = (origin, Vector((0.0, ref_len, 0.0)), 0.0)
            print("No 'root' bone found; creating IK containers as top-level bones at the origin.")

        # Regenerate: remove any existing bone that shares a target name.
        for name, _parent, _source in IK_BONE_SPEC:
            existing = edit_bones.get(name)
            if existing:
                edit_bones.remove(existing)
                print(f"Removed existing bone: {name}")

        # Create pass: build every bone with its rest transform first.
        created = []
        for name, _parent, source in IK_BONE_SPEC:
            head, tail, roll = captured[source] if source else container_transform
            bone = edit_bones.new(name)
            bone.head = head
            bone.tail = tail
            bone.roll = roll
            bone.use_deform = False     # IK/auxiliary bones skin no vertices
            bone.use_connect = False    # keep the copied transform; don't snap to parent tail
            created.append(name)
            label = f"copies {source}" if source else "at root origin"
            print(f"Created {name} ({label})")

        # Parent pass: wire up the hierarchy now that every bone exists. A spec parent of
        # "root" maps to the root bone, or to top-level (None) when there is no root bone.
        for name, parent, _source in IK_BONE_SPEC:
            bone = edit_bones[name]
            if parent == "root":
                bone.parent = root_bone  # None => top-level bone
                parent_label = "root" if root_bone else "(top level)"
            else:
                bone.parent = edit_bones[parent]
                parent_label = parent
            bone.use_connect = False
            print(f"Parented {name} -> {parent_label}")

        return created


def register():
    bpy.utils.register_class(GenerateIKBonesOperator)


def unregister():
    bpy.utils.unregister_class(GenerateIKBonesOperator)


if __name__ == "__main__":
    register()
