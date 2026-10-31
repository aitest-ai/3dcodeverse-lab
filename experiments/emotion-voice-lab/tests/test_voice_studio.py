import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import voice_studio as vs


class VoiceStudioTest(unittest.TestCase):
    def setUp(self):
        self.line = {"id": "case_01", "text": "你好！", "emotion": "開心",
                     "strength": 0.65, "speed": 1.0, "language": "zh"}

    def test_vector(self):
        self.assertEqual(vs.emotion_vector("happy"), [1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(vs.emotion_vector("calm"), [0, 0, 0, 0, 0, 0, 0, 1])
        self.assertIsNone(vs.emotion_vector("natural"))

    def test_validation(self):
        self.assertEqual(vs.validate_line(self.line)["emotion"], "happy")
        for change in ({"id": "../unsafe"}, {"strength": 1.5},
                       {"speed": 2}, {"emotion": "other"}, {"language": "tw"}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    vs.validate_line({**self.line, **change})

    def test_autoip_is_only_a_draft(self):
        draft = vs.autoip_draft(self.line)
        self.assertEqual(draft["voice_engine"], "indextts2")
        self.assertNotIn("url", draft)
        self.assertEqual(draft["emotion"], "happy")

    def test_vllm_payload(self):
        with tempfile.TemporaryFile() as file:
            with wave.open(file, "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(22050)
                out.writeframes(b"\x00\x00" * 200)
            file.seek(0)
            audio = file.read()
        payload = vs.vllm_payload(self.line, "IndexTTS-2.5", audio)
        self.assertEqual(payload["extra_params"]["emo_vector"][0], 1)
        self.assertEqual(payload["extra_params"]["emo_alpha"], 0.65)
        self.assertTrue(payload["ref_audio"].startswith("data:audio/wav;base64,"))
        natural = vs.vllm_payload({**self.line, "emotion": "natural"}, "model", audio)
        self.assertNotIn("emo_vector", natural["extra_params"])

    def test_plan_never_generates_fake_audio(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(__file__).resolve().parents[1] / "cases.json"
            output = Path(tmp) / "out"
            manifest = vs.run(project, output, "plan")
            result = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(len(result["samples"]), 4)
            self.assertTrue(all(x["status"] == "planned_no_audio" for x in result["samples"]))
            self.assertEqual(list(output.glob("*.wav")), [])


if __name__ == "__main__":
    unittest.main()
