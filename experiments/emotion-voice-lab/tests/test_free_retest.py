"""Offline safety regressions. No network, GPU, synthesis or paid storage."""
import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import free_retest as mod

class Job:
    def __init__(self,value=None,error=None): self.value=value; self.error=error; self.cancelled=False
    def result(self,timeout=None):
        if self.error: raise self.error
        return self.value
    def cancel(self): self.cancelled=True

class FakeClient:
    def __init__(self,quota_error=False): self.calls=[]; self.quota_error=quota_error; self.jobs=[]
    def submit(self,**kwargs):
        self.calls.append(kwargs)
        if kwargs['api_name']=='/on_example_click': return Job([mod.BASE+'/example.wav'])
        job=Job(mod.BASE+'/sample.wav',RuntimeError('You have exceeded your ZeroGPU runs limit') if self.quota_error else None)
        self.jobs.append(job)
        return job

class Reference(io.BytesIO):
    url=mod.BASE+'/example.wav'

class FreeRetestTests(unittest.TestCase):
    def setUp(self):
        self.plan=ROOT/'cases_happy_retest_v1.json'
        self.lines=json.loads(self.plan.read_text(encoding='utf-8'))['lines']
    def run_mock(self,fail=False,reference_error=False):
        client=FakeClient(fail); captured={}
        def factory(*args,**kwargs): captured.update(kwargs); return client
        helper=types.SimpleNamespace(file_url=lambda x:x,get_wav_report=lambda x:{'sha256':'mock-only','audio_url':x})
        gradio=types.SimpleNamespace(Client=factory,handle_file=lambda x:x)
        with tempfile.TemporaryDirectory() as d, patch.dict(sys.modules,{'probe_official_demo':helper,'gradio_client':gradio}), contextlib.redirect_stdout(io.StringIO()):
            with patch.object(mod,'urlopen',side_effect=OSError('offline') if reference_error else None,return_value=Reference(b'public-example-only')):
                report=mod.evaluate(self.plan,Path(d)/'report.json',client_factory=factory)
        return report,client,captured
    def test_strength_and_speed_controls(self):
        for line in self.lines:
            kwargs=mod.request_fields(line)
            self.assertEqual(kwargs['emo_weight'],line['strength'])
            self.assertEqual(kwargs['duration_factor'],1.0)
            self.assertFalse(kwargs['emo_random'])
        self.assertEqual(mod.request_fields(self.lines[0])['vec1'],1.0)
    def test_invalid_controls_rejected(self):
        for delta in ({'strength':float('nan')},{'strength':1.1},{'speed':0.9},{'emotion':'other'},{'text':''}):
            with self.subTest(delta=delta),self.assertRaises(ValueError): mod.request_fields({**self.lines[0],**delta})
    def test_anonymous_no_billing_credentials(self):
        report,client,kwargs=self.run_mock()
        self.assertIs(kwargs['token'],False)
        self.assertEqual(kwargs['max_workers'],1)
        self.assertFalse(report['billing_credentials_used'])
        self.assertFalse(report['paid_gpu_job_started'])
        self.assertFalse(report['autoip_called'])
        self.assertEqual(report['artifact_uploads'],0)
        self.assertEqual(report['successful_audio_count'],6)
    def test_first_quota_error_stops_all_later_requests(self):
        report,client,_=self.run_mock(True)
        self.assertEqual(len(client.jobs),1)
        self.assertTrue(client.jobs[0].cancelled)
        self.assertEqual(report['status'],'blocked')
        self.assertEqual(len(report['skipped']),5)
        self.assertEqual(report['automatic_retries'],0)
    def test_reference_failure_does_not_generate(self):
        report,client,_=self.run_mock(reference_error=True)
        self.assertEqual(len(client.jobs),0)
        self.assertEqual(report['status'],'blocked')
    def test_refuses_overwrite_before_any_call(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'report.json'; output.write_text('existing')
            with self.assertRaises(FileExistsError): mod.evaluate(self.plan,output)
            self.assertEqual(output.read_text(),'existing')

if __name__=='__main__': unittest.main()
