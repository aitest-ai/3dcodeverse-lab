"""V20: port V19 ring fitting onto original MPFB meshes before GLB export.
Pure geometry is separate from bpy. No deletion, new faces, or baked body mask.
"""
from collections import Counter, defaultdict
import hashlib
import numpy as np


def periodic(theta, values, targets):
    order = np.argsort(theta)
    t, v = np.asarray(theta)[order], np.asarray(values)[order]
    return np.interp(targets, np.r_[t[-1]-2*np.pi, t, t[0]+2*np.pi],
                     np.r_[v[-1], v, v[0]])


def ring(points, polygons, upper):
    p = np.asarray(points, dtype=float)
    _, first, inverse = np.unique(np.round(p, 6), axis=0,
                                  return_index=True, return_inverse=True)
    welded = p[first]
    edges = Counter()
    for poly in polygons:
        ids = inverse[np.asarray(poly, dtype=int)]
        for a, b in zip(ids, np.roll(ids, -1)):
            if a != b: edges[tuple(sorted((int(a), int(b))))] += 1
    adjacent = defaultdict(set)
    for (a, b), count in edges.items():
        if count == 1: adjacent[a].add(b); adjacent[b].add(a)
    components, seen = [], set()
    for root in adjacent:
        if root in seen: continue
        pending, component = [root], []
        seen.add(root)
        while pending:
            v = pending.pop(); component.append(v)
            for n in adjacent[v]:
                if n not in seen: seen.add(n); pending.append(n)
        if len(component) >= 12 and np.ptp(welded[component, 0]) > .15:
            components.append(component)
    if not components: raise ValueError('No genuine wide garment opening')
    ids = (max if upper else min)(components,
                                 key=lambda x: welded[x, 2].mean())
    if any(len(adjacent[i]) != 2 for i in ids):
        raise ValueError('Garment boundary must form a closed loop')
    return welded, np.asarray(ids)


def displacement(pants, pant_faces, shirt, shirt_faces):
    points = np.asarray(pants, dtype=float)
    p, rim = ring(points, pant_faces, True)
    s, hem = ring(shirt, shirt_faces, False)
    if (len(p), len(rim), len(hem)) != (211, 16, 36):
        raise ValueError('Not the verified V19 cargo/tucked-shirt topology: '
                         + str((len(p), len(rim), len(hem))))
    center = np.array([0., (s[hem, 1].min()+s[hem, 1].max())/2])
    angle = lambda q: np.arctan2(q[:, 1]-center[1], q[:, 0]-center[0])
    theta, stheta = angle(p[rim]), angle(s[hem])
    floor = periodic(stheta, s[hem, 2], theta)+.014
    order = np.argsort(theta); reverse = np.argsort(order)
    heights = np.maximum(p[rim, 2], floor)[order]
    for _ in range(50):
        heights = np.maximum(floor[order], .25*np.roll(heights, 1)
                             +.5*heights+.25*np.roll(heights, -1))
    dz = heights[reverse]-p[rim, 2]
    radius = np.linalg.norm(p[rim, :2]-center, axis=1)
    sr = periodic(stheta, np.linalg.norm(s[hem, :2]-center, axis=1), theta)
    dr = np.maximum(radius, sr+.006)-radius
    a = angle(points); z = periodic(theta, p[rim, 2], a)
    fade = np.clip((points[:, 2]-(z-.16))/.16, 0, 1)
    fade = fade*fade*(3-2*fade)
    radial = points[:, :2]-center
    radial /= np.maximum(np.linalg.norm(radial, axis=1)[:, None], 1e-9)
    delta = np.zeros_like(points)
    delta[:, :2] = radial*periodic(theta, dr, a)[:, None]*fade[:, None]
    delta[:, 2] = periodic(theta, dz, a)*fade
    maximum = float(np.linalg.norm(delta, axis=1).max())
    if maximum > .045 or not np.isfinite(delta).all():
        raise ValueError('Unsafe source waist change; maximum '+str(maximum))
    return delta, {'original_pants_welded_vertices': len(p),
                   'waist_ring_vertices': len(rim), 'shirt_hem_vertices': len(hem),
                   'moved_source_vertices': int((np.linalg.norm(delta, axis=1)>1e-7).sum()),
                   'maximum_displacement_m': maximum,
                   'algorithm': 'V19 full-ring overlap + radial clearance + 16cm falloff'}


def coordinates(obj):
    local = np.array([tuple(v.co) for v in obj.data.vertices], dtype=float)
    mat = np.array(obj.matrix_world)
    return (np.column_stack((local, np.ones(len(local)))) @ mat.T)[:, :3]


def digest_mesh(obj):
    h = hashlib.sha256()
    h.update(np.array([tuple(v.co) for v in obj.data.vertices], dtype='<f4').tobytes())
    for face in obj.data.polygons:
        h.update(np.array(face.vertices[:], dtype='<i4').tobytes())
    for vertex in obj.data.vertices:
        for group in vertex.groups:
            h.update(np.array([group.group, group.weight], dtype='<f8').tobytes())
    for uv in obj.data.uv_layers:
        h.update(np.array([tuple(x.uv) for x in uv.data], dtype='<f4').tobytes())
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            h.update(key.name.encode())
            h.update(np.array([tuple(v.co) for v in key.data], dtype='<f4').tobytes())
    return h.hexdigest()


def apply_native(shirt, pants):
    import bpy
    before = coordinates(pants)
    delta, report = displacement(before, [p.vertices[:] for p in pants.data.polygons],
                                 coordinates(shirt), [p.vertices[:] for p in shirt.data.polygons])
    keys = list(pants.data.shape_keys.key_blocks) if pants.data.shape_keys else []
    originals = [np.array([tuple(v.co) for v in key.data]) for key in keys]
    local = np.array([tuple(v.co) for v in pants.data.vertices])
    local_delta = delta @ np.array(pants.matrix_world.inverted().to_3x3()).T
    old_faces = tuple(tuple(p.vertices) for p in pants.data.polygons)
    # Write all key positions from snapshots, avoiding Basis alias double-writes.
    pants.data.vertices.foreach_set('co', np.asarray(local+local_delta, dtype='f4').ravel())
    for key, old in zip(keys, originals):
        key.data.foreach_set('co', np.asarray(old+local_delta, dtype='f4').ravel())
    pants.data.update()
    pants.update_tag(refresh={'DATA'})
    bpy.context.view_layer.update()
    assert tuple(tuple(p.vertices) for p in pants.data.polygons) == old_faces
    error = 0.
    if keys:
        new_basis = np.array([tuple(v.co) for v in keys[0].data])
        for key, old in zip(keys[1:], originals[1:]):
            now = np.array([tuple(v.co) for v in key.data])
            error = max(error, float(np.max(np.abs((now-new_basis)-(old-originals[0])))))
        if error > 2e-6: raise AssertionError('Relative morph deltas changed')
    if not np.allclose(coordinates(pants), before+delta, atol=2e-6):
        raise AssertionError('Native coordinates did not accept world-space correction')
    report.update({'source_mesh_vertices': len(pants.data.vertices),
                   'source_mesh_faces': len(pants.data.polygons),
                   'shape_key_count_including_basis': len(keys),
                   'maximum_relative_morph_error': error,
                   'topology_preserved': True, 'native_mpfb_before_export': True})
    return report
