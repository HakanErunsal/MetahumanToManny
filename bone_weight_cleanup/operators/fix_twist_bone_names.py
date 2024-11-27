import bpy

class FixTwistBoneNamesOperator(bpy.types.Operator):
    bl_idname = "object.fix_twist_bone_names"
    bl_label = "Fix Twist Bone Names"
    bl_description = "Renames 'twistCor' vertex groups to 'twist' and removes corresponding 'twist' groups if they exist"

    def execute(self, context):
        # Ensure there is a mesh object selected
        if not context.object or context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        mesh = context.object
        print(f"Processing vertex groups for object: {mesh.name}")
        
        # Get all the vertex groups
        vertex_groups = mesh.vertex_groups
        twist_cor_groups = [vg for vg in vertex_groups if "twistCor" in vg.name]

        if not twist_cor_groups:
            self.report({'INFO'}, "No 'twistCor' vertex groups found.")
            return {'CANCELLED'}

        print(f"Found twistCor groups: {[vg.name for vg in twist_cor_groups]}")

        # Loop through each "twistCor" vertex group
        for twist_cor_group in twist_cor_groups:
            # Find the name of the corresponding group without "Cor"
            corresponding_group_name = twist_cor_group.name.replace("twistCor", "twist")
            corresponding_group = vertex_groups.get(corresponding_group_name)

            # If the corresponding group exists, delete it
            if corresponding_group:
                print(f"Found corresponding group: {corresponding_group_name}, removing it.")
                vertex_groups.remove(corresponding_group)
            else:
                print(f"No corresponding group found for: {twist_cor_group.name}")

            # Rename the "twistCor" group by removing "Cor"
            new_group_name = twist_cor_group.name.replace("twistCor", "twist")
            print(f"Renaming group {twist_cor_group.name} to {new_group_name}")
            twist_cor_group.name = new_group_name

        self.report({'INFO'}, "Finished processing 'twistCor' vertex groups.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FixTwistBoneNamesOperator)

def unregister():
    bpy.utils.unregister_class(FixTwistBoneNamesOperator)

if __name__ == "__main__":
    register()