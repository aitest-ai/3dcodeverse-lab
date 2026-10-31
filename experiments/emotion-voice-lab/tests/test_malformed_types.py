import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import voice_studio as vs


class MalformedTypeTests(unittest.TestCase):
    def setUp(self):
        self.line = {"id": "one", "text": "Hello", "emotion": "開心",
                     "language": "en", "strength": 0.6, "speed": 1}

    def test_fields_reject_malformed_json_types_as_value_error(self):
        for field in ("language", "emotion", "text", "strength", "speed"):
            for value in (None, [], {}, True, False):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        vs.validate_line({**self.line, field: value})
        for field, value in (("language", ["en"]), ("emotion", ["開心"]),
                             ("strength", [0.6]), ("speed", [1]), ("text", ["hello"])):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    vs.validate_line({**self.line, field: value})

    def test_malformed_line_and_emotion_vector_raise_value_error(self):
        for value in (None, [], {}, True, "hello"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    vs.validate_line(value)
        for value in (None, [], {}, True):
            with self.assertRaises(ValueError):
                vs.emotion_vector(value)

    def test_malformed_projects_fail_cleanly_before_output(self):
        malformed = [None, [], True, {"character": [], "lines": []},
                     {"character": {"id": "auntie"}, "lines": {}},
                     {"character": {"id": "auntie"}, "lines": [{**self.line, "language": ["en"]}]}]
        with tempfile.TemporaryDirectory() as tmp:
            project, output = Path(tmp) / "project.json", Path(tmp) / "output"
            script = Path(vs.__file__)
            for obj in malformed:
                with self.subTest(project=obj):
                    project.write_text(json.dumps(obj), encoding="utf-8")
                    result = subprocess.run([sys.executable, str(script), "--project", str(project), "--output", str(output)], text=True, capture_output=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("錯誤：", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertFalse(output.exists())

    def test_valid_numeric_strings_and_missing_settings_still_work(self):
        self.assertEqual(vs.validate_line({**self.line, "strength": "0.6", "speed": "1"})["speed"], 1)
        self.assertEqual(vs.validate_line({"id": "one", "text": "Hello"})["language"], "zh")
