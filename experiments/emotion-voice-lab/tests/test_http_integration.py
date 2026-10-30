"""真正的 HTTP 端對端模擬：API 收到請求→WAV 回應→manifest 與 SHA256。無需 GPU。"""
import base64
import hashlib
import json
import sys
import tempfile
import threading
import unittest
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import voice_studio as vs


def sample_wav():
    buffer = BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(22050)
        writer.writeframes(bytes(22050 * 2 // 10))
    return buffer.getvalue()


class FakeSpeechHandler(BaseHTTPRequestHandler):
    received = []
    def do_POST(self):
        if self.path != "/v1/audio/speech":
            self.send_error(404)
            return
        n = int(self.headers["Content-Length"])
        if n > 1024 * 1024:
            self.send_error(413)
            return
        data = json.loads(self.rfile.read(n).decode())
        self.__class__.received.append(data)
        wav = sample_wav()
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(wav)))
        self.end_headers()
        self.wfile.write(wav)

    def log_message(self, *args):
        pass


class EndToEndMockTests(unittest.TestCase):
    def test_four_lines_reach_http_endpoint_and_save_valid_wav(self):
        FakeSpeechHandler.received = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeSpeechHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                reference = root / "reference.wav"
                reference.write_bytes(sample_wav())
                project = Path(__file__).resolve().parents[1] / "cases.json"
                out = root / "results"
                manifest = vs.run(project, out, provider="vllm",
                                  api_base="http://127.0.0.1:" + str(server.server_port),
                                  reference=str(reference))
                data = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertEqual(len(data["samples"]), 4)
                self.assertEqual(len(FakeSpeechHandler.received), 4)
                expected = ["natural", "happy", "angry", "sad"]
                for i, (entry, payload) in enumerate(zip(data["samples"], FakeSpeechHandler.received)):
                    self.assertEqual(entry["emotion"], expected[i])
                    self.assertEqual(entry["status"], "generated")
                    audio = (out / entry["file"]).read_bytes()
                    self.assertEqual(entry["sha256"], hashlib.sha256(audio).hexdigest())
                    self.assertTrue(audio.startswith(b"RIFF"))
                    self.assertEqual(payload["input"], "你怎麼現在才來？我都快收攤了啦！")
                    self.assertTrue(payload["ref_audio"].startswith("data:audio/wav;base64,"))
                    decoded = base64.b64decode(payload["ref_audio"].split(",", 1)[1])
                    self.assertEqual(decoded, reference.read_bytes())
                    if expected[i] == "natural":
                        self.assertNotIn("emo_vector", payload["extra_params"])
                    else:
                        self.assertEqual(sum(payload["extra_params"]["emo_vector"]), 1.0)
                        self.assertEqual(payload["extra_params"]["emo_vector"][vs.EMOTIONS.index(expected[i])], 1.0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

    def test_refuses_invalid_remote_http_address(self):
        with self.assertRaises(ValueError):
            vs.generate("http://example.org", {})

    def test_http_server_non_audio_is_rejected(self):
        class BadHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = b'{"error":"wrong model"}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), BadHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaises(ValueError):
                vs.generate("http://127.0.0.1:" + str(server.server_port), {"input": "Hello"})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
