#!/usr/bin/env python3
"""Review assets derived exclusively from frozen V016 route/collision and V017 geometry QA."""
import json,zipfile,io,base64,hashlib,math
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolyPatch
import trimesh
P=Path(__file__).resolve().parent;O=P/'outputs';v=json.loads((O/'v017_clearance_audit.json').read_text());samples=json.loads((O/'V017_route_samples.json').read_text())['samples'];z=zipfile.ZipFile(P/'V016_Runtime.zip');obstacles=json.loads(z.read('dist/extension_collision.json'))['obstacles']
fig,ax=plt.subplots(figsize=(12,6),layout='constrained')
for ob in obstacles:
 pts=np.array(ob['polygon'])
 ax.add_patch(PolyPatch(pts,fill=True,alpha=.25))
pts=np.array([(p['x'],p['z']) for p in samples]);ax.plot(pts[:,0],pts[:,1],label='V004 route centerline',lw=2)
markers=v['markers'];ax.scatter([p['x'] for p in markers],[p['z'] for p in markers],s=110,marker='o',label='Measured tight spots')
for i,m in enumerate(markers):
 ax.annotate(f"{i+1}: {m['margin_m']*100:.1f} cm",(m['x'],m['z']),xytext=(5,12+8*(i%2)),textcoords='offset points',fontsize=9)
ax.set(xlabel='Local x (m)',ylabel='Local z (m)',title='V017 | V004 merchant lane clearance audit (2D model only)');ax.axis('equal');ax.legend(loc='best');ax.grid(alpha=.25)
fig.savefig(O/'V017_Clearance_Route_Map.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(11,4),layout='constrained');ax.plot([p['s_m'] for p in samples],[p['capsule_horizontal_margin_m'] for p in samples],label='Horizontal free margin after 0.26m player radius');ax.axhline(0);ax.axhline(.5,ls=':',label='0.50 m reference, not regulatory limit');ax.set(xlabel='Distance along full route (m)',ylabel='Free margin (m)',title='V017 | Nearest modeled obstacle clearance along V004 section');ax.legend();ax.grid(alpha=.25);fig.savefig(O/'V017_Clearance_Margin_Profile.png',dpi=160);plt.close(fig)
# Blender-friendly diagnostic-only GLB: 4 independent annular meshes; never used for collision.
s=trimesh.Scene()
for i,m in enumerate(markers):
 n=24;vertices=[]
 for radius in (.23,.31):
  for a in np.linspace(0,2*math.pi,n,endpoint=False):vertices.append((m['x']+radius*math.cos(a),m['y'],m['z']+radius*math.sin(a)))
 faces=[]
 for j in range(n):
  k=(j+1)%n;faces.extend(((j,k,n+k),(j,n+k,n+j)))
 mesh=trimesh.Trimesh(vertices=np.asarray(vertices),faces=np.asarray(faces),process=False);mesh.visual.face_colors=[228,176,54,185];s.add_geometry(mesh,geom_name=f'V017_diagnostic_only_{i+1}',node_name=f'V017_diagnostic_only_{i+1}')
f=O/'V017_Clearance_Diagnostic_Rings.glb';f.write_bytes(s.export(file_type='glb'))
check=trimesh.load(f,force='scene');assert len(check.geometry)==len(markers) and sum(len(g.faces) for g in check.geometry.values())==48*len(markers)
images=[('通行路線與柱位',O/'V017_Clearance_Route_Map.png'),('沿線淨空曲線',O/'V017_Clearance_Margin_Profile.png')]
imgs=''.join('<figure><img alt="'+title+'" src="data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()+'"><figcaption>'+title+'（僅以模型資料計算；非實景測繪）</figcaption></figure>' for title,path in images)
a=v['summary']
html='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V017 通行淨空診斷</title><style>body{font:16px system-ui,'Noto Sans TC',sans-serif;line-height:1.65;margin:0 auto;padding:26px 18px;max-width:1000px;background:#f6f5f1;color:#2d3336}h1{font-size:1.6rem}h2{font-size:1.1rem}figure{margin:18px 0}figure img{width:100%;height:auto;border-radius:8px;border:1px solid #dadada}figcaption{color:#647078;font-size:13px}section{background:white;border-radius:12px;padding:18px;margin-top:18px}.pill{display:inline-block;background:#f0ece3;padding:4px 10px;border-radius:99px;font-size:13px}strong{font-variant-numeric:tabular-nums}footer{font-size:13px;color:#53606b}</style><h1>登別伊達時代村 V017 — 商家門前通行淨空診斷</h1><p><span class="pill">可回溯候選版／沒有改建築與碰撞</span></p><section><h2>量測結果</h2><p>V004 既有商家街中心路線 237 個取樣點皆位於 V004 模型可行走範圍；扣除角色半徑 26 公分後，至最近模型柱子的最低水平淨餘距為 <strong>23.20 公分</strong>（路線 s≈89.87 公尺）。整段中心線最大縱坡約 1.58%。</p><p>這只能證明目前路線中心線的二維幾何模型未與已登記障礙相交；<strong>不能證明各店入口、柱廊橫向通道、門檻、無障礙通行或室內可進入</strong>。建築與柱位仍有作者推估成分。</p></section><section><h2>量測圖</h2>'''+imgs+'''</section><section><h2>遊戲內診斷</h2><p>V017 Runtime 在 B 精修模式新增「步行淨空診斷 關／開」，預設關閉。標記只提示中心路線靠近既有柱碰撞的位置，不具碰撞、不更改人或路線。</p></section><footer>原始資料：V016 封存的 scene_view.json、extension_collision.json 與 collision.json，經 SHA-256 核對。地理與立面現況未實地量測。</footer></html>'''
(O/'Noboribetsu_Date_V017_R1_Review.html').write_text(html)
print('review created',[(x.name,x.stat().st_size) for x in O.glob('*.png')],f.stat().st_size)