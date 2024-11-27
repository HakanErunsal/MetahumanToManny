# MetahumanToManny
This blender script helps convert and bind metahuman skeletal mesh to manny (ue5 skeleton)

# Requirements
Install the addon in blender
Install [game rig tools](https://toshicg.gumroad.com/l/game_rig_tools)

# 1. Export & Import
Export metahuman skeletal mesh from unreal either using a level sequencer or separately
Import it to blender

# 2. Fixing the head
Head has a lot of additional bones, and these branch bones causing issues with ue5 manny because it does not have them. Select the head mesh and the skeleton that comes with it. Run "Clean Up Face Bone Weights" and "Fix seams". And then run "Cleanup unused vertex groups" if you don't want to use them for blendshapes.

# 3. Fixing the body
Select the body, run "Fix Twist Bone Names", "Fix toes", "Fix seams" and "Cleanup unused vertex groups". Depending on your situation and your goal, you can skip some of these, up to you.

# 4. Reparenting the mesh
Go to Game Rig Tools, initiate a mannequin, fix your rest pose to match the metahuman rest pose. Apply rig.
Select both body and face mesh, Alt+P and "Clear and Keep Transformation", this will detach them from their skeleton, from now on, you can just delete the armatures that comes with metahuman as it is unnecessary to keep them. Select body and face again, then select the Deform Armature of the Game Rig Tool, Ctrl+P "With Empty Groups". Done.

Now your metahuman will be fully compatible with unreal 5 mannequin. You can export by selecting body, face and the skeleton after switching parent armature to Unreal, import it to unreal 5 with using UE5 Mannequin as skeleton.
