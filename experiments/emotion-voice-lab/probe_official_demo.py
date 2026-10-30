#!/usr/bin/env python3
"""Evaluation only: four requests to the official demo, no user audio or paid job.
No audio is uploaded to this repository. Returned demo URLs are temporary.
Bundled demo voice is NOT cleared for use as a production game character.
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
from urllib.parse import urlsplit

BASE = 'https://indexteam-indextts-2-5-demo.hf.space'
TEXT = '你怎麼現在才來？我都快收攤了啦！'

def get_wav_report(url: str) -> dict:
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != urlsplit(BASE).hostname:
        raise ValueError('Refusing unexpected audio host')
    with urllib.request.urlopen(url, timeout=45) as response:
        audio = response.read(20 * 1024 * 1024 + 1)
    if len(audio) > 20 * 1024 * 1024:
        raise ValueError('Audio response exceeds evaluation limit')
    with wave.open(io.BytesIO(audio), 'rb') as wav:
        rate, frames, width, channels = wav.getframerate(), wav.getnframes(), wav.getsampwidth(), wav.getnchannels()
        raw = wav.readframes(frames)
    if not rate or not frames or len(raw) != frames * width * channels:
        raise ValueError('Empty or truncated WAV')
    result = {'sha256': hashlib.sha256(audio).hexdigest(), 'bytes': len(audio),
              'duration_seconds': round(frames/rate, 3), 'sample_rate': rate,
              'channels': channels, 'sample_width': width, 'audio_url': url,
              'listening_quality': 'not_evaluated', 'url_is_temporary': True}
    if width == 2:
        samples = struct.unpack('<' + str(len(raw)//2) + 'h', raw)
        rms = math.sqrt(sum(v*v for v in samples)/len(samples))/32768
        result.update(rms_dbfs=round(20*math.log10(max(rms, 1e-12)), 2),
                      clipping_ratio=round(sum(abs(v)>=32760 for v in samples)/len(samples), 6))
        if rms < 0.00001:
            raise ValueError('Generated WAV is silent')
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='demo-probe-report.json')
    args = parser.parse_args()
    report = {'started_at': datetime.now(timezone.utc).isoformat(), 'model': 'IndexTTS-2.5',
              'provider': 'official_huggingface_demo', 'endpoint': BASE,
              'text': TEXT, 'speed': 1.0, 'strength': 0.65,
              'reference': {'source': 'official bundled example 0', 'purpose': 'demo evaluation only',
                            'commercial_character_rights': 'not_verified'},
              'paid_gpu_job_started': False, 'autoip_called': False, 'samples': []}
    try:
        from gradio_client import Client, handle_file
        client = Client(BASE, download_files=False, verbose=False, analytics_enabled=False,
                        httpx_kwargs={'timeout': 60.0})
        example_job = client.submit(example=0, api_name='/on_example_click')
        example = example_job.result(timeout=90)
        ref = example[0]
        ref_url = ref.get('url') if isinstance(ref, dict) else ref
        if not ref_url:
            raise ValueError('Official demo did not return its bundled reference URL')
        if urlsplit(ref_url).hostname != urlsplit(BASE).hostname:
            raise ValueError('Unexpected reference host; no audio uploaded')
        report['reference']['file_name'] = ref.get('orig_name') if isinstance(ref,dict) else None
        for emotion, vector_index in [('natural', None), ('happy', 1), ('angry', 2), ('sad', 3)]:
            kwargs = {'emo_control_method': 'Same as the voice reference' if vector_index is None else 'Use emotion vectors',
                      'prompt': handle_file(ref_url), 'text': TEXT, 'lang_choice': 'ZH', 'emo_ref_path': None,
                      'emo_weight': 0.65, 'emo_text': '', 'emo_random': False, 'duration_factor': 1.0}
            kwargs.update({'vec'+str(i): 1.0 if vector_index == i else 0.0 for i in range(1,9)})
            start = time.monotonic()
            entry = {'emotion': emotion, 'status': 'requested'}
            try:
                job = client.submit(**kwargs, api_name='/gen_single')
                value = job.result(timeout=180)
                if isinstance(value, (list,tuple)):
                    value=value[0]
                url = value.get('url') if isinstance(value,dict) else value
                if not isinstance(url,str):
                    raise ValueError('Demo returned no audio URL')
                entry.update(get_wav_report(url))
                entry['status'] = 'real_model_audio_generated'
            except Exception as exc:
                entry.update(status='failed', error_type=type(exc).__name__, error=str(exc)[:800])
            entry['elapsed_seconds'] = round(time.monotonic()-start, 2)
            report['samples'].append(entry)
            print('DEMO_SAMPLE', json.dumps(entry, ensure_ascii=False), flush=True)
            if entry['status'] == 'failed':
                break  # Respect quota/access failures: no retries, no alternate identities.
        report['status'] = 'success' if len(report['samples'])==4 and all(x['status']=='real_model_audio_generated' for x in report['samples']) else 'incomplete'
    except Exception as exc:
        report.update(status='blocked', error_type=type(exc).__name__, error=str(exc)[:800])
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat()
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print('DEMO_REPORT',json.dumps(report, ensure_ascii=False),flush=True)
    return 0 if report['status']=='success' else 2

if __name__=='__main__':
    raise SystemExit(main())
