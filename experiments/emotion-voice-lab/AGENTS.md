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
