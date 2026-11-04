"""Make labelled 2x2 comparison MP4s from actual browser screenshots, with original clip timing.
Eight sampled phases per view; no fabricated/interpolated character frames. FFmpeg duplicates frames
for common 24fps container compatibility. A is always left, B right inside each camera panel.
"""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'videos';OUT.mkdir(exist_ok=True)
catalog=json.loads((R/'evidence/frame-catalog.json').read_text());result=[]
for character in ['harbor-courier-review','taiwan-oldman-review']:
    for clip in ['Walk','Run']:
        entries=[v for v in catalog['sequences'] if v['character']==character and v['clip']==clip]
        assert len(entries)==4
        d=entries[0]['duration_s'];fps=8/d;cmd=['ffmpeg','-y','-v','error','-threads','2'];filters=[]
        for i,view in enumerate(['front','side','back','elbow']):
            folder=R/'evidence/frames'/character/clip/view;assert len(list(folder.glob('*.png')))==8
            cmd+=['-framerate',str(fps),'-i',str(folder/'%03d.png')]
            title=f'{view.upper()} | A before (left) / B candidate (right)'
            filters.append(f'[{i}:v]loop=loop=5:size=8:start=0,setpts=N/({fps}*TB),scale=640:-2,pad=640:440:0:26:color=0x182321,drawtext=text=\'{title}\':fontcolor=white:fontsize=16:x=10:y=5[v{i}]')
        filters+=['[v0][v1]hstack=inputs=2[top]','[v2][v3]hstack=inputs=2[bottom]','[top][bottom]vstack=inputs=2[out]']
        dest=OUT/f'{character}-{clip.lower()}-webgl-comparison.mp4'
        cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[out]','-r','24','-t',str(d*6),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        subprocess.run(cmd,check=True)
        result.append({'file':dest.name,'character':character,'clip':clip,'source':'Real WebGL2 A/B screenshots','sampled_phases_per_view':8,'views':['front','side','back','elbow'],'loops':6,'original_clip_duration_s':d,'bytes':dest.stat().st_size,'warning':'Sampled frame sequence, not real-time GPU performance or human art approval'})
        print(dest.name,dest.stat().st_size,flush=True)
(OUT/'video-index.json').write_text(json.dumps({'videos':result,'art_approved':False},ensure_ascii=False,indent=2)+'\n')
