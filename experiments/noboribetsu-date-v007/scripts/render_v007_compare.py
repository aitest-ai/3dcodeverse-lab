#!/usr/bin/env python3
"""VTK diagnostic render of actual GLBs, identical cameras, not WebGL or Blender evidence."""
import os,sys,json
from pathlib import Path
import vtk,numpy as np,trimesh
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'base/dist/assets'; OUT=ROOT/'v007_outputs'
OUT.mkdir(exist_ok=True)
render=vtk.vtkRenderer();render.SetBackground(.83,.86,.84);render.SetBackground2(.96,.97,.92);render.GradientBackgroundOn()
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.SetSize(1152,720);win.SetMultiSamples(4);win.AddRenderer(render)

def actor(mesh,sign=False):
    vs=np.asarray(mesh.vertices,dtype=np.float32);fs=np.asarray(mesh.faces,dtype=np.int64)
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(vs,deep=True))
    cells=vtk.vtkCellArray();raw=np.column_stack((np.full(len(fs),3,dtype=np.int64),fs)).reshape(-1)
    cells.SetCells(len(fs),numpy_to_vtkIdTypeArray(raw,deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    m=vtk.vtkPolyDataMapper();m.SetInputData(poly)
    a=vtk.vtkActor();a.SetMapper(m)
    prop=a.GetProperty();prop.SetDiffuse(.74);prop.SetAmbient(.29);prop.SetSpecular(.04);prop.SetSpecularPower(12);prop.SetInterpolationToPhong()
    mat=getattr(mesh.visual,'material',None)
    if mat is not None and getattr(mat,'baseColorFactor',None) is not None:
        c=np.asarray(mat.baseColorFactor,dtype=float)[:3]/255
        prop.SetColor(*(float(x) for x in c))
    tex=getattr(mat,'baseColorTexture',None)
    if tex is not None and hasattr(mesh.visual,'uv') and mesh.visual.uv is not None:
        uv=np.asarray(mesh.visual.uv,dtype=np.float32)
        if len(uv)==len(vs):
            vcoords=vtk.vtkFloatArray();vcoords.SetName('TextureCoordinates');vcoords.SetNumberOfComponents(2);vcoords.SetNumberOfTuples(len(uv))
            for i,(u,v) in enumerate(uv):vcoords.SetTuple2(i,float(u),float(v))
            poly.GetPointData().SetTCoords(vcoords)
            image=np.flipud(np.asarray(tex.convert('RGB'),dtype=np.uint8));vimg=vtk.vtkImageData();vimg.SetDimensions(image.shape[1],image.shape[0],1)
            colors=numpy_to_vtk(image.reshape(-1,3),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);colors.SetNumberOfComponents(3);vimg.GetPointData().SetScalars(colors)
            texvtk=vtk.vtkTexture();texvtk.SetInputData(vimg);texvtk.RepeatOn();texvtk.InterpolateOn();a.SetTexture(texvtk)
            if sign:prop.SetColor(1,1,1)
    prop.BackfaceCullingOff()
    return a

def add_scene(facade):
 actors=[]
 for name in ['v004_merchant_road.glb','v004_merchant_facades.glb','v004_merchant_signs.glb','v005_east_road.glb',facade,'v005_east_signs.glb','v006_tail_road.glb']:
  file=ASSETS/name if name != 'v007_east_facades.glb' else OUT/name
  sc=trimesh.load(file,force='scene',process=False)
  for mesh in sc.geometry.values():
   a=actor(mesh,'signs.glb' in name);render.AddActor(a);actors.append(a)
 # frozen V002 DEM context
 geo=json.loads((ROOT/'src/baseline/scene_geometry.json').read_text())
 terr=geo['terrain'];v=np.asarray(terr['vertices'],dtype=np.float32);f=np.asarray(terr['triangles'],dtype=np.int64)
 mask=(v[:,0]>-24)&(v[:,0]<125)&(v[:,1]>-110)&(v[:,1]<-30)
 f=f[mask[f].all(axis=1)];used=np.unique(f.ravel());mapping=np.full(len(v),-1,dtype=np.int64);mapping[used]=np.arange(len(used))
 p=v[used];eus=np.column_stack((p[:,0],p[:,2],-p[:,1]));mesh=trimesh.Trimesh(vertices=eus,faces=mapping[f],process=False)
 g=actor(mesh);g.GetProperty().SetColor(.47,.55,.43);g.GetProperty().SetDiffuse(.55);g.GetProperty().SetAmbient(.45);render.AddActor(g);actors.append(g)
 return actors

for name,pos,target in [('waraji',(54,3.4,65.2),(51,3.2,77)),('utsuroi',(61,3.6,71),(55,3.3,59)),('approach',(34,3.6,59.3),(73,3.55,78.3))]:
 pair=[]
 for version,filename in [('V006 原始候選','v005_east_facades.glb'),('V007 材質與暖簾精修','v007_east_facades.glb')]:
  for obj in list(render.GetActors()):render.RemoveActor(obj)
  add_scene(filename)
  cam=render.GetActiveCamera();cam.SetPosition(*pos);cam.SetFocalPoint(*target);cam.SetViewUp(0,1,0);cam.SetViewAngle(66);cam.SetClippingRange(.15,230)
  if not render.GetLights().GetNumberOfItems():
   a=vtk.vtkLight();a.SetLightTypeToSceneLight();a.SetPosition(-25,40,37);a.SetFocalPoint(60,2,70);a.SetIntensity(1.3);a.SetColor(1,.95,.84);render.AddLight(a)
   b=vtk.vtkLight();b.SetLightTypeToSceneLight();b.SetPosition(75,23,120);b.SetFocalPoint(20,2,58);b.SetIntensity(.74);b.SetColor(.83,.87,1);render.AddLight(b)
  win.Render();shot=vtk.vtkWindowToImageFilter();shot.SetInput(win);shot.SetInputBufferTypeToRGB();shot.ReadFrontBufferOff();shot.Update();writer=vtk.vtkPNGWriter();out=OUT/f'{name}_{"v006" if filename.startswith("v005") else "v007"}.png';writer.SetFileName(str(out));writer.SetInputConnection(shot.GetOutputPort());writer.Write()
  img=Image.open(out).convert('RGB');pair.append(img)
  print('RENDER',name,version,out.stat().st_size,flush=True)
 w,h=pair[0].size;canvas=Image.new('RGB',(w*2,h+53),(250,250,248));canvas.paste(pair[0],(0,53));canvas.paste(pair[1],(w,53));d=ImageDraw.Draw(canvas)
 font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
 ft=ImageFont.truetype(font_path,23) if os.path.exists(font_path) else ImageFont.load_default()
 d.text((25,12),'V006 baseline — unchanged',(38,44,37),font=ft)
 d.text((w+25,12),'V007 candidate — estimated, not surveyed',(38,44,37),font=ft)
 out=OUT/f'V007_{name}_same_camera.png';canvas.save(out);print('COMPARE',out,flush=True)