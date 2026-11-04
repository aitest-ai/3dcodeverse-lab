from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1]
def asset(rel):
 p=r/rel;return {'url':'../'+rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
a=r/'assets/harbor-courier-review/0.1.0'
report=json.loads((a/'motion-audit.json').read_text());motion={k:{'speed_mps':v['speed_mps'],'note':'原始 CC0 動作；接地／步速、袖口及肩帶修正候選。服裝、手肘、重心仍待美術驗收。' if k in ['Walk','Run'] else '原有待機，接地修正候選。' if k=='Idle' else '實驗片段：姿態混合或步行加根節點轉向，腳滑／支撐腳尚待修正，禁止正式地圖取用。'} for k,v in report['clips'].items()}
c={'id':'harbor-courier-review','name':'Harbor 郵差 · 完整衣鞋','version':'0.1.0','height_m':1.76,'fps':30,'profileSummary':'65 骨 · Quaternius T-pose','profile':'../assets/harbor-courier-review/0.1.0/skeleton-profile.json','source':asset('sources/harbor-v02/assets/harbor-courier-v02.glb'),'candidate':asset('assets/harbor-courier-review/0.1.0/harbor-courier-review.glb'),'motions':motion,'provenance':{'pr':137,'commit':'8e877a07f19571436c2658a885db77206014a74c','author':'Quaternius / 3dcodeverse-lab styling','source':'../sources/harbor-v02/THIRD_PARTY_NOTICES.md'},'license':'Quaternius CC0-1.0 + existing project-authored outfit under user task authorization','warnings':['所有動畫尚未美術核准','起停／轉身為實驗候選','不具遊戲端即時布料／Foot IK','來源原圖已是 256px，本版保存原位元組，沒有恢復不存在的細節']}
(r/'assets/registry.json').write_text(json.dumps({'schema_version':1,'version':'0.1.0','characters':[c],'art_approved':False},ensure_ascii=False,indent=2))
b=r/'assets/taiwan-oldman-review/0.1.0';rr=json.loads((b/'motion-audit.json').read_text())
old={'id':'taiwan-oldman-review','name':'V29 騎樓阿伯 · 較矮寬身形','version':'0.1.0','height_m':1.60,'fps':30,'profileSummary':'53 骨 · MPFB A-pose · 獨立 rest/roll 適配','profile':'../assets/taiwan-oldman-review/0.1.0/skeleton-profile.json','source':{**asset('assets/taiwan-oldman-review/0.1.0/oldman-retarget-baseline.glb'),'label':'重定向初稿（非原 V29 動作）'},'candidate':asset('assets/taiwan-oldman-review/0.1.0/oldman-retarget-candidate.glb'),'motions':{k:{'speed_mps':v['speed_mps'],'note':'Quaternius→MPFB rest/軸向適配及烘焙候選；服裝、手肘、腳滑尚待美術驗收。'} for k,v in rr['variants']['candidate'].items()},'provenance':{'pr':48,'commit':'1b1f3695abde627362f6cdd78031e442fbee9ea4','documentation_head':'0cef2282394b911e61cb3cde169f31be0034af95','artifact_id':13039030982,'original_source':'../sources/oldman-v29/oldman.blend','original_GLBS':['../sources/oldman-v29/oldman.glb','../sources/oldman-v29/oldman_stress.glb'],'author':'MakeHuman Community / MRT garments / existing 3dcodeverse styling; Quaternius motion'},'license':'MakeHuman CC0-1.0; MRT CC0 shirt/pants; Quaternius CC0 motion. See LICENSE-SOURCE-HEADERS.txt','warnings':['原 V29 只有短姿態片段，這裡 A 為本次重定向初稿，B 為接地候選','不同53骨、A姿態與骨長，未複製65骨動畫或 inverse bind','原有手機仍綁手，握持未適配','未提供起停／轉身','來源原圖512px完整保留，未宣稱高解析度原素材已取回']}
reg=json.loads((r/'assets/registry.json').read_text());reg['characters'].append(old);(r/'assets/registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')

reg=json.loads((r/'assets/registry.json').read_text())
for c in reg['characters']:
 c['profile_sha256']=hashlib.sha256((r/'web'/c['profile']).resolve().read_bytes()).hexdigest()
 c['art_approved']=False;c['game_ready']=False
(r/'assets/registry.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
