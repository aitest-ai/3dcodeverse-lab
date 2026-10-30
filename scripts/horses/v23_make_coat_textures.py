#!/usr/bin/env python3
"""Original skin-friendly coat microtexture generator for CC0 horse V2.3.

Creates *actual* raster PBR images (albedo, tangent-space normal, roughness),
rather than shader-only patterns that disappear on glTF export.
The appearance is a synthetic surface detail experiment, not scanned fur or
a claim of anatomical fidelity. No outside textures or rights are required.
"""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def make_maps(kind,out,size=1024):
    assert kind in ("Horse","Horse_White")
    rng=np.random.default_rng(20261030 if kind=="Horse" else 20261031)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Low-contrast multiscale noise avoids a speckled/plastic look.
    h=np.zeros((size,size),dtype=np.float32)
    for resolution,amplitude in [(16,.52),(65,.30),(260,.14)]:
        noise=rng.random((resolution,resolution),dtype=np.float32)
        image=Image.fromarray((noise*255).astype("uint8"),"L")
        image=image.resize((size,size),Image.Resampling.BICUBIC)
        h+=(np.array(image,dtype=np.float32)/255-.5)*amplitude
    h+=rng.normal(0,.040,(size,size)).astype(np.float32)
    h=np.clip(h,-.42,.42)
    # Flecks: low opacity directional fibers, no sharp stripes.
    fiber=Image.new("L",(size,size),0)
    drawer=ImageDraw.Draw(fiber)
    for _ in range(34000):
        x=int(rng.integers(0,size))
        y=int(rng.integers(0,size))
        length=int(rng.integers(2,9))
        v=int(rng.integers(9,32))
        drawer.line((x,y,x+int(length*.24),y+length),fill=v,width=1)
    fiber=fiber.filter(ImageFilter.GaussianBlur(.40))
    h+=np.array(fiber,dtype=np.float32)/255*.09
    base=np.array((126,66,38) if kind=="Horse" else (198,193,180),dtype=np.float32)
    # Readable natural color, but not a photographic claim.
    variation=(h*27 if kind=="Horse" else h*20)[...,None]
    rgb=np.clip(base[None,None,:]+variation*np.array([1.0,.82,.7]),0,255).astype(np.uint8)
    Image.fromarray(rgb,"RGB").save(out/"coat_albedo.png",optimize=True)
    dzdy,dzdx=np.gradient(h)
    strength=.33
    nx=-dzdx*strength;ny=-dzdy*strength
    nz=np.ones_like(nx)
    norm=np.sqrt(nx*nx+ny*ny+nz*nz)
    normal=np.stack((nx/norm*.5+.5,ny/norm*.5+.5,nz/norm*.5+.5),axis=-1)
    Image.fromarray(np.uint8(np.clip(normal*255,0,255)),"RGB").save(out/"coat_normal.png",optimize=True)
    rough=np.uint8(np.clip(.76+h*.06,.48,.91)*255)
    Image.fromarray(np.stack([rough]*3,axis=-1),"RGB").save(out/"coat_roughness.png",optimize=True)
    print("HORSE_COAT_PBR_IMAGES",kind,[(p.name,p.stat().st_size) for p in out.glob("*.png")],flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("horse",choices=["Horse","Horse_White"])
    a.add_argument("out")
    a.add_argument("--size",type=int,default=1024)
    args=a.parse_args()
    make_maps(args.horse,args.out,args.size)
