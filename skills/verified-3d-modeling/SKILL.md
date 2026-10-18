---
name: verified-3d-modeling
description: Reproducible code-first 3D modeling with measurement, multi-view inspection and issue-specific repair.
---

# 可驗證 3D 建模 Skill（自建版）

本文件供 Coding Agent 與開發者閱讀，不是官方 3DCodeVerse Harness，也**不會自動安裝成 ChatGPT 系統的永久技能**。

## 程序

1. 明確寫出目標、參考照片、尺寸單位、座標軸、可接受誤差及使用場景（瀏覽器、列印、動畫）。
2. 規劃可獨立修改的零件與名稱；用固定尺寸參數而非散落的數值。
3. 使用 Three.js / Blender Python / CadQuery 等生成真正的 3D 幾何與可重跑的原始碼。
4. 從幾何資料進行數值驗收：包圍盒、接地、貼牆、零件接合、穿透、物件間距及關節角度（適用時）。
5. 從正、側、後及俯視等角度渲染，檢查遮擋、材質、法線、比例、燈光及外觀。若涉及真實建築，必須與可信參考資料比對。
6. 對失敗項目明確標記、局部修復，再執行相同測試；留下修復前後差異。
7. 交付程式、模型（例如 GLB/STEP）、驗證 JSON、多視角預覽及重現指令。通過若干規則，不代表所有物理與視覺問題都解決。

## 整合官方 Harness

如果環境已成功安裝官方 3DCodeVerse，優先以 `3dcodeverse doctor` 確認環境，再依其 `harness/docs/INSTALL.md`、`RUNBOOK.md` 執行實際 agent loop 與評估。

切勿聲稱只用 CadQuery 產出模型就等同官方的 Planner、VLM Judge 或多代理自動修正。若無法執行真正的官方 Harness，報告必須寫「獨立方法測試」。

## 安全與資料

避免把密鑰、商業授權資料集或敏感學生資料上傳公開 GitHub。外部資料與開源依賴先確認授權。
官方來源：https://github.com/gaoypeng/3dcodeverse
