#!/usr/bin/env python3
"""Free-only official demo retest. No paid fallback, account tokens or retries.
Only bundled demonstration audio; production voice rights remain unverified.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

BASE = 'https://indexteam-indextts-2-5-demo.hf.space'
ORDER = ['original_happy_035', 'original_happy_050', 'neutraltext_happy',
         'neutraltext_natural', 'neutraltext_angry', 'original_happy_065_repeat']
EMOTIONS = ('happy','angry','sad','afraid','disgusted','melancholic','surprised','calm')


def request_fields(line):
    emotion = line['emotion']
    strength = float(line['strength'])
    if emotion not in ('natural', *EMOTIONS):
        raise ValueError('Unrecognized emotion')
    if not 0.1 <= strength <= 1 or float(line['speed']) != 1:
        raise ValueError('Retest requires strength in [0.1, 1] and speed 1.0')
    if not isinstance(line['text'], str) or not 1 <= len(line['text']) <= 100:
        raise ValueError('Only short evaluation text is allowed')
    kwargs = dict(emo_control_method='Same as the voice reference' if emotion == 'natural' else 'Use emotion vectors',
                  text=line['text'], lang_choice='ZH', emo_ref_path=None,
                  emo_weight=strength, emo_text='', emo_random=False, duration_factor=1.0)
    kwargs.update({f'vec{i+1}': float(e == emotion) for i,e in enumerate(EMOTIONS)})
    return kwargs


def evaluate(plan, output, client_factory=None):
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
    report = dict(schema_version='1.0', started_at=datetime.now(timezone.utc).isoformat(),
                  provider='official_huggingface_demo_anonymous', model='IndexTTS-2.5', endpoint=BASE,
                  status='not_started', samples=[], skipped=[], seed_control='not_exposed_by_demo',
                  requested_budget=0, autoip_called=False, paid_gpu_job_started=False,
                  billing_credentials_used=False, automatic_retries=0, artifact_uploads=0,
                  reference=dict(source='official bundled example 0', production_rights='not_verified'),
                  prior_happy_result='rejected_by_user_sounds_angry')
    path = Path(output)
    if path.exists():
        raise FileExistsError('Refusing to overwrite previous report')
    try:
        from gradio_client import Client, handle_file
        from probe_official_demo import file_url, get_wav_report
        data = json.loads(Path(plan).read_text(encoding='utf-8'))
        mapping = {x['id']: x for x in data['lines']}
        lines = [mapping[x] for x in ORDER]
        for line in lines:
            request_fields(line)
        factory = client_factory or Client
        client = factory(BASE, token=False, download_files=False, verbose=False,
                         analytics_enabled=False, max_workers=1, httpx_kwargs={'timeout':45.0})
        example = client.submit(example=0, api_name='/on_example_click').result(timeout=60)
        ref_url = file_url(example[0])
        with urlopen(ref_url, timeout=30) as response:
            if not response.url.startswith(BASE+'/'):
                raise ValueError('Unexpected reference redirect')
            raw = response.read(20*1024*1024+1)
        if len(raw)>20*1024*1024:
            raise ValueError('Reference exceeds size limit')
        report['reference'].update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                                  previous_round_sha256='not_recorded; same example index, byte identity not proven')
        for index,line in enumerate(lines):
            start=time.monotonic()
            entry={**line,'status':'requested','listening_quality':'not_evaluated'}
            job=None
            try:
                kwargs=request_fields(line)
                kwargs['prompt']=handle_file(ref_url)
                entry['requested_vector']=[kwargs[f'vec{i}'] for i in range(1,9)]
                job=client.submit(**kwargs,api_name='/gen_single')
                value=job.result(timeout=120)
                entry.update(get_wav_report(file_url(value)))
                entry['status']='real_model_audio_generated'
            except Exception as exc:
                if job is not None:
                    job.cancel()
                error=str(exc)[:1000]
                entry.update(status='failed',error_type=type(exc).__name__,error=error)
                report['stopped_reason']='quota_or_access' if any(x in error.lower() for x in ('quota','limit','authenticate','credit')) else 'provider_error'
            entry['elapsed_seconds']=round(time.monotonic()-start,2)
            report['samples'].append(entry)
            print('FREE_RETEST_SAMPLE '+json.dumps(entry,ensure_ascii=False),flush=True)
            if entry['status']=='failed':
                report['skipped']=[dict(id=l['id'],reason='stop_on_first_failure_no_retry') for l in lines[index+1:]]
                break
        successes=sum(x['status']=='real_model_audio_generated' for x in report['samples'])
        report['status']='completed' if successes==len(lines) else ('partial' if successes else 'blocked')
        report['successful_audio_count']=successes
    except Exception as exc:
        report.update(status='blocked',error_type=type(exc).__name__,error=str(exc)[:1000],successful_audio_count=0)
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('FREE_RETEST_REPORT '+json.dumps(report,ensure_ascii=False),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--plan',default=str(Path(__file__).with_name('cases_happy_retest_v1.json')))
    p.add_argument('--output',default='free-retest-report.json')
    args=p.parse_args()
    r=evaluate(args.plan,args.output)
    raise SystemExit(0 if r['status']=='completed' else 2)
