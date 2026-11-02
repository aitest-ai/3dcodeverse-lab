#!/usr/bin/env python3
"""Finalize V014 optional inlay from frozen V013; no old file writes."""
from pathlib import Path
import json,hashlib,zipfile,shutil,base64,datetime
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np
import trimesh
R=Path(__file__).resolve().parent;OUT=Path('/mnt/data')
D=R/'candidate';SRC=R/'base';E=R/'evidence';PATCH=R/'v014_center_stones.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

p=json.loads(PATCH.read_text());geom=trimesh.Trimesh(vertices=np.array(p['positions']).reshape((-1,3)),faces=np.array(p['indices']).reshape((-1,3)),process=False)
geom.visual.vertex_colors=np.concatenate([np.array(p['colors']).reshape((-1,3))*255,np.full((p['vertices'],1),255)],axis=1).astype('uint8')
model_path=OUT/'Noboribetsu_Date_V014_R1_Central_Stones.glb';geom.export(model_path)
probe=trimesh.load(model_path,force='scene',process=False);assert sum(len(g.faces) for g in probe.geometry.values())==p['triangles']

# Independent build from same immutable base: two final outputs must byte-for-byte agree.
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('integrate',R/'integrate_v014.py');m=module_from_spec(spec);spec.loader.exec_module(m)
second=R/'replay';shutil.rmtree(second,ignore_errors=True);m.run(SRC,second,PATCH)
first_hash={x.relative_to(D).as_posix():sha(x) for x in D.rglob('*') if x.is_file()}
second_hash={x.relative_to(second).as_posix():sha(x) for x in second.rglob('*') if x.is_file()}
assert first_hash==second_hash
with (R/'V014_replay_qa.json').open('w') as f:json.dump({'status':'PASS_BYTE_IDENTICAL','files':len(first_hash),'matched':len(first_hash),'old_input_files':108,'old_files_unchanged':104,'source_v013_sha256':sha('/mnt/data/files/Noboribetsu_Date_V013_R1_Runtime.zip')},f,indent=2)

# Actual 3D browser screenshots are saved from a special isolated Xvfb / Chromium / SwiftShader test.
a=Image.open(E/'V014_V004_before_RealWebGL2.png').convert('RGB');b=Image.open(E/'V014_V004_after_RealWebGL2.png').convert('RGB');assert a.size==b.size
canvas=Image.new('RGB',(a.width*2,a.height+55),'#faf9f6');canvas.paste(a,(0,55));canvas.paste(b,(a.width,55));draw=ImageDraw.Draw(canvas)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:font=ImageFont.truetype(font_path,20)
except:font=None
draw.text((18,14),'V013 / BEFORE  (original paving)',fill='#23372e',font=font);draw.text((a.width+18,14),'V014 / AFTER  (optional stone study)',fill='#23372e',font=font)
comp=OUT/'Noboribetsu_Date_V014_R1_Comparison.png';canvas.save(comp,optimize=True)

def datauri(p):return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
html='''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V014 實際 WebGL2 比較</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f5f3ed;color:#25372e;font-family:system-ui,"Noto Sans TC",sans-serif;line-height:1.65}main{max-width:1050px;margin:0 auto;padding:24px}h1{margin:0 0 6px}p{margin:8px 0 18px}.note{background:#e7e7df;padding:12px 16px;border-radius:12px}.stage{position:relative;width:100%;aspect-ratio:850/510;overflow:hidden;border-radius:16px;border:1px solid #bec6bc;background:#ddd;touch-action:pan-y}.stage img{position:absolute;inset:0;display:block;width:100%;height:100%;object-fit:contain}.foreground{clip-path:inset(0 50% 0 0)}.divider{position:absolute;top:0;bottom:0;left:50%;width:3px;background:#f8f6ef;box-shadow:0 0 0 1px #324b3d}.hint{position:absolute;top:14px;left:14px;border-radius:10px;background:#f4f2e8ed;padding:6px 12px;font-size:13px}.controls{margin-top:12px;display:flex;align-items:center;gap:14px}input{flex:1;accent-color:#476955}footer{font-size:13px;color:#637263;margin:22px 0}a{color:#275e54}</style></head><body><main><h1>登別伊達時代村｜V014 石板設計比較</h1><p>真正 Chromium WebGL2 / SwiftShader，同一鏡位，拖曳下方滑桿即可比較。</p><div class="stage"><img alt="V013 原始鋪面" src="'''+datauri(E/'V014_V004_before_RealWebGL2.png')+'''"><img id="foreground" class="foreground" alt="V014 新增中央石板候選" src="'''+datauri(E/'V014_V004_after_RealWebGL2.png')+'''"><div id="divider" class="divider"></div><span class="hint">左側顯示 V014 新石板｜右側顯示原鋪面</span></div><div class="controls"><label for="slider">石板候選顯示比例</label><input id="slider" type="range" min="0" max="100" value="50"><output id="value">50%</output></div><p class="note">**資料界線：** 此為依實景照片「街道中央有淺色石板」得到的美術設計候選。石板在 V004 街段的確切位置與尺寸<strong>尚未確認</strong>；測試使用隔離瀏覽器與測試專用雜湊替身，不等於私人網站 HTTPS 或 Android 真機驗收。</p><footer>50 塊石板 · 100 個三角面 · 不更改原始 GLB、A/B 路線及碰撞。舊版完整保留。</footer></main><script>const slider=document.getElementById('slider'),foreground=document.getElementById('foreground'),divider=document.getElementById('divider'),value=document.getElementById('value');function update(){let x=+slider.value;foreground.style.clipPath=`inset(0 ${100-x}% 0 0)`;divider.style.left=x+'%';value.textContent=x+'%'}slider.addEventListener('input',update);update()</script></body></html>'''
review=OUT/'Noboribetsu_Date_V014_R1_Review.html';review.write_text(html,encoding='utf8')

