#!/usr/bin/env python3
"""Make both lightweight runtime review (relative images) and all-inline offline review."""
from pathlib import Path
import argparse,html,base64
DIR=Path(__file__).parent
ITEMS=[('utsuroi_side','變裝攝影館側牆','移除過密直立木條，改為較疏支柱及下半部木板'),
 ('utsuroi_cornice','變裝攝影館屋簷視角','檢視屋簷、上層結構是否因側牆修改而出現破圖'),
 ('utsuroi_walk','變裝攝影館街道視角','以步行者視線檢查正面和側牆的銜接'),
 ('waraji_control','草鞋屋保護對照','控制組：草鞋屋 V008 幾何保持不變')]
def build(inline:bool):
 def img(name):
  file=DIR/'outputs'/name
  if not file.exists():raise FileNotFoundError(file)
  if inline:return 'data:image/png;base64,'+base64.b64encode(file.read_bytes()).decode()
  return 'evidence/'+name
 sections=[]
 for key,title,description in ITEMS:
  a=img(key+'_V008.png');b=img(key+'_V009.png')
  sections.append(f'''<section class="compare" aria-label="{html.escape(title)}">
  <h2>{html.escape(title)}</h2><p>{html.escape(description)}</p>
  <div class="compare-area">
   <img class="before" src="{a}" alt="{html.escape(title)} V008 舊模型">
   <img class="after" src="{b}" alt="{html.escape(title)} V009 精修模型">
   <div class="line" aria-hidden="true"></div><span class="tag left">V008</span><span class="tag right">V009</span>
  </div>
  <label>拖曳比較：<input type="range" value="50" min="0" max="100" aria-label="{html.escape(title)} 新舊比較位置"></label>
 </section>''')
 return '''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>登別伊達時代村 V009｜同鏡位模型比較</title>
 <style>*,*:before,*:after{box-sizing:border-box}body{background:#f5f3ef;color:#29392f;margin:0;font-family:system-ui,"Noto Sans TC",sans-serif}main{max-width:1100px;margin:auto;padding:clamp(14px,4vw,28px)}a{color:#396e59}h1{font-size:clamp(24px,5vw,35px)}h2{font-size:21px}.note{padding:15px 18px;border-left:3px solid #888;color:#435c4e;background:#ebece6;line-height:1.8}.compare{background:#fff;border:1px solid #dddfd8;border-radius:14px;padding:clamp(12px,2vw,22px);margin:24px 0;box-shadow:0 3px 16px #00000008}.compare>p{line-height:1.7}.compare-area{position:relative;width:100%;aspect-ratio:1080/675;background:#e0e5de;overflow:hidden}.compare-area img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.after{clip-path:inset(0 50% 0 0)}.line{position:absolute;top:0;bottom:0;width:2px;left:50%;background:#fff;box-shadow:0 0 3px #333}.tag{position:absolute;top:10px;padding:5px 10px;font-size:13px;background:#26372dcc;color:white;border-radius:5px}.tag.left{left:10px}.tag.right{right:10px}label{display:block;margin-top:12px;font-size:15px}input{display:block;width:100%;accent-color:#49735b;margin:10px 0;min-height:24px}footer{line-height:1.7;color:#647064;font-size:14px;padding:20px 0}</style></head><body><main>
 <h1>登別伊達時代村 V009｜近景修正比較</h1><p class="note">這些畫面是把實際 GLB 重新讀入後，由 VTK 使用同一組鏡頭與光線產生；<strong>不是 Three.js WebGL2 真正遊戲截圖，也不是 Blender Cycles 渲染。</strong> 變裝攝影館用途可由<a href="https://edo-trip.jp/facility/utsuroi-kan/">官方資料</a>查證，側牆細節仍屬作者推估，並非 2026 實景還原。</p>
 '''+''.join(sections)+'''<footer>V009 保留 231.5664 公尺的原路線與碰撞、草鞋屋 V008 模型。Android、WebGL2 GPU、私人網址與 Blender 正式母檔仍未驗收。</footer></main><script>
 for(const section of document.querySelectorAll('section.compare')){const slider=section.querySelector('input');const after=section.querySelector('.after');const line=section.querySelector('.line');const update=()=>{const v=Number(slider.value);after.style.clipPath=`inset(0 ${100-v}% 0 0)`;line.style.left=v+'%';};slider.addEventListener('input',update);update();}
 </script></body></html>'''

def main():
 out=DIR/'outputs';out.mkdir(exist_ok=True)
 (out/'Noboribetsu_Date_V009_R1_Review.html').write_text(build(True),encoding='utf-8')
 dest=DIR/'runtime/dist';(dest/'evidence').mkdir(exist_ok=True,parents=True)
 for key,*_ in ITEMS:
  for stage in ('V008','V009'):
   import shutil
   shutil.copy2(out/f'{key}_{stage}.png',dest/'evidence'/f'{key}_{stage}.png')
 (dest/'review_v009.html').write_text(build(False),encoding='utf-8')
 print('Saved offline and runtime comparison pages')

if __name__=='__main__':main()