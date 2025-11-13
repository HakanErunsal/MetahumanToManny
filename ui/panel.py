import bpy

class BoneWeightCleanupPanel(bpy.types.Panel):
    bl_label = "MetahumanToManny"
    bl_idname = "OBJECT_PT_bone_weight_cleanup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MetahumanToManny'

    def draw(self, context):
        layout = self.layout

        layout.label(text="Bone Weight Tools:")
        layout.operator("object.cleanup_bone_weights", text="Clean Up Face Bone Weights")
        layout.operator("object.fix_twist_bone_names", text="Fix Twist Bone Names")
        layout.operator("object.fix_seams", text="Fix seams")
        layout.operator("object.fix_toes", text="Fix toes")
        layout.operator("object.cleanup_unused_vertex_groups", text="Cleanup unused vertex groups")
        layout.operator("object.fix_finger_bulges", text="Fix finger bulges")

def register():
    bpy.utils.register_class(BoneWeightCleanupPanel)


def unregister():
    bpy.utils.unregister_class(BoneWeightCleanupPanel)
