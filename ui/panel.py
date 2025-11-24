import bpy

class MetahumanToMannySettings(bpy.types.PropertyGroup):
    bAutoLookForLOD: bpy.props.BoolProperty(
        name="Auto Find LODs",
        description="Automatically find and process all LOD meshes (LOD0, LOD1, LOD2, etc.)",
        default=True
    )

class BoneWeightCleanupPanel(bpy.types.Panel):
    bl_label = "MetahumanToManny"
    bl_idname = "OBJECT_PT_bone_weight_cleanup"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MetahumanToManny'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.metahuman_to_manny_settings

        # In Place Conversion section (top)
        box = layout.box()
        box.label(text="In Place Conversion", icon='MODIFIER')
        box.operator("object.in_place_conversion", text="In Place Conversion")
        
        layout.separator()

        # Settings section
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        box.prop(settings, "bAutoLookForLOD")
        
        layout.separator()

        # Face section
        box = layout.box()
        box.label(text="Face Cleanup", icon='MESH_DATA')
        box.operator("object.cleanup_bone_weights", text="Clean Up Face Bone Weights")
        
        layout.separator()

        # Vertex Groups section
        box = layout.box()
        box.label(text="Vertex Groups", icon='GROUP_VERTEX')
        box.operator("object.cleanup_all_vertex_groups", text="Cleanup All")
        box.separator()
        box.operator("object.fix_twist_bone_names", text="Fix Twist Bone Names")
        box.operator("object.fix_finger_bulges", text="Fix Finger Bulges")
        box.operator("object.fix_toes", text="Fix Toes")
        box.operator("object.cleanup_unused_vertex_groups", text="Cleanup Unused Groups")
        
        layout.separator()

        # Mesh Cleanup section
        box = layout.box()
        box.label(text="Mesh Cleanup", icon='MESH_CUBE')
        box.operator("object.fix_seams", text="Fix Seams")
        
        layout.separator()

        # Hierarchy section
        box = layout.box()
        box.label(text="Hierarchy", icon='OUTLINER')
        box.operator("object.setup_lod_hierarchy", text="Setup LOD Hierarchy")
        box.operator("object.bind_to_manny", text="Bind to Manny")

def register():
    bpy.utils.register_class(MetahumanToMannySettings)
    bpy.utils.register_class(BoneWeightCleanupPanel)
    bpy.types.Scene.metahuman_to_manny_settings = bpy.props.PointerProperty(type=MetahumanToMannySettings)


def unregister():
    del bpy.types.Scene.metahuman_to_manny_settings
    bpy.utils.unregister_class(BoneWeightCleanupPanel)
    bpy.utils.unregister_class(MetahumanToMannySettings)
