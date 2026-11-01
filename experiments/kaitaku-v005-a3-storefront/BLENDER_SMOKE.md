# V005 A3 Blender 5.2.3 bpy Smoke

Status: **PASS**.

GitHub Actions run `41265998752` downloaded official Blender **5.2.3 LTS**, verified the official Blender SHA256, and then executed `scripts/blender5/kaitaku_v005_a3_smoke.py` using real `bpy`.

## Verified code paths

- FinalPolish A global closed-window backing/reveal material assignment.
- A3 local storefront material-copy and reassignment path.
- Five synthetic `V005 clustered grass` objects through the real grass component rebuild helper.
- Protected geometry sentinel hash remains unchanged.
- Runtime A and A3 pinned hashes are available to the Blender helper module.

Synthetic grass fixture:
- objects: 5
- components before: 280
- components removed: 205
- components kept: 75

This is deliberately a small synthetic fixture. It proves the helper code executes in real Blender 5.2.3; it does **not** replace the future full 456 MB V005 master writeback and native render review.

The full `blender-candidate` job remains gated on a same-repository source artifact whose V005 .blend and baseline GLB hashes must match the pinned values.
