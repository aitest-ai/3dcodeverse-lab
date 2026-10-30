# Emotion Voice Studio｜角色情緒語音工作室

**2026-10-31 狀態：已從官方 IndexTTS-2.5 示範服務實際取得自然、開心、生氣三段人聲。第四段悲傷遇到免費額度限制。AutoIP API 與自架 vLLM 仍未完成真實產音驗證。**

請先閱讀 [真實測試報告](reports/2026-10-31-evaluation.md)。不要把單元測試通過，或 plan／autoip-draft，描述成真實人聲生成。

## 離線台詞編輯器

下載整個資料夾，以瀏覽器開啟 `studio.html`。`studio-data.js` 必須在同一資料夾。支援台詞、情緒、強度、語速及語言設定，以及 JSON 匯入／匯出。匯入會保留授權與自訂 metadata；不支援或格式錯誤的資料會被拒絕，不會默默改寫。

「瀏覽器預聽」只是裝置 TTS，不是 IndexTTS，也不會套用情緒。實測三段配音已另行交付使用者，不存放於公開 Git。

## 不需 GPU 的測試

```bash
cd experiments/emotion-voice-lab
python3 -m unittest discover -s tests -v
node --test tests/studio-data.test.js
python3 voice_studio.py --provider plan --output outputs/preview-v1
python3 voice_studio.py --provider autoip-draft --output outputs/autoip-v1
```

目前為 16 項 Python 測試與 6 項 Node 測試。plan 與 autoip-draft 不產生 WAV，不呼叫付費服務。

**輸出路徑必須是尚不存在的全新資料夾。** 即使只是 plan，也不能覆蓋先前的 manifest。重試時換用 `outputs/preview-v2` 等新版本。批次中斷會保留已完成的音檔，但不寫成功 manifest。

## 自架 vLLM 用戶端

依 [vLLM-Omni 官方部署文件](https://github.com/vllm-project/vllm-omni/blob/main/recipes/IndexTeam/IndexTTS-2_5.md) 啟動相容服務，並準備已獲明確授權的 WAV 參考音檔：

```bash
python3 voice_studio.py \
  --provider vllm \
  --project cases.json \
  --reference /private/authorized_reference.wav \
  --api-base http://127.0.0.1:8092 \
  --model IndexTTS-2.5 \
  --output outputs/first-run-v1
```

模型名稱必須與伺服器一致。遠端服務僅使用 HTTPS。參考聲音會傳送至你設定的服務；勿將私人錄音或金鑰提交到 Git。此用戶端目前通過 mock HTTP 測試；官方 Gradio demo 的成功不能冒充此路徑也已實測。不同部署的語言範圍仍需核對，介面可選不代表每個後端都已驗證。

## 官方示範服務的真實測試

`probe_official_demo.py` 使用 `gradio_client==2.0.3`，僅取服務內建範例聲音，固定同一句話與語速，最多四次合成；遇到額度／存取錯誤即停止，不改帳號或 IP。這不是正式批次配音服務。

```bash
python3 -m pip install gradio_client==2.0.3
python3 probe_official_demo.py --output demo-probe-report.json
```

本次已完成三段，完整紀錄在測試報告。示範聲音的正式角色／商用權利尚未確認，只作功能評估；未完成臺灣口音與情緒自然度的人工驗收。

## AutoIP

公告提供 `voice_engine=indextts2`、`emotion`、`emotion_strength`、`speed`。完整 REST endpoint、認證、voice ID、工作狀態及取得音檔流程尚待官方文件核對。目前 `autoip-draft` 只有待驗證欄位草稿，不會送出請求，也不扣點。

## 跨 AI 協作

先讀 [AGENTS.md](AGENTS.md)。保持角色與台詞 ID 唯一，產音使用新的版本資料夾；原始聲音、生成音訊、權重與金鑰不得提交公開 Git。新增模型或角色必須記錄授權、版本、SHA-256 與人工評分，從獨立分支／PR 提交，不修改本庫機甲、馬匹或 Blender 工作流程。

本工具可日後獨立成另一個 repository，目前保留於 PR #33 分支，不代表已合併或正式上線。

## 來源

- [IndexTTS 官方倉庫](https://github.com/index-tts/index-tts)
- [IndexTTS-2.5 模型卡](https://huggingface.co/IndexTeam/IndexTTS-2.5)
- [官方示範服務](https://huggingface.co/spaces/IndexTeam/IndexTTS-2.5-Demo)
- [AutoIP](https://autoip.app/)

模型授權與參考聲音權利須分別核對。本庫不附帶上游模型權重。
