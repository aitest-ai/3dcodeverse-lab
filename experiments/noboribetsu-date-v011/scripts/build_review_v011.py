#!/usr/bin/env python3
"""Build self-contained V010/V011 comparison without external image assets."""
from pathlib import Path
import base64, html
root=Path(__file__).resolve().parents[1]
a=root/'source_prev/evidence/V010_V009_StreetEnd_WebGL2.png'
b=root/'evidence/V011_street_end_WebGL2.png'
mobile=root/'evidence/V011_Mobile_Emulated_WebGL2.png'
enc=lambda p:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
page=r'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>登別伊達時代村 V011｜地形修復驗收</title>
<style>
:root{--ink:#30473d;--green:#355847;--paper:#f8f7f1;--line:#dddcd0;--accent:#bf7751}*{box-sizing:border-box}
body{margin:0;background:var(--paper);font-family:system-ui,-apple-system,"Noto Sans TC",sans-serif;color:var(--ink)}main{max-width:1130px;margin:auto;padding:32px 18px 65px}header{border-bottom:1px solid var(--line);padding-bottom:22px}small{letter-spacing:0.15em;text-transform:uppercase;color:#687c70}h1{font-size:clamp(25px,4.5vw,40px);margin:10px 0}p{line-height:1.7}article{background:white;border:1px solid var(--line);border-radius:16px;padding:18px;margin-top:25px}h2{font-size:19px;margin:0 0 14px}.compare{position:relative;overflow:hidden;border-radius:10px;aspect-ratio:8/5;background:#dde8dc;isolation:isolate}.compare img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;pointer-events:none}.compare .over{width:50%;overflow:hidden;position:absolute;inset:0}.compare .over img{width:200%;max-width:none}.compare .split{position:absolute;left:50%;top:0;bottom:0;width:3px;background:#fff;box-shadow:0 0 0 1px #30473d60;pointer-events:none}.compare .handle{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;color:#30473d;border:2px solid var(--accent);border-radius:999px;padding:8px 12px;font-weight:800;pointer-events:none}.compare input{position:absolute;z-index:5;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize;margin:0}.meta{display:flex;justify-content:space-between;gap:12px;font-weight:700;margin-top:9px}.meta span:first-child{color:#a95b3b}.meta span:last-child{color:#32634a}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:21px 0}.stats div{background:#edeee7;padding:15px;border-radius:10px}.stats strong{display:block;font-size:24px;font-variant-numeric:tabular-nums}.stats label{display:block;font-size:13px;color:#617369;margin-top:3px}.notes{border-left:3px solid var(--accent);padding-left:14px;color:#596c61}.mobile{width:min(100%,320px);border-radius:8px;border:1px solid var(--line)}
@media(max-width:650px){.stats{grid-template-columns:1fr 1fr}.compare{aspect-ratio:8/5}article{padding:12px}main{padding:20px 10px 45px}}
</style></head><body><main><header><small>登別伊達時代村 · 3D EXPERIMENT / V011 R1</small><h1>街尾地形補洞｜真實 WebGL2 前後比較</h1><p>兩張圖片來自相同的 231.6 公尺街尾位置、相同視角（202°）、相同 Chromium＋SwiftShader 渲染條件。V011 僅補回原始 B 地形缺失的三角面，未重做道路或建築。</p></header>
<div class="stats"><div><strong>148 格</strong><label>原本沒有三角面的地形</label></div><div><strong>296 面</strong><label>新增視覺補洞三角面</label></div><div><strong>0 面</strong><label>原有 B 地形遭刪除數</label></div></div>
<article><h2>01　完整畫面比較</h2><div class="compare" id="c1"><img src="@@BEFORE@@" alt="V010 原本有黑白破洞的街尾實際 WebGL2 畫面"><div class="over"><img src="@@AFTER@@" alt="V011 補好缺失三角面的街尾 WebGL2 畫面"></div><div class="split"></div><div class="handle">⇔</div><input type="range" min="0" max="100" value="50" aria-label="拖曳比較 V010 與 V011"></div><div class="meta"><span>V010 原版</span><span>V011 補洞版</span></div><p>拖曳圖片中間的分隔線，可以查看左前方草坡黑白破洞消失的結果。文字及版本編號也有正常更新。</p></article>
<article><h2>02　手機直式操作回歸</h2><img class="mobile" src="@@MOBILE@@" alt="V011 Chromium 手機直式 WebGL2 模擬實測截圖"><p>Chromium 手機直式模擬，同時使用搖桿與環顧後，移動約 0.79 公尺、放手漂移為 0。<strong>尚未在 Android 實體手機測試。</strong></p></article>
<article><h2>03　修補來源與界線</h2><p>從 V010 封存的 B 場景讀取原始草地幾何，確認 148 個 2×2 公尺網格沒有三角面，並從附近的原始地形高度平滑插補 84 個缺失格點。修補直接沿用 B 場景原本的 <code>Original_grass</code> 材質及 UV，沒有另貼假草皮，也不增加碰撞或宣稱現地高度。</p><p class="notes">驗收為獨立 Chromium + ANGLE SwiftShader 的真 WebGL2 場景；因環境阻擋 top-level 導覽，測試以虛擬子資源及預先雜湊確認的測試專用 SHA adapter 執行。正式執行包沒有測試替身，仍使用瀏覽器原生 WebCrypto。私人網站、實體 Android、Blender 原生母檔尚未驗收。</p></article></main>
<script>document.querySelectorAll('.compare').forEach(c=>{const i=c.querySelector('input'),over=c.querySelector('.over'),line=c.querySelector('.split'),handle=c.querySelector('.handle');const apply=()=>{let v=Number(i.value);over.style.width=v+'%';over.querySelector('img').style.width=10000/v+'%';line.style.left=v+'%';handle.style.left=v+'%'};i.addEventListener('input',apply);apply();});</script>
</body></html>'''
# The overlay image should always retain its original frame width, not scale with
# mask width. Use container-size 100cqw to keep image exactly aligned.
page=page.replace('over.querySelector(\'img\').style.width=10000/v+\'%\'','over.querySelector(\'img\').style.width=c.clientWidth+\'px\'')
page=page.replace('src="@@BEFORE@@"','src="'+enc(a)+'"')
page=page.replace('src="@@AFTER@@"','src="'+enc(b)+'"')
page=page.replace('src="@@MOBILE@@"','src="'+enc(mobile)+'"')
out=Path('/mnt/data/Noboribetsu_Date_V011_R1_Review.html')
out.write_text(page,encoding='utf8')
print('Review',out.stat().st_size,'bytes')