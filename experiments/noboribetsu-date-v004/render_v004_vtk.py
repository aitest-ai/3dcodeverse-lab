#!/usr/bin/env python3
"""Render exact V004 GLB geometry using VTK for diagnostic views, NOT Three.js or Blender Cycles acceptance."""
import os,sys,zipfile,json
from pathlib import Path
import vtk,numpy as np,trimesh
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from PIL import Image
ROOT=Path(__file__).resolve().parent
DIST=ROOT/'runtime/dist/assets'

r=vtk.vtkRenderer();r.SetBackground(0.82,0.86,0.84);r.SetBackground2(0.97,.97,.93);r.GradientBackgroundOn()
w=vtk.vtkRenderWindow();w.SetOffScreenRendering(True);w.SetSize(1440,900);w.SetMultiSamples(4);w.AddRenderer(r)

def actor(mesh,materialName='',texture=None):
    vs=np.asarray(mesh.vertices,dtype=np.float32)
    fs=np.asarray(mesh.faces,dtype=np.int64)
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(vs,deep=True))
    cells=vtk.vtkCellArray();packed=np.hstack([np.full((len(fs),1),3,dtype=np.int64),fs]).reshape(-1)
    cells.SetCells(len(fs),numpy_to_vtkIdTypeArray(packed,deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    if texture is not None and mesh.visual.kind=='texture' and getattr(mesh.visual,'uv',None) is not None:
        uv=np.asarray(mesh.visual.uv,dtype=np.float32)
        coords=vtk.vtkFloatArray();coords.SetName('TextureCoordinates');coords.SetNumberOfComponents(2);coords.SetNumberOfTuples(len(uv))
        for i,(u,v) in enumerate(uv):coords.SetTuple2(i,float(u),float(v))
        poly.GetPointData().SetTCoords(coords)
    m=vtk.vtkPolyDataMapper();m.SetInputData(poly)
    a=vtk.vtkActor();a.SetMapper(m)
    prop=a.GetProperty();prop.SetDiffuse(.76);prop.SetAmbient(.26);prop.SetSpecular(.08);prop.SetSpecularPower(9);prop.SetInterpolationToPhong()
    if hasattr(mesh.visual,'material') and mesh.visual.material is not None:
        mat=mesh.visual.material
        bc=getattr(mat,'baseColorFactor',None)
        if bc is not None:prop.SetColor(float(bc[0])/255,float(bc[1])/255,float(bc[2])/255)
    if texture is not None:
        image=np.flipud(np.asarray(texture.convert('RGBA'),dtype=np.uint8))
        arr=vtk.vtkImageData();arr.SetDimensions(image.shape[1],image.shape[0],1)
        colors=numpy_to_vtk(image.reshape(-1,4),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);colors.SetNumberOfComponents(4);arr.GetPointData().SetScalars(colors)
        vt=vtk.vtkTexture();vt.SetInputData(arr);vt.InterpolateOn();a.SetTexture(vt);prop.SetColor(1,1,1)
    prop.BackfaceCullingOff()
    return a

for name in ['v004_merchant_road.glb','v004_merchant_facades.glb','v004_merchant_signs.glb']:
    scene=trimesh.load(str(DIST/name),force='scene',process=False)
    for mesh in scene.geometry.values():
        tex=getattr(getattr(mesh.visual,'material',None),'baseColorTexture',None) if name.endswith('signs.glb') else None
        r.AddActor(actor(mesh,texture=tex))

# Subset only the frozen V002 DEM, as context, no external reference image. This avoids floating buildings.
geo=json.loads((ROOT/'baseline/data/scene_geometry.json').read_text())
terr=geo['terrain'];vs=np.asarray(terr['vertices'],dtype=np.float32);faces=np.asarray(terr['triangles'],dtype=np.int64)
mask=(vs[:,0]>-24)&(vs[:,0]<76)&(vs[:,1]>-95)&(vs[:,1]<-30)
selected=faces[mask[faces].all(axis=1)];used=np.unique(selected.reshape(-1));lookup={int(k):i for i,k in enumerate(used)}
pos=vs[used];eus=np.column_stack((pos[:,0],pos[:,2],-pos[:,1]));f=np.vectorize(lookup.get)(selected)
mesh=trimesh.Trimesh(vertices=eus,faces=f,process=False);ground=actor(mesh);ground.GetProperty().SetColor(.47,.55,.43);ground.GetProperty().SetDiffuse(.55);ground.GetProperty().SetAmbient(.45);r.AddActor(ground)

l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPosition(-25,40,37);l.SetFocalPoint(22,2,60);l.SetIntensity(1.25);l.SetColor(1,.95,.84);r.AddLight(l)
l2=vtk.vtkLight();l2.SetLightTypeToSceneLight();l2.SetPosition(75,23,120);l2.SetFocalPoint(20,2,58);l2.SetIntensity(.7);l2.SetColor(.83,.87,1);r.AddLight(l2)

views={
 'V004_diagnostic_walk_east.png':{'pos':(-1.8,3.35,62.0),'target':(32,3.85,60.1),'up':(0,1,0),'angle':70},
 'V004_diagnostic_merchant_mid.png':{'pos':(14,3.75,62.4),'target':(38,3.75,60.0),'up':(0,1,0),'angle':72},
 'V004_diagnostic_aerial.png':{'pos':(19,26,99),'target':(25,3.4,59.2),'up':(0,1,0),'angle':54},
 'V004_diagnostic_sevenmangoku.png':{'pos':(28,3.4,61.2),'target':(32,4.2,69.0),'up':(0,1,0),'angle':65},
}
for name,view in views.items():
    cam=r.GetActiveCamera();cam.SetPosition(*view['pos']);cam.SetFocalPoint(*view['target']);cam.SetViewUp(*view['up']);cam.SetViewAngle(view['angle']);cam.SetClippingRange(.15,220)
    w.Render()
    filt=vtk.vtkWindowToImageFilter();filt.SetInput(w);filt.SetInputBufferTypeToRGB();filt.ReadFrontBufferOff();filt.Update()
    writer=vtk.vtkPNGWriter();writer.SetFileName(str(ROOT/name));writer.SetInputConnection(filt.GetOutputPort());writer.Write()
    print('RENDERED',name,(ROOT/name).stat().st_size,flush=True)