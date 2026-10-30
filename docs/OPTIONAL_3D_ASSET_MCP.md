# 選配：其他 AI 共用的跨網站 3D 資產搜尋（3D Asset Server MCP）

來源：[arielshad/3d-asset-server](https://github.com/arielshad/3d-asset-server)，Apache-2.0 的開源搜尋伺服器，提供 REST API、MCP。此文件只是**可選連接方式**：沒有在本 GitHub 儲存庫自動安裝，也沒有替使用者連接第三方帳號。

## 有什麼用

同一個 AI 可以搜尋 Poly Haven、ambientCG、Kenney、BlenderKit 等不同來源，顯示物件類型、價格、授權、是否能下載及格式。網站目前表示共搜尋約 26 個資源站；每個回傳模型仍須確認原來源授權，不能因為搜尋工具本身是 Apache-2.0 就把所有搜尋結果視為 CC0。

- 服務端：https://3d.shep.bot
- REST 參考：https://3d.shep.bot/docs/api/reference
- MCP 設定：https://3d.shep.bot/docs/mcp

## 其他 AI 如要啟用，請使用者在它們自己的開發環境執行

Claude Code 使用者（自行決定是否連接外部伺服器）：

```bash
claude mcp add --transport http 3d-assets https://3d.shep.bot/mcp
```

Codex CLI 配置方式（使用者自行編輯 `~/.codex/config.toml`）：

```toml
[mcp_servers.3d-assets]
url = "https://3d.shep.bot/mcp"
```

其他工具請參考該服務的 MCP 官方文件。**本專案不自動覆寫你的任何 MCP 設定**，也不向這個第三方服務傳送私有程式碼、存取權杖或未公開模型。

## 讓 AI 找素材時的安全驗收

1. 優先要求 **CC0** 來源，並列出原始連結與許可證。
2. 先顯示搜尋結果，不要直接批次下載。確認必要時才取得檔案。
3. 下載之後先檢查附帶的 `README`、授權、檔案類型及壓縮包內容，不能自動執行不明腳本。
4. 對圖片轉 3D、掃描模型或人類角色，還要檢查人物肖像／隱私及素材的商用權限。
5. 必須將檔案來源、作者、授權、下載日期寫進 `asset_manifest.json` 或伴隨的 `source_license.json`。
6. 匯入 Blender，跑本庫 `scripts/assets/glb_quality_report.py`、既有 glTF validator 與視覺驗收。
7. 資產真正下載或安裝之前，不得聲稱已成為本地／GitHub 模型庫的一部分。

## 為何不在 GitHub 直接綁定遠端 MCP？

GitHub Actions 目前只需要最小唯讀權限，以及品質檢查所需的 CPU。遠端 MCP 搜尋服務是另一家營運的網路端點，其可用性、記錄與回傳資料都需另外評估。為了安全，保留**由個別 AI 工具使用者明確啟用**的選擇，不會把外部服務偷偷加入所有機器人的工作階段。
