#!/usr/bin/env python3
"""Package finished V011 Runtime/SourceQA from immutable outputs (no rebuild)."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/mnt/data')
REV=DEST/'Noboribetsu_Date_V011_R1_Review.html'
qa_files=[
 'V011_source_terrain_qa.json','V011_delta_qa.json','V011_webgl2_qa.json',
 'V011_mobile_qa.json','V011_visual_geometry_qa.json',
 'V011_review_html_qa.json','V011_clean_replay_qa.json']
qa={p:json.loads((ROOT/'evidence'/p).read_text()) for p in qa_files}
assert all(q.get('status','PASS')=='PASS' or q.get('success')==True or q.get('result')=='PASS' or q.get('status') is None for q in qa.values())
assert qa['V011_webgl2_qa.json']['success'] and qa['V011_mobile_qa.json']['result']=='PASS'
assert qa['V011_visual_geometry_qa.json']['dark_pixels_after']==0
assert qa['V011_clean_replay_qa.json']['regenerated_dist_files_matched']==84
v={'schema':'noboribetsu-date-v011-r1/1','status':'candidate_local_webgl2_visual_gap_repair_verified',
'base':'Noboribetsu_Date_V010_R1_Runtime.zip','route_length_m':231.56641497226084,
'root_cause':{'source_grid_step_m':2,'source_grid_total_cells':40000,
 'fully_missing_cells':148,'original_terrain_triangles':79704,
 'missing_terrain_triangles':296,'missing_height_grid_nodes':84,
 'local_x_range_m':[116,174],'local_z_range_m':[116,162]},
'repair':{'scope':'B visual-only grass mesh, no physics changes','new_triangles':296,
 'method':'4-neighbor Laplace infill, original boundary elevations fixed; NOT SURVEYED',
 'source_original_grass_material_used':True,
 'patch_sha256':qa['V011_clean_replay_qa.json']['patch_sha256'],
 'source_B_sha256':qa['V011_clean_replay_qa.json']['source_b_sha256']},
'checks':{'real_chromium_swiftshader_webgl2':True,
 'scene_loaded':True,'scene_triangles':qa['V011_webgl2_qa.json']['tail']['renderer']['triangles'],
 'stage_A_B_switch_zero_drift':True,'mobile_portrait_emulation':True,
 'mobile_movement_m':qa['V011_mobile_qa.json']['movement_m'],
 'mobile_release_drift_m':qa['V011_mobile_qa.json']['drift_m'],
 'v010_original_files_unchanged':94,'v010_original_files_changed':4,
 'v011_runtime_files':101,'fresh_dist_files_identical':84,
 'roi_black_pixels_before':1270,'roi_black_pixels_after':0,
 'html_review_desktop_mobile':True,'real_webcrypto_in_isolated_browser':False,
 'isolated_browser_used_test_only_digest_adapter':True},
'unverified':{'private_website_cdn_https_login':True,'android_physical_device':True,
 'native_blender_master':True,'cycles':True,'surveyed_terrain_heights':True},
'preservation':{'source_V010_archive_unchanged':True,'all_GLBS':True,
 'collision':True,'routing':True,'original_textures':True,'official_site_preview':True,
 'no_auto_merge':True}}
valpath=DEST/'Noboribetsu_Date_V011_R1_Validation.json';valpath.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
report=f'''# 登別伊達時代村 V011 R1｜街尾地形幾何補洞交付報告

## 已實作

從凍結 V010 Runtime（SHA-256 `{qa['V011_clean_replay_qa.json']['v010_archive_sha256']}`）讀取原始 B GLB。B GLB 重新解壓為 188,663,252 bytes，SHA-256 `{v['repair']['source_B_sha256']}`；原地形材質 `Original_grass` 有 79,704 個三角面，2 公尺格網應有 40,000 個面格，其中 **148 格完全沒有三角面，合計缺失 296 面**，另有 84 個格點缺少高程。缺口集中 X 116–174、Z 116–162 m，恰位於 V010 實際街尾視角左側的黑白破圖。

V011 使用原始周邊高度作四鄰點離散調和補值，新增 296 面 B 場景視覺補洞，不改舊 GLB。補洞共用原草地材質與 UV (`u=x/8`, `v=z/8+1`)，不改路線、高程來源檔、碰撞、建築、貼圖或人物；**補值為作者估計，不是官方實測高程**。

## 真 WebGL2 驗證

Xvfb + Chromium + ANGLE SwiftShader **真 WebGL2** 載入並繪出 1,432,282 個三角面／95 個幾何／47 張紋理（單次測試，非裝置效能保證）。V010/V011 同位置（231.566 m 街尾）、相同 960×600 相機的獨立實際渲染顯示黑白破洞消失；固定影像區域中 RGB max 小於 32 的深黑像素數由 1,270 → 0。A 首次載入並切回 B，全部相機視角差異為零；保留五棟灰量體共排除 100 面。

手機直式 Chromium 模擬下雙指搖桿與環顧同時有效，角色前進 **{qa['V011_mobile_qa.json']['movement_m']:.3f} m**，放手位移 **{qa['V011_mobile_qa.json']['drift_m']:.3f} m**；這不是 Android 真機測試。

## 可重建性

從乾淨 V010 ZIP 重新解壓，重跑 `build_v011_terrain_patch.py` 與 `integrate_v011.py`：**84／84 個 dist 輸出檔案 SHA256 逐檔完全一致**。V010 原本 98 份檔案中 94 個完全不變、4 個版本或介面程式改動，加 3 個檔案，V011 Runtime 共 101 個檔案。所有原始 GLB、碰撞與控制計算基礎完全保留。原始 V010 ZIP 也未覆寫。

V011 新增的補洞 JSON 使用真 `crypto.subtle.digest('SHA-256')` 驗證原始 bytes，資料長度／結構不符會拒絕載入。**實際 WebGL2 隔離測試**因環境阻擋 localhost/HTTPS top-level navigation，只能使用虛擬子資源與測試專用、預先 Python SHA256 核對的長度→雜湊 adapter；該 adapter 完全不在 Runtime。另附正常 localhost 伺服器供實際 WebCrypto/網站環境查核。

## 明確未驗收

1. 私人網站真正 CDN、登入、HTTPS 與部署：未測、不覆蓋。
2. Android 實體手機效能、GPU 記憶體與操作：未測。
3. Blender-native `.blend` / Cycles 同鏡位：未測。
4. 84 格高程補值是否與真實地形完全吻合：沒有現地測量資料。
5. SwiftShader FPS 不等於實體 GPU 的 FPS，不能據此宣稱效能提升。

## 交付內容

- `Noboribetsu_Date_V011_R1_Runtime.zip`：整份可執行 V011；解壓執行 `python start_v011_local.py`，瀏覽器開啟 `http://127.0.0.1:8765/index.html`。
- `Noboribetsu_Date_V011_R1_SourceQA.zip`：所有可重跑生成程式、資料契約、實測 QA JSON、兩版真實 WebGL2 截圖與比較證據。
- `Noboribetsu_Date_V011_R1_Review.html`：內嵌 V010/V011 同鏡位 PNG，可離線滑桿比較。
- `v011_terrain_gap_patch.json`：單獨的補洞模型資料；需使用本版 Runtime 的原草地材質，不是一份自給自足的 GLB。
- `Noboribetsu_Date_V011_R1_Validation.json`：整體驗證摘要。

**狀態：V011 R1 候選，待原生 Android／私人網站／Blender 驗收；勿自動合併或部署。**
'''
(DEST/'Noboribetsu_Date_V011_R1_Delivery_Report.md').write_text(report,encoding='utf8')
# Keep original raw V010 archive closed; use the already assembled new root.
runtime=DEST/'Noboribetsu_Date_V011_R1_Runtime.zip'
with ZipFile(runtime,'w',compression=ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in sorted((ROOT/'runtime_full').rglob('*')):
  if p.is_file():z.write(p,p.relative_to(ROOT/'runtime_full').as_posix())
print('runtime bytes',runtime.stat().st_size)
source=DEST/'Noboribetsu_Date_V011_R1_SourceQA.zip'
with ZipFile(source,'w',compression=ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for folder in ['source','evidence','outputs']:
  for p in sorted((ROOT/folder).rglob('*')):
   if p.is_file() and p.suffix in ('.py','.json','.png','.md','.txt'):
    z.write(p,f'{folder}/{p.relative_to(ROOT/folder).as_posix()}')
 z.write(DEST/'Noboribetsu_Date_V011_R1_Delivery_Report.md','V011_R1_Delivery_Report.md')
 z.write(valpath,'V011_R1_Validation.json')
print('source bytes',source.stat().st_size)
for p in (runtime,source):
 with ZipFile(p) as z:
  assert z.testzip() is None
  print(p.name,'files',len(z.namelist()))
manifest={'schema':'noboribetsu-date-v011-hashes/1','base_v010_runtime_sha256':qa['V011_clean_replay_qa.json']['v010_archive_sha256'],
 'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [runtime,source,REV,DEST/'Noboribetsu_Date_V011_R1_Validation.json',DEST/'Noboribetsu_Date_V011_R1_Delivery_Report.md',ROOT/'outputs/v011_terrain_gap_patch.json']}}
(DEST/'Noboribetsu_Date_V011_R1_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')