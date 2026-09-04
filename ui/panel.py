import bpy


class MetahumanToMannySettings(bpy.types.PropertyGroup):
    bAutoLookForLOD: bpy.props.BoolProperty(
        name="Auto Find LODs",
        description="Automatically find and process all LOD meshes (LOD0, LOD1, LOD2, etc.)",
        default=True
    )


class OBJECT_PT_metahuman_to_manny(bpy.types.Panel):
    """Main panel: the one-click path most users need."""
    bl_label = "MetahumanToManny"
    bl_idname = "OBJECT_PT_metahuman_to_manny"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MetahumanToManny'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.metahuman_to_manny_settings

        # Primary one-click workflow.
        box = layout.box()
        box.label(text="Quick Convert", icon='MODIFIER')
        col = box.column(align=True)
        col.scale_y = 1.5
        col.operator("object.in_place_conversion", text="Convert Skeleton To Manny", icon='ARMATURE_DATA')
        col.operator("object.generate_ik_bones", text="Generate IK Bones", icon='CON_KINEMATIC')

        # Settings.
        box = layout.box()
        box.label(text="Settings", icon='PREFERENCES')
        box.prop(settings, "bAutoLookForLOD")


class OBJECT_PT_metahuman_to_manny_manual(bpy.types.Panel):
    """Collapsible sub-panel: the individual steps, for converting one stage at a time."""
    bl_label = "Manual Steps (optional)"
    bl_idname = "OBJECT_PT_metahuman_to_manny_manual"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MetahumanToManny'
    bl_parent_id = "OBJECT_PT_metahuman_to_manny"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Face section
        box = layout.box()
        box.label(text="Face Cleanup", icon='MESH_DATA')
        box.operator("object.cleanup_bone_weights", text="Clean Up Face Bone Weights")

        # Vertex Groups section
        box = layout.box()
        box.label(text="Vertex Groups", icon='GROUP_VERTEX')
        box.operator("object.cleanup_all_vertex_groups", text="Cleanup All")
        box.separator()
        box.operator("object.fix_twist_bone_names", text="Fix Twist Bone Names")
        box.operator("object.fix_finger_bulges", text="Fix Finger Helpers")
        box.operator("object.fix_toes", text="Fix Toes")
        box.operator("object.cleanup_unused_vertex_groups", text="Cleanup Unused Groups")

        # Mesh Cleanup section
        box = layout.box()
        box.label(text="Mesh Cleanup", icon='MESH_CUBE')
        box.operator("object.fix_seams", text="Fix Seams")

        # Hierarchy section
        box = layout.box()
        box.label(text="Hierarchy", icon='OUTLINER')
        box.operator("object.setup_lod_hierarchy", text="Setup LOD Hierarchy")
        box.operator("object.bind_to_manny", text="Bind to Manny")


# Parent panel must be registered before its child sub-panel.
classes = (
    MetahumanToMannySettings,
    OBJECT_PT_metahuman_to_manny,
    OBJECT_PT_metahuman_to_manny_manual,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.metahuman_to_manny_settings = bpy.props.PointerProperty(type=MetahumanToMannySettings)


def unregister():
    del bpy.types.Scene.metahuman_to_manny_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
