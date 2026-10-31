"""V23 character-specific native seam repair, pinned to the V22 source.
The seven inner/outer pairs were diagnosed from the actual neutral mesh.
Reject a different source or ambiguous mapping; do not move the outer lip,
raise the waistband, create faces, edit UVs/weights, or paint over the gap.
"""
import numpy as np
from source_waist import coordinates
from local_cloth import write_world

# World positions from the verified V22 output, used only to identify original
# native source vertices; live source coordinates determine each displacement.
PAIRS=[
([-0.01560523489,-0.17383825817,0.95184624745],[-0.01445017705,-0.17386630344,0.95205504961]),
([-0.01163039281,-0.17425511623,0.96012609992],[-0.01056832669,-0.17425939610,0.96021415385]),
([-0.00015075372,-0.17520900565,0.96901521821],[0.00103153374,-0.17528498466,0.96938821332]),
([-0.01957816488,-0.17322735602,0.94249642470],[-0.01849811972,-0.17326848643,0.94270297235]),
([-0.02003523812,-0.17246321426,0.93339467705],[-0.01891309294,-0.17272383537,0.93434694124]),
([-0.01617393411,-0.17151702298,0.92794748124],[-0.01515520330,-0.17164389239,0.92844309896]),
([-0.01135205118,-0.17050421303,0.92239081568],[-0.01080111208,-0.17059382351,0.92276558214])]


def apply(pants):
    points=coordinates(pants);target=points.copy();rows=[];changed=[]
    for inner_ref,outer_ref in PAIRS:
        ids=[]
        for ref in (inner_ref,outer_ref):
            distance=np.linalg.norm(points-np.asarray(ref),axis=1)
            matches=np.where(distance<8e-6)[0]
            if len(matches)!=1:
                raise RuntimeError('Native lip match not unique '+str((ref,matches.tolist(),float(distance.min()))))
            ids.append(int(matches[0]))
        inner,outer=ids
        # +Y is behind the front-facing panel; +X is toward its covered area.
        target[inner]=points[outer]+np.asarray([.0002,.0012,0.])
        changed.append(inner)
        rows.append({'inner_native_vertex':inner,'outer_native_vertex':outer,
                     'before_world':points[inner].tolist(),'outer_world':points[outer].tolist(),
                     'after_world':target[inner].tolist()})
    if len(set(changed))!=7 or set(changed)&{r['outer_native_vertex'] for r in rows}:
        raise RuntimeError('Source lip correspondence overlaps')
    delta=target-points;length=np.linalg.norm(delta,axis=1)
    if length.max()>.002:raise RuntimeError('More than 2mm requested; reject rather than stretch cloth')
    write_world(pants,target)
    return {'method':'seven original inner lip points tucked behind paired unchanged outer edge',
            'pairs':rows,'changed_vertices':int((length>1e-7).sum()),
            'maximum_shift_m':float(length.max()),'maximum_height_change_m':float(abs(delta[:,2]).max()),
            'outer_lip_unchanged':True,'upper_body_unchanged':True,
            'source_specific_not_general_remesher':True,'inset_x_m':.0002,'behind_outer_y_m':.0012}
