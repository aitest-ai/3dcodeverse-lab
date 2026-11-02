#!/usr/bin/env python3
"""V027 read-only version-contract audit: no assets are uploaded or changed."""
import sys, zipfile, hashlib, json
if len(sys.argv)!=3: raise SystemExit("usage: python audit_v027_archive.py V025_Runtime.zip V026_Runtime.zip")
def sha(b):return hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(sys.argv[1]) as a, zipfile.ZipFile(sys.argv[2]) as b:
    ap=set(a.namelist()); bp=set(b.namelist())
    assert (len(ap),len(bp))==(134,137)
    changed=sorted(n for n in ap & bp if sha(a.read(n)) != sha(b.read(n)))
    assert changed==['dist/app.js','dist/index.html','dist/qa.json','dist/scene_view.json'],changed
    added=sorted(bp-ap)
    assert added==['README_V026.md','dist/assets/v026_v004_sash_depth.glb','dist/v026_sash_depth.json'],added
    assert len(ap & bp)-len(changed)==130
    c=json.loads(b.read('dist/v026_sash_depth.json'))
    assert sha(b.read('dist/assets/v026_v004_sash_depth.glb'))==c['new_glb_sha256']
    assert sha(b.read('dist/assets/v025_v004_pbr_microdetail.glb'))==c['source_v025_sha256']
    assert len(json.loads(b.read('dist/scene_view.json'))['route'])==472
    assert c['triangles']==952 and c['retained_base_triangles']==792
    assert not c['route_changed'] and not c['collision_changed']
    print(json.dumps({'result':'PASS','unchanged':130,'modified':changed,'new':added,'route_points':472,'native_blender':'PENDING'},ensure_ascii=False,indent=2))
