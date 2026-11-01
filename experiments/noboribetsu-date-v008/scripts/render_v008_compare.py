#!/usr/bin/env python3
"""Actual GLB VTK diagnostic A/B, identical camera and lights. NOT browser WebGL or Blender Cycles."""
import argparse,os,pathlib
import numpy as np,trimesh,vtk
from PIL import Image,ImageDraw,ImageFont
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray

def actor(mesh):
 vs=np.asarray(mesh.vertices,dtype=np.float32);fs=np.asarray(mesh.faces,dtype=np.int64)
 points=vtk.vtkPoints();points.SetData(numpy_to_vtk(vs,deep=True))
 cells=vtk.vtkCellArray();raw=np.column_stack((np.full(len(fs),3,dtype=np.int64),fs)).reshape(-1);cells.SetCells(len(fs),numpy_to_vtkIdTypeArray(raw,deep=True))
 poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
 material=getattr(mesh.visual,'material',None);base=getattr(material,'baseColorFactor',None)
 mapr=vtk.vtkPolyDataMapper();mapr.SetInputData(poly);act=vtk.vtkActor();act.SetMapper(mapr)
 prop=act.GetProperty();prop.SetAmbient(.36);prop.SetDiffuse(.78);prop.SetSpecular(.045);prop.SetSpecularPower(12);prop.BackfaceCullingOff()
 if base is not None:prop.SetColor(*(float(z) for z in np.array(base[:3])/255))
 else:prop.SetColor(.60,.55,.45)
 tex=getattr(material,'baseColorTexture',None)
 if tex is not None and getattr(mesh.visual,'uv',None) is not None:
  uv=np.asarray(mesh.visual.uv,dtype=np.float32)
  if len(uv)==len(vs):
   coords=vtk.vtkFloatArray();coords.SetName('TextureCoordinates');coords.SetNumberOfComponents(2);coords.SetNumberOfTuples(len(uv))
   for i,(u,v) in enumerate(uv):coords.SetTuple2(i,float(u),float(v))
   poly.GetPointData().SetTCoords(coords)
   tarr=np.flipud(np.asarray(tex.convert('RGB'),dtype=np.uint8));vimg=vtk.vtkImageData();vimg.SetDimensions(tarr.shape[1],tarr.shape[0],1)
   scal=numpy_to_vtk(tarr.reshape(-1,3),deep=True,array_type=vtk.VTK_UNSIGNED_CHAR);scal.SetNumberOfComponents(3);vimg.GetPointData().SetScalars(scal)
   vtex=vtk.vtkTexture();vtex.SetInputData(vimg);vtex.RepeatOn();vtex.InterpolateOn();act.SetTexture(vtex)
 return act

def main(base,out):
 out.mkdir(exist_ok=True,parents=True)
 root=base/'dist/assets'
 r=vtk.vtkRenderer();r.SetBackground(.83,.87,.84);r.SetBackground2(.94,.96,.93);r.GradientBackgroundOn()
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.SetSize(1120,700);win.SetMultiSamples(2);win.AddRenderer(r)
 l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPosition(-23,40,37);l.SetFocalPoint(60,3,70);l.SetIntensity(1.35);r.AddLight(l)
 l2=vtk.vtkLight();l2.SetLightTypeToSceneLight();l2.SetPosition(75,25,120);l2.SetFocalPoint(30,3,63);l2.SetIntensity(.7);r.AddLight(l2)
 fixed=[]
 for file in ['v004_merchant_road.glb','v004_merchant_facades.glb','v004_merchant_signs.glb','v005_east_road.glb','v005_east_signs.glb','v006_tail_road.glb']:
  sc=trimesh.load(root/file,force='scene',process=False)
  for obj in sc.geometry.values():fixed.append(actor(obj))
 for name,pos,target in [
  ('waraji_front',(54,3.4,65.2),(51,3.2,77)),
  ('waraji_eave',(54,5.45,66.2),(52,5.3,76.1)),
  ('utsuroi',(61,3.6,71),(55,3.3,59))]:
  pair=[]
  for stage,facade in [('V007',root/'v007_east_facades.glb'),('V008',out/'v008_waraji_architecture.glb')]:
   r.RemoveAllViewProps()
   for ob in fixed:r.AddActor(ob)
   sc=trimesh.load(facade,force='scene',process=False)
   for mesh in sc.geometry.values():r.AddActor(actor(mesh))
   cam=r.GetActiveCamera();cam.SetPosition(*pos);cam.SetFocalPoint(*target);cam.SetViewUp(0,1,0);cam.SetViewAngle(66 if name!='waraji_eave' else 47);cam.SetClippingRange(.15,230)
   win.Render();shot=vtk.vtkWindowToImageFilter();shot.SetInput(win);shot.SetInputBufferTypeToRGB();shot.ReadFrontBufferOff();shot.Update()
   wr=vtk.vtkPNGWriter();dest=out/f'{name}_{stage}.png';wr.SetFileName(str(dest));wr.SetInputConnection(shot.GetOutputPort());wr.Write()
   pair.append(Image.open(dest).convert('RGB'))
  w,h=pair[0].size;canvas=Image.new('RGB',(w*2,h+54),(248,248,243));canvas.paste(pair[0],(0,54));canvas.paste(pair[1],(w,54))
  d=ImageDraw.Draw(canvas)
  font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
  ft=ImageFont.truetype(font_path,22) if os.path.exists(font_path) else ImageFont.load_default()
  d.text((18,12),'V007 — source frozen',(35,46,41),font=ft)
  d.text((w+18,12),'V008 — photo-guided structural hypothesis',(35,46,41),font=ft)
  output=out/f'V008_{name}_same_camera.png';canvas.save(output)
  print('RENDERED',output,output.stat().st_size,flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('base',type=pathlib.Path);ap.add_argument('out',type=pathlib.Path);a=ap.parse_args();main(a.base,a.out)