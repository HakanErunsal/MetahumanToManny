import bpy
from .operators import cleanup_bone_weights, fix_twist_bone_names, fix_seams, fix_toes, cleanup_unused_vertex_groups, fix_finger_bulges
from .ui import panel

bl_info = {
    "name": "MetahumanToManny",
    "blender": (4, 2, 4),
    "category": "Object",
    "author": "Hakan",
    "version": (1, 0, 10),
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
    panel.register()

def unregister():
    cleanup_bone_weights.unregister()
    fix_twist_bone_names.unregister()
    fix_seams.unregister()
    fix_toes.unregister()
    cleanup_unused_vertex_groups.unregister()
    fix_finger_bulges.unregister()
    panel.unregister()

if __name__ == "__main__":
    register()
