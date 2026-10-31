"""V20 reference-motion retarget and evaluated eight-view waist QA.
Uses unchanged V19 reference skeleton motion, not guessed native Euler axes.
"""
import math
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'taiwan_waist_v19'))
from waist_core import GLB, quaternion_matrix

C = np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]], dtype=float)


def slerp(a, b, t):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    dot = float(np.dot(a, b))
    if dot < 0: b = -b; dot = -dot
    if dot > .9995:
        q = a+t*(b-a); return q/np.linalg.norm(q)
    angle = math.acos(np.clip(dot, -1, 1))
    return (math.sin((1-t)*angle)*a+math.sin(t*angle)*b)/math.sin(angle)


class ReferenceMotion:
    def __init__(self, path):
        self.g = GLB(path)
        self.nodes = self.g.doc['nodes']
        self.rest = self.g.global_matrices()
        self.joints = {self.nodes[i]['name']: i for i in self.g.doc['skins'][0]['joints']}
        assert len(self.joints) == 53
        self.channels = []
        animations = self.g.doc.get('animations', [])
        if len(animations) != 1: raise ValueError('Expected one verified stress clip')
        for channel in animations[0]['channels']:
            s = animations[0]['samplers'][channel['sampler']]
            if s.get('interpolation', 'LINEAR') not in ('LINEAR', 'STEP'):
                raise ValueError('Unsupported reference interpolation')
            if channel['target']['path'] not in ('rotation', 'translation', 'scale'):
                raise ValueError('Reference clip must only animate bone transforms')
            self.channels.append((channel['target'], self.g.accessor(s['input']).ravel(),
                                  self.g.accessor(s['output']), s.get('interpolation', 'LINEAR')))

    def matrices(self, seconds):
        changes = {}
        for target, times, values, mode in self.channels:
            upper = int(np.searchsorted(times, seconds, side='right'))
            if upper == 0: value = values[0]
            elif upper >= len(times): value = values[-1]
            else:
                t = float((seconds-times[upper-1])/(times[upper]-times[upper-1]))
                a, b = values[upper-1], values[upper]
                if mode == 'STEP': value = a
                elif target['path'] == 'rotation': value = slerp(a, b, t)
                else: value = a*(1-t)+b*t
            changes.setdefault(target['node'], {})[target['path']] = value
        local = []
        for i, n in enumerate(self.nodes):
            props = dict(n); props.update(changes.get(i, {}))
            if 'matrix' in props:
                if i in changes: raise ValueError('Animated matrix node is unsupported')
                m = np.asarray(props['matrix']).reshape(4,4).T
            else:
                m = np.eye(4)
                m[:3,:3] = quaternion_matrix(props.get('rotation', [0,0,0,1])) @ np.diag(props.get('scale', [1,1,1]))
                m[:3,3] = props.get('translation', [0,0,0])
            local.append(m)
        parents = {c: i for i,n in enumerate(self.nodes) for c in n.get('children', [])}
        result = {}
        def resolve(i):
            if i not in result:
                result[i] = (resolve(parents[i]) if i in parents else np.eye(4)) @ local[i]
            return result[i]
        for i in range(len(local)): resolve(i)
        return result

    def native_pose(self, rig, seconds, frame, insert_keys=False):
        import bpy
        from mathutils import Matrix
        scene = bpy.context.scene; scene.frame_set(frame)
        desired = self.matrices(seconds)
        world = np.array(rig.matrix_world); inv_world = np.linalg.inv(world)
        ordered = sorted(rig.pose.bones, key=lambda b: len(b.bone.parent_recursive))
        targets = {}
        for bone in ordered:
            index = self.joints[bone.name]
            deformation = C @ desired[index] @ np.linalg.inv(self.rest[index]) @ C.T
            target = inv_world @ deformation @ world @ np.array(bone.bone.matrix_local)
            bone.rotation_mode = 'QUATERNION'
            bone.matrix = Matrix(target.tolist())
            targets[bone.name] = target
            bpy.context.view_layer.update()
        err = max(float(np.max(np.abs(np.array(b.matrix)-targets[b.name]))) for b in ordered)
        if err > 2e-4: raise AssertionError('Native rig did not reproduce reference deformation: '+str(err))
        if insert_keys:
            for bone in ordered:
                for prop in ('location', 'rotation_quaternion', 'scale'):
                    bone.keyframe_insert(data_path=prop, frame=frame, group=bone.name)
        return err


def arm_faces(body, rig):
    names = set()
    for side in ('l', 'r'):
        root = rig.data.bones['upperarm_'+side]
        names.add(root.name); names.update(b.name for b in root.children_recursive)
    group_names = {g.index: g.name for g in body.vertex_groups}
    weights = [sum(g.weight for g in v.groups if group_names.get(g.group) in names) for v in body.data.vertices]
    return [sum(weights[i] for i in p.vertices)/len(p.vertices) > .5 for p in body.data.polygons]


def evaluated_bvh(obj):
    import bpy
    from mathutils.bvhtree import BVHTree
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh = ev.to_mesh()
    try:
        if len(mesh.polygons) != len(obj.data.polygons): raise RuntimeError('Unexpected evaluated topology')
        return BVHTree.FromPolygons([ev.matrix_world @ v.co for v in mesh.vertices],
                                   [list(p.vertices) for p in mesh.polygons], all_triangles=False)
    finally: ev.to_mesh_clear()


def scan8(body, shirt, pants, limbs):
    from mathutils import Vector
    trees = [evaluated_bvh(o) for o in (body, shirt, pants)]
    rows = []
    def hit(tree, origin, direction):
        point, _, face, distance = tree.ray_cast(origin, direction, 2.)
        return (float(distance), face) if point is not None else (float('inf'), -1)
    for view in range(8):
        angle = view*math.pi/4
        radial = Vector((math.sin(angle), -math.cos(angle), 0))
        tangent = Vector((math.cos(angle), math.sin(angle), 0))
        row = {'degrees': view*45, 'rays': 1025, 'visible_waist_skin': 0,
               'waist_body_hits': 0, 'natural_limb_occlusions': 0}
        for iz in range(25):
            z = .94+.19*iz/24
            for ix in range(41):
                origin = radial+tangent*(-.18+.36*ix/40)+Vector((0,-.035,z))
                b, face = hit(trees[0], origin, -radial)
                s, _ = hit(trees[1], origin, -radial); p, _ = hit(trees[2], origin, -radial)
                if face < 0: continue
                if limbs[face]: row['natural_limb_occlusions'] += 1; continue
                row['waist_body_hits'] += 1
                if b < min(s,p)-.0015: row['visible_waist_skin'] += 1
        rows.append(row)
    return {'views': rows, 'rays': 8200,
            'visible_waist_skin': sum(r['visible_waist_skin'] for r in rows),
            'waist_body_hits': sum(r['waist_body_hits'] for r in rows)}
