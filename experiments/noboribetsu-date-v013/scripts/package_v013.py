#!/usr/bin/env python3
"""Package reviewed V013 without touching V012 archives or altering original geometry."""
from pathlib import Path
import zipfile,hashlib,json,base64,html,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/mnt/data')

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def make_html():
 images={}
 for tag in ('v005','v004'):
  for side in ('before','after'):
   p=(ROOT/('qa_final' if tag=='v005' else 'qa_v004')/f'V013_{tag}_{side}_WebGL2.png')
   images[f'{tag}_{side}']='data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
 sections=[]
 for title,k,descr in [
  ('V005 商家街｜草鞋屋、變裝攝影館附近','v005','真 WebGL2 渲染差異可見但克制。比較畫面由測試用相機位置設定取得；不是實際走路抵達的驗收。'),
  ('V004 商家街｜保留既有石邊','v004','此區已有較完整石邊與舊化材質，新增效果在本鏡位幾乎無法分辨，為了避免重疊沒有刻意加重色彩。')]:
  a=images[f'{k}_before'];b=images[f'{k}_after']
  sections.append(f'''<section class="comparison"><h2>{html.escape(title)}</h2><p>{html.escape(descr)}</p>
<div class="frame" data-slider><img src="{a}" class="base" alt="未開啟 V013 路緣的相同遊戲場景">
<div class="top"><img src="{b}" alt="開啟 V013 路緣的相同遊戲場景"></div><div class="line"></div>
<input type="range" min="0" max="100" value="50" aria-label="拖曳比較新舊模型" /></div>
<div class="labels"><span>左側：原 V012 效果</span><span>右側：新增 V013 效果</span></div></section>''')
 page='''<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>登別伊達時代村 V013｜商家街路緣比較</title><style>
:root{font-family:system-ui,-apple-system,'Noto Sans TC',sans-serif;color:#263a32;background:#f4f4ef}*{box-sizing:border-box}
body{margin:0}header{padding:2.6rem max(24px,calc((100% - 940px)/2));background:#e6ebe4;border-bottom:1px solid #cdd4cb}
main{max-width:940px;margin:auto;padding:1.2rem 20px 4rem}h1{font-size:clamp(1.5rem,4vw,2.1rem);margin:0 0 .7rem}h2{font-size:1.25rem}
p{line-height:1.75;color:#485a50}.meta{display:flex;flex-wrap:wrap;gap:12px}.chip{background:#fff;border:1px solid #d4ded5;border-radius:8px;padding:7px 12px}
.comparison{background:#fff;border:1px solid #d5ddd5;border-radius:12px;padding:20px;margin:24px 0}
.frame{position:relative;overflow:hidden;aspect-ratio:5/3;background:#dce5da;--split:50%;}
.frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.frame .top{position:absolute;inset:0;overflow:hidden;clip-path:inset(0 0 0 var(--split));pointer-events:none}
.frame .top img{width:100%;height:100%;object-fit:contain}
.frame .line{position:absolute;top:0;bottom:0;left:var(--split);border-left:3px solid white;filter:drop-shadow(0 0 2px #555);pointer-events:none}
.frame input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:ew-resize}
.labels{display:flex;justify-content:space-between;font-size:.83rem;color:#52695e;padding-top:8px}.note{border-left:3px solid #9daa9b;padding:12px;background:#fff}
</style></head><body><header><h1>登別伊達時代村 V013</h1><p>V004／V005 商家街道路與草地交界的選擇性精修</p>
<div class="meta"><span class="chip">2,436 面新視覺幾何</span><span class="chip">V011／V012 完整保留</span><span class="chip">Chromium WebGL2 實測</span></div></header><main>
<p class="note">拖曳圖片中的滑桿，查看**同一場景與相機**在開啟和關閉 V013 新路緣時的差異。畫面經 Chromium WebGL2 軟體渲染測試，僅供美術對照；尚未驗證 Android 真機或私人網站 CDN／HTTPS。</p>
'''+''.join(sections)+'''<p>資料來源：凍結的 V002 GSI 高程、V004 與 V005 道路模型；土色及草色是作者推估的視覺補強，不是測量道路、排水或實地地形還原。V004 的既有石邊優先保留。</p></main>
<script>document.querySelectorAll('[data-slider]').forEach(el=>{const inp=el.querySelector('input');function change(){el.style.setProperty('--split',inp.value+'%')}inp.addEventListener('input',change);change()})</script></body></html>'''
 (OUT/'Noboribetsu_Date_V013_R1_Review.html').write_text(page,encoding='utf8')

def packages():
 root=ROOT/'runtime'
 runtime=OUT/'Noboribetsu_Date_V013_R1_Runtime.zip'
 with zipfile.ZipFile(runtime,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for file in sorted(root.rglob('*')):
   if file.is_file():z.write(file,file.relative_to(root).as_posix())
 qa=OUT/'Noboribetsu_Date_V013_R1_SourceQA.zip'
 with zipfile.ZipFile(qa,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for folder,arc in [('scripts','source'),('qa','evidence'),('qa_final','evidence/webgl_v005'),('qa_v004','evidence/webgl_v004'),('outputs','assets')]:
   for file in sorted((ROOT/folder).glob('*')):
    if file.is_file():z.write(file,arc+'/'+file.name)
  for file in [OUT/'Noboribetsu_Date_V013_R1_Review.html',OUT/'Noboribetsu_Date_V013_R1_Delivery_Report.md']:
   z.write(file,file.name)
 for f in [runtime,qa]:
  with zipfile.ZipFile(f) as z:
   bad=z.testzip()
   if bad:raise RuntimeError('CRC failure '+bad)
 return [runtime,qa]
if __name__=='__main__':
 make_html()
 if '--all' in sys.argv:print([str(x) for x in packages()])