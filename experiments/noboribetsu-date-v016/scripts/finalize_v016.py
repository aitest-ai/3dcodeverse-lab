#!/usr/bin/env python3
"""Package V016 diagnostic-only candidate without modifying V015 archives."""
from pathlib import Path
import json,hashlib,zipfile,base64,datetime,html
R=Path(__file__).resolve().parent;O=R/'outputs';E=R/'evidence';D=R/'base';O.mkdir(exist_ok=True)
P=Path('/mnt/data');stem='Noboribetsu_Date_V016_R1'
audit=json.loads((O/'V016_audit_qa.json').read_text());replay=json.loads((O/'V016_clean_replay_qa.json').read_text())
integrity=json.loads((O/'V016_integrity_qa.json').read_text());webgl=json.loads((O/'V016_webgl_toggle_qa.json').read_text())
assert replay['matched_files']==113 and integrity['unchanged_original_files']==108
assert webgl['real_webgl2'] and webgl['loaded']=='true' and webgl['success']
assert webgl['toggle_observed']=={'initial':'false','on':'true','off':'false','metric':False,'disabled':False}
rows=json.loads((O/'v016_grade_inspection.json').read_text())['burial_samples']
body=f'''# 登別伊達時代村 V016 R1｜V004 商家石基座連續構件與高程診斷

日期：2026-11-02（臺灣時間）。以原封存 V015 Runtime + SourceQA 為唯一基準，**不覆寫舊檔、不更新網站、不宣稱新建築已完工**。

## 本次最重要的校正

V015 記錄的「4 處埋地柱腳」，是高等學問所 2 個與北京亭 2 個**沿連續基座的取樣位置**，不是 4 個獨立待替換石墩。回讀 V004 實際 `stone_foot` 網格後，發現其兩條連續石基座各高約 0.55m：這 4 個位置埋入地形約 0.0621–0.10804m，仍露出 0.44196–0.48790m（約 80–89%）。僅憑此不能推定施工錯誤。

本版**沒有新增 4 個永久石墩、沒有抬高整棟建築，也沒有改道路或碰撞**。V015 已補強的 8 處懸空位置與其原始模型維持原樣，是否符合真實照片仍待美術驗收。

## V016 實作

- 新增 `dist/v016_grade_inspection.json`，逐點記錄高度、原基座區塊與來源雜湊，約 {len((O/'v016_grade_inspection.json').read_bytes())} bytes。
- 場景新增預設**關閉**的「基座取樣診斷」切換，開啟後在 B 精修場景標示 4 個取樣位置；4 個環形標記僅用於查核、沒有碰撞或路線效果；A 骨架不顯示。
- 保留 V014 中央石板開關、V015 八處補強及 V011～V013 全部修復。不把診斷標記當成新建築、石材或正式美術成果。
- 新增兩棟建築的同鏡位 VTK GLB 幾何診斷比較（**不是 WebGL2 交互畫面**）。

## 實際驗證

- **來源與模型**：V004 `stone_foot` 為 5 個連續石質區塊，涉及這 4 個取樣的為其中 2 條；V004 facades GLB SHA256 驗證通過。所有 4 個記錄都有至少 44cm 可見石基座。
- **正式 WebGL2 載入與操作**：Xvfb + Chromium + SwiftShader 確實建立 WebGL2，完整 B 模型、V011～V016 資料均載入。新切換按鈕在隔離測試中成功 `關→開→關`、標記數為 4、預設隱藏、V015 8 處支撐保持存在；沒有頁面 JS 載入錯誤。隔離環境為虛擬子資源，使用**測試專用 SHA adapter**；Python 已獨立實算模型 SHA。正式 Runtime 仍使用 `crypto.subtle.digest`，不包含 adapter。
- **畫面界線**：V016 無標記的實際 WebGL2 截圖可取得，但「顯示標記」後的第二張實際 WebGL2 截圖因 SwiftShader 效能逾時，**未通過真正 WebGL2 前後畫面驗收**。因此比較頁使用 VTK 幾何診斷圖片，明確分開來源。
- **完整性**：V015 112 個執行檔中 108 個 SHA256 完全不變，只有 `dist/app.js`、`dist/index.html`、`dist/scene_view.json`、`dist/qa.json` 變更，另新增 V016 診斷 JSON，總共 113 檔。從原始 V015 兩份 ZIP 在空白暫存區重建，**113／113 SHA256 一致**；Node 語法驗證通過。

## 仍未驗證

Android 實體手機、私人網站 HTTPS／CDN／登入、Blender 原生 `.blend`/Cycles、石基座真正的現地高程與材質。這 4 處埋地取樣**目前列為待人工實景核對，而非已修復或已證明瑕疵**。

## 重建方式

解壓 V015 Runtime ZIP 到 `base/`，V015 SourceQA ZIP 到 `source/`，把本包 `source/build_v016_audit.py` 和 `source/integrate_v016.py` 複製到同一根目錄；依序執行。若原始 GLB SHA256、V015 支撐 JSON 或其他契約不符立即停止。也可使用 `replay_v016.py` 做乾淨比較。工具只建立新版本，保留 V015 母檔與 ZIP。

**V016 是可操作的診斷候選，不是四處石基座的最終修繕版。**
'''
(P/f'{stem}_Delivery_Report.md').write_text(body)
styles='''body{font:16px/1.7 system-ui,"Noto Sans TC",sans-serif;background:#f5f2eb;color:#24312b;margin:0}.wrap{max-width:1150px;margin:auto;padding:28px}header{background:#263b34;color:#faf6ee;padding:27px;border-radius:15px}h1{margin:.1em 0}.note{color:#d8e6de}section{margin:23px 0;background:white;border-radius:12px;padding:20px;box-shadow:0 1px 5px #0001}img{width:100%;height:auto;border-radius:8px}small{color:#65766b}.tag{display:inline-block;background:#ece6d4;padding:2px 9px;border-radius:6px}th,td{border-bottom:1px solid #ddd;padding:8px;text-align:left}table{border-collapse:collapse;width:100%;}'''
block=[]
for key,name in [('Gakumonjo','高等學問所'),('Beijingtei','北京亭')]:
 image=(E/f'V016_{key}_Geometry_Comparison.png').read_bytes();data='data:image/png;base64,'+base64.b64encode(image).decode('ascii')
 block.append(f'<section><h2>{name}｜同鏡位診斷</h2><p>左：原始 V015 基座；右：V016 顯示取樣標記（黃色）。<strong>以下是 VTK 幾何診斷，不是 WebGL2 前後截圖。</strong></p><img alt="{name} VTK GLB 原始和標示比較" src="{data}"></section>')
