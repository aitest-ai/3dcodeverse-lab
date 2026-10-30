import bpy,json
R="/home/claude/lab/outfits/Modular Character Outfits - Fantasy[Standard]/Exports/glTF (Godot-Unreal)/Outfits/"
out={}
for g in ("Male","Female"):
  for k in ("Peasant","Ranger"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=R+f"{g}_{k}.gltf")
    d={}
    for o in bpy.data.objects:
        if o.type!='MESH' or o.name.startswith("Icosphere"): continue
        me=o.data; uv=me.uv_layers.active.data; part=o.name.split("_",2)[2]
        for p in me.polygons:
            ls=list(p.loop_indices)
            for i in range(1,len(ls)-1):
                t=[uv[ls[0]].uv,uv[ls[i]].uv,uv[ls[i+1]].uv]
                d.setdefault(part+"|"+str(p.material_index)+"|"+me.materials[p.material_index].name.split('.')[0],[]).append([c for q in t for c in (round(q[0],5),round(q[1],5))])
    out[g+"_"+k]=d
json.dump(out,open("/home/claude/lab/outfits/uv.json","w"))
print({k:{p:len(v) for p,v in d.items()} for k,d in out.items()}["Male_Peasant"], list(out['Male_Ranger'].keys()))
