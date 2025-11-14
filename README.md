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

### Face Cleanup
- **Clean Up Face Bone Weights** (`object.cleanup_bone_weights`)
  - Merges child bone weights into `head`, `neck_02`, `neck_01`.

### Vertex Groups
- **Cleanup All** (`object.cleanup_all_vertex_groups`)
  - Runs all vertex group cleanup operations: Fix Twist Bones, Fix Finger Bulges, Fix Toes.
- **Fix Twist Bone Names** (`object.fix_twist_bone_names`)
  - Renames `*twistCor*` groups to `*twist*` and removes duplicates.
- **Fix Finger Bulges** (`object.fix_finger_bulges`)
  - Merges `*_bulge` groups into base groups and removes bulges.
- **Fix Toes** (`object.fix_toes`)
  - Merges toe groups into `ball_l` / `ball_r`.
- **Cleanup Unused Groups** (`object.cleanup_unused_vertex_groups`)
  - Select both a Mesh and its Armature. Deletes vertex groups that don't map to bones.

### Mesh Cleanup
- **Fix Seams** (`object.fix_seams`)
  - Get rid of seams that cause problems after binding to new skeleton.

### Hierarchy
- **Setup LOD Hierarchy** (`object.setup_lod_hierarchy`)
  - Sets up the LOD mesh hierarchy for the selected mesh.
- **Bind to Manny** (`object.bind_to_manny`)
  - Binds the selected mesh to the Manny skeleton.