# 交接點 0.9.0 · 2026-11-05（臺北時間）

本輪接續 Draft PR #154 固定提交 `454be2fcf9a18ece5a8077351a4a5d9b3cf79489`，分支 `feat/character-studio-v09-quadruped-review-20261105`。僅新增 v09 路徑；不改 main、既有母檔、原有工作室、馬匹正式 registry／Release 或任何其他網站。

## 已完成

- 柴犬 `quaternius-shibainu-grounded-review / 0.2.0`，SHA `922427fae1ced358766e21c3cf1d9a0f78602c5aacbc739db7580e32d9b2cbff`；新增 WalkTurnLeft／WalkTurnRight，四個 Walk 週期走 90° 弧線，半徑約 0.917 m。12 段舊 GLB 動畫、網格、蒙皮、材質、骨長與全部舊 BIN 精確保留。
- 原生 46 joints，前腿二鏈／後腿四鏈 IK；沿用四足自己的相位，世界支撐點固定。支撐期 IK／FF 採原 Idle 足掌朝向，擺動期平滑回原生姿勢。最初只鎖足掌中心，邊緣仍滑約 7.4 mm，已淘汰並另記，沒有當成成品。
- A 是本輪只轉根節點的試作（未通過），不是原作者／前版已發行的轉向。A/B 各有可編輯五段 FK 母檔；其他九段原生動作需用另附的原生母檔編輯。
- 馬沿用棕／白 2.3.0 原檔，50 joints、13 clips，沒有新增馬或更動原版。母檔沒有原生 IK 約束，不能直接套柴犬。納入同場播放、足底高度與循環診斷，按鈕可跳到最低蹄面。
- 新馬診斷 profile 區分首鍵時間、末鍵時間與鍵跨度；Three.js duration 是末鍵時刻，包含首鍵前停留，舊 profile 的時間跨度不能當整個播放時間軸。

## 驗證

柴犬兩段新增動作各 513 個 120 Hz 實際瀏覽器樣本（A/B 各 1026）。支撐中心最大漂移約 51.3 → 0.155 mm；足掌邊緣由約 58.2 → 2.614 mm，未宣稱零滑。足底未穿地；第四個四分之一圓結束到下一輪的全網格接縫通過。

兩馬 Idle／Walk／Gallop 120 Hz 診斷；另外十段每匹只做 12 Hz 播放預覽，不冒充步態驗收。顯示設定下，Walk 最低約 -10.98 mm（FrontR，0.6333 s），Gallop 最低約 -15.11 mm；Gallop 全網格首尾差約 135.68 mm。這些是保留原檔上的已知失敗。原地動畫沒有校準速度或世界根位移，腳滑尚未評定。

Blender 冷開 A/B 曲面對照、實際瀏覽器全原生身體頂點探測、動作匯出與幾何修改拒絕各列證據。馬 Blender 對照僅為臨時權重同步工作副本的身體首格，沒有改馬母檔或宣稱全部毛髮逐格一致。124 張實際瀏覽器連續畫面、柴犬與棕馬各一段 WebM；實際編碼時長見 ffprobe。人工美術、手機真機、Godot／地圖、完整自碰撞未測。

## 交付與延續

[README_V09.md](../README_V09.md) 是操作／重現入口。Runtime 有三個動物與瀏覽器；Sources 有完整本輪直接輸入、原生母檔、貼圖、授權與雜湊。Blender 5.2.3 LTS e13b728c6880，4 CPU quota、16 GiB、無 GPU；Chromium + SwiftShader。兩份 ZIP 全新解壓後，Blender 重建 A/B GLB 與交付檔 SHA 完全一致；獨立 localhost 的三模型、下載、操作、診斷跳轉及錯誤重試實測通過，見 evidence-v09/clean-rebuild.json 與 delivery-smoke.json。不可把程式測試說成人工核准。

下一步修馬：先核對 Gallop 首鍵偏移與原生各骨尾鍵，在新 ID／版本的工作副本重建適合馬骨長與關節方向的求解器，逐蹄修正後再烘焙；不能只把根節點提高來掩蓋穿地。保留原材質、拓樸、母檔與已發行 2.3.0，不更新正式 registry／Release，先出驗收候選。柴犬後續需起停／直走轉向銜接及美術檢視。

全部 `art_approved=false`、`game_ready=false`。台灣衣物、基隆河 V110／V111 和彩虹橋最新來源缺口沿用原盤點，沒有回退 V103。
