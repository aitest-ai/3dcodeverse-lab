"""Summarize measured browser/Blender results and build a local evidence player; never art-approve assets."""
import json,hashlib,struct,sys,math,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'evidence-v05';sys.path.insert(0,str(R/'scripts'));from v05.overlay import read

def values(d,b,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];count=a['count']*{'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];return struct.unpack_from('<'+'f'*count,b,v.get('byteOffset',0)+a.get('byteOffset',0))
rows=[]
for key,id in [('vivi','vroid-vivi-motion-review'),('shiba','quaternius-shibainu-grounded-review')]:
 candidate=R.parents[1]/'work/v05'/f'{key}-reexport.glb'
 if not candidate.exists():continue
 original=R/'library-v05'/id/'0.1.0/model.glb';d,b=read(original);x,y=read(candidate);errors=[]
 for a in d['animations']:
  aa=next(aa for aa in x['animations'] if aa['name']==a['name']);other={(c['target']['node'],c['target']['path']):aa['samplers'][c['sampler']] for c in aa['channels']}
  for c in a['channels']:
   s=a['samplers'][c['sampler']];t=other[(c['target']['node'],c['target']['path'])];v=values(d,b,s['output']);w=values(x,y,t['output']);assert len(v)==len(w);errors.append(max(abs(a-b) for a,b in zip(v,w)))
 maximum=max(errors);assert maximum<.00002,maximum;rows.append({'id':id,'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'new_candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'maximum_animation_component_error':maximum,'original_geometry_skin_material_texture_prefix':'unchanged','bitwise_identical':False,'registered':False})
(E/'export-roundtrip.json').write_text(json.dumps({'method':'Actually cold-open mother and run export_motion_v05.py for both assets. Compare every animation output component; float rounding allowed, new SHA recorded. New outputs remain unregistered work files.','entries':rows},indent=2)+'\n')
try:
 import numpy as np
 from scipy.spatial import cKDTree
 agreement=[]
 for key in ['vivi','shiba']:
  cold=json.loads((E/f'{key}-cold-geometry.json').read_text());browser=json.loads((E/f'{key}-geometry-sample.json').read_text())[1]['meshes'];tree=cKDTree(np.concatenate(list(cold.values())));maximum=max(float(max(tree.query(m['vertices'])[0])) for m in browser);assert maximum<.00001,(key,maximum);agreement.append({'key':key,'clip':'Run' if key=='vivi' else 'Gallop','t':.3,'max_nearest_surface_vertex_distance_m':maximum,'vertices':sum(len(m['vertices']) for m in browser)})
 (E/'browser-blender-surface-agreement.json').write_text(json.dumps({'method':'All unique primitive position arrays from actual Chromium deformation vs independently cold-opened Blender surface at the same t=.30; nearest-vertex comparison (no topology/collision claim).','entries':agreement},indent=2)+'\n')
except ImportError:pass
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','format=duration,size:stream=nb_read_frames,avg_frame_rate','-of','json',str(E/'shiba-live-browser.webm')]));(E/'live-video.json').write_text(json.dumps({'source':'Actual browser canvas MediaRecorder captureStream(24), 6 seconds wall-clock request','probe':meta,'real_time_performance_approved':False,'note':'Software GPU dropped frames; encoded duration differs from wall-clock capture. Not physical-device performance.'},indent=2)+'\n')
from PIL import Image,ImageOps,ImageDraw
frames=json.loads((E/'frame-catalog.json').read_text())['sequences']
for key,clip in [('vivi','Walk'),('vivi','Run'),('shiba','Walk'),('shiba','Gallop')]:
 canvas=Image.new('RGB',(800,4*245+35),'#f3f5f1');draw=ImageDraw.Draw(canvas);draw.text((12,10),f'{key} {clip}: actual browser A/B; front / side / back / feet; phases 0.125 and 0.625',fill='#222222')
 for row,view in enumerate(['front','side','back','feet']):
  seq=next(s for s in frames if s['key']==key and s['clip']==clip and s['view']==view)
  for col,index in enumerate([1,5]):
   im=Image.open(E/seq['frames'][index]['file']);im.thumbnail((395,240));canvas.paste(im,(col*400,row*245+35))
 canvas.save(E/f'{key}-{clip}-overview.jpg',quality=90)
for e in json.loads((R/'library-v05/catalog.json').read_text())['entries']:
 key='vivi' if e['id'].startswith('vroid') else 'shiba';seq=next(s for s in frames if s['key']==key and s['clip']=='Walk' and s['view']=='front');im=Image.open(E/seq['frames'][0]['file']);w,h=im.size;im=im.crop((0 if e['variant']=='before' else w//2,0,w//2 if e['variant']=='before' else w,h));im.thumbnail((360,280));im.convert('RGB').save(E/'thumbnails'/f"{e['id']}.jpg",quality=88)
(E/'index.html').write_text('''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0.5.0 實際瀏覽器動作證據</title><style>body{margin:24px;background:#eef2ed;color:#24352e;font:16px system-ui}main{max-width:1300px;margin:auto}img{width:100%;border-radius:12px}select,button,input{padding:10px;margin:6px}video{width:min(100%,1000px)}a{color:#176849}p{line-height:1.7}</style><main><h1>實際瀏覽器 A/B 連續畫面</h1><p>208 張 Chromium WebGL 畫面；A 與 B 同片段、同相位、同鏡位。以下是取樣畫面播放器，不代表即時效能或人工美術核准。<a href="../web-v05/">開啟即時 3D 驗收場</a></p><select id="seq"></select><button id="play">播放取樣</button><input id="phase" type="range" min="0" max="7" step="1" value="0"><span id="label"></span><img id="image"><h2>實際錄影</h2><p>柴犬 WebM：瀏覽器 canvas 連續錄製，要求 6 秒牆鐘時間，實際編碼約 5.36 秒；SwiftShader 可能掉格。手機真機未測。</p><video controls src="shiba-live-browser.webm"></video><p><a href="browser-contacts.json">120 Hz 接地量測</a> · <a href="browser-ui.json">瀏覽器操作結果</a> · <a href="blender-cold.json">母檔冷開檢查</a> · <a href="../README_V05.md">限制與來源</a></p></main><script>let data,index=0,active=false,last=0;const $=id=>document.getElementById(id);function show(){const s=data[index],f=s.frames[+$('phase').value];$('image').src=f.file;$('label').textContent=`${f.time_s.toFixed(3)} s · ${Math.round(f.phase*100)}%`;}fetch('frame-catalog.json').then(r=>r.json()).then(x=>{data=x.sequences;data.forEach((s,i)=>$('seq').add(new Option(`${s.key} / ${s.clip} / ${s.view}`,i)));show()});$('seq').onchange=()=>{index=+$('seq').value;$('phase').max=data[index].frames.length-1;$('phase').value=0;show()};$('phase').oninput=()=>{active=false;show()};$('play').onclick=()=>{active=!active;$('play').textContent=active?'暫停取樣':'播放取樣'};function tick(t){requestAnimationFrame(tick);if(!active||!data)return;const s=data[index];if(t-last>s.duration_s*1000/s.frames.length){$('phase').value=(+$('phase').value+1)%s.frames.length;show();last=t}}requestAnimationFrame(tick);</script>''')
print('Evidence summary / gallery generated')