# Explicitly separate: actual WebGL2 pass; button+AB were observed but cleanup timed out.
before=np.asarray(a,dtype=np.int16);after=np.asarray(b,dtype=np.int16);changed=np.any(np.abs(after-before)>14,axis=2)
qa={'schema':'noboribetsu-date-v014-validation/1','status':'CANDIDATE_WITH_EXPLICIT_GATES','geometry':json.loads((R/'V014_geometry_qa.json').read_text()),'clean_replay_files':len(first_hash),'clean_replay_identical':True,
    'webgl2':{'actual_browser_rendered':True,'browser':'Chromium Xvfb SwiftShader WebGL2','v011_v012_v013_loaded':True,'v014_loaded':True,'javascript_errors_observed':0,'missing_requests_observed':0,'before_after_changed_pixels_threshold14':int(changed.sum()),'scene_total_draw_triangles_after':1439198,
      'test_only_sha_adapter':True,'native_webcrypto_in_real_site_not_tested':True},
    'ui':{'user_toggle_false_true_observed':True,'ab_eye_target_up_fov_zero_observed':True,'test_process_browser_cleanup_timed_out':True},
    'assets':{'inlay_glb_sha256':sha(model_path),'inlay_json_sha256':sha(PATCH),'underlying_v004_road_sha256':p['asset_source']['v004_road_sha256']},
    'not_tested':['Android actual device','private website actual HTTPS/CDN/login','Blender-native .blend/Cycles','actual stone position and dimensions surveyed']}
