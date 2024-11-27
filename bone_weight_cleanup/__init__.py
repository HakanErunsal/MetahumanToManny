import bpy
from .operators import cleanup_bone_weights, fix_twist_bone_names, fix_seams, fix_toes, cleanup_unused_vertex_groups
from .ui import panel

bl_info = {
    "name": "Bone Weight Cleanup",
    "blender": (4, 2, 4),
    "category": "Object",
    "author": "Hakan",
    "version": (1, 0, 7),
    "description": "Collection of tools for cleaning up armature vertex groups and more.",
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
    panel.register()


def unregister():
    cleanup_bone_weights.unregister()
    fix_twist_bone_names.unregister()
    fix_seams.unregister()
    fix_toes.unregister()
    cleanup_unused_vertex_groups.unregister()
    panel.unregister()


if __name__ == "__main__":
    register()
