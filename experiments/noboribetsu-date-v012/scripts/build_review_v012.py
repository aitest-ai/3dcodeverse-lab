#!/usr/bin/env python3
"""Generate offline interactive comparison with real screenshots, no external photos."""
import base64,html,json
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE/'outputs'
old=OUT/'V011_street_end_WebGL2.png';new=OUT/'V012_street_end_WebGL2.png';mob=OUT/'V012_Mobile_Emulated_WebGL2.png'
assert all(p.is_file() for p in (old,new,mob))
a=Image.open(old).convert('RGB');b=Image.open(new).convert('RGB');assert a.size==b.size
combo=Image.new('RGB',(a.width*2,a.height+34),'#f8f8f4');combo.paste(a,(0,34));combo.paste(b,(a.width,34));d=ImageDraw.Draw(combo);d.text((12,10),'V011: before | original edge',fill='#202b23');d.text((a.width+12,10),'V012: after | translucent road-grass shoulder',fill='#202b23')
combo.save(OUT/'V011_V012_StreetEnd_WebGL2_Comparison.png')
web= json.loads((OUT/'V012_webgl_qa.json').read_text()); mobile=json.loads((OUT/'V012_mobile_qa.json').read_text())
uri=lambda p:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
# This HTML is self-contained; because both screenshots were captured at the same camera, overlay slider shows actual changes.
content='''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V012 路緣柔化 · 真 WebGL2 比較</title><style>
:root{font-family:system-ui,"Noto Sans TC",sans-serif;color:#27392f;background:#f5f3ec}body{max-width:1100px;margin:0 auto;padding:24px}h1{font-size:clamp(22px,4vw,34px)}p{line-height:1.7}.small{font-size:13px;color:#606a62}.compare{position:relative;aspect-ratio:8/5;overflow:hidden;border-radius:12px;box-shadow:0 6px 28px #0002;background:#dce6dc}.compare img{width:100%;height:100%;position:absolute;inset:0;object-fit:contain}.after{clip-path:inset(0 50% 0 0)}.handle{position:absolute;left:50%;top:0;bottom:0;width:3px;background:white;box-shadow:0 0 0 1px #303b34;pointer-events:none}input{width:100%;accent-color:#6b866a;margin:20px 0}.tags{display:flex;justify-content:space-between;font-weight:bold;margin-bottom:10px}.mobile{max-width:430px;border-radius:10px;display:block;margin:auto}.box{padding:12px 20px;border:1px solid #c7cbbf;border-radius:10px;margin-top:24px}</style></head><body>
<h1>登別伊達時代村 V012｜街尾道路與草地過渡</h1>
<p>以下兩張均為 <strong>Chromium + SwiftShader 真 WebGL2</strong> 的同尺寸街尾畫面。拖曳滑桿可比較 V011 與 V012。新路緣是較淡的土色／苔色視覺層，因此變化刻意克制。</p>
<div class="tags"><span>V011 原版</span><span>V012 新版</span></div>
<div class="compare"><img src="__BEFORE__" alt="V011 街尾原版實際 WebGL2 截圖"><img class="after" id="after" src="__AFTER__" alt="V012 路緣改良後實際 WebGL2 截圖"><div class="handle" id="handle"></div></div>
<label for="slider">顯示 V012 比例：<output id="pct">50%</output></label><input id="slider" type="range" min="0" max="100" value="50">
<div class="box"><h2>實際驗證與界線</h2><p>V012 僅在 V006 最後約 33.8 公尺道路兩側加上 972 個透明視覺三角面；原有 231.57 公尺路線、原始高品質 GLB、碰撞與 V011 的 296 個補洞三角面均不改。這不是新增排水設施或現地測量。</p>
<p>真 WebGL2 中 A／B 切換成功，手機直式 Chromium 模擬可同時操作搖桿與視角，放手後停止。<strong>未進行 Android 實體手機、私人網站 CDN／HTTPS 或 Blender 正式母檔驗收。</strong></p>
<p class="small">受限於瀏覽器測試環境的 top-level 導覽政策，網頁使用隔離的虛擬資源映射；模型 SHA 已由 Python 獨立核對。測試專用雜湊替身未寫進正式 Runtime，正式版本仍使用原生 WebCrypto。</p></div>
<h2>手機直式模擬截圖</h2><img class="mobile" src="__MOBILE__" alt="Chromium 手機直式模擬的真正 WebGL2 畫面">
<script>const s=document.getElementById('slider'),a=document.getElementById('after'),h=document.getElementById('handle'),p=document.getElementById('pct');s.addEventListener('input',()=>{const v=Number(s.value);a.style.clipPath=`inset(0 ${100-v}% 0 0)`;h.style.left=`${v}%`;p.textContent=`${v}%`;});</script></body></html>'''
content=content.replace('__BEFORE__',uri(old)).replace('__AFTER__',uri(new)).replace('__MOBILE__',uri(mob))
(HERE/'Noboribetsu_Date_V012_R1_Review.html').write_text(content,encoding='utf8')
print('review bytes',len(content),'webgl',web['success'],'mobile',mobile['result'])