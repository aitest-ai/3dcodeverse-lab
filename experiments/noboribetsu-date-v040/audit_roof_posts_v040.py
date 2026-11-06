#!/usr/bin/env python3
"""Read-only V040 audit of V039 original roof and wood-post GLBs.
Usage: python audit_roof_posts_v040.py /path/to/V039_inspector/assets
Requires numpy and trimesh. Never mutates any GLB.
"""
from pathlib import Path
import hashlib, json, sys
import numpy as np
import trimesh

SHAS = {
    'v004_merchant_facades.glb': '132ee6c0add22fbfe4a9872d82cb5e6bed0e2e4f282533b6c61de6c156a7a5e3',
    'v039_v004_right_gable_G.glb': 'bced01973a6a4c1909427092175ee924e73a1daed01b0f66608c60c0a91ffc03',
    'v039_v004_F_plus_right_gable_FG.glb': '5583d3d9c54eb19ac4396f4a9803e57fe337daeaf70e446c249a5337758d5985',
}
def main(folder):
    root = Path(folder)
    for name, expected in SHAS.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    g = trimesh.load(root / 'v039_v004_right_gable_G.glb', force='scene').geometry
    fg = trimesh.load(root / 'v039_v004_F_plus_right_gable_FG.glb', force='scene').geometry
    assert len(g) == len(fg) == 17
    for name in g:
        assert np.array_equal(g[name].faces, fg[name].faces), name
        if name != 'plaster_offwhite':
            assert np.array_equal(g[name].vertices, fg[name].vertices), name
    a, b = g['plaster_offwhite'].vertices, fg['plaster_offwhite'].vertices
    moved = np.flatnonzero(np.any(a != b, axis=1)).tolist()
    assert moved == [2, 3, 6, 7]
    assert np.allclose(a[moved, 1] - b[moved, 1], .225, atol=2e-6)
    wood = g['wood_dark']
    top_pairs = [(20, 21), (32, 33), (44, 45), (56, 57)]
    ys = []
    for pair in top_pairs:
        tris = wood.triangles[list(pair)]
        assert np.all(wood.face_normals[list(pair), 1] > .99)
        assert np.ptp(tris[:, :, 1]) < 1e-5
        ys.append(float(tris[0, 0, 1]))
    assert max(ys) - min(ys) < 1e-5
    roof_g, roof_fg, top = float(a[2, 1]), float(b[2, 1]), ys[0]
    report = {
        'pass': True, 'original_glbs_unchanged': True,
        'moved_plaster_vertex_ids': moved,
        'wood_top_face_pairs': top_pairs,
        'G_plaster_y': roof_g, 'FG_plaster_y': roof_fg, 'wood_top_y': top,
        'FG_wood_top_above_roof': top - roof_fg,
        'G_wood_top_above_roof': top - roof_g,
        'geometry_units_are_not_site_measurements': True,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
