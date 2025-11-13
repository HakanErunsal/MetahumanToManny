# MetahumanToManny (Blender 4.2)

Tools to clean up MetaHuman meshes for Manny skeleton compatibility. Focus on vertex-group fixes, minor modeling ops, and armature-aligned cleanup.

## Requirements
- Blender 4.2.4 or newer (per `bl_info`)

## Installation
- Option A (ZIP): Use the packaged file in `dist/MetahumanToManny-1.0.10.zip`.
  - Blender → Edit → Preferences → Add-ons → Install → select the ZIP → enable "MetahumanToManny".
- Option B (Folder): Copy the folder `MetahumanToManny` into your Blender addons path.

## Where to find it
- 3D Viewport → Sidebar (N) → Tab: "MetahumanToManny" → Panel: "MetahumanToManny".

## Operators
- Clean Up Face Bone Weights (`object.cleanup_bone_weights`)
  - Select both a Mesh and its Armature. Merges child bone weights into `head`, `neck_02`, `neck_01`.
- Fix Twist Bone Names (`object.fix_twist_bone_names`)
  - Active object must be a Mesh. Renames `*twistCor*` groups to `*twist*` and removes duplicates.
- Fix Seams (`object.fix_seams`)
  - Active object must be a Mesh. Selects non-manifold and merges by distance (0.0001).
- Fix Toes Vertex Groups (`object.fix_toes`)
  - Active object must be a Mesh. Merges toe groups into `ball_l` / `ball_r`.
- Clean Up Unused Vertex Groups (`object.cleanup_unused_vertex_groups`)
  - Select both a Mesh and its Armature. Deletes mesh groups that don't map to pose bones.
- Fix Finger Bulges (`object.fix_finger_bulges`)
  - Active object must be a Mesh. Merges `*_bulge` groups into base groups and removes bulges.

