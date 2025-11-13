import bpy

class FixFingerBulgesOperator(bpy.types.Operator):
    bl_idname = "object.fix_finger_bulges"
    bl_label = "Fix Finger Bulges"
    bl_description = "Merge bulge vertex groups into their corresponding original groups and delete the bulge groups."

    def merge_vertex_groups(self, obj, src_group_name, target_group_name):
        """Merge weights from src_group_name into target_group_name and remove src_group_name."""
        if target_group_name not in obj.vertex_groups:
            self.report({'WARNING'}, f"Target vertex group '{target_group_name}' not found.")
            return

        if src_group_name not in obj.vertex_groups:
            self.report({'WARNING'}, f"Source vertex group '{src_group_name}' not found.")
            return

        # Get the source and target groups
        src_group = obj.vertex_groups[src_group_name]
        target_group = obj.vertex_groups[target_group_name]

        # Add weights from the source group to the target group
        for v in obj.data.vertices:
            try:
                src_weight = src_group.weight(v.index)
            except RuntimeError:
                src_weight = 0

            try:
                target_weight = target_group.weight(v.index)
            except RuntimeError:
                target_weight = 0

            merged_weight = src_weight + target_weight
            target_group.add([v.index], merged_weight, 'REPLACE')

        # Remove the source group
        obj.vertex_groups.remove(src_group)

    def execute(self, context):
        # Ensure a mesh object is selected
        obj = context.object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        print(f"Processing bulge vertex groups for object: {obj.name}")
        
        # Find and process all bulge vertex groups
        bulge_groups = [vg for vg in obj.vertex_groups if "bulge" in vg.name]
        for bulge_group in bulge_groups:
            bulge_name = bulge_group.name
            target_name = bulge_name.replace("_bulge", "")
            
            print(f"Merging '{bulge_name}' into '{target_name}'...")
            self.merge_vertex_groups(obj, bulge_name, target_name)

        print("Finished processing bulge vertex groups.")
        self.report({'INFO'}, "Finger bulge groups have been fixed.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FixFingerBulgesOperator)

def unregister():
    bpy.utils.unregister_class(FixFingerBulgesOperator)

if __name__ == "__main__":
    register()
