"""Inspect true glTF binary morphs rather than trusting Blender shape-key names.

Requires only Python stdlib. Fails if mouthOpen exists on body but is absent
from both original fitted teeth/tongue. Also verifies eye-blinks in eyelashes.
Can be called in GitHub Actions on any exported .glb, before publication.
"""
import json,sys,struct,pathlib,math

REQUIRED_BODY={"mouthOpen","jawLeft","jawRight","mouthSmileLeft",
               "mouthSmileRight","eyeBlinkLeft","eyeBlinkRight",
               "browInnerUp","mouthFrownLeft","mouthFrownRight"}

def measure(accessor):
    maximum=accessor.get("max",[])
    minimum=accessor.get("min",[])
    displacement=max([abs(x) for x in maximum+minimum],default=0)
    nonzero=accessor.get("sparse",{}).get("count",accessor.get("count",0))
    return {"nonzero_sparse_count":nonzero,"max_component_displacement_m":displacement}

def analyze(path):
    raw=pathlib.Path(path).read_bytes()
    assert len(raw)>=20
    magic,ver,total=struct.unpack_from("<4sII",raw,0)
    assert magic==b"glTF" and ver==2 and total==len(raw)
    size,kind=struct.unpack_from("<I4s",raw,12)
    assert kind==b"JSON"
    data=json.loads(raw[20:20+size])
    assert data.get("skins"),"Missing real skinned rig"
    metrics={}
    for mesh in data["meshes"]:
        name=mesh.get("name","?")
        names=mesh.get("extras",{}).get("targetNames",[])
        shapes={}
        for prim in mesh["primitives"]:
            targets=prim.get("targets",[])
            assert len(targets)==len(names),(name,len(targets),len(names))
            for key,t in zip(names,targets):
                if "POSITION" not in t:continue
                val=measure(data["accessors"][t["POSITION"]])
                if key not in shapes or val["max_component_displacement_m"]>shapes[key]["max_component_displacement_m"]:
                    shapes[key]=val
        metrics[name]=shapes
    bodies=[(name,m) for name,m in metrics.items() if REQUIRED_BODY <= set(m)]
    assert bodies, "Body is missing ten original faceunit targets"
    assert any(m["mouthOpen"]["max_component_displacement_m"]>.001 for _,m in bodies), \
        "Body mouth morph is inert"
    oral={name:m for name,m in metrics.items() if "tongue" in name.lower() or "teeth" in name.lower()}
    eyes={name:m for name,m in metrics.items() if "lash" in name.lower() or "brow" in name.lower()}
    oral_moving={name:m["mouthOpen"] for name,m in oral.items()
                  if m.get("mouthOpen",{}).get("max_component_displacement_m",0)>.00015}
    eyelid_moving={name:{k:m[k] for k in ("eyeBlinkLeft","eyeBlinkRight") if
                m.get(k,{}).get("max_component_displacement_m",0)>.00015}
                for name,m in eyes.items()}
    eyelid_moving={k:v for k,v in eyelid_moving.items() if v}
    report={"file":str(path),"body_morphs":{n:m for n,m in bodies},
            "oral_meshes":oral,"oral_moving":oral_moving,
            "eyelash_brow_meshes":eyes,"eye_accessory_moving":eyelid_moving,
            "all_mesh_names":list(metrics)}
    assert oral, "GLB contains no real oral accessory geometry"
    assert oral_moving, "Black-mouth problem persists: teeth and tongue both static"
    assert eyelid_moving, "Blink poses will not follow fitted eyelashes/eyebrows"
    print("REAL_ORAL_EYE_ACCESSORY_SHAPE_QA_PASSED",json.dumps(report,ensure_ascii=False))
    return report

if __name__=="__main__":
    if len(sys.argv)<2:raise SystemExit("Usage: python verify_glb_mouth_morphs.py character.glb ...")
    for filename in sys.argv[1:]:analyze(filename)
