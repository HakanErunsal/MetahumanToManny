import bpy

class FixToesOperator(bpy.types.Operator):
    bl_idname = "object.fix_toes"
    bl_label = "Fix Toes Vertex Groups"
    bl_description = "Merge toe vertex groups into ball_l and ball_r, then delete the original groups"

    def execute(self, context):
        # Ensure a mesh object is selected
        if not bpy.context.object or bpy.context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        mesh = bpy.context.object
        print(f"Processing vertex groups for object: {mesh.name}")

        # Ensure the target groups ball_l and ball_r exist
        if "ball_l" not in mesh.vertex_groups:
            mesh.vertex_groups.new(name="ball_l")
        if "ball_r" not in mesh.vertex_groups:
            mesh.vertex_groups.new(name="ball_r")
        
        # Get all the vertex groups that contain "toe"
        toe_groups = [vg for vg in mesh.vertex_groups if "toe" in vg.name.lower()]

        if not toe_groups:
            self.report({'INFO'}, "No 'toe' vertex groups found.")
            return {'CANCELLED'}

        print(f"Found vertex groups to merge: {[vg.name for vg in toe_groups]}")

        # Separate into left and right toe groups based on the suffix (_l or _r)
        left_groups = [vg for vg in toe_groups if "_l" in vg.name]
        right_groups = [vg for vg in toe_groups if "_r" in vg.name]

        # Process left and right groups
        self.merge_and_clean(mesh, left_groups, "ball_l")
        self.merge_and_clean(mesh, right_groups, "ball_r")

        self.report({'INFO'}, "Vertex groups merged and cleaned.")
        return {'FINISHED'}

    def merge_and_clean(self, mesh, groups, target_group_name):
        """Merges the weights from the specified groups into the target group and deletes the original groups."""
        target_group = mesh.vertex_groups.get(target_group_name)

        for group in groups:
            group_name = group.name
            print(f"Merging weights of group '{group_name}' into '{target_group_name}'")

            # Merge the weights into the target group
            self.merge_vertex_group_weights(mesh, group_name, target_group_name)

            # Remove the original group after merging
            mesh.vertex_groups.remove(group)
            print(f"Deleted vertex group: {group_name}")

    def merge_vertex_group_weights(self, obj, src_group_name, target_group_name):
        """Merges the weights from the source vertex group into the target vertex group."""
        src_group = obj.vertex_groups.get(src_group_name)
        target_group = obj.vertex_groups.get(target_group_name)

        if not src_group or not target_group:
            return
        
        # Merge the weights from the source to the target group
        for v in obj.data.vertices:
            try:
                src_weight = src_group.weight(v.index)
            except RuntimeError:
                src_weight = 0

            try:
                target_weight = target_group.weight(v.index)
            except RuntimeError:
                target_weight = 0

            # Add the merged weight to the target group
            merged_weight = src_weight + target_weight
            target_group.add([v.index], merged_weight, 'REPLACE')

def register():
    bpy.utils.register_class(FixToesOperator)

def unregister():
    bpy.utils.unregister_class(FixToesOperator)

if __name__ == "__main__":
    register()
