#!/usr/bin/env python3
"""Produce verifiable, self-contained V005 R1 candidate delivery without touching V004."""
from pathlib import Path
import zipfile,json,hashlib,base64,html,shutil

ROOT=Path(__file__).resolve().parent.parent
RUNTIME=ROOT/'runtime';DIST=RUNTIME/'dist';TOP=Path('/mnt/data')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(1<<20):h.update(c)
 return h.hexdigest()
models=json.loads((DIST/'v005_manifest.json').read_text())
nav=json.loads((RUNTIME/'V005_navigation_qa.json').read_text())
assets=json.loads((RUNTIME/'V005_assets_qa.json').read_text())
replay=json.loads((ROOT/'V005_replay_sha256.json').read_text())
surf=json.loads((ROOT/'V005_surface_qa.json').read_text())
ph=json.loads((RUNTIME/'V005_osm_placeholder_audit.json').read_text())
webgl=json.loads((ROOT/'V005_webgl_probe.json').read_text())
assert nav['ok'] and assets['ok'] and replay['all_bitwise_equal']
assert surf['below_dem_count']==0 and surf['samples']>=500
assert len(assets['legacy_file_unchanged'])==46 and len(assets['legacy_file_changes'])==4
assert len(ph['target_footprints'])==5
assert all(not attempt.get('status',{}).get('ok',False) for attempt in webgl)

