"""Recolour the CC0 Quaternius outfit atlases into pilot-style variants using the UV islands of each part (keeps the painted shading/detail)."""
import json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
T="/home/claude/lab/outfits/Modular Character Outfits - Fantasy[Standard]/Textures/"
UV=json.load(open("/home/claude/lab/outfits/uv.json"))
def mask_for(g_kind, parts, slot0=True, size=4096):
    m=Image.new('L',(size,size),0); d=ImageDraw.Draw(m)
    for key,tris in UV[g_kind].items():
        part,slot,mat=key.split("|")
        if part in parts and (slot=="0" or not slot0):
            for t in tris: d.polygon([(t[0]*size,(1-t[1])*size),(t[2]*size,(1-t[3])*size),(t[4]*size,(1-t[5])*size)],fill=255)
    return m.filter(ImageFilter.MaxFilter(5))
def colorize(arr, mask, target, lum_min=0):
    mk=(np.asarray(mask)>0)
    l=(arr[...,0]*.299+arr[...,1]*.587+arr[...,2]*.114)
    sel=mk&(l>=lum_min)
    if not sel.any(): return
    mean=l[sel].mean()
    k=np.clip(l[sel]/mean,0.25,2.0)[:,None]
    arr[sel]=np.clip(np.array(target,dtype=np.float32)[None,:]*k,0,255)
VARS={
 "Peasant":{"khaki":[(("Body","Arms"),(112,116,76),110),(("Legs",),(86,90,62),0)],
            "navy":[(("Body","Arms"),(226,231,240),110),(("Legs",),(34,46,74),0),(("Feet",),(40,34,32),0)]},
 "Ranger":{"leather":[(("Body",),(112,72,42),0),(("Arms",),(96,62,36),0),(("Legs",),(150,132,92),0)]},
}
for g in ("Male","Female"):
    for kind,vs in VARS.items():
        src=np.asarray(Image.open(T+f"{kind}/T_{kind}_BaseColor.png").convert('RGB'),dtype=np.float32)
        for vn,rules in vs.items():
            arr=src.copy()
            for parts,col,lmin in rules: colorize(arr,mask_for(f"{g}_{kind}",set(parts)),col,lmin)
            Image.fromarray(arr.astype(np.uint8)).resize((2048,2048),Image.LANCZOS).save(f"/home/claude/lab/outfits/recolor/{g}_{kind}_{vn}.png")
            print(g,kind,vn)
