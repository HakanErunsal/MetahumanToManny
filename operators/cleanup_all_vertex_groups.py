import bpy

class CleanupAllVertexGroupsOperator(bpy.types.Operator):
    bl_idname = "object.cleanup_all_vertex_groups"
    bl_label = "Cleanup All"
    bl_description = "Runs all vertex group cleanup operations: Fix Twist Bones, Fix Finger Bulges, Fix Toes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure a mesh object is selected
        if not context.object or context.object.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        print("\n=== Running All Vertex Group Cleanups ===")
        
        # Run Fix Twist Bone Names
        print("\n[1/3] Running Fix Twist Bone Names...")
        bpy.ops.object.fix_twist_bone_names()
        
        # Run Fix Finger Bulges
        print("\n[2/3] Running Fix Finger Bulges...")
        bpy.ops.object.fix_finger_bulges()
        
        # Run Fix Toes
        print("\n[3/3] Running Fix Toes...")
        bpy.ops.object.fix_toes()
        
        self.report({'INFO'}, "All vertex group cleanups completed!")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CleanupAllVertexGroupsOperator)

def unregister():
    bpy.utils.unregister_class(CleanupAllVertexGroupsOperator)

if __name__ == "__main__":
    register()
