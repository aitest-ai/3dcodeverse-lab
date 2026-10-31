#!/usr/bin/env python3
"""Four bounded real-model demo requests. No user audio, paid job, or audio in Git.
Bundled reference: demonstration only, NOT cleared for production characters.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
import struct
import time
import urllib.request
import wave
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, quote

BASE = 'https://indexteam-indextts-2-5-demo.hf.space'
TEXT = '你怎麼現在才來？我都快收攤了啦！'

def file_url(value):
    """Gradio may wrap FileData in one or more update/value dictionaries."""
    for _ in range(6):
        if isinstance(value,(list,tuple)) and value:
            value=value[0]
        elif isinstance(value,dict) and 'value' in value:
            value=value['value']
        else:
            break
    if isinstance(value,dict):
        candidate=value.get('url') or value.get('path')
    else:
        candidate=value
    if not isinstance(candidate,str) or not candidate:
        raise ValueError('Demo did not return FileData: '+str(value)[:300])
    if candidate.startswith('/') or candidate.startswith('examples/'):
        candidate=BASE+'/gradio_api/file='+quote(candidate,safe='/')
    parsed=urlsplit(candidate)
    if parsed.scheme!='https' or parsed.hostname!=urlsplit(BASE).hostname or parsed.username or parsed.password:
        raise ValueError('Refusing unexpected demo audio origin')
    return candidate

def get_wav_report(url: str) -> dict:
    url=file_url(url)
    with urllib.request.urlopen(url, timeout=45) as response:
        if urlsplit(response.url).hostname!=urlsplit(BASE).hostname:
            raise ValueError('Unexpected audio redirect')
        audio=response.read(20*1024*1024+1)
    if len(audio)>20*1024*1024:
        raise ValueError('Audio exceeds evaluation limit')
    with wave.open(io.BytesIO(audio),'rb') as wav:
        rate,frames,width,channels=wav.getframerate(),wav.getnframes(),wav.getsampwidth(),wav.getnchannels()
        raw=wav.readframes(frames)
    if not rate or not frames or len(raw)!=frames*width*channels:
        raise ValueError('Empty or truncated WAV')
    result={'sha256':hashlib.sha256(audio).hexdigest(),'bytes':len(audio),
            'duration_seconds':round(frames/rate,3),'sample_rate':rate,'channels':channels,
            'sample_width':width,'audio_url':url,'listening_quality':'not_evaluated','url_is_temporary':True}
    if width==2:
        samples=struct.unpack('<'+str(len(raw)//2)+'h',raw)
        rms=math.sqrt(sum(v*v for v in samples)/len(samples))/32768
        result.update(rms_dbfs=round(20*math.log10(max(rms,1e-12)),2),
                      clipping_ratio=round(sum(abs(v)>=32760 for v in samples)/len(samples),6))
        if rms<0.00001:
            raise ValueError('Generated WAV is silent')
    return result

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='demo-probe-report.json')
    args=parser.parse_args()
    report={'started_at':datetime.now(timezone.utc).isoformat(),'model':'IndexTTS-2.5',
            'provider':'official_huggingface_demo','endpoint':BASE,'text':TEXT,'speed':1.0,'strength':0.65,
            'reference':{'source':'official bundled example 0','purpose':'demo evaluation only',
                         'commercial_character_rights':'not_verified'},
            'paid_gpu_job_started':False,'autoip_called':False,'samples':[]}
    try:
        from gradio_client import Client, handle_file
        client=Client(BASE,download_files=False,verbose=False,analytics_enabled=False,httpx_kwargs={'timeout':60.0})
        example_job=client.submit(example=0,api_name='/on_example_click')
        example=example_job.result(timeout=90)
        ref_url=file_url(example[0])
        report['reference']['resolved']=True
        for emotion,index in [('natural',None),('happy',1),('angry',2),('sad',3)]:
            kwargs={'emo_control_method':'Same as the voice reference' if index is None else 'Use emotion vectors',
                    'prompt':handle_file(ref_url),'text':TEXT,'lang_choice':'ZH','emo_ref_path':None,
                    'emo_weight':0.65,'emo_text':'','emo_random':False,'duration_factor':1.0}
            kwargs.update({'vec'+str(i):1.0 if index==i else 0.0 for i in range(1,9)})
            start=time.monotonic()
            entry={'emotion':emotion,'status':'requested'}
            job=None
            try:
                job=client.submit(**kwargs,api_name='/gen_single')
                value=job.result(timeout=180)
                entry.update(get_wav_report(file_url(value)))
                entry['status']='real_model_audio_generated'
            except Exception as exc:
                if job is not None:
                    job.cancel()
                entry.update(status='failed',error_type=type(exc).__name__,error=str(exc)[:800])
            entry['elapsed_seconds']=round(time.monotonic()-start,2)
            report['samples'].append(entry)
            print('DEMO_SAMPLE',json.dumps(entry,ensure_ascii=False),flush=True)
            if entry['status']=='failed':
                break  # Respect quota/access failures; no retries or alternate identities.
        report['status']='success' if len(report['samples'])==4 and all(x['status']=='real_model_audio_generated' for x in report['samples']) else 'incomplete'
    except Exception as exc:
        report.update(status='blocked',error_type=type(exc).__name__,error=str(exc)[:800])
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('DEMO_REPORT',json.dumps(report,ensure_ascii=False),flush=True)
    return 0 if report['status']=='success' else 2

if __name__=='__main__':
    raise SystemExit(main())
