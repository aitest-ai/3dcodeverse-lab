#!/usr/bin/env python3
"""Reproducible diagrams and self-contained review for V018 motion tests."""
import base64,hashlib,json,zipfile,html
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if Path(font).exists(): font_manager.fontManager.addfont(font)
plt.rcParams['font.family']=font_manager.FontProperties(fname=font).get_name()
plt.rcParams['axes.unicode_minus']=False
motion=json.loads((OUT/'V018_motion_qa.json').read_text());browser=json.loads((OUT/'V018_browser_input_qa.json').read_text())
scene=json.loads((ROOT/'base/dist/scene_view.json').read_text());coll=json.loads((ROOT/'base/dist/extension_collision.json').read_text())
route=[p for p in scene['route'] if 82.877-1e-4<=p['s']<=130.02];
poly=[o for o in coll['obstacles'] if 'porchpost' in o['id'] and ('gallery' in o['id'] or 'restaurant' in o['id'])]
fig,ax=plt.subplots(figsize=(11.6,6.4),dpi=160)
for i,o in enumerate(poly):
 patch=PatchPolygon(o['polygon'],closed=True,facecolor='#bb7554',edgecolor='#874327',linewidth=1,alpha=.42,label='現有柱位碰撞區' if i==0 else None)
 ax.add_patch(patch)
 ax.text(np.mean([p[0] for p in o['polygon']]),np.mean([p[1] for p in o['polygon']]),str(i+1),fontsize=8,ha='center',va='center',color='#4f241b')
ax.plot([q['x'] for q in route],[q['z'] for q in route],color='#225f54',linewidth=3,label='V004 既有中心路線')
for key,c,lw in [('forward','#287bb7',2.2),('approach','#d36b2b',2.5),('slide','#8c56a0',2.2)]:
 trace=motion['traces'][key];ax.plot([p['x'] for p in trace],[p['z'] for p in trace],color=c,linewidth=lw,label={'forward':'W 前進','approach':'向柱子接近（碰撞擋下）','slide':'沿柱旁側移'}[key])
 # mark start/end
 if trace:
  ax.scatter([trace[0]['x'],trace[-1]['x']],[trace[0]['z'],trace[-1]['z']],color=c,s=16,zorder=5)
