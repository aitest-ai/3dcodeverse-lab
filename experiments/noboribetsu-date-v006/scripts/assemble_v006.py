#!/usr/bin/env python3
"""Produce offline V006 runtime + editable source-QA package, with immutable V005 lineage."""
from pathlib import Path
import hashlib,json,zipfile,base64,html,shutil,os
root=Path(__file__).resolve().parent.parent;d=root/'dist';out=Path('/mnt/data');e=root/'evidence'
qa_files=['V006_navigation_qa.json','V006_placeholder_qa.json','V006_surface_qa.json','V006_replay_qa.json','V006_http_qa.json']
qas={n:json.loads((e/n).read_text()) for n in qa_files}
assert qas['V006_navigation_qa.json']['status']=='PASS_STATIC_NAVIGATION_ONLY'
assert qas['V006_placeholder_qa.json']['status']=='PASS_NODE_THREE_GEOMETRY_NOT_WEBGL'
assert qas['V006_surface_qa.json']['status']=='PASS_STATIC_SURFACE_ONLY'
assert qas['V006_replay_qa.json']['status']=='PASS'
assert qas['V006_http_qa.json']['status']=='PASS_HTTP_RESOURCES_ONLY'
status={'version':'V006-tail-candidate-r1','local_date':'2026-11-01','version_status':'candidate_static_pass_external_acceptance_pending',
 'base':'V005-east-candidate-r1','scope':'final two OSM route legs; no new building',
 'route_m':231.56641497226084,'added_m':33.84248088413378,
 'QA':{n:{'status':q['status']} for n,q in qas.items()},
 'V005_artifact_unchanged':{'old_dist_files':56,'changed_files':['app.js','index.html','qa.json','scene_view.json'],'unchanged_old_assets':52},
 'original_B_osm_replacements':qas['V006_placeholder_qa.json']['removed_by_building'],
 'browser_webgl2':'NOT_AVAILABLE_IN_THIS_ENVIRONMENT','Android_physical':'NOT_TESTED','Blender_native':'NOT_RUN',
 'private_site':'UNCHANGED','third_person':'OFF','geometry_source':'Frozen 2026-10-31 V002 OSM + GSI DEM, not surveyed'}
