"""Independently verify all 8 finished GLBs and build exact requested ZIP.
Runs outside Blender with Pillow, json, and stdlib only.
"""
import io, json, struct, zipfile
from pathlib import Path
from PIL import Image

ROOT=Path("outputs/taiwan_characters")
IDS=("you","boss","uncle","jie","oldman","cop","shui","bro")
LABELS={"you":"主角","boss":"便當店老闆娘","uncle":"阿財叔","jie":"外送員阿杰",
        "oldman":"騎樓阿伯","cop":"警察大哥","shui":"夜市阿水伯","bro":"隔壁攤大哥"}
REQUIRED_KEYS=("mouthOpen","mouthSmile","mouthFrown","eyeBlinkLeft","eyeBlinkRight",
               "browDownLeft","browDownRight","browInnerUp")
BONES=("Root","pelvis","spine_01","spine_02","spine_03","neck_01","head",
       "upperarm_l","upperarm_r","lowerarm_l","lowerarm_r","hand_l","hand_r",
       "thigh_l","thigh_r","calf_l","calf_r","foot_l","foot_r")
all_reports={}
manifest={"schema_version":1,"package_id":"taiwan-characters","game":"台灣街頭喜劇遊戲",
          "format":"glTF 2.0 GLB","units":"meter","number_of_characters":8,
          "source":"Verified original MPFB 2.0.18 + Blender 5.2.3 source artifact #40991317263",
          "source_url":"https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/40991317263",
          "license_policy":"Every source asset tagged below; Blender/MPFB source code not redistributed",
          "characters":{}}
files=[]
for cid in IDS:
    p=ROOT/(cid+".glb")
    assert p.is_file() and 10000<p.stat().st_size<=6000000,(cid,"glb filesize",p.stat().st_size if p.exists() else None)
    report=json.loads((ROOT/(cid+"_report.json")).read_text(encoding="utf-8"))
    assert report["body_vertices"]==13380,(cid,report["body_vertices"])
    assert report["helper_vertices_physically_deleted"]>0
    assert report["helper_mask_modifiers_remaining"]==0
    assert set(REQUIRED_KEYS)<=set(report["shape_keys"])
    assert all(report["expression_affected_vertices"][k]>5 for k in REQUIRED_KEYS)
    assert set(BONES)<=set(report["required_bones"])
    assert report["height_m"]>1.4 and report["height_m"]<1.9
    with p.open("rb") as f:
        magic,version,length=struct.unpack("<4sII",f.read(12))
        assert magic==b"glTF" and version==2 and length==p.stat().st_size
        sz,t=struct.unpack("<I4s",f.read(8));assert t==b"JSON"
        doc=json.loads(f.read(sz))
        bin_sz,t=struct.unpack("<I4s",f.read(8));assert t==b"BIN\x00"
        bin_data=f.read(bin_sz)
    nodes={n.get("name","") for n in doc.get("nodes",[])}
    assert set(BONES)<=nodes,(cid,"missing bones",set(BONES)-nodes)
    assert doc.get("skins") and doc.get("meshes") and doc.get("materials")
    named={m.get("name",""):m for m in doc["meshes"]}
    for n in ("Top_"+cid,"Pants_"+cid):
        assert any(n in name for name in named),(cid,n,"separate mesh")
    names=set()
    for mesh in doc["meshes"]:
        names.update(mesh.get("extras",{}).get("targetNames",[]))
        names.update(mesh.get("targetNames",[]))
    assert set(REQUIRED_KEYS)<=names,(cid,"targetNames",names)
    dimensions=[]
    for image in doc.get("images",[]):
        view=doc["bufferViews"][image["bufferView"]]
        offset=view.get("byteOffset",0)
        data=bin_data[offset:offset+view["byteLength"]]
        with Image.open(io.BytesIO(data)) as im:
            w,h=im.size
            assert w<=1024 and h<=1024,(cid,image.get("name"),w,h)
            dimensions.append({"name":image.get("name",""),"width":w,"height":h})
    assert dimensions,(cid,"no embedded textures")
    # Both clothing meshes must actually use a PBR image texture.
    for garment in ("Top_"+cid,"Pants_"+cid):
        matching=[m for n,m in named.items() if garment in n]
        uses_image=False
        for mesh in matching:
            for prim in mesh.get("primitives",[]):
                matindex=prim.get("material")
                if matindex is None:continue
                mat=doc["materials"][matindex]
                uses_image |= "baseColorTexture" in mat.get("pbrMetallicRoughness",{})
        assert uses_image,(cid,garment,"missing texture")
    for kind in ("front","face","side"):
        img=ROOT/(cid+"_"+kind+".png")
        assert img.is_file() and img.stat().st_size>1500,(cid,"missing Blender render",kind)
        with Image.open(img) as im:
            im.verify()
        files.append(img)
    files.append(p)
    report.update({"independent_glb_textures":dimensions,
                   "exported_target_names":sorted(names),
                   "independent_verdict":"STRUCTURE_PASS_VISUAL_REVIEW_REQUIRED"})
    all_reports[cid]=report
    manifest["characters"][cid]={
        "display_name":LABELS[cid],"glb":cid+".glb",
        "front":cid+"_front.png","face":cid+"_face.png","side":cid+"_side.png",
        "height_m":report["height_m"],
        "license":"CC0",
        "author":"aitest-ai / project procedural production",
        "source_assets":[
            {"component":"MakeHuman hm08 body geometry and standard game-engine rig",
             "author":"MakeHuman Community contributors","license":"CC0",
             "origin":"MPFB 2.0.18 / MakeHuman system assets"},
            {"component":"MakeHuman system skin, eyes, face parts and clothing",
             "author":"MakeHuman Community contributors","license":"CC0",
             "origin":"makehuman_system_assets_cc0.zip"},
            {"component":"Custom garments textures, hair and accessories",
             "author":"aitest-ai / project procedural production","license":"CC0",
             "origin":"scripts/taiwan_characters/build_one.py"}
        ],
        "qa_status":"STRUCTURE_PASS_VISUAL_REVIEW_REQUIRED",
        "art_qa_notes":"View renders for helper shells, clipping, face proportion, anatomy and garment fit; static views cannot establish animation fit."}
report_path=ROOT/"report.json"
manifest_path=ROOT/"asset_manifest.json"
report_path.write_text(json.dumps({
  "package":"taiwan-characters","source_run_id":40991317263,
  "status":"STRUCTURE_PASS_VISUAL_REVIEW_REQUIRED",
  "characters":all_reports,
  "warning":"Structural, texture, file-size and image-presence checks passed. Human visual approval and deformation/clipping tests remain pending."
},ensure_ascii=False,indent=2),encoding="utf-8")
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
files.extend((report_path,manifest_path))
zip_path=Path("outputs/taiwan-characters.zip")
with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files,key=lambda x:x.name):
        z.write(p,arcname=p.name)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert len(names)==34,(len(names),names)
    assert names.count("asset_manifest.json")==1 and names.count("report.json")==1
print("TAIWAN_CHARACTERS_PACKAGE_READY",zip_path,zip_path.stat().st_size,"bytes",len(files),"files")
