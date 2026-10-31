# Emotion Voice Studio｜跨 AI 交接規範

1. 先閱讀 README.md 與 cases.json；保持角色 ID、台詞 ID 唯一。
2. 本原型只是角色語音管線。plan、autoip-draft 不產生音檔，不得描述成已完成真正語音。
3. vllm 模式需要已啟動的 IndexTTS-2.5 服務和取得授權的 WAV；不得擅自使用真實人物聲音。
4. 不提交聲音檔、原始人聲、個資、金鑰或模型權重至公開 GitHub。
5. 新增角色後先執行 python3 -m unittest discover -s tests -v，與 python3 voice_studio.py --provider plan。
6. 新角色先建立分支、測試、PR，再合併；不可覆寫既有音訊檔案，使用全新 ID。
7. AutoIP 目前只確認公告中顯示的參數，完整 API URL、認證、工作狀態和音色 ID 待官方文件驗證後才接入。
8. 面向臺灣遊戲和教學，需讓聽眾檢查臺灣語氣、地名、發音與情緒是否一致。
9. 音訊輸出應搭配 manifest、SHA-256、授權聲明與人工驗收紀錄，在私有儲存空間共享；公開 repo 僅存程式與非敏感 metadata。

## 使用者於 2026-10-31 明確限制：繼續測試，但不要用到付費

- 本次與延續的語音重測以零新增費用為硬限制，除非使用者之後明確改變授權。
- 不啟動 Hugging Face Jobs、Inference Endpoints、租用 GPU、AutoIP 點數或其他付費 API；不購買訂閱／額度。
- 公開 ZeroGPU 示範使用明確匿名的 token=False，不讓已登入付費帳號的預付點數自動接手。
- 使用同一官方服務與身分；遇額度、權限、逾時等錯誤即停止，不能換帳號或服務繞過額度。
- GitHub 僅使用已確認公開儲存庫的標準 ubuntu-latest runner。不要新增 artifact、快取或付費大型 runner。
- free_retest.py 一次最多 6 次生成；工作流程另加整體程序硬逾時。不得在沒有新授權時自行排程重試。
- 測試或流程通過不代表情緒通過。舊 happy 音檔已被使用者評為「仍像生氣」，在新一輪盲聽完成前不得改成合格。
- 正式結果必須區分：計畫、模擬測試、真正生成、成功取回、聽感驗收。不能把未拿到的音檔描述成已完成。
