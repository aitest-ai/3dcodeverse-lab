"""Attach real MakeHuman Faceunits 01 CC0 morphs to *morphed*, baked MPFB human.

This module never fabricates facial vertex motions. It reads the real official
Mika Suominen .target files, ignores deleted MPFB helper vertices >= 13380,
uses TargetService's own target parser / scale transform, and verifies that
every shape differs from the original 13,380-vertex basis.
"""
from pathlib import Path
import json,math

# Each right-side value is an actual Faceunits01 target filename (minus extension).
# These preserve requested game naming; "mouthOpen" aliases ARKit jawOpen.
FACE_MORPHS = {
    "mouthOpen": "jawOpen",
    "jawLeft": "jawLeft",
    "jawRight": "jawRight",
    "mouthSmileLeft": "mouthSmileLeft",
    "mouthSmileRight": "mouthSmileRight",
    "eyeBlinkLeft": "eyeBlinkLeft",
    "eyeBlinkRight": "eyeBlinkRight",
    "browInnerUp": "browInnerUp",
    "mouthFrownLeft": "mouthFrownLeft",
    "mouthFrownRight": "mouthFrownRight",
}
MAX_VERTICES = 13380

def attach_faceunits(basemesh, asset_root, target_service):
    if len(basemesh.data.vertices) != MAX_VERTICES:
        raise RuntimeError("Helper meshes MUST be physically removed before face units")
    if basemesh.data.shape_keys and len(basemesh.data.shape_keys.key_blocks)>1:
        raise RuntimeError("Phenotype targets must be baked before facial expression keys")
    folder=Path(asset_root).resolve()/"original"/"targets"/"faceunits"
    if not folder.is_dir():raise RuntimeError("Missing original Faceunits01 target folder "+str(folder))
    basis=basemesh.shape_key_add(name="Basis",from_mix=False) if basemesh.data.shape_keys is None else basemesh.data.shape_keys.key_blocks[0]
    assert len(basis.data)==MAX_VERTICES
    metrics={}
    for export_name,original_name in FACE_MORPHS.items():
        source=folder/(original_name+".target")
        if not source.is_file():raise RuntimeError("CC0 original target unavailable: "+str(source))
        safe=[]
        trimmed=0
        for line in source.read_text(encoding="utf-8").splitlines():
            cols=line.split()
            if not cols or cols[0].startswith("#"):
                safe.append(line);continue
            try: idx=int(cols[0])
            except ValueError: continue
            if len(cols)<4:raise RuntimeError("Malformed official target line "+source.name)
            if idx>=MAX_VERTICES:
                trimmed+=1
                continue
            if idx<0:raise RuntimeError("Negative vertex ID")
            safe.append(line)
        # Keep MPFB's exact target parser and units; do not copy positions from
        # another human or apply arbitrary fake face-space sphere distortions.
        key=target_service.target_string_to_shape_key("\n".join(safe)+"\n",export_name,basemesh)
        key.value=0
        count=0;sumsq=0;max_move=0
        for n,p in enumerate(key.data):
            d=(p.co-basis.data[n].co).length
            if d>1e-6:
                count+=1
                sumsq+=d*d
                max_move=max(max_move,d)
        if count<10 or max_move<.0001:
            raise RuntimeError("Face key is empty / not meaningfully applied: "+export_name+f" count={count} max={max_move}")
        metrics[export_name]={"source":source.name,"license":"CC0",
                              "nonzero_vertices":count,
                              "trimmed_helper_vertices":trimmed,
                              "rms_displacement_m":math.sqrt(sumsq/count),
                              "max_displacement_m":max_move}
        print("REAL_FACEUNIT_ATTACHED",export_name,json.dumps(metrics[export_name]))
    assert set(metrics)==set(FACE_MORPHS)
    return metrics
