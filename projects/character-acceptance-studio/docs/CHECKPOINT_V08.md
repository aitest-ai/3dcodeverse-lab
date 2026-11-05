# 交接點 0.8.0 · 2026-11-05（臺北時間）

本輪接續 Draft PR #152 固定提交 `36547a2349caebd6ae1d04e13ebbb5055479572f`，獨立分支 `feat/character-studio-v08-vita-transitions-20261105`。僅新增 v08 檔案，保留所有舊母檔、版本與 main，不合併或部署任何網站。入口：[README_V08.md](../README_V08.md)。

## 成果

Vita `vroid-vita-motion-review / 0.2.0` 補齊 Start／Stop／TurnLeft／TurnRight。既有 Idle／Walk／Run 的 JSON 軌與全部舊 BIN 精確保留，原網格、155 joints、蒙皮、貼圖與 VRM metadata 不改。新版 SHA：`73810ed0414c723da46dd74dfe227b4c1aec83e4321a6cd0eda0a7ec5f7e7194`。Vivi 0.3.0 完全不改。

Start／Stop 以各角色自己的步幅與鞋底點重解 IK，骨盆高度從 Idle 的腿長 0.99 比例混合到前版 Walk 的相位曲線；不把 Vivi 的局部軌搬過來。轉身用 heading-aware 軸向修正，最後 15% 回到完整 Idle 姿勢。Idle 已含手指／衣片修正，必須在修正後才 settle，不得再次疊加手指彎曲。

網頁改為每個版本從自己的 GLB 提取 root clips，消除共用 Vivi 步幅的隱患。Vita 一個 Walk 週期約 0.764 m、Vivi 約 0.600 m。根位移與朝向在獨立父節點累積；不要改 AnimationMixer 擁有的根軌。前版 Vita 沒有新增片段，選它們或連續流程會切至新版單角色；不以參考姿勢冒充修改前動作。

## 證據與重現

四段新增動作共 804 個實際 Chromium／SwiftShader 120 Hz 樣本，含鍵格間取樣。最小鞋底高度約 2.08 mm，最大接觸漂移約 3.07 mm；軀幹最大前傾約 3.36°。指定衣片／腿部與手部 Skin proper crossing 為零，原指甲嵌合分開處理。這不是全身、衣物厚度、自碰撞或美術通過。

兩位角色起停與轉身流程的 22 個全網格接縫測試包含第三循環及第四輪重啟；實際根位移持續累積。冷開 Blender 對照、重新匯出、幾何修改拒絕、固定 ID／版本／SHA 與覆蓋拒絕都有獨立證據。136 張實際瀏覽器連續畫面與 2 段 WebM；以 ffprobe 編碼時長為準，軟體繪圖會掉格。見 `evidence-v08/acceptance-summary.json`。

初次生成在 metadata 寫入時遇到 `h` 名稱被校準數值覆蓋，已修正。網格和動作當時已匯出；完整修正版的可重建性以乾淨套件重建另外核對，見 `deliveries/verification-v08.json`，不可只據第一次程序中斷便聲稱重建完成。

Blender 5.2.3 LTS e13b728c6880、4 CPU quota／16 GiB、無 GPU。Runtime 含兩位角色與檢視程式；Vita Sources 含本輪所有直接輸入，Vivi Sources 保留可編輯母檔、原 VRM／貼圖。較早完整生產鏈留在各前版固定提交；沒有把本輪包裝成全部舊分支的混合版本。

## 下一步

先由使用者／美術檢視 Vita 的起停步態、轉向手肘與衣片輪廓；可用網頁輸出逐格觀察 JSON。程式檢查不代替人工美術核准。後續可沿用既有柴犬／馬做動物接地與轉向擴充，使用自己的四足相位、脊椎／足端語意，不搬人體雙足規則。

手機真機、Godot／地圖、任意速度混合、地形接地、完整衣物碰撞未測；全部 `art_approved=false`、`game_ready=false`。原台灣 V29–V31、基隆河 V110／V111 與彩虹橋盤點缺口保留，沒有回退 V103。20 款候選與既有動物原檔完整保留。