report=f'''# 登別伊達時代村 V005 R1｜商家街第二段工程交付報告

日期：2026-11-01（臺灣時間）  
狀態：**候選版，來源與步行驗收通過；正式瀏覽器與美術驗收未通過**。

## 已完成

V004 R1 道路終點由 **130.0146 m** 擴建至 **{nav['new_route_m']:.4f} m**，本輪新增 **{nav['add_m']:.4f} m**；新路段沿 V002 凍結 OpenStreetMap 路線第 5 個端點至第 6 個端點（局部 x 42.1249→101.7464、z 61.8949→93.9860）。不更動既有核心、V004 範圍或私人預覽網站。

兩棟新增建物：**わらじ屋（草鞋屋，OSM way/283905573）**、**うつろい館（變裝攝影館，OSM way/283905580）**。建築位置與平面來自凍結 V002 OSM；官方網站確認店家功能，但 **屋高、立面、牆材、窗櫺、屋瓦、檐口、木柱與招牌位置仍屬作者估計**。未建室內，未加入第三人稱，不打包第三方實景照片。

新增 3 份 GLB：

| 檔名 | 位元組 | SHA256 |
|---|---:|---|
'''
for n,p in models['models'].items():report+=f"| {n} | {p['bytes']:,} | `{p['sha256']}` |\n"
report+=f'''
## 已完成的真實程式驗證（不是遊戲畫面通過）

- V004 `dist/` 既有 **50 檔中 46 檔完全沒變**；只改 `app.js`, `index.html`, `qa.json`, `scene_view.json`，為 V005 必要接線。V004 三份新模型、V003 高品質 B 分片、A 模型、導航、控制器與碰撞資產 SHA 未變。
- 真實 3D GLB 各自重新讀入確認存在有效三角面；V005 路面／建築／招牌實際三角面數為 **{assets['models']['v005_east_road.glb']['triangles']:,} / {assets['models']['v005_east_facades.glb']['triangles']:,} / {assets['models']['v005_east_signs.glb']['triangles']}**。
- A／B **{nav['scanned']} 次** 路線碰撞點查核無阻擋；從入口走到 197.7 m 街尾再返回入口的模擬步行均無碰撞，A／B 相機姿態切換漂移為零。
- V002 GSI DEM 高程截面（非實測道路）取路寬 7 條橫向位置，避免直線插值使路段陷入草地。沿線 **{surf['samples']} 個視覺路面對 DEM 抽樣，埋入地形數為 {surf['below_dem_count']}**，最低圖面淨高差約 {surf['min_clearance_m']*100:.1f} 公分。此渲染層抬升不屬現場鋪面高程宣稱。
- 原始 V003 B GLB 靜態解包：`わらじ屋`（8 triangles）與 `うつろい館`（7 triangles）原灰色 OSM 量體確實存在，runtime 有對應替換邏輯；實際 WebGL 顯示與遮蓋仍未驗收。
- 重播：重新從凍結 V004 ZIP 獨立解壓，執行生成、整合與導航測試；新 GLB、碰撞、程式、場景描述等 **{len(replay['files'])} 份產物的 SHA-256 逐位元相同**。

## 未通過／不可宣稱

1. Chromium 144 軟體 WebGL2 兩組顯示設定皆無法建立 context。**無法宣告 V005 預覽真正玩過、畫面已通過或載入速度。**
2. Android 實機未測；私人網站 CDN、登入／公開設定未測也未變動。
3. 本環境無 Blender 5.2 執行檔，附 `blender_v005_extension_only.py` 只能在有 Blender 的機器建立獨立可編輯擴建母檔；這裡沒有正式 `.blend`、Cycles A/B，也沒合併既有 V003／V004 母檔。
4. 5 張 VTK 幾何圖為真實 GLB 模型獨立診斷，材質與光照 **不同於 Three.js／Blender Cycles**；不可當成實景照片對照驗收。
5. 本次新增路面寬度約 6 m 是作者估計，不是消防、無障礙或現場通行淨寬資料。

## 來源與版本

- V002 / V003 / V004 來源保留，這是獨立 V005 R1 候選；不改舊 ZIP 或正式網址。
- OpenStreetMap 歷史地理來源：© OpenStreetMap contributors / ODbL，凍結於 2026-10-31 V002 專案。
- 官方園區圖：https://edo-trip.jp/map/
- 草鞋屋官方：https://edo-trip.jp/facility/waraji-ya/ （2025-04 整修後店家用途）
- 變裝攝影館官方：https://edo-trip.jp/facility/utsuroi-kan/
- 原本 V003 R3 的 Three.js 著作權資訊、原始材質授權不變，隨 Runtime 保留。

下一輪：優先使用可運作的瀏覽器實測 V005 模型、消除舊灰色量體；再用現地照片比對 2 棟建物，確認真正檐口、立面方向與鋪面細節，最後依原 OSM 路線考慮往更深處擴建。
'''
report_path=TOP/'Noboribetsu_Date_V005_R1_Delivery_Report.md'
report_path.write_text(report,encoding='utf8')
readme=f'''# 登別伊達時代村 V005 商家街第二段｜執行候選 R1

**工程與碰撞已完成，真實 WebGL2／Android／Blender 正式 `.blend` 未驗收。**

## 快速開啟

1. 解壓本 Runtime ZIP（保留 dist/ 子資料夾）。
2. 安裝 Python 3.10+，在 ZIP 解壓目錄執行 `python start_server.py`。
3. 用支援 WebGL 2 的桌面瀏覽器開 `http://127.0.0.1:8766/`；首次下載需完整 V003 B 高品質模型，A 版本第一次點選才載入。
4. 電腦用方向鍵／WASD 及滑鼠、手機以虛擬搖桿與滑動方式操作；點選 A/B 會切換，但兩種版本均沿相同約 197.7 m 路線。勿直接開 `dist/index.html`，SHA-256 校驗需要安全環境。

## 內容

保留 V004 R1 約 130.0 m 核心；新增約 67.7 m 連續道路，新增「わらじ屋」與「うつろい館」外觀候選及作者製作的原創招牌（未使用官方照片貼圖）。V004 原本 3 棟建築均保留，總路線約 197.7 m。外觀比例尚未實景驗收，沒有室內與第三人稱人物。

## 測試界線

本輪真實 GLB 回讀、哈希檢查、A/B 782 點碰撞、雙向步行及 680 個 DEM 表面抽樣通過，但目前測試環境無 WebGL2，**沒有宣稱完整遊玩可用**。請見 `Noboribetsu_Date_V005_R1_Validation.json` 與 SourceQA ZIP 的來源程式。

源資料 © OpenStreetMap contributors / ODbL；外觀模型為原創估計重建，不屬官方。前三版、私人網站、GitHub main 與 Draft PR 均未改動。
'''
(RUNTIME/'README.md').write_text(readme,encoding='utf8')
(RUNTIME/'start_server.py').write_text('''#!/usr/bin/env python3
"""Serve only the extracted V005 dist, locally; no uploads or network publishing."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
root=Path(__file__).resolve().parent/'dist'
assert (root/'index.html').is_file()
server=ThreadingHTTPServer(('127.0.0.1',8766),partial(SimpleHTTPRequestHandler,directory=str(root)))
print('V005 local preview: http://127.0.0.1:8766/ (Ctrl+C to stop)')
try:server.serve_forever()
except KeyboardInterrupt:pass
''',encoding='utf8')

