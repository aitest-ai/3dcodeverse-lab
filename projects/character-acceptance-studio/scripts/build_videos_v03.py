"""Four-view MP4s from actual browser framebuffers. Eight distinct phases, not 24fps evidence."""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];OUT=R/'videos-v03';OUT.mkdir(exist_ok=True)
catalog=json.loads((R/'evidence-v03/frame-catalog.json').read_text());result=[]
for character in ['harbor-courier-review','taiwan-oldman-review']:
    for clip in ['Walk','Run','Start','Stop','TurnLeft','TurnRight']:
        entries=[v for v in catalog['sequences'] if v['character']==character and v['clip']==clip]
        assert len(entries)==4
        d=entries[0]['duration_s'];fps=8/d;cmd=['ffmpeg','-y','-v','error','-threads','2'];filters=[]
        compare=entries[0]['mode'].startswith('A ')
        for i,view in enumerate(['front','side','back','feetwide']):
            folder=R/'evidence-v03/frames'/character/clip/view;assert len(list(folder.glob('*.png')))==8
            cmd+=['-framerate',str(fps),'-i',str(folder/'%03d.png')]
            title=f'{view.upper()} | '+('A v0.2 left / B v0.3 right' if compare else 'B v0.2 only - no v0.1 clip')
            filters.append(f'[{i}:v]loop=loop=3:size=8:start=0,setpts=N/({fps}*TB),scale=640:-2,pad=640:440:0:26:color=0x182321,drawtext=text=\'{title}\':fontcolor=white:fontsize=16:x=10:y=5[v{i}]')
        filters+=['[v0][v1]hstack=inputs=2[top]','[v2][v3]hstack=inputs=2[bottom]','[top][bottom]vstack=inputs=2[out]']
        dest=OUT/f'{character}-{clip.lower()}-webgl.mp4'
        cmd+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map','[out]','-r','24','-t',str(d*4),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
        subprocess.run(cmd,check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)]))
        result.append({'file':dest.name,'character':character,'clip':clip,'source':entries[0]['source'],'mode':entries[0]['mode'],'sampled_phases_per_view':8,'views':['front','side','back','feetwide'],'loops':4,'original_clip_duration_s':d,'bytes':dest.stat().st_size,'video':{k:probe['streams'][0][k] for k in ['codec_name','width','height','r_frame_rate','nb_frames']},'duration_s':probe['format']['duration'],'warning':'8 distinct framebuffer samples per camera repeated into a compatible 24fps container; not real-time GPU performance or art approval'})
        print(dest.name,dest.stat().st_size,flush=True)
(OUT/'video-index.json').write_text(json.dumps({'videos':result,'art_approved':False},ensure_ascii=False,indent=2)+'\n')
