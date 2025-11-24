from .operators import cleanup_bone_weights, fix_twist_bone_names, fix_seams, fix_toes, cleanup_unused_vertex_groups, fix_finger_bulges, setup_lod_hierarchy, cleanup_all_vertex_groups, bind_to_manny, in_place_conversion
from .ui import panel

bl_info = {
    "name": "MetahumanToManny",
    "blender": (4, 2, 4),
    "category": "Object",
    "author": "Hakan",
    "version": (1, 2, 0),
    "description": "Collection of tools for cleaning up armature vertex groups and fixing issues to make it compatible with Manny.",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "warning": "",
}

def register():
    cleanup_bone_weights.register()
    fix_twist_bone_names.register()
    fix_seams.register()
    fix_toes.register()
    cleanup_unused_vertex_groups.register()
    fix_finger_bulges.register()
    setup_lod_hierarchy.register()
    cleanup_all_vertex_groups.register()
    bind_to_manny.register()
    in_place_conversion.register()
    panel.register()

def unregister():
    cleanup_bone_weights.unregister()
    fix_twist_bone_names.unregister()
    fix_seams.unregister()
    fix_toes.unregister()
    cleanup_unused_vertex_groups.unregister()
    fix_finger_bulges.unregister()
    setup_lod_hierarchy.unregister()
    cleanup_all_vertex_groups.unregister()
    bind_to_manny.unregister()
    in_place_conversion.unregister()
    panel.unregister()

if __name__ == "__main__":
    register()