trs=''.join(f'<tr><td>{html.escape(x["building"])}</td><td>{x["sample_index"]}</td><td>{x["burial_depth_m"]*100:.1f} cm</td><td>{x["remaining_exposed_height_m"]*100:.1f} cm</td></tr>' for x in rows)
markup=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V016 接地診斷</title><style>{styles}</style></head><body><div class="wrap"><header><div class="tag" style="color:#27382d">V016 · DIAGNOSTIC</div><h1>商家石基座接地診斷</h1><p class="note">從 V015 原始 GLB 查核，四處是兩條連續石基座的取樣位置，不是四顆獨立埋地石墩。</p></header><section><h2>四處取樣數據</h2><table><thead><tr><th>建築</th><th>取樣序號</th><th>埋入深度</th><th>仍露出高度</th></tr></thead><tbody>{trs}</tbody></table><p>原石基座約高 55cm。未新增永久修補幾何；已保留 V015 八處懸空補強。</p></section>{''.join(block)}<section><h2>驗收界線</h2><p><strong>完整 Chromium WebGL2 載入及診斷按鈕操作通過</strong>；但顯示標記後的第二張真實 WebGL2 截圖因軟體渲染逾時。上方僅呈現 VTK 診斷，不冒稱實際瀏覽器比較。實際 Android、原站 HTTPS、Blender 母檔仍未驗。</p></section></div></body></html>'''
(P/f'{stem}_Review.html').write_text(markup)
# Runtime contains only newly versioned files; avoids overwriting source archive.
def zipdir(out,root,extra=None):
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for f in sorted(root.rglob('*')):
   if f.is_file():z.write(f,str(f.relative_to(root)))
  for rel,path in (extra or []):z.write(path,rel)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None;return len(z.namelist())
runtime=P/f'{stem}_Runtime.zip';assert zipdir(runtime,D)==113
source=P/f'{stem}_SourceQA.zip'
source_files=['build_v016_audit.py','integrate_v016.py','verify_v016.py','replay_v016.py','qa_v016_toggle.py','qa_v016_webgl.py','render_v016_vtk.py','finalize_v016.py']
extras=[('source/'+n,R/n) for n in source_files]
extras += [('generated/v016_grade_inspection.json',O/'v016_grade_inspection.json')]
extras += [('evidence/'+f.name,f) for f in sorted(E.glob('*.png'))]
extras += [('evidence/'+f.name,f) for f in sorted(O.glob('*_qa.json'))]
extras += [('evidence/'+f.name,f) for f in sorted(O.glob('*_qa.json')) if False]
extras += [('evidence/'+f.name,f) for f in sorted(O.glob('V016_*qa.json')) if ('evidence/'+f.name,f) not in extras]
extras += [('evidence/V016_webgl_toggle_qa.json',O/'V016_webgl_toggle_qa.json')]
extras += [('evidence/V016_webgl_visual_qa.json',O/'V016_webgl_qa.json')]
extras += [('evidence/DELIVERY_REPORT.md',P/f'{stem}_Delivery_Report.md'),('evidence/REVIEW.html',P/f'{stem}_Review.html')]
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 seen=set()
 for dest,f in extras:
  if dest in seen:continue
  seen.add(dest);z.write(f,dest)
with zipfile.ZipFile(source) as z:assert z.testzip() is None;source_count=len(z.namelist())
manifest={'schema':'noboribetsu-date-v016-delivery-sha256/1','status':'DIAGNOSTIC_CANDIDATE_REAL_WEBGL_TOGGLE_PASS_VISUAL_COMPARE_PENDING',
 'artifacts':{p.name:{'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (runtime,source,P/f'{stem}_Review.html',P/f'{stem}_Delivery_Report.md')},
 'original_model_unchanged':True,'new_permanent_footings':0,'replay_matched':113,'webgl_loaded_and_toggle_passed':True,'webgl2_after_screenshot_verified':False}
(P/f'{stem}_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'runtime_bytes':runtime.stat().st_size,'runtime_files':113,'source_bytes':source.stat().st_size,'source_files':source_count,'SHA':manifest['artifacts'][runtime.name]['sha256']},ensure_ascii=False,indent=2))