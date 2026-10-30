# Emotion Voice Studio｜臺灣遊戲與動畫的角色情緒語音原型

狀態：**已建立台詞編輯器、JSON/Manifest 工作流程、IndexTTS-2.5 vLLM API 用戶端與單元測試；尚未在 GPU 或 AutoIP 帳號上實際生成 AI 配音。**

此工具以獨立資料夾提供，之後可以搬移到專屬 repository。**不會修改 3DCodeVerse 的既有機甲、馬匹、GLB 或 Blender 工作流程。**

## 怎麼試？

不用 GPU：下載此資料夾並以瀏覽器打開 studio.html。你可以增加台詞、選擇自然／開心／生氣／悲傷等 9 種情緒、調整強度 0.1–1 和語速 0.75–1.33，匯入／匯出角色台詞 JSON。

「瀏覽器預聽」只使用裝置內建 TTS，**不是 IndexTTS，不能代表真實情緒配音品質**。

離線檢查台詞（Python 3.10+，無須套件、無須 GPU）：

~~~bash
cd experiments/emotion-voice-lab
python3 -m unittest discover -s tests -v
python3 voice_studio.py --provider plan --output outputs/preview
python3 voice_studio.py --provider autoip-draft --output outputs/autoip-draft
~~~

產出的 manifest.json 會列出各角色台詞、情緒及狀態。plan 與 autoip-draft 都**不產生 WAV，也不會扣任何點數**。

## 真正生成 IndexTTS-2.5 WAV

先自行啟動或租用一個符合 [vLLM-Omni 官方 IndexTTS-2.5 部署文件](https://github.com/vllm-project/vllm-omni/blob/main/recipes/IndexTeam/IndexTTS-2_5.md) 的服務。需具 NVIDIA GPU 或能存取 GPU 服務，且持有已取得聲音使用授權的 WAV 參考音檔。

~~~bash
python3 voice_studio.py \
  --provider vllm \
  --project cases.json \
  --reference /private/authorized_reference.wav \
  --api-base http://127.0.0.1:8092 \
  --model IndexTTS-2.5 \
  --output outputs/first-real-voice
~~~

模型名稱必須與你啟動的伺服器一致；某些部署使用模型絕對路徑。此功能依 vLLM-Omni 的 POST /v1/audio/speech 契約發出 WAV 參考聲音、8 維情緒向量、情緒強度、語速及語言，生成 WAV 並記錄 SHA-256。執行時不需要將任何聲音上傳到 GitHub。這是可用的客戶端程式，**但目前未做過真實伺服器端到端測試**。

安全建議：若改用遠端服務，僅能使用 HTTPS，且注意參考錄音會傳送至服務端。不可提交任何含有真人聲音或 API 密鑰的檔案至公開 repo。

## AutoIP 狀態

使用者提供的 2026-10-31 公告確認有 voice_engine=indextts2、emotion、emotion_strength、speed 等參數，但 AutoIP 公開資料尚不足以確認完整 REST URL、認證、音色 ID、非同步工作狀態與音檔取得方式。本工具只能用 autoip-draft 模式產生**待驗證請求草稿**；並不假裝已成功串接。等有完整官方 API 文件再寫真正 adapter。

## 驗收方式

第一輪固定同一句「你怎麼現在才來？我都快收攤了啦！」，測自然、開心、生氣、悲傷四種情緒。使用同一個、已取得授權的參考聲音，讓至少三位聽眾就音色一致、情緒自然、臺灣口音、發音正確四項各評 1–5 分，並記錄成本與生成時間。

中文支援不代表自然臺灣國語，也不代表有臺語能力，不能免除人工試聽。生成結果若將來跨 AI 共用，應儲存在有適當存取權限的音訊儲存服務，透過角色 ID、台詞 ID、版本及 SHA-256 索引；不直接將敏感音檔公開。

## 給其他 AI

閱讀同資料夾的 AGENTS.md、cases.json 與 voice_studio.py。新增角色時，先寫 JSON，再跑單元測試／plan；真實生成經品質驗收後再建立 PR。請勿把計畫、請求草稿或尚未驗證的情緒效果描述為已生成音檔。

## 來源與授權

- IndexTTS 官方程式庫：https://github.com/index-tts/index-tts
- 模型資料：https://huggingface.co/IndexTeam/IndexTTS-2.5
- vLLM-Omni 使用文件：https://github.com/vllm-project/vllm-omni/blob/main/recipes/IndexTeam/IndexTTS-2_5.md
- AutoIP 官方首頁：https://autoip.app/

IndexTTS 模型使用 **bilibili Model Use License**（請自行核對使用條件）；本 PoC 既未附帶模型權重，也未重製上游程式庫。
