"""VTK geometry diagnostic. NOT a WebGL or Cycles rendering."""
from pathlib import Path
import numpy as np,trimesh,vtk,json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;D=R/'base/dist';O=R/'outputs'
colors={'plaster_offwhite':(.76,.76,.69),'plaster_lower':(.68,.65,.56),'wood_dark':(.26,.20,.16),'wood_timber':(.35,.26,.17),'paper_panels':(.79,.76,.67),'wood_patina':(.37,.28,.19),'wood_lintel':(.36,.28,.20),'wood_grain_light':(.47,.39,.28),'panel_black':(.12,.12,.12),'stone_foot':(.48,.46,.41),'stone_warm_grey':(.53,.52,.46),'tile_lit':(.35,.39,.40),'tile_ash':(.27,.31,.33),'tile_variation':(.35,.35,.35),'tile_slate':(.28,.29,.30),'ridge_tile':(.33,.34,.36),'plaster_warm':(.70,.62,.46),'road_asphalt':(.36,.35,.33),'road_patinated_edge':(.36,.35,.32)}
facade=trimesh.load(D/'assets/v004_merchant_facades.glb',force='scene');road=trimesh.load(D/'assets/v004_merchant_road.glb',force='scene');patch=trimesh.load(O/'V015_V004_Post_Grounding.glb',force='scene')
def actor(mesh, rgb):
 v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces);pts=vtk.vtkPoints();pts.SetNumberOfPoints(len(v))
 for i,(x,y,z) in enumerate(v):pts.SetPoint(i,float(x),float(y),float(z))
 cells=vtk.vtkCellArray()
 for a,b,c in f:
  t=vtk.vtkTriangle();t.GetPointIds().SetId(0,int(a));t.GetPointIds().SetId(1,int(b));t.GetPointIds().SetId(2,int(c));cells.InsertNextCell(t)
 poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 normal=vtk.vtkPolyDataNormals();normal.SetInputData(poly);normal.ConsistencyOn();normal.SplittingOff();normal.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normal.GetOutputPort());a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(rgb);a.GetProperty().SetAmbient(.45);a.GetProperty().SetDiffuse(.52);a.GetProperty().SetSpecular(.05);return a
actors=[actor(mesh,colors.get(name,(.45,.43,.40))) for s in [facade,road] for name,mesh in s.geometry.items()]
foot_actor=actor(next(iter(patch.geometry.values())),(.44,.42,.38))
for enabled in (False,True):
 ren=vtk.vtkRenderer();ren.SetBackground(.77,.82,.83);win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(900,550);win.AddRenderer(ren)
 for a in actors:ren.AddActor(a)
 if enabled:ren.AddActor(foot_actor)
 light=vtk.vtkLight();light.SetPosition(0,25,60);light.SetFocalPoint(12,0,57);light.SetIntensity(.8);ren.AddLight(light)
 cam=ren.GetActiveCamera();cam.SetPosition(5.10,1.64,59.75);cam.SetFocalPoint(5.10,1.12,58.31);cam.SetViewUp(0,1,0);cam.SetViewAngle(42)
 ren.ResetCameraClippingRange();win.Render()
 filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.Update();wr=vtk.vtkPNGWriter();wr.SetFileName(str(O/f'V015_V004_Grounding_{"after" if enabled else "before"}_VTK.png'));wr.SetInputConnection(filt.GetOutputPort());wr.Write();win.Finalize()
 files=[str(O/'V015_V004_Grounding_before_VTK.png'),str(O/'V015_V004_Grounding_after_VTK.png')]
imgs=[Image.open(p).convert('RGB') for p in files]
W,H=imgs[0].size;out=Image.new('RGB',(2*W,H+55),'#f8f7f2');out.paste(imgs[0],(0,55));out.paste(imgs[1],(W,55));d=ImageDraw.Draw(out);d.text((18,18),'V014  BEFORE / original floating stone plinths',fill='#242424');d.text((W+18,18),'V015  AFTER / 8 small reversible under-foot supports',fill='#242424');out.save(O/'V014_V015_Grounding_VTK_Comparison.png')
print('created VTK comparison',out.size)