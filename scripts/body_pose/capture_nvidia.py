"""Explicit, consent-gated call to the PINNED official NVIDIA gRPC client.
No implicit cloud call, no automatic API retries, no hard-coded key, no raw-video commit.
"""
from __future__ import annotations
import argparse,json,math,os,subprocess,sys
from fractions import Fraction
from pathlib import Path
from pose_io import UPSTREAM_COMMIT,load_nova,sha256
FUNCTION_ID='254b3621-bb66-4b7b-9c89-621c352b4d91'

def validate_media(meta:dict)->dict:
    streams=meta.get('streams',[])
    if len(streams)!=1:raise ValueError('Expected one selected video stream')
    s=streams[0]
    if s.get('codec_name')!='h264' or s.get('pix_fmt')!='yuv420p':raise ValueError('Pilot requires H.264, 8-bit yuv420p; re-encode explicitly first')
    if s.get('color_transfer') in {'smpte2084','arib-std-b67'}:raise ValueError('HDR not supported')
    fps=float(Fraction(s.get('avg_frame_rate','0/1')))
    if not 0<fps<=60:raise ValueError('Pilot requires 0 < fps <= 60')
    times=[float(f['best_effort_timestamp_time']) for f in meta.get('frames',[]) if 'best_effort_timestamp_time' in f]
    if len(times)<2:raise ValueError('Missing decoded frame timestamps')
    dt=1/fps
    if not all(math.isfinite(t) for t in times) or any(abs((b-a)-dt)>max(1e-4,dt*.002) for a,b in zip(times,times[1:])):raise ValueError('Variable frame rate or dropped frame; use explicit CFR conversion')
    if len(times)/fps>30:raise ValueError('Pilot is intentionally limited to 30 seconds per request')
    if s.get('width',0)<=0 or s.get('height',0)<=0:raise ValueError('Invalid dimensions')
    return {'fps':fps,'frames':len(times),'width':s['width'],'height':s['height']}

def validate_boxes(path:Path,media:dict,track_id:int):
    lines=path.read_text().splitlines()
    if not lines or not 1<=int(lines[0])<=50:raise ValueError('Invalid tracked-body count')
    seen=set();selected=set()
    for line in lines[1:]:
        if not line.strip():continue
        values=line.split()
        if len(values)!=6:raise ValueError('BBox rows require frame_id tracking_id x y w h')
        f,t=map(int,values[:2]);x,y,w,h=map(float,values[2:])
        if (f,t) in seen:raise ValueError('Duplicate frame/track bbox')
        seen.add((f,t))
        if not 0<=f<media['frames']:raise ValueError('BBox frame outside clip')
        if (x,y,w,h)==(-1.,-1.,-1.,-1.):continue
        if not all(math.isfinite(v) for v in (x,y,w,h)) or x<0 or y<0 or w<=0 or h<=0 or x+w>media['width']+.01 or y+h>media['height']+.01:raise ValueError('BBox outside image or invalid')
        if t==track_id:selected.add(f)
    if selected!=set(range(media['frames'])):raise ValueError('Selected person must have a valid bbox in every frame; split missing sections')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client-root',type=Path,required=True);p.add_argument('--video',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--track-id',type=int,default=1)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--bbox',type=Path);group.add_argument('--single-person-full-frame',action='store_true')
    p.add_argument('--confirm-upload',action='store_true');a=p.parse_args()
    if not a.confirm_upload:raise SystemExit('Upload not authorized. Read NVIDIA trial privacy terms, then explicitly pass --confirm-upload.')
    key=os.environ.get('NVIDIA_API_KEY','')
    if not key:raise SystemExit('Set NVIDIA_API_KEY locally or as a GitHub Secret; do NOT paste it into chat or source code.')
    client=a.client_root.resolve();video=a.video.resolve();out=a.output.resolve()
    if out.exists():raise SystemExit('Output directory already exists; choose a new directory to preserve prior evidence.')
    commit=subprocess.run(['git','-C',str(client),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
    if commit!=UPSTREAM_COMMIT:raise SystemExit('Client commit differs from pinned schema; review it before updating the lock.')
    if video.suffix.lower()!='.mp4' or not video.is_file() or video.stat().st_size>50_000_000:raise SystemExit('Pilot accepts an existing H.264 MP4 up to 50,000,000 bytes.')
    probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,avg_frame_rate,pix_fmt,color_transfer:frame=best_effort_timestamp_time','-show_frames','-of','json',str(video)],capture_output=True,text=True,check=True,timeout=60)
    media=validate_media(json.loads(probe.stdout));out.mkdir(parents=True)
    if a.single_person_full_frame:
        boxes=out/'single_person_full_frame.txt'
        boxes.write_text('1\n'+'\n'.join(f"{f} {a.track_id} 0 0 {media['width']} {media['height']}" for f in range(media['frames'])))
    else:boxes=a.bbox.resolve()
    validate_boxes(boxes,media,a.track_id)
    script=client/'body-pose/scripts/body_pose.py';raw=out/'pose.json'
    argv=[str(script),'--preview-mode','--target','grpc.nvcf.nvidia.com:443','--function-id',FUNCTION_ID,'--video-input',str(video),'--bbox-input',str(boxes),'--output',str(raw),'--overlay-output',str(out/'overlay.mp4'),'--timeout','550']
    # The OS argv contains only the environment lookup, never the actual API key.
    runner="import os,runpy,sys;sys.path.insert(0,"+repr(str(script.parent))+");sys.argv="+repr(argv)+"+['--api-key',os.environ['NVIDIA_API_KEY']];runpy.run_path("+repr(str(script))+",run_name='__main__')"
    receipt={'upstream_commit':commit,'function_id':FUNCTION_ID,'video_sha256':sha256(video),'bbox_sha256':sha256(boxes),'media':media,'cloud_request_attempted':True,'response_validated':False,'pose_quality_approved':False}
    try:
        result=subprocess.run([sys.executable,'-c',runner],cwd=str(script.parent),capture_output=True,text=True,timeout=600)
        (out/'client_redacted.log').write_text((result.stdout+'\n'+result.stderr).replace(key,'[REDACTED]'))
        receipt['client_exit_code']=result.returncode
        if result.returncode:raise RuntimeError('NVIDIA request failed; see redacted log. No automatic retry was made.')
        normalized=load_nova(raw,media['fps'],a.track_id,'opencv','nvidia-capture')
        if len(normalized['frames'])!=media['frames']:raise RuntimeError('Server returned fewer frames than input')
        receipt['response_validated']=True;receipt['pose_sha256']=sha256(raw);receipt['frames']=len(normalized['frames'])
        (out/'normalized.json').write_text(json.dumps(normalized))
    finally:(out/'capture_receipt.json').write_text(json.dumps(receipt,indent=2))
    print('Received and structurally validated NVIDIA pose output. Accuracy and retarget still require review.')
if __name__=='__main__':main()
