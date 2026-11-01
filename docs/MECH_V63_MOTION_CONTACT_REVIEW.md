# 臺北機甲 v6.3｜三款敵機動作、貼地與交會實測

本版本是 v6.2 Draft PR #66 的後續，**獨立 Draft，不動 main、公開網站或前版素材**。

## 真正的 Blender 工程

以 GitHub v6.2 已完成的三款可編輯 BLEND 母檔（Actions Run `41289012052`）做動作品質改善，而不是重做方塊角色。原始 v6.2 的 36 張 Blender Run/Fire/Hit/Dodge 動畫截圖及 BVH 幾何檢查證明：

- Assault、Ranger 的 Run 最深鞋底約 -0.10 m；Heavy 約 -0.168 m。
- Heavy Run 第 7、22 影格存在肩甲／胸甲與盾牌／胸甲的少數三角面交會。
- 舊版 GLB 載入器刪除整條 root.position，**連原本 Run 的 glTF Y-up 垂直接地曲線也刪掉**，導致 Blender 已做的腳底矯正無法用在遊戲中。

`scripts/blender5/mecha_v63_grounded_variants.py` 重新對**每一款所有 48 個 Run 影格**使用真正 Blender 蒙皮實體的最低鞋底高度計算矯正，只更新現有 Run action 的 root local-Y 曲線；重裝型左臂盾牌與肩甲外移 0.15 m，其餘 PBR 貼圖、15 骨架、六動作保留。新檔案名稱 `enemy_{assault,ranger,heavy}_v63.blend` 和對應 GLB，沒有覆蓋 v6.2 原始母檔。

修正後 48 影格 Run 最低鞋底：Assault +0.00700m；Ranger +0.00700m；Heavy +0.00608m。Heavy 原本交會的兩組零件在 Run 7/22/38 抽樣全部 BVH **0 次三角面交會**。這是局部幾何驗證，不代表全部姿勢或 Windows WebGPU 遊玩通過。

- 真正 Blender 36 張原始動態取樣：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41291600781
- 真正 Blender 新 3 套母檔、GLB、12 張動作預覽：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41292456661

## 程式整合

- `examples/threejs/mech-root-motion-v63.js`：保留 `root.position.y` 垂直接地動畫，只將 glTF `root.position.x/z` 設回原值，不與 OSM 控制器重複位移。遇無效 root track 保守拒絕。
- `examples/threejs/mech-enemy-action-v63.js`：Fire 僅在 **真實射擊事件** 時播放一次，預警期間不會假開火；真實 HP 降低才觸發 Hit，最後返回 Run/Idle。
- `examples/threejs/mech-enemy-glb-v63.js`：使用 `SkeletonUtils.clone` 複製真骨架，優先載入 v6.3 新 GLB，失敗退回 v6.2 高品質 GLB；兩者都失敗才保留原本程序化敵機。複製實體於關卡清除時真正卸載，不修改 AI／碰撞／HP／世界位置。
- 完整 Windows 整合包另有 `mech-combat.js` 與 `patch_slop.py`，不會把整個第三方 Slop Taipei 原始碼混進此資產倉庫。

Node 22 GitHub Actions：https://github.com/aitest-ai/3dcodeverse-lab/actions/runs/41292923771 已成功。完整 Windows ZIP 的 Python/Node 隔離回歸測試 **63／63 PASS**，但不等於 Windows WebGPU／真實 GPU FPS、五分鐘臺北 101 戰鬥或全部穿模驗收。

## 下次最重要的人工驗收

在真實 Windows Chrome／Edge 開啟完整 3D 臺北城市，從臺北 101 三波防衛開始，錄製重裝型靠近胸甲的左肩／盾牌於 Run、Fire、Hit、Dodge 下的角度。測試斜坡、橋下、路緣及側閃；FPS、記憶體與 GPU 只記錄實際可測量的數字，不推估。現階段沒有更新公開遊戲網頁，也沒有自動合併任何 PR。
