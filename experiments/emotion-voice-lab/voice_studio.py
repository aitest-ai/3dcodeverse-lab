#!/usr/bin/env python3
"""跨專案角色情緒語音原型。僅能克隆已獲授權的參考聲音。"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

EMOTIONS = ("happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm")
ALIASES = {"自然": "natural", "開心": "happy", "生氣": "angry", "悲傷": "sad",
           "害怕": "afraid", "厭惡": "disgusted", "憂鬱": "melancholic",
           "驚訝": "surprised", "平靜": "calm"}
LANGUAGES = {"zh", "en", "ja", "es", "ar"}

def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError("無效的角色或台詞 ID")
    return value

def numeric_setting(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(name + "必須為數字")
    try:
        return float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(name + "必須為數字") from exc

def validate_line(raw):
    if not isinstance(raw, dict):
        raise ValueError("每筆台詞必須為 JSON 物件")
    line = dict(raw)
    line["id"] = safe_id(line.get("id"))
    if not isinstance(line.get("text"), str):
        raise ValueError("台詞內容必須為文字")
    line["text"] = line["text"].strip()
    emotion = line.get("emotion", "natural")
    if not isinstance(emotion, str):
        raise ValueError("情緒必須為文字")
    line["emotion"] = ALIASES.get(emotion, emotion)
    line["strength"] = numeric_setting(line.get("strength", 0.6), "情緒強度")
    line["speed"] = numeric_setting(line.get("speed", 1.0), "語速")
    line["language"] = line.get("language", "zh")
    if not 1 <= len(line["text"]) <= 2000:
        raise ValueError("台詞長度必須在 1 到 2000 字元")
    if line["emotion"] not in ("natural", *EMOTIONS):
        raise ValueError("未知情緒")
    if not 0.1 <= line["strength"] <= 1.0:
        raise ValueError("情緒強度超出範圍")
    if not 0.75 <= line["speed"] <= 1.33:
        raise ValueError("語速超出範圍")
    if not isinstance(line["language"], str) or line["language"] not in LANGUAGES:
        raise ValueError("不支援的語言")
    return line

def load_project(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(obj, dict) or not isinstance(obj.get("character"), dict)
            or not isinstance(obj.get("lines"), list)):
        raise ValueError("專案需要角色物件與台詞陣列")
    safe_id(obj["character"].get("id"))
    lines = [validate_line(line) for line in obj["lines"]]
    if not lines or len({line["id"] for line in lines}) != len(lines):
        raise ValueError("需要非空且不重複的台詞 ID")
    return obj["character"], lines

def emotion_vector(emotion):
    if not isinstance(emotion, str):
        raise ValueError("情緒必須為文字")
    key = ALIASES.get(emotion, emotion)
    if key == "natural":
        return None
    if key not in EMOTIONS:
        raise ValueError("未知情緒")
    return [1.0 if e == key else 0.0 for e in EMOTIONS]

def autoip_draft(line):
    """依公告產生請求欄位草稿；不是已驗證的 HTTP API。"""
    line = validate_line(line)
    return {"voice_engine": "indextts2", "emotion": line["emotion"],
            "emotion_strength": line["strength"], "speed": line["speed"],
            "text": line["text"], "language": line["language"]}

def vllm_payload(line, model, wav_bytes):
    line = validate_line(line)
    if wav_bytes[:4] != b"RIFF" or wav_bytes[8:12] != b"WAVE":
        raise ValueError("參考檔必須為 WAV")
    extra = {"lang": line["language"], "text_normalization": True}
    vec = emotion_vector(line["emotion"])
    if vec is not None:
        extra.update({"emo_vector": vec, "emo_alpha": line["strength"]})
    return {"model": model, "input": line["text"], "response_format": "wav",
            "speed": line["speed"], "extra_params": extra,
            "ref_audio": "data:audio/wav;base64," + base64.b64encode(wav_bytes).decode("ascii")}

def generate(api_base, payload):
    if not (api_base.startswith("https://") or
            api_base.startswith("http://localhost:") or
            api_base.startswith("http://127.0.0.1:")):
        raise ValueError("僅接受 HTTPS 或本機 HTTP 語音服務")
    req = Request(api_base.rstrip("/") + "/v1/audio/speech",
                  data=json.dumps(payload).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=180) as response:
        typ = response.headers.get("Content-Type", "")
        if not (typ.startswith("audio/") or typ.startswith("application/octet-stream")):
            raise ValueError("API 回傳的不是音訊")
        wav = response.read(60 * 1024 * 1024 + 1)
    if len(wav) > 60 * 1024 * 1024 or wav[:4] != b"RIFF" or wav[8:12] != b"WAVE":
        raise ValueError("API 未回傳有效 WAV")
    return wav

def run(project, output, provider="plan", api_base="", model="IndexTTS-2.5", reference=""):
    role, lines = load_project(project)
    output = Path(output)
    if provider not in {"plan", "autoip-draft", "vllm"}:
        raise ValueError("未知的服務模式")
    reference_bytes = b""
    if provider == "vllm":
        if not reference or not api_base:
            raise ValueError("vllm 模式需要 --reference 與 --api-base")
        reference_bytes = Path(reference).read_bytes()
        if len(reference_bytes) > 20 * 1024 * 1024:
            raise ValueError("參考音檔超過 20MB")
    # Reserve a fresh run directory atomically before any API request. Never reuse
    # a directory, even for plan mode: it may contain a generated manifest.
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.mkdir()
    except FileExistsError as exc:
        raise ValueError("輸出路徑已存在；請使用新的版本資料夾，既有音訊不會覆寫") from exc
    manifest = {"schema_version": "1.0", "character": role,
                "provider": provider, "samples": []}
    for line in lines:
        entry = dict(line)
        if provider == "plan":
            entry["status"] = "planned_no_audio"
        elif provider == "autoip-draft":
            entry.update({"status": "unverified_request_draft",
                          "request_draft": autoip_draft(line)})
        elif provider == "vllm":
            wav = generate(api_base, vllm_payload(line, model, reference_bytes))
            filename = role["id"] + "__" + line["id"] + ".wav"
            with (output / filename).open("xb") as audio_file:
                audio_file.write(wav)
            entry.update({"status": "generated", "file": filename,
                          "sha256": hashlib.sha256(wav).hexdigest()})
        else:
            raise ValueError("未知的服務模式")
        manifest["samples"].append(entry)
    dest = output / "manifest.json"
    with dest.open("x", encoding="utf-8") as manifest_file:
        manifest_file.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return dest

def main():
    p = argparse.ArgumentParser(description="Emotion Voice Studio PoC")
    p.add_argument("--project", default=str(Path(__file__).parent / "cases.json"))
    p.add_argument("--output", default="outputs/voice-studio")
    p.add_argument("--provider", choices=["plan", "autoip-draft", "vllm"], default="plan")
    p.add_argument("--api-base", default=os.environ.get("VOICE_VLLM_URL", ""))
    p.add_argument("--model", default=os.environ.get("VOICE_VLLM_MODEL", "IndexTTS-2.5"))
    p.add_argument("--reference", default=os.environ.get("VOICE_REFERENCE_WAV", ""))
    args = p.parse_args()
    try:
        print(run(args.project, args.output, args.provider,
                  args.api_base, args.model, args.reference))
        if args.provider != "vllm":
            print("尚未產生真正語音：這是計畫／API 草稿模式。")
        return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print("錯誤：" + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
