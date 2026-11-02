#!/usr/bin/env python3
"""V016 3D geometry diagnostic only: not a browser/WebGL screenshot."""
from pathlib import Path
import json,numpy as np,trimesh,vtk
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;D=R/'base/dist';O=R/'evidence';O.mkdir(exist_ok=True)
fac=trimesh.load(D/'assets/v004_merchant_facades.glb',force='scene')
road=trimesh.load(D/'assets/v004_merchant_road.glb',force='scene')
old=trimesh.load(R/'source/models/V015_V004_Post_Grounding.glb',force='scene')
audit=json.loads((R/'outputs/v016_grade_inspection.json').read_text())
assert len(audit['burial_samples'])==4
colors={'stone_foot':(.48,.47,.42),'stone_warm_grey':(.54,.53,.49),'road_asphalt':(.37,.36,.34),'road_patinated_edge':(.36,.34,.31)}
def actor(mesh, rgb, ambient=.40):
 v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces,dtype=int)
 pts=vtk.vtkPoints();pts.SetNumberOfPoints(len(v))
 for i,(x,y,z) in enumerate(v):pts.SetPoint(i,float(x),float(y),float(z))
 cells=vtk.vtkCellArray()
 for a,b,c in f:
  tri=vtk.vtkTriangle();tri.GetPointIds().SetId(0,int(a));tri.GetPointIds().SetId(1,int(b));tri.GetPointIds().SetId(2,int(c));cells.InsertNextCell(tri)
 poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 norm=vtk.vtkPolyDataNormals();norm.SetInputData(poly);norm.SplittingOff();norm.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norm.GetOutputPort())
 ac=vtk.vtkActor();ac.SetMapper(mapper);ac.GetProperty().SetColor(*rgb)
 ac.GetProperty().SetAmbient(ambient);ac.GetProperty().SetDiffuse(.60);return ac
actors=[]
for scene in (fac,road):
 for name,mesh in scene.geometry.items():
  if name.startswith('tile_'):col=(.34,.36,.38)
  elif name.startswith('wood') or name=='panel_black':col=(.33,.25,.18)
  elif name.startswith('plaster'):col=(.73,.71,.64)
  else:col=colors.get(name,(.43,.42,.37))
  actors.append(actor(mesh,col))
for mesh in old.geometry.values():actors.append(actor(mesh,(.42,.41,.38)))
markers=[]
for p in audit['burial_samples']:
 n=32;v=[];faces=[]
 for j in range(n):
  a=j*np.pi*2/n
  for rad in (.27,.36):v.append((p['x']+np.cos(a)*rad,p['marker_y'],p['z']+np.sin(a)*rad))
 for j in range(n):
  k=2*j;nextk=2*((j+1)%n)
  faces.extend([(k,k+1,nextk+1),(k,nextk+1,nextk)])
 mesh=trimesh.Trimesh(vertices=np.asarray(v),faces=np.asarray(faces),process=False)
 markers.append(actor(mesh,(1,.67,.09),ambient=.9))
# Both cameras inspect a real buried sample at the higher end of each continuous stone plinth.
cases=[('Beijingtei',(40.0,3.3,61.5),(41.1,1.55,59.0)),('Gakumonjo', (15.2,3.4,65.0),(20.3,1.6,58.0))]
for key,eye,focus in cases:
 for label,enabled in [('unmarked',False),('marked',True)]:
  ren=vtk.vtkRenderer();ren.SetBackground(.77,.83,.85);win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(650,400);win.AddRenderer(ren)
  for a in actors:ren.AddActor(a)
  if enabled:
   for a in markers:ren.AddActor(a)
  cam=ren.GetActiveCamera();cam.SetPosition(*eye);cam.SetFocalPoint(*focus);cam.SetViewUp(0,1,0);cam.SetViewAngle(39)
  ren.ResetCameraClippingRange();win.Render()
  grab=vtk.vtkWindowToImageFilter();grab.SetInput(win);grab.Update()
  fn=str(O/f'V016_{key}_{label}_VTK.png');writer=vtk.vtkPNGWriter();writer.SetFileName(fn);writer.SetInputConnection(grab.GetOutputPort());writer.Write();win.Finalize()
  print(fn,flush=True)
 images=[Image.open(O/f'V016_{key}_{lab}_VTK.png').convert('RGB') for lab in ('unmarked','marked')]
 canvas=Image.new('RGB',(1300,455),(246,245,240))
 for i,im in enumerate(images):canvas.paste(im,(650*i,55))
 d=ImageDraw.Draw(canvas);d.text((18,16),key+' / V015 as-built stone base (no V016 marks)',fill='#222222')
 d.text((668,16),key+' / V016 FOUR-POINT INSPECTION MARKERS ON',fill='#222222')
 canvas.save(O/f'V016_{key}_Geometry_Comparison.png')
print('V016 VTK diagnostics complete')