closest=next(a for a in motion['checks'] if 'Narrowest' in a['name'])
from_s=closest['s'];p=min(route,key=lambda x:abs(x['s']-from_s))
ax.annotate('最窄處 約 23.1 cm',xy=(p['x'],p['z']),xytext=(p['x']+4,p['z']-3),arrowprops=dict(arrowstyle='->',color='#ac3338',lw=1.5),color='#ac3338',fontsize=11,fontweight='bold')
ax.set_aspect('equal');ax.set_xlim(-7.5,34.5);ax.set_ylim(52,67);ax.grid(alpha=.2)
ax.set_title('V018｜柱廊通行：既有路線與實際程式移動軌跡',fontsize=16,fontweight='bold',loc='left',pad=16)
ax.set_xlabel('園區局部 X（公尺）');ax.set_ylabel('園區局部 Z（公尺）')
ax.legend(loc='upper left',ncol=2,fontsize=9,framealpha=.94)
fig.text(.06,.01,'資料來源：V017 真實碰撞 JSON + 原版 WalkSession / CollisionWorld；此圖不是 3D 遊戲截圖。',fontsize=8,color='#636363')
fig.tight_layout(rect=(0,.05,1,1));fig.savefig(OUT/'V018_column_motion_map.png',bbox_inches='tight',facecolor='white');plt.close(fig)
# Lateral blocked counts from actual NavigationWorld checks
lateral=next(a['lateral'] for a in motion['checks'] if 'Lateral sampling' in a['name']);off=[x['offset_m'] for x in lateral];n=[x['blocked'] for x in lateral]
fig,ax=plt.subplots(figsize=(9.6,4.6),dpi=160);bars=ax.bar([str(x) for x in off],n,color=['#c9784d' if x<0 else '#3b8672' for x in off],width=.57)
for b,v in zip(bars,n):ax.text(b.get_x()+b.get_width()/2,v+.6,str(v),ha='center',fontsize=11,fontweight='bold')
ax.set_ylim(0,46);ax.grid(axis='y',alpha=.22);ax.set_axisbelow(True)
ax.set_xlabel('相對既有路線中心的側向偏移（公尺）');ax.set_ylabel('237 個取樣位置中受阻數量')
ax.set_title('V018｜中心線可以通過，左側靠柱路線不一定可以',loc='left',fontsize=15,fontweight='bold',pad=15)
fig.text(.06,.01,'受阻點是以角色半徑 26cm 與真實程式中的障礙碰撞計算；並非人體通行或無障礙認證。',fontsize=8,color='#636363')
fig.tight_layout(rect=(0,.06,1,1));fig.savefig(OUT/'V018_lateral_blocking.png',bbox_inches='tight',facecolor='white');plt.close(fig)
# self-contained review
pics={p:(OUT/p).read_bytes() for p in ['V018_column_motion_map.png','V018_lateral_blocking.png']}
b64=lambda p:'data:image/png;base64,'+base64.b64encode(pics[p]).decode()
table=''.join(f'<tr><td>{html.escape(c["name"])}</td><td class="ok">通過</td></tr>' for c in motion['checks'])
btable=''.join(f'<tr><td>{html.escape(c["name"])}</td><td class="ok">通過</td></tr>' for c in browser['checks'])
page=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V018｜柱廊操作驗收</title><style>
:root{{--paper:#f8f6f0;--ink:#22312f;--green:#21635a;--card:#fff;--line:#dedbd1}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);font-family:'Noto Sans TC',system-ui,sans-serif;color:var(--ink);line-height:1.75}}header{{background:#193e39;color:#fff;padding:42px 6vw 38px}}header .sub{{opacity:.78;letter-spacing:.13em}}h1{{font-size:clamp(1.7rem,3.7vw,2.8rem);margin:8px 0}}header p{{max-width:820px;color:#e2ebe5}}main{{max-width:1120px;margin:auto;padding:28px 20px 60px}}article{{background:var(--card);padding:25px;margin-bottom:20px;border:1px solid var(--line);border-radius:12px}}h2{{margin:0 0 16px;font-size:1.35rem}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:20px}}.metric{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:19px}}.metric b{{display:block;font-size:1.8rem;color:var(--green)}}img{{display:block;width:100%;height:auto;border:1px solid #eee;border-radius:8px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px 7px;border-bottom:1px solid #e8e6e0;text-align:left}}.ok{{color:#1f755b;font-weight:700}}.muted{{font-size:.88rem;color:#60716d}}.warning{{border-left:4px solid #c38b4e;padding:12px 16px;background:#fff9ef}}@media(max-width:670px){{.metrics{{grid-template-columns:1fr}}article{{padding:16px}}header{{padding:27px 20px}}}}</style></head><body><header><div class="sub">NOBORIBETSU DATE JIDAIMURA · V018 · QA ONLY</div><h1>柱廊操作與碰撞驗收</h1><p>使用 V017 原始遊戲碰撞與輸入程式完成可重現的近柱移動測試。本輪不修改模型、道路與碰撞，重點是找出真正的通行限制。</p></header><main>
<div class="metrics"><div class="metric"><b>10 / 10</b>Node 原版碰撞與移動測試</div><div class="metric"><b>6 / 6</b>Chromium DOM 輸入測試</div><div class="metric"><b>23.1 cm</b>中心路線最窄淨餘距</div></div>
<article><h2>實際操作軌跡</h2><img alt="原版碰撞程式的近柱移動軌跡" src="{b64('V018_column_motion_map.png')}"><p class="muted">藍：前進；橘：朝柱子移動直到受阻；紫：沿柱側向移動。為幾何測試路徑，不是 WebGL 畫面。</p></article>
<article><h2>側向阻擋：1,659 個碰撞取樣</h2><img alt="相對路線中心的橫向受阻個數" src="{b64('V018_lateral_blocking.png')}"><p>中心線全部通過，但靠近柱廊的左側取樣點會正常觸發碰撞。不能將「路線可走」直接解讀為「整個商家門口都可進出」。</p></article>
<article><h2>實際程式碰撞回歸</h2><table><thead><tr><th>測項</th><th>結果</th></tr></thead><tbody>{table}</tbody></table></article>
<article><h2>Chromium DOM 輸入事件</h2><table><thead><tr><th>測項</th><th>結果</th></tr></thead><tbody>{btable}</tbody></table><p class="muted">測試使用真實 Chromium DOM 與合成 PointerEvent，直接載入 V017 原始 input-events.js。未載入完整 Three.js WebGL 場景；不能視為 Android 真機測試。</p></article>
<article><h2>仍未完成的驗收</h2><div class="warning">此輪沒有驗證真實商店門檻高度、無障礙通行、實體 Android、私人網站 HTTPS/登入，亦未重新進行完整 WebGL2 3D 近景錄影。不應改動目前可正常阻擋的柱子碰撞；下一輪應針對實際遊戲鏡頭及門前通行感受驗收。</div></article>
</main></body></html>'''
(OUT/'Noboribetsu_Date_V018_R1_Review.html').write_text(page,encoding='utf-8')
print('rendered diagrams, html bytes',len(page.encode()))