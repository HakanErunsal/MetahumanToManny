"""Shared helpers for the MetahumanToManny operators.

Consolidates logic that was previously copy-pasted across the operator modules:
LOD discovery, vertex-group weight merging, Object-mode normalization, and
selection resolution.
"""

import bpy
import re

# Matches a trailing LOD suffix such as "_LOD0", "_LOD12".
_LOD_PATTERN = re.compile(r'_LOD\d+$')


def find_all_lod_meshes(base_mesh, return_prefix=False):
    """Find every LOD mesh that shares base_mesh's prefix (e.g. FaceMesh_LOD0, _LOD1, ...).

    Returns the LOD meshes sorted by name, or ``(lod_meshes, prefix)`` when
    ``return_prefix=True``. If no ``_LOD`` siblings are found, falls back to
    ``[base_mesh]`` (with the full name as the prefix).
    """
    base_name = base_mesh.name
    match = _LOD_PATTERN.search(base_name)
    # Strip the LOD suffix to get the shared prefix; otherwise use the full name.
    prefix = base_name[:match.start()] if match else base_name

    print(f"Looking for LOD meshes with prefix: '{prefix}'")

    lod_meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        obj_match = _LOD_PATTERN.search(obj.name)
        if obj_match and obj.name[:obj_match.start()] == prefix:
            lod_meshes.append(obj)
            print(f"  Found matching LOD: {obj.name}")

    if lod_meshes:
        lod_meshes.sort(key=lambda x: x.name)  # consistent ordering
        result = lod_meshes
    else:
        result = [base_mesh]

    return (result, prefix) if return_prefix else result


def merge_vertex_group_weights(obj, src_group_name, target_group_name,
                               create_target=False, remove_source=True):
    """Sum the weights of ``src_group_name`` into ``target_group_name`` per vertex.

    - ``create_target``: create the target group first if it is missing.
    - ``remove_source``: delete the source group after merging.

    Returns True if a merge happened, False if it was skipped (missing group or
    a self-merge). Guards against ``src == target`` so a real group is never
    summed onto itself and then deleted.
    """
    if create_target and target_group_name not in obj.vertex_groups:
        print(f"Creating target vertex group: {target_group_name}")
        obj.vertex_groups.new(name=target_group_name)

    if src_group_name == target_group_name:
        print(f"Skipping self-merge for '{src_group_name}'")
        return False

    src_group = obj.vertex_groups.get(src_group_name)
    target_group = obj.vertex_groups.get(target_group_name)
    if src_group is None or target_group is None:
        print(f"Skipping merge '{src_group_name}' -> '{target_group_name}': group not found.")
        return False

    for v in obj.data.vertices:
        try:
            src_weight = src_group.weight(v.index)
        except RuntimeError:
            src_weight = 0
        try:
            target_weight = target_group.weight(v.index)
        except RuntimeError:
            target_weight = 0
        target_group.add([v.index], src_weight + target_weight, 'REPLACE')

    if remove_source:
        print(f"Deleting vertex group: {src_group_name}")
        obj.vertex_groups.remove(src_group)
    return True


def ensure_object_mode(context):
    """Switch to Object mode if the active object is in another mode.

    Operators that call ``bpy.ops.object.*`` (select_all, mode_set, parent_set)
    poll-fail when invoked from Edit/Pose mode; calling this first lets the panel
    buttons work regardless of the mode the user started in.
    """
    if context.object and context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')


def get_target_mesh(context):
    """Resolve the mesh to operate on: the first selected mesh, else the active
    object if it is a mesh. Lets a tool run even when the armature is the active
    object but the target mesh is merely selected."""
    for obj in context.selected_objects:
        if obj.type == 'MESH':
            return obj
    if context.object and context.object.type == 'MESH':
        return context.object
    return None


def get_mesh_and_armature(context):
    """Resolve ``(mesh, armature)`` from the current selection (first of each)."""
    mesh = None
    armature = None
    for obj in context.selected_objects:
        if obj.type == 'MESH' and mesh is None:
            mesh = obj
        elif obj.type == 'ARMATURE' and armature is None:
            armature = obj
    return mesh, armature
