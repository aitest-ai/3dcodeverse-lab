# REA 安裝與實際執行

## 環境與安裝

- Node.js `v24.22.1`、npm `11.9.0`，符合檢查當時官方 main README 的 Node 24.x 最低要求。
- 來源：https://github.com/morluto/rea；npm 官方包 `rea-agents`。
- 首次 `npx --yes rea-agents setup --help` 取得 CLI；接著 `setup --client codex --dry-run --format json` 先檢查計畫。
- 安裝計畫只為 Codex 增加 REA MCP 註冊與 matching skill，保留其他設定，並提出原設定的 backup path。使用者明確授權後，本次執行：

```sh
npx --yes rea-agents@6.8.0 setup --client codex --yes --format json
npx --yes rea-agents@6.8.0 doctor --client codex --json
```

`rea-setup-result.json` 的 status 為 `ready`，appliedActions 為 `configured_codex`、`installed_skill`。Doctor 的 Codex registration 與 skill 均為 `aligned`，CLI package 6.8.0、skill version 49。官方 main 的技能版本較新，不能把 main 能力當成已安裝版本具備的工具。

安裝實際修改本工作環境 `/home/agent/.codex/config.toml` 並安裝 `/home/agent/.agents/skills/reverse-engineer-anything`。這是本次使用者明確授權的 setup 範圍，不代表改動使用者自己的桌面 Codex、帳號全域設定或其他未附加環境。

## MCP 與 CLI 的區別

本對話的工具清單不支援由 shell setup 後熱載入新 MCP，也沒有可用的對話 host 重啟工具。Doctor 的 `live_server.state=unknown`；因此沒有宣稱本對話已成功用 MCP 呼叫。若在自己的 Codex CLI 開新 session，需保留 npx cache 與設定，再重新連接 REA MCP。

本次採使用者已授權的**官方 CLI fallback**完成真實呼叫，不需要為繼續工作而等待重啟。沒有安裝 Hopper、Ghidra、IDA 或 Kuna；Doctor 的 `environment_healthy=false` 反映 native provider 未配置，並不表示以下內建靜態工具失敗。

## 真實呼叫

```sh
npx --yes rea-agents@6.8.0 inspect-artifact /absolute/path/KochiGame_GirlFishing.zip \
  --detail summary --evidence_output /new/path/rea-kochi-bundle --format json
npx --yes rea-agents@6.8.0 inspect-desktop-application /absolute/path/Windows --format json
npx --yes rea-agents@6.8.0 inspect-pe-imports /absolute/path/GirlFishing-Win64-Shipping.exe \
  --max-file-bytes 180000000 --format json
```

ZIP 原始 Evidence ID：`ev_4b819fb1bcd148aa9cadf6adfb6f21d23c4d9e9c6cdaa9f595b5516ea8188d6b`。摘要 projection 是另一個 ID，不應混為同一 operation。

PE 匯入 Evidence ID：`ev_c476dd9cdd24b59a3b7ea7d9448efefc70a7e40015df4d7ac0fdce42d2670da2`。PE SHA-256 與手動版本字串分析一致。

PE 操作首次因預設 64 MiB read budget 拒絕 152 MB EXE；依明確 remediation 與官方 CLI help 提高到 180,000,000 bytes 後完成。首次錯誤保留 `evidence/rea-pe-imports-initial-limit.json`；成功結果保留 `evidence/rea-pe-imports.json`。

REA `inspect-desktop-application` 在檔案證據中識別 Unreal 封裝。專用 retoc 另行處理 IoStore info/list，兩者職責不混用；REA 沒有被當成 Blender、FBX、骨架或拓樸編輯器。

## 未完成能力

本對話 MCP live invocation 未測；native pseudocode/assembly deep provider 未配置；原作 Oodle 壓縮 chunk 尚無可用解析鏈。未執行遊戲、記憶體掛鉤、DRM／加密繞過或下載專有 codec。完整已知限制見原作研究報告。