(out/'Noboribetsu_Date_V006_R1_Validation.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
server=root/'start_server.py'
s=server.read_text().replace('V005 local preview','V006 local candidate')
server.write_text(s)
readme='''# 登別伊達時代村 V006 R1（獨立候選）

本版從 V005 R1 沿凍結 V002 OSM 再延伸 33.8425 m，總路線 231.5664 m；修正 V004/V005 五棟建物替換時留下的灰色量體碎面。保留原 V003 B 高品質模型與 A 懶載入，不降低解析度。**不宣稱現場測繪、官方建築還原或完整 WebGL2 驗收。**

## 本機開啟

將 ZIP 解壓，保持 `dist/` 檔案架構，在最外層執行：

```bash
python start_server.py
```

開啟 `http://127.0.0.1:8766/`。請使用支援 WebGL 2 的桌面瀏覽器；Android/私人 CDN 尚未測試。本環境中 Chromium WebGL2 建立失敗，因此只能確認真實 GLB、碰撞、幾何排除、Node Three.js 模擬及本機 HTTP；**未宣稱遊戲實際渲染成功**。

### 版本繼承
- V002 大手門／遊戯館；V003 R3 完整高品質模型＋A 懶載入。
- V004 商家街第一段三棟估計立面；V005 草鞋屋與變裝攝影館估計立面；V006 不新增建物，只接最後兩段已凍結 OSM 道路。
- 原始 V005 既有 56 份 dist 檔中 52 份完全不變，僅 4 份更新；沒有改寫舊版本 ZIP／私人預覽。
- 第三人稱仍停用。

`Noboribetsu_Date_V006_R1_Validation.json` 提供證據摘要，`Noboribetsu_Date_V006_R1_Review.html` 是離線同鏡位幾何比較（非遊玩頁）。

來源：© OpenStreetMap contributors (ODbL)、日本國土地理院高程來源與 V002 衍生資料；商家外觀為作者推估，不能當成現場建築紀錄。
'''
(root/'README.md').write_text(readme)
report='''# 登別伊達時代村 3D 漫遊｜V006 R1 擴建與品質修正報告

**2026-11-01，候選版。** 保留 V002、V003、V004、V005，不合併舊 PR、不上線、不開放分享設定。

## 本輪實際改良

- **路線**：從 V005 197.7239 m 沿凍結 V002 OSM 最後兩段再延伸 33.8425 m，成為 231.5664 m 連續步行路線。兩段各約 13.70、20.14 m，沒有猜測捷徑。
- **新增 3D 幾何**：`v006_tail_road.glb`，一份真正獨立的 GLB，內含路面 972 三角面與低對比路側過渡 324 三角面，共 1296 三角面。路寬約 6m 是沿用 V005 的作者假設，非實地測量。沒有新增建築、室內或人物。
- **地形接地**：從凍結 V002 GSI DEM 在七條橫向位置取樣，V006 路段 2592 個幾何頂點回讀後均高於 DEM，原始地形覆蓋失敗數 0，表面與 DEM 的 4.2cm / 5cm 差異是顯示層的防閃爍間距，不代表實際路面高度。
- **灰色 OSM 建物**：在實際 V003 高品質 B GLB 解包出的 368 面 OSM 灰色量體上，改用 0.1mm 頂點連通塊而非個別三角面中心點判定。針對 V004 三棟（28、28、20 面）與 V005 兩棟（12、12 面），合計完整排除 100 面，剩下 268 面非目標量體；再排一次應拒絕繼續。原 V003 B GLB 位元組完全保留。
- **導覽與碰撞**：A/B 共 944 個檢查點、完整去回步行、原路線姿態切換均通過，最大單步高程差約 0.088m；V006 增加 162 個步行碰撞三角面。
- **重建驗證**：由 V005 Runtime 的封存 ZIP、凍結 V002 幾何、獨立工程腳本重新產出 11 個主要產物，SHA-256 全部一致；V005 56 個既有 dist 檔僅 `app.js`、`index.html`、`qa.json`、`scene_view.json` 改變，其他 52 個均無變動。
- **本機 HTTP**：七份資源可透過 localhost 正常回傳且 SHA 匹配；這不是 WebGL2 渲染通過。

## 明確未驗證

1. **WebGL 2**：此環境 Chromium 四組 EGL/SwiftShader/ANGLE 設定均無法取得 context，無法宣稱整個 Three.js 場景可正常播放、灰量體畫面完全消失或 FPS/記憶體表現。
2. **Android 真機／私人網站 CDN 登入**：未測，未更新網址。
3. **Blender-native 可編輯 `.blend`／Cycles 同鏡位**：未執行。這一輪 Blender 回寫尚未升格正式母檔；只提供可重建程序化幾何與 glTF。
4. **現場照片與建築還原精度**：V004／V005 五棟外觀仍是原創估計版本；未添加未核實的新建築。
5. **OSM 地理資料限制**：最後兩段為 V002 凍結 OSM 可見的道路軸線，並非經現地步行勘查保證可通行。

## 交付方式

`Runtime.zip` 含獨立本機播放器與既有完整資產；`SourceQA.zip` 含重建／整合／導航、灰量體遮罩實際測試、來源摘要與 4 組 V005/V006 同鏡位診斷圖片。`Review.html` 可離線比較；不是可玩的 WebGL 場景。

凍結來源 © OpenStreetMap contributors（ODbL），地形來源為 V002 所附 GSI DEM1A 衍生。原圖未以官方照片貼圖形式隨包重製。
'''
(out/'Noboribetsu_Date_V006_R1_Delivery_Report.md').write_text(report)
# Standalone offline photo comparison with embedded locally rendered, original geometries.
images={}
for angle in ['aerial','bend','end_looking_back','from_shops']:
 images[angle]={'before':base64.b64encode((root/f'V005_same_{angle}.png').read_bytes()).decode(),
                'after':base64.b64encode((root/f'V006_{angle}.png').read_bytes()).decode()}
css='''body{margin:0;background:#f8f7f1;color:#273a32;font-family:system-ui,"Noto Sans TC",sans-serif}main{max-width:1250px;margin:auto;padding:32px 22px}h1{font-size:2rem;margin:0 0 7px}.sub{color:#647369}.hero{background:#eaece4;padding:18px 24px;border-radius:16px;margin:22px 0}section{margin:35px 0}h2{font-size:1.25rem}.compare{position:relative;width:100%;aspect-ratio:16/10;overflow:hidden;border-radius:12px;border:1px solid #d3d8d0;background:#e7e6de}.compare img{width:100%;height:100%;position:absolute;inset:0;object-fit:contain}.compare .after{clip-path:inset(0 0 0 50%)}.compare::after{content:"";position:absolute;left:50%;top:0;bottom:0;width:2px;background:white;box-shadow:0 0 3px #333}input[type=range]{width:100%;margin-top:14px;accent-color:#966b4f}.labels{display:flex;justify-content:space-between;color:#5c675f;font-size:.92rem}.note{font-size:.92rem;color:#5d6a60}a{color:#476e61}footer{border-top:1px solid #d9ddd6;padding:22px 0;color:#607069}'''
js='''document.querySelectorAll('input[type=range]').forEach(input=>{input.addEventListener('input',()=>{const parent=input.closest('section').querySelector('.compare');const n=Number(input.value);parent.querySelector('.after').style.clipPath=`inset(0 ${100-n}% 0 0)`;parent.style.setProperty('--pct',n+'%');parent.style.setProperty('--pos',n+'%');});});'''
sections=[]
for angle,title in [('aerial','商家街延伸鳥瞰'),('bend','V006 轉角'),('end_looking_back','V006 街尾回望'),('from_shops','由商家街眺望新道路')]:
 a=images[angle];sections.append(f'''<section><h2>{title}</h2><div class="compare"><img alt="V005 同鏡位" src="data:image/png;base64,{a['before']}"><img class="after" alt="V006 新道路同鏡位" src="data:image/png;base64,{a['after']}"></div><input aria-label="V005 V006 同鏡位比較滑桿" type="range" min="0" max="100" value="50"><div class="labels"><span>左：V006 新版</span><span>右：V005 舊版</span></div></section>''')
index=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V006 R1｜幾何比較</title><style>{css}</style></head><body><main><h1>登別伊達時代村 V006 R1</h1><div class="sub">兩段新道路／五棟舊量體修正｜同鏡位比較</div><div class="hero"><strong>V005 197.7 m → V006 231.6 m</strong><p>延伸凍結 V002 OSM 最後兩段，總增加 33.84 m。五棟舊灰色量體的實際 B 模型幾何排除測試通過，沒有新增臆測建築。</p><p class="note">畫面為離線 VTK 依實際 GLB 幾何的診斷渲染，非最終 Three.js 遊戲畫面、Blender Cycles 或現場實景。可拖動下方滑桿查看新舊版本。</p></div>{''.join(sections)}<footer>© OpenStreetMap contributors / ODbL，來源地形 V002 GSI DEM；外觀推估，不代表官方建築。WebGL2、Android、私人預覽仍未驗收。</footer></main><script>{js}</script></body></html>'''
(out/'Noboribetsu_Date_V006_R1_Review.html').write_text(index,encoding='utf8')
# Consolidate runtime ZIP; preserve full V005 high quality model and all dependent files.
(runtime:=out/'Noboribetsu_Date_V006_R1_Runtime.zip').unlink(missing_ok=True)
with zipfile.ZipFile(runtime,'w') as z:
 for p in sorted(d.rglob('*')):
  if p.is_file():z.write(p,'dist/'+str(p.relative_to(d)),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
 z.write(root/'README.md','README.md',compress_type=zipfile.ZIP_DEFLATED)
 z.write(root/'start_server.py','start_server.py',compress_type=zipfile.ZIP_DEFLATED)
 z.write(out/'Noboribetsu_Date_V006_R1_Validation.json','Noboribetsu_Date_V006_R1_Validation.json',compress_type=zipfile.ZIP_DEFLATED)
# Source package deliberately excludes any large private V002/V005 full model, but includes editable procedural sources and small QA primitive.
(source:=out/'Noboribetsu_Date_V006_R1_SourceQA.zip').unlink(missing_ok=True)
with zipfile.ZipFile(source,'w') as z:
 for p in sorted((root/'scripts').glob('*')):
  if p.is_file():z.write(p,'source/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 for p in sorted((root/'baseline').glob('*')):
  if p.is_file():z.write(p,'baseline/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 for p in sorted(e.glob('*')):
  if p.is_file():z.write(p,'evidence/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 for p in sorted(root.glob('V00*.png')):
  z.write(p,'screenshots/'+p.name,compress_type=zipfile.ZIP_DEFLATED)
 for p in (out/'Noboribetsu_Date_V006_R1_Validation.json',out/'Noboribetsu_Date_V006_R1_Delivery_Report.md'):
  z.write(p,p.name,compress_type=zipfile.ZIP_DEFLATED)
 z.write(root/'README.md','README.md',compress_type=zipfile.ZIP_DEFLATED)
for zpath in (runtime,source):
 with zipfile.ZipFile(zpath) as z:
  bad=z.testzip()
  if bad:raise RuntimeError('ZIP integrity failed: '+bad)
 print('PACKED',zpath,zpath.stat().st_size)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
all_out={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (runtime,source,out/'Noboribetsu_Date_V006_R1_Review.html',out/'Noboribetsu_Date_V006_R1_Delivery_Report.md',out/'Noboribetsu_Date_V006_R1_Validation.json',root/'dist/assets/v006_tail_road.glb')}
(out/'Noboribetsu_Date_V006_R1_SHA256.json').write_text(json.dumps(all_out,ensure_ascii=False,indent=2)+'\n')