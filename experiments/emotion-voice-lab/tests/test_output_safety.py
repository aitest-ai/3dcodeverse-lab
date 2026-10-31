import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import voice_studio as vs
from test_http_integration import sample_wav


class OutputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = Path(__file__).resolve().parents[1] / "cases.json"
        self.reference = self.root / "reference.wav"
        self.reference.write_bytes(sample_wav())

    def run_voice(self, output):
        return vs.run(self.project, output, "vllm", "http://127.0.0.1:8092",
                      reference=str(self.reference))

    def test_repeat_generation_preserves_every_byte_without_api_call(self):
        output = self.root / "v1"
        with patch.object(vs, "generate", return_value=sample_wav()):
            self.run_voice(output)
        before = {p.name: p.read_bytes() for p in output.iterdir()}
        with patch.object(vs, "generate") as generate:
            with self.assertRaisesRegex(ValueError, "輸出路徑已存在"):
                self.run_voice(output)
            generate.assert_not_called()
        self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_plan_cannot_replace_generated_manifest(self):
        output = self.root / "v1"
        with patch.object(vs, "generate", return_value=sample_wav()):
            self.run_voice(output)
        before = (output / "manifest.json").read_bytes()
        for provider in ("plan", "autoip-draft"):
            with self.assertRaises(ValueError):
                vs.run(self.project, output, provider)
        self.assertEqual(before, (output / "manifest.json").read_bytes())

    def test_mid_batch_failure_leaves_no_success_manifest_and_retry_is_safe(self):
        output = self.root / "failed"
        with patch.object(vs, "generate", side_effect=[sample_wav(), ValueError("API failed")]):
            with self.assertRaisesRegex(ValueError, "API failed"):
                self.run_voice(output)
        self.assertFalse((output / "manifest.json").exists())
        self.assertEqual(len(list(output.glob("*.wav"))), 1)
        with patch.object(vs, "generate") as generate:
            with self.assertRaises(ValueError):
                self.run_voice(output)
            generate.assert_not_called()
        with patch.object(vs, "generate", return_value=sample_wav()):
            manifest = self.run_voice(self.root / "retry-v2")
        self.assertEqual(len(json.loads(manifest.read_text())["samples"]), 4)

    def test_existing_empty_directory_and_symlink_are_not_reused(self):
        output = self.root / "empty"
        output.mkdir()
        link = self.root / "link"
        link.symlink_to(output, target_is_directory=True)
        for path in (output, link):
            with self.assertRaises(ValueError):
                vs.run(self.project, path)
        self.assertEqual(list(output.iterdir()), [])
