"""blender -b working.blend --python this.py -- /absolute/work/new-version.glb
This exports a NEW review candidate, not a byte-identical or VRM roundtrip promise.
"""
import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
assert out.suffix=='.glb' and not out.exists(),'Choose a new .glb path'
assert not out.is_relative_to(R/'library-v04') and not out.is_relative_to(R/'sources-v04'),'Never overwrite locked assets/sources'
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_rest_position_armature=True)
print('NEW_CANDIDATE_REQUIRES_REVIEW',out)