validation={'schema':'noboribetsu-date-v005-r1-validation/1','version':'V005-east-candidate-r1','status':'STATIC_NAV_PASS_REAL_WEBGL_NOT_TESTED',
'route_start_m':0,'route_end_m':nav['new_route_m'],'added_m':nav['add_m'],
'buildings':['わらじ屋','うつろい館'],'models':assets['models'],
'legacy_dist_files_unchanged':46,'legacy_dist_files_changed':assets['legacy_file_changes'],
'navigation':{'passed':nav['ok'],'A_B_points_tested':nav['scanned'],'walk':nav['walk'],'switch_zero_drift':nav['camera_switch_zero_drift']},
'visual_dem_surface':{'sampled':surf['samples'],'below_dem_count':surf['below_dem_count'],'min_clearance_m':surf['min_clearance_m']},
'static_osm_mass_triangles':{x:v['triangles_at_centroid'] for x,v in ph['target_footprints'].items()},
'replay_build_bit_exact':replay['all_bitwise_equal'],'webgl2_probe':webgl,
'android':'NOT_TESTED','blender_native':'NOT_EXECUTED','private_site':'NOT_CHANGED','github_merged':False,
'visual':'VTK independent GLB render, not Three.js or site photo match',
'interiors':'NOT_BUILT','third_person':'DISABLED'}
(TOP/'Noboribetsu_Date_V005_R1_Validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

pictures=[
 ('V005_route_overview.png','道路與 OSM 位置（平面診斷）','顯示 V004→V005 的連續導引線，未使用官方地圖當貼圖。'),
 ('V005_diagnostic_entry.png','V004／V005 轉接街段','原建築與新路段接續，注意尚無 WebGL2 畫面驗收。'),
 ('V005_diagnostic_waraji.png','草鞋屋外觀候選','木格柵、騎樓與暖簾為原創估計造型，非逐尺實測。'),
 ('V005_diagnostic_utsuroi.png','變裝攝影館候選','正面方向沿 OSM 面向道路，屋高與立面待實景核對。'),
 ('V005_diagnostic_aerial.png','商家街鳥瞰診斷','原 V004 三棟與本輪新增兩棟，均為實際 GLB 幾何。'),
 ('V005_diagnostic_from_end.png','從 V005 街尾回望','新增道路路面與地形銜接；周邊缺資料的建築不憑空捏造。'),
]
CSS='''body{margin:0;background:#f6f5ef;color:#233e36;font-family:system-ui,"Noto Sans TC",sans-serif;line-height:1.55}header{background:#e5efe8;padding:2.5rem 1.2rem;border-bottom:1px solid #c7d6cc}main{max-width:1160px;margin:auto;padding:1rem}h1{font-size:clamp(1.5rem,4vw,2.3rem);margin:.3rem 0}p{max-width:75ch}small{color:#536c5c}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,410px),1fr));gap:1.5rem}figure{margin:0;background:#fff;border-radius:13px;overflow:hidden;border:1px solid #d8e3d8}img{width:100%;height:auto;display:block}figcaption{padding:1rem}figcaption b{display:block;margin-bottom:.25rem}.notice{background:#fffbe9;border-left:4px solid #b69762;padding:.9rem}footer{padding:2rem 0;color:#586b61}'''
html_text=['<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V005 R1 診斷圖</title><style>'+CSS+'</style></head><body><header><div style="max-width:1160px;margin:auto"><small>登別伊達時代村｜V005 R1 CANDIDATE</small><h1>商家街第二段 3D 擴建成果</h1><p>總步行路線 <strong>197.72 m</strong>，本輪新增 <strong>67.71 m</strong>、兩棟具名商店建築。以下是從<strong>實際 GLB</strong> 回讀渲染的診斷圖，不是原場景照片，也不是 Three.js 正式遊玩畫面。</p></div></header><main><p class="notice">工程測試通過；WebGL2、Android 真機、Blender 原生母檔與實景美術比對仍未通過。已保留 V002／V003／V004，不覆蓋私人網址。</p><section class="grid">']
for name,title,detail in pictures:
 p=ROOT/name
 blob=base64.b64encode(p.read_bytes()).decode()
 html_text.append(f'<figure><img src="data:image/png;base64,{blob}" alt="{html.escape(title)}"><figcaption><b>{html.escape(title)}</b><small>{html.escape(detail)}</small></figcaption></figure>')
html_text.append('</section><footer>座標來源：凍結 V002 OSM / GSI 高程；建築外觀為估計。正式使用前仍需實景及裝置驗收。</footer></main></body></html>')
(TOP/'Noboribetsu_Date_V005_R1_Review.html').write_text(''.join(html_text),encoding='utf8')

def zip_it(out,entries,comp=zipfile.ZIP_DEFLATED):
 with zipfile.ZipFile(out,'w',compression=comp,compresslevel=6,allowZip64=True) as z:
  for arc,path in entries:z.write(path,arc)
 with zipfile.ZipFile(out) as z:
  bad=z.testzip();assert bad is None,bad
 return {'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'files':len(entries)}

rentries=[('dist/'+str(p.relative_to(DIST)).replace('\\','/'),p) for p in sorted(DIST.rglob('*')) if p.is_file()]
rentries += [('README.md',RUNTIME/'README.md'),('start_server.py',RUNTIME/'start_server.py'),('Noboribetsu_Date_V005_R1_Validation.json',TOP/'Noboribetsu_Date_V005_R1_Validation.json')]
rf=zip_it(TOP/'Noboribetsu_Date_V005_R1_Runtime.zip',rentries)

sentries=[('source/'+p.name,p) for p in sorted((ROOT/'scripts').glob('*')) if p.is_file() and (p.suffix in {'.py','.mjs','.json'})]
evidences=[
 ROOT/'V005_replay_sha256.json',ROOT/'V005_surface_qa.json',ROOT/'V005_webgl_probe.json',ROOT/'V005_route_overview.png',
 RUNTIME/'V005_navigation_qa.json',RUNTIME/'V005_osm_placeholder_audit.json',RUNTIME/'V005_assets_qa.json',
 DIST/'v005_manifest.json',DIST/'v005_collision.json',DIST/'v005_build_qa.json', ROOT/'build_stdout.json',
]
evidences += [ROOT/x[0] for x in pictures if x[0].startswith('V005_diagnostic')]
sentries += [('evidence/'+p.name,p) for p in evidences]
sentries += [(p.name,p) for p in [TOP/'Noboribetsu_Date_V005_R1_Validation.json',TOP/'Noboribetsu_Date_V005_R1_Review.html',report_path]]
sf=zip_it(TOP/'Noboribetsu_Date_V005_R1_SourceQA.zip',sentries)
delivery={'runtime':rf,'source_qa':sf,'report_sha256':sha(report_path),'review_sha256':sha(TOP/'Noboribetsu_Date_V005_R1_Review.html')}
(TOP/'Noboribetsu_Date_V005_R1_SHA256.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(delivery,ensure_ascii=False,indent=2))