valpath=OUT/'Noboribetsu_Date_V014_R1_Validation.json';valpath.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
readme='''# 登別伊達時代村 V014 — V004 中央石板設計候選\n\n這一輪不是擴園或重建場景。以 V013 原 ZIP 為凍結來源，只在 V004 s=89.5–124.5m 內加入一小段 50 塊淺色中央石板設計研究，並提供真正遊戲中的開／關按鈕。\n\n## 內容\n\n- `build_v014.py`：只讀 V013 路線與 V004 原始石邊位置，新增 50 塊石板（100 面），不更動原有模型。\n- `integrate_v014.py`：從 V013 完整執行包建立另一份 V014 runtime，防止覆蓋。\n- `qa_v014_webgl.py`：隔離 Xvfb + Chromium 的實際 WebGL2 測試，僅 QA 使用測試專用 SHA 替身與鏡位，正式 Runtime 絕不包含。\n- `V014_geometry_qa.json`, `V014_replay_qa.json`, `V014_Validation.json`：各自的檢查證據。\n- `V014_V004_before_RealWebGL2.png`、`V014_V004_after_RealWebGL2.png`：相同鏡位真實渲染圖。\n\n## 重建方式\n\n1. 解壓 V013 Runtime ZIP 到新的 `v013` 資料夾（有 `dist`）。\n2. 執行 `python build_v014.py v013 v014_center_stones.json`。\n3. 執行 `python integrate_v014.py v013 v014 v014_center_stones.json`。\n4. 在一般支援 WebGL2 的電腦，以本機 HTTP 伺服器提供 `v014/dist`（不要以 file:// 開啟）；於 B 場景中使用「中央石板候選」開關。\n\n## 重要的真實性界線\n\n- 實景照片只能支持「時代村某段商家街有中央淺色石板」的視覺特徵，不能核對本段確切位置或尺寸。此項是可拆除、可關閉的作者推估設計。\n- 原道路 GLB、V011 地形補洞、V012/V013 路緣、A 骨架、231.5664m 路線及碰撞全部保留。\n- Chromium 已完成真 WebGL2 渲染和畫面比較；實際私人站 HTTPS、Android 真機與 Blender-native 未驗。\n- 只在隔離 QA 中使用 Python 獨立 SHA 核對後的測試替身；正式 Runtime 保留 WebCrypto 原生 SHA。\n'''
(R/'README_V014_SourceQA.md').write_text(readme,encoding='utf8')
report=f'''# 登別伊達時代村 V014 R1｜中央石板設計候選交付報告\n\n日期：2026-11-02\n\n**成果：** 從 V013 完整保存的 108 個執行檔非破壞性衍生 V014，加入 50 塊／100 面中央淺色石板。原始 V004 路面與其距離最近的舊石邊約 2.89m；不重畫已完成的瓦片、人物、石邊、道路或 V011–V013。\n\n**視覺差異：** Xvfb/Chromium/SwiftShader 真 WebGL2 進場、同鏡位開關石板，達 {int(changed.sum()):,} 個超過 14 色差的畫素。UI 開關與 A/B 切換零視角漂移在測試中觀察通過，但瀏覽器清理程序最後逾時，明確不記為全流程自動測試無瑕通過。\n\n**來源：** 參照登別伊達時代村商家街照片的中央石板設計語彙，但實際 V004 有無這段石板尚未調查；不能當現地測量或已完成復原。官方設施 https://edo-trip.jp/tw/eat/；其他街景參考 https://www.mapple.net/spot/1000977/ 。外部照片不複製進遊戲或 ZIP。\n\n**完整性：** 原 V013 108 檔中 104 檔 SHA 相同，僅 `dist/app.js`、`dist/index.html`、`dist/qa.json`、`dist/scene_view.json` 修改，另新增兩檔。從 V013 同一來源乾淨重建，{len(first_hash)}/{len(first_hash)} 檔逐位元一致。\n\n**仍未測：** Android 真機、正式私人站 HTTPS/CDN、Blender Native `.blend`/Cycles、石板現地位置與比例。既有網站保持不變。\n'''
reportpath=OUT/'Noboribetsu_Date_V014_R1_Delivery_Report.md';reportpath.write_text(report,encoding='utf8')

# Zip runtime without changing relative project shape.
runtime=OUT/'Noboribetsu_Date_V014_R1_Runtime.zip'
with zipfile.ZipFile(runtime,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(D.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(D))
# source archive includes code + validated images and note, not 72 MB original GLBs.
source=OUT/'Noboribetsu_Date_V014_R1_SourceQA.zip'
files=[R/'build_v014.py',R/'integrate_v014.py',R/'qa_v014_webgl.py',R/'v014_center_stones.json',R/'V014_geometry_qa.json',R/'V014_replay_qa.json',R/'README_V014_SourceQA.md',valpath,reportpath,review,comp,model_path,E/'V014_V004_before_RealWebGL2.png',E/'V014_V004_after_RealWebGL2.png']
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for f in files:z.write(f,('source/' if f.suffix in ['.py','.json','.md'] else 'evidence/')+f.name)
for f in [runtime,source]:
 with zipfile.ZipFile(f) as z:assert z.testzip() is None
manifest={'schema':'noboribetsu-date-v014-artifact-manifest/1','source_v013_sha256':sha('/mnt/data/files/Noboribetsu_Date_V013_R1_Runtime.zip'),'outputs':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f)} for f in [runtime,source,model_path,review,comp,reportpath,valpath]}}
(OUT/'Noboribetsu_Date_V014_R1_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'replay':len(first_hash),'runtime_bytes':runtime.stat().st_size,'source_bytes':source.stat().st_size,'stone_triangles':p['triangles'],'change_pixels':int(changed.sum()),'output_files':[f.name for f in [runtime,source,review,comp,model_path,reportpath,valpath]]},ensure_ascii=False,indent=2))