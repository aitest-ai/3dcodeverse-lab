"""Strict NVIDIA NIM Nova-77 JSONL adapter. Standard library only.
Pinned upstream: NVIDIA-Maxine/nim-clients d02b7d57541b8598ac4c057947b10b2e42ccb1ee.
Legacy 34-point data is intentionally rejected rather than silently mis-mapped.
"""
from __future__ import annotations
import argparse,hashlib,json,math,struct
from pathlib import Path
UPSTREAM_COMMIT='d02b7d57541b8598ac4c057947b10b2e42ccb1ee'
# Target bone: source joint segment, verified against upstream Nova77 diagram.
SEGMENTS={'pelvis':(0,1),'spine_01':(1,2),'spine_02':(2,3),'spine_03':(3,4),'neck_01':(4,6),'head':(6,7),'clavicle_l':(11,12),'upperarm_l':(12,13),'lowerarm_l':(13,14),'clavicle_r':(39,40),'upperarm_r':(40,41),'lowerarm_r':(41,42),'thigh_l':(67,68),'calf_l':(68,69),'foot_l':(69,70),'ball_l':(70,71),'thigh_r':(72,73),'calf_r':(73,74),'foot_r':(74,75),'ball_r':(75,76)}
REQUIRED_JOINTS=sorted({i for pair in SEGMENTS.values() for i in pair})
def sha256(path):
    with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def finite_vector(value,size,label):
    if not isinstance(value,(list,tuple)) or len(value)!=size:raise ValueError(f'{label}: expected {size} numbers')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in value):raise ValueError(f'{label}: non-finite/non-numeric value')
    return [float(v) for v in value]
def camera_to_blender(p):
    # Official projection: (fx*x/z+cx, fy*y/z+cy). Right/down/away -> right/forward/up.
    x,y,z=p;return [x,z,-y]
def load_nova(path,fps,tracking_id,axes='opencv',provenance='unverified-input'):
    if not math.isfinite(fps) or not 0<fps<=240:raise ValueError('fps must be finite and in (0,240]')
    if axes not in {'opencv','blender'}:raise ValueError('axes must be explicitly opencv or blender')
    if provenance not in {'synthetic','unverified-input','nvidia-capture'}:raise ValueError('Unknown provenance')
    path=Path(path)
    if path.suffix=='.partial':raise ValueError('Refusing incomplete upstream .partial file')
    frames=[];previous=None
    for line_no,text in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not text.strip():continue
        row=json.loads(text)
        if not isinstance(row,dict):raise ValueError(f'line {line_no}: expected one frame object, not JSON array')
        frame=row.get('frame_id')
        if isinstance(frame,bool) or not isinstance(frame,int) or frame<0:raise ValueError(f'line {line_no}: invalid frame_id')
        if previous is not None and frame!=previous+1:raise ValueError(f'frame {frame}: duplicate/out-of-order/missing frame; segment the clip explicitly')
        previous=frame;detections=row.get('detections')
        if not isinstance(detections,list):raise ValueError('Missing detections array')
        selected=[d for d in detections if d.get('tracking_id')==tracking_id]
        if len(selected)!=1:raise ValueError(f'frame {frame}: track {tracking_id} absent or duplicated; never switch people automatically')
        body=selected[0];points=body.get('keypoints_3d',[]);confidence=body.get('keypoints_confidence',[])
        if len(points)!=77 or len(confidence)!=77:raise ValueError(f'frame {frame}: expected Nova-77; legacy 34-point and unknown schemas are NOT interchangeable')
        points=[finite_vector(p,3,f'joint {i}') for i,p in enumerate(points)]
        confidence=finite_vector(confidence,77,'confidence')
        if any(c<0 for c in confidence):raise ValueError('Negative confidence')
        for name,dims in (('rest_pose',3),('joint_rotations',4)):
            if name in body:
                if len(body[name])!=77:raise ValueError(f'{name}: expected 77 entries')
                for item in body[name]:
                    values=finite_vector(item,dims,name)
                    if name=='joint_rotations' and abs(sum(x*x for x in values)-1)>.05:raise ValueError('Invalid quaternion norm; upstream order must be XYZW')
        if axes=='opencv':points=[camera_to_blender(p) for p in points]
        frames.append({'frame':frame,'points':points,'confidence':confidence})
    if len(frames)<2:raise ValueError('At least two consecutive frames are required')
    return {'schema':'3dcodeverse.pose/1','source_schema':'NVIDIA-NIM-Nova77-JSONL','source_sha256':sha256(path),'upstream_commit':UPSTREAM_COMMIT,'provenance':provenance,'live_inference_verified':False,'fps':float(fps),'tracking_id':tracking_id,'input_axes':axes,'units':'meter','output_axes':'Blender-Z-up','frames':frames}
def read_glb(path):
    data=Path(path).read_bytes()
    if len(data)<20:raise ValueError('Truncated GLB')
    magic,version,size=struct.unpack_from('<4sII',data)
    if magic!=b'glTF' or version!=2 or size!=len(data):raise ValueError('Invalid GLB header')
    doc=None;binary=b'';pos=12
    while pos<len(data):
        if pos+8>len(data):raise ValueError('Truncated GLB chunk header')
        size,kind=struct.unpack_from('<I4s',data,pos);pos+=8
        if size%4 or pos+size>len(data):raise ValueError('Invalid GLB chunk size')
        chunk=data[pos:pos+size];pos+=size
        if kind==b'JSON':
            if doc is not None:raise ValueError('Duplicate JSON chunk')
            doc=json.loads(chunk)
        elif kind==b'BIN\0':binary=chunk
    if doc is None:raise ValueError('Missing GLB JSON')
    return doc,binary
def accessor_values(doc,binary,index):
    a=doc['accessors'][index]
    if 'sparse' in a or 'bufferView' not in a:raise ValueError('Sparse/implicit animation accessors not supported by this verifier')
    view=doc['bufferViews'][a['bufferView']]
    if view.get('buffer',0)!=0:raise ValueError('External buffers are not supported')
    fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]
    count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    fmt='<'+fmt*count;size=struct.calcsize(fmt);stride=view.get('byteStride',size)
    start=view.get('byteOffset',0)+a.get('byteOffset',0);end=view.get('byteOffset',0)+view['byteLength']
    if stride<size or a['count']<=0 or start+(a['count']-1)*stride+size>min(end,len(binary)):raise ValueError('Accessor outside binary buffer')
    return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a['count'])]
def verify_glb(path,clip_name=None):
    doc,binary=read_glb(path)
    if not doc.get('skins'):raise ValueError('GLB has no skin')
    skins=[[doc['nodes'][j].get('name',str(j)) for j in s['joints']] for s in doc['skins']];clips=[]
    for anim in doc.get('animations',[]):
        changed=0;ranges=[];targets=[]
        for channel in anim['channels']:
            sampler=anim['samplers'][channel['sampler']]
            times=[v[0] for v in accessor_values(doc,binary,sampler['input'])]
            if not all(math.isfinite(t) for t in times) or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Invalid animation time order')
            values=accessor_values(doc,binary,sampler['output'])
            if not all(math.isfinite(x) for v in values for x in v):raise ValueError('Non-finite animation output')
            interpolation=sampler.get('interpolation','LINEAR')
            if channel['target']['path']=='rotation':
                check=values[1::3] if interpolation=='CUBICSPLINE' else values
                if any(abs(sum(x*x for x in q)-1)>.01 for q in check):raise ValueError('Non-unit GLB rotation quaternion')
            if any(max(abs(x-y) for x,y in zip(values[0],v))>1e-5 for v in values[1:]):changed+=1
            ranges.extend((times[0],times[-1]));targets.append(doc['nodes'][channel['target']['node']].get('name'))
        clips.append({'name':anim.get('name'),'channels':len(anim['channels']),'changing_channels':changed,'duration_s':max(ranges)-min(ranges),'target_nodes':sorted(set(targets))})
    selected=[a for a in clips if a['name']==clip_name] if clip_name else clips
    if clip_name and (not selected or not any(a['changing_channels']>0 for a in selected)):raise ValueError(f'Missing or static requested clip {clip_name}')
    morphs=[sorted(m.get('extras',{}).get('targetNames',[])) for m in doc.get('meshes',[]) if m.get('extras',{}).get('targetNames')]
    return {'file':Path(path).name,'sha256':sha256(path),'skins':skins,'clips':clips,'morph_target_sets':sorted(morphs),'mesh_count':len(doc.get('meshes',[]))}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('--fps',type=float,required=True);p.add_argument('--track-id',type=int,required=True);p.add_argument('--axes',choices=['opencv','blender'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=load_nova(a.input,a.fps,a.track_id,a.axes);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8');print(f"Validated {len(result['frames'])} frames; live inference remains unverified")
if __name__=='__main__':main()
