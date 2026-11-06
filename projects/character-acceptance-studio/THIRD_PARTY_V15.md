# v15 來源、授權與修改紀錄

日期：2026-11-06（Asia/Taipei）。新增原生動作：aitest-ai 工作流程／Codex 協作，版本 horse-brown-locomotion-review、horse-white-locomotion-review 0.1.0；未從外部不相容骨架套動作、未訓練模型。

直接輸入為 v14 walk-smooth-review 0.1.0，來源 Quaternius CC0 原生 Horse（https://quaternius.com/ ）、aitest-ai Horse Library v2.3.0 的原創 PBR 修改與逐版原生適配。完整來源 URL、原包、作者、素材授權與雜湊保留於 catalog／skeleton-profile／adaptation、`sources-v04/horses/`，並沿用 THIRD_PARTY_V14.md、V13、V12、V11、V10、V04 與 THIRD_PARTY_NOTICES.md。

本版只新增停步姿勢再起步、±15° 行進轉向與控制器。原始拓樸、50 骨層級、母檔、權重、貼圖像素／解析度與 18 段既有 GLB 動作不變；原母檔保留，另寫新 asset ID。新母檔有 21 rig actions＋6 root actions。新增曲線可用 motion-v15 的文字 TRS 與生成程式重現。具體 SHA-256 見 config-v15/horses.lock.json 及各隨包 adaptation.json，修改後另立版本。

Three.js 與附帶 addons：MIT；three-vrm：MIT（延用工作室檢視器依賴；本階段馬匹不使用 VRM）；各原始 LICENSE 與 notices 仍隨 Runtime 交付。本階段沒有新增付費、帳戶限制或模型權重素材。
