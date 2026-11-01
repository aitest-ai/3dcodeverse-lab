#!/usr/bin/env python3
"""Fixed camera rendering from actual GLBs via VTK. NOT browser WebGL or Blender."""
from pathlib import Path
import argparse,importlib.util,os
import vtk,trimesh
from PIL import Image,ImageDraw,ImageFont

BASE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('v008_renderer',BASE/'v009_vtk_actor.py')
if not spec or not spec.loader:raise RuntimeError('V008 renderer unavailable')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main(root,out):
 out.mkdir(parents=True,exist_ok=True)
 r=vtk.vtkRenderer();r.SetBackground(.83,.87,.84);r.SetBackground2(.94,.96,.93);r.GradientBackgroundOn()
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(True);win.SetSize(1080,675);win.SetMultiSamples(2);win.AddRenderer(r)
 l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPosition(-23,40,37);l.SetFocalPoint(60,3,65);l.SetIntensity(1.35);r.AddLight(l)
 l2=vtk.vtkLight();l2.SetLightTypeToSceneLight();l2.SetPosition(75,25,120);l2.SetFocalPoint(30,3,63);l2.SetIntensity(.7);r.AddLight(l2)
 fixed=[]
 for name in ['v004_merchant_road.glb','v004_merchant_facades.glb','v004_merchant_signs.glb','v005_east_road.glb','v005_east_signs.glb','v006_tail_road.glb']:
  sc=trimesh.load(root/'dist/assets'/name,force='scene',process=False)
  fixed.extend(m.actor(g) for g in sc.geometry.values())
 cameras=[
  ('utsuroi_side',(61,3.6,71),(55,3.3,59),66),
  ('utsuroi_cornice',(61,5.15,69.4),(54,5.30,59.5),50),
  ('utsuroi_walk',(63,2.70,73),(56,3.05,61),67),
  ('waraji_control',(54,3.4,65.2),(51,3.2,77),66)
 ]
 for key,pos,target,angle in cameras:
  pair=[]
  for stage,file in [('V008',root/'dist/assets/v008_waraji_architecture.glb'),('V009',out/'v009_utsuroi_facade.glb')]:
   r.RemoveAllViewProps()
   for ob in fixed:r.AddActor(ob)
   sc=trimesh.load(file,force='scene',process=False)
   for mesh in sc.geometry.values():r.AddActor(m.actor(mesh))
   cam=r.GetActiveCamera();cam.SetPosition(*pos);cam.SetFocalPoint(*target);cam.SetViewUp(0,1,0);cam.SetViewAngle(angle);cam.SetClippingRange(.15,230)
   win.Render();sh=vtk.vtkWindowToImageFilter();sh.SetInput(win);sh.SetInputBufferTypeToRGB();sh.ReadFrontBufferOff();sh.Update()
   writer=vtk.vtkPNGWriter();dst=out/f'{key}_{stage}.png';writer.SetFileName(str(dst));writer.SetInputConnection(sh.GetOutputPort());writer.Write()
   pair.append(Image.open(dst).convert('RGB'))
  w,h=pair[0].size;canvas=Image.new('RGB',(w*2,h+50),(245,245,241));canvas.paste(pair[0],(0,50));canvas.paste(pair[1],(w,50))
  d=ImageDraw.Draw(canvas);font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
  f=ImageFont.truetype(font,22) if Path(font).exists() else ImageFont.load_default()
  d.text((14,10),'V008 — frozen facade candidate',fill=(40,47,40),font=f)
  d.text((w+14,10),'V009 — sidewall-grid corrective proposal',fill=(40,47,40),font=f)
  name=out/f'V009_{key}_same_camera.png';canvas.save(name);print('RENDER',name,name.stat().st_size,flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('runtime_root',type=Path);ap.add_argument('outputs',type=Path);q=ap.parse_args()
 main(q.runtime_root,q.outputs)