# MetahumanToManny

A Blender 4.2+ add-on that cleans up MetaHuman meshes and rigs so they bind to the UE5 **Manny** skeleton: vertex-group fixes, seam and weight cleanup, LOD hierarchy setup, and IK-bone generation.

## Requirements

Blender 4.2.0 or newer.

## Installation

1. Download `MetahumanToManny-<version>.zip` from the [Releases](https://github.com/HakanErunsal/MetahumanToManny/releases) page.
2. In Blender, open **Edit → Preferences → Get Extensions**, click the **⌄** menu (top right), choose **Install from Disk**, and pick the zip.

Find the panel under **3D Viewport → Sidebar (`N`) → MetahumanToManny** tab.

## Quick start

The **Quick Convert** section covers most conversions:

1. Export the MetaHuman skeletal meshes to Manny from Unreal, then import them into Blender.
2. Select one LOD mesh, then Shift-select the armature.
3. Click **Convert Skeleton To Manny**. The add-on processes the remaining LODs in the same run.
4. Optional: click **Generate IK Bones** to add the UE5 Manny IK bones.
5. Select an LOD mesh again and run **Setup LOD Hierarchy** (under Manual Steps).
6. Select every mesh plus the LOD empty, Shift-select the armature, and export.

### FBX export settings

| Setting | Value |
| --- | --- |
| Selected Objects | true |
| Object Types | Empty, Armature, Mesh |
| Forward | Y Forward |
| Up | Z Up |
| Smoothing | Face |
| Add Leaf Bones | false |

Only the face mesh needs material-section reordering.

## Panel layout

**Quick Convert** holds the two buttons most conversions need: **Convert Skeleton To Manny** and **Generate IK Bones**. **Manual Steps** (collapsed by default) holds each stage for one-at-a-time conversion.

## Operators

### Quick Convert

**Convert Skeleton To Manny** (`object.in_place_conversion`):
runs Clean Up Face Bone Weights, Cleanup All Vertex Groups, and Fix Seams on the selected mesh and its LODs, then removes every armature bone not in `bone_keep_list.json`.

**Generate IK Bones** (`object.generate_ik_bones`):
adds the UE5 Manny IK/auxiliary bones (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`, `interaction`, `center_of_mass`) to the selected armature. The bones are non-deforming, rebuild on re-run, and work on skeletons that have no root bone.

### Manual Steps

**Face Cleanup**
- **Clean Up Face Bone Weights** (`object.cleanup_bone_weights`): merges child-bone weights into `head`, `neck_02`, `neck_01`.

**Vertex Groups**
- **Cleanup All** (`object.cleanup_all_vertex_groups`): runs Fix Twist Bone Names, Fix Finger Helpers, and Fix Toes.
- **Fix Twist Bone Names** (`object.fix_twist_bone_names`): renames `*twistCor*` groups to `*twist*`, merging the weights into any existing `*twist*` group.
- **Fix Finger Helpers** (`object.fix_finger_bulges`): merges MetaHuman finger helper groups (`*_bulge_l`, `*_half_r`, `*_mcp_*`, `*_pip_*`, `*_dip_*`, `*_palm_*`, `*_palmMid_*`, `*_side_inn_*`, `*_side_out_*`, `*_in_*`, `*_slide_*`) into the Manny finger bone they belong to, then removes them. Without this the helper-only vertices at the pinky and ring fingertips bind to nothing.
- **Fix Toes** (`object.fix_toes`): merges toe groups into `ball_l` / `ball_r`.
- **Cleanup Unused Groups** (`object.cleanup_unused_vertex_groups`): with a mesh and its armature selected, deletes vertex groups that map to no bone.

**Mesh Cleanup**
- **Fix Seams** (`object.fix_seams`): merges duplicate seam vertices that break skinning after a rebind.

**Hierarchy**
- **Setup LOD Hierarchy** (`object.setup_lod_hierarchy`): parents the LOD meshes to a LodGroup empty so Unreal recognizes the LODs on import.
- **Bind to Manny** (`object.bind_to_manny`): binds the selected mesh to the Manny skeleton.
