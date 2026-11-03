# KochiGame 檔案清單與引擎判定

本報告只靜態讀取可存取的資料；沒有啟動任何參考遊戲 EXE、腳本或 DLL。原 ZIP、解壓內容及影片不加入原創遊戲或 GitHub。

## 驗證結果

- ZIP：`KochiGame_GirlFishing.zip`，465,170,862 bytes。
- SHA-256：`b971e5f70a58b1a53c2b981e49a73efc4e1e9e90f4ae344c442c67c1d0971997`。
- 402 個目錄／檔案項目；總解壓 738,716,909 bytes。
- 檢查 ZIP 路徑、Windows drive 前綴、`..`、符號連結、加密旗標、單檔／總大小與壓縮比。通過後才解壓；每個成員在讀取解壓時由 zipfile 驗證 CRC。
- 未遇到加密 ZIP 或加密 IoStore 旗標；未提供或嘗試猜測任何金鑰。
- 附件下載工具上限 32 MiB，Drive 連接器上限 256 MiB，兩者皆拒絕；後來由使用者提供之原始 Drive 資料夾找到同名 465,170,862-byte 檔案，經正常公開下載流程取得。無法對比未下載成功的 Sediment 附件雜湊，因此不宣稱兩者逐位元相同。

## 引擎證據

| 狀態 | 證據 | 解讀 |
|---|---|---|
| 已由檔案驗證 | `Windows/GirlFishing/Binaries/Win64/GirlFishing-Win64-Shipping.exe`：PE32+ / AMD64，152,220,160 bytes；REA PE import parser | Windows 64 位元 Shipping 主程式 |
| 已由檔案驗證 | 同一 EXE 的 UTF-16LE 字串 `Unreal Engine 5.6.1`，byte offset 131,379,224 | Unreal 5.6 分支／5.6.1 版本標記；不是完整原始建置重現證明 |
| 已由檔案驗證 | 同一 EXE 的 UTF-16LE 字串 `++UE5+Release-5.6`，byte offset 113,171,712 | Unreal 5.6 分支／5.6.1 版本標記；不是完整原始建置重現證明 |
| 已由檔案驗證 | 同一 EXE 的 UTF-16LE 字串 `++UE5+Release-5.6-CL-44394996`，byte offset 113,171,776 | Unreal 5.6 分支／5.6.1 版本標記；不是完整原始建置重現證明 |
| 已由檔案驗證 | `Windows/GirlFishing/Content/Paks/GirlFishing-Windows.utoc` 標頭 `-==--==--==--==-`；retoc info 為 `Compressed | Indexed`、Oodle | Unreal IoStore；不是依副檔名猜測 |
| 已由檔案驗證 | REA desktop 的 Unreal package marker，及 `Engine/`、Shipping EXE、`.pak/.utoc/.ucas` 佈局 | 多項證據一致，排除僅因目錄名稱而判定 |

## 封裝與資產

retoc v0.1.5 列出 2,441 chunks：812 ExportBundleData、1,401 ShaderCode、223 BulkData、4 ShaderCodeLibrary、1 ContainerHeader。812 是套件／ExportBundleData 數，不是角色數或場景數。477 個 chunk 路徑位於 `GirlFishing/Content/`，可能包含同資產的主資料與 bulk，不能當成 477 個不同資產。

- 模型／骨架／動畫／材質以 cooked `.uasset` 與 `.ubulk` 邏輯路徑記錄於 IoStore；沒有證據顯示這份 Shipping 包含可直接匯入 Blender 的原始 FBX／GLB。
- 大容器 `.ucas` 是內容資料，`.utoc` 是索引／chunk 表，`.pak` 是另一層封裝。目錄列表可讀不代表所有內容都已解碼。
- `Manifest_UFSFiles_Win64.txt` 是打包 manifest；不是獨立存在於解壓目錄的每份原始 `.uasset`。
- `MaterialX/libraries/` 有多種 shader library 原始碼；隨附此類檔案不證明角色實際使用 MaterialX。

## 工具與限制

REA 6.8.0 實際完成 ZIP artifact、desktop runtime candidates 與 PE import 三種靜態操作，Evidence 含 subject digest。ZIP 摘要的 `examined=1204` 是 REA 圖觀察單位，與 ZIP 402 個成員不是同一統計口徑。PE 操作先碰到預設 64 MiB budget，依工具 remediation 明確提高為 180,000,000 bytes 後成功。

retoc info/list 成功。選擇性轉換 xBP 為 2 成功／6 失敗，xModel 為 13 成功／74 失敗；成功者多為小型未壓縮材質／結構套件。直接讀取 BP_GirlBase chunk 回報 Oodle 動態依賴下載連線失敗。沒有取得或重新散布該專有 library，沒有將失敗套件標為已解出。其原始錯誤存於 `evidence/retoc-get-bp.log`。

## 可重驗證證據

- `evidence/zip-inventory.json`：完整 ZIP 成員大小與 CRC metadata。
- `evidence/rea-kochi-summary.json`、`rea-kochi-evidence.json`、`rea-kochi-desktop.json`、`rea-pe-imports.json`。
- `evidence/retoc-info.txt`、`retoc-paths.txt`、`reference-facts.json`（版本字串位置）。
- 參考資料來源：https://drive.google.com/drive/folders/1ddgiY_8wChh1yMnaKcpsTs9R9GYenKuw

## ZIP 成員（依原始目錄順序）

| bytes | compressed bytes | path |
|---:|---:|---|
| 0 | 0 | `Windows/` |
| 0 | 0 | `Windows/Engine/` |
| 0 | 0 | `Windows/Engine/Binaries/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/DbgHelp/` |
| 2232720 | 977559 | `Windows/Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/` |
| 1073 | 358 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/disney_brdf_2012.mtlx` |
| 1481 | 461 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/disney_brdf_2015.mtlx` |
| 40125 | 3790 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/gltf_pbr.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/` |
| 2706 | 467 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_add.mtlx` |
| 9897 | 2197 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_conductor.mtlx` |
| 9871 | 2057 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_dielectric.mtlx` |
| 2601 | 874 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_diffuse.mtlx` |
| 769 | 336 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_emission.mtlx` |
| 1773 | 648 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_layer.mtlx` |
| 2128 | 471 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_mix.mtlx` |
| 2164 | 728 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_sheen.mtlx` |
| 6973 | 2093 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_sss.mtlx` |
| 2094 | 797 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/lama/lama_translucent.mtlx` |
| 10888 | 2350 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/open_pbr_surface.mtlx` |
| 28452 | 4215 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/standard_surface.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/translation/` |
| 6409 | 969 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/translation/standard_surface_to_gltf_pbr.mtlx` |
| 5012 | 856 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/translation/standard_surface_to_usd.mtlx` |
| 20684 | 2616 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/bxdf/usd_preview_surface.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/cmlib/` |
| 4956 | 491 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/cmlib/cmlib_defs.mtlx` |
| 17743 | 1514 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/cmlib/cmlib_ng.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genglsl/` |
| 617 | 200 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genglsl/lights_genglsl_impl.mtlx` |
| 186 | 123 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genglsl/mx_directional_light.glsl` |
| 378 | 206 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genglsl/mx_point_light.glsl` |
| 637 | 282 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genglsl/mx_spot_light.glsl` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genmsl/` |
| 614 | 200 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genmsl/lights_genmsl_impl.mtlx` |
| 192 | 127 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genmsl/mx_directional_light.metal` |
| 384 | 206 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genmsl/mx_point_light.metal` |
| 643 | 284 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/genmsl/mx_spot_light.metal` |
| 2465 | 613 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/lights/lights_defs.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/` |
| 8817 | 2452 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/core.mdl` |
| 2815 | 1139 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/hsv.mdl` |
| 24235 | 4475 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/noise.mdl` |
| 1086 | 620 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/pbrlib.mdl` |
| 36005 | 6705 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/pbrlib_1_6.mdl` |
| 10593 | 2378 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/pbrlib_1_7.mdl` |
| 1306 | 737 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/pbrlib_1_8.mdl` |
| 6307 | 1640 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/sampling.mdl` |
| 543 | 333 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/stdlib.mdl` |
| 122659 | 10408 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/stdlib_1_6.mdl` |
| 576 | 350 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/stdlib_1_7.mdl` |
| 20597 | 2447 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/stdlib_1_8.mdl` |
| 73630 | 5958 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/mdl/materialx/swizzle.mdl` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genglsl/` |
| 681 | 288 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genglsl/nprlib_genglsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genmdl/` |
| 779 | 348 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genmdl/nprlib_genmdl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genmsl/` |
| 678 | 287 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genmsl/nprlib_genmsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genosl/` |
| 715 | 316 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/genosl/nprlib_genosl_impl.mtlx` |
| 2690 | 827 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/nprlib_defs.mtlx` |
| 4965 | 947 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/nprlib/nprlib_ng.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/` |
| 2850 | 1159 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_environment_fis.glsl` |
| 246 | 151 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_environment_none.glsl` |
| 1116 | 541 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_environment_prefilter.glsl` |
| 382 | 216 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_generate_albedo_table.glsl` |
| 2808 | 1136 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_generate_prefilter_env.glsl` |
| 2246 | 730 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_microfacet.glsl` |
| 3223 | 1287 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_microfacet_diffuse.glsl` |
| 3255 | 1192 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_microfacet_sheen.glsl` |
| 19693 | 5688 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_microfacet_specular.glsl` |
| 779 | 389 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_shadow.glsl` |
| 177 | 138 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_transmission_opacity.glsl` |
| 525 | 308 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/lib/mx_transmission_refract.glsl` |
| 98 | 78 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_add_edf.glsl` |
| 170 | 138 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_anisotropic_vdf.glsl` |
| 590 | 307 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_artistic_ior.glsl` |
| 1784 | 731 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_blackbody.glsl` |
| 1059 | 386 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_burley_diffuse_bsdf.glsl` |
| 2241 | 667 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_conductor_bsdf.glsl` |
| 3760 | 806 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_dielectric_bsdf.glsl` |
| 150 | 104 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_displacement_float.glsl` |
| 145 | 105 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_displacement_vector3.glsl` |
| 4378 | 893 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_generalized_schlick_bsdf.glsl` |
| 349 | 229 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_generalized_schlick_edf.glsl` |
| 989 | 376 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_oren_nayar_diffuse_bsdf.glsl` |
| 460 | 204 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_roughness_anisotropy.glsl` |
| 277 | 137 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_roughness_dual.glsl` |
| 1402 | 499 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_sheen_bsdf.glsl` |
| 1080 | 420 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_subsurface_bsdf.glsl` |
| 914 | 385 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_translucent_bsdf.glsl` |
| 92 | 76 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/mx_uniform_edf.glsl` |
| 4812 | 708 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genglsl/pbrlib_genglsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genmdl/` |
| 10145 | 1341 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genmdl/pbrlib_genmdl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genmsl/` |
| 4695 | 703 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genmsl/pbrlib_genmsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/` |
| 247 | 169 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_anisotropic_vdf.osl` |
| 252 | 179 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_burley_diffuse_bsdf.osl` |
| 1205 | 600 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_conductor_bsdf.osl` |
| 1428 | 584 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_dielectric_bsdf.osl` |
| 1639 | 685 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_generalized_schlick_bsdf.osl` |
| 212 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_oren_nayar_diffuse_bsdf.osl` |
| 839 | 463 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_sheen_bsdf.osl` |
| 272 | 197 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_subsurface_bsdf.osl` |
| 199 | 136 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_surface.osl` |
| 178 | 132 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/legacy/mx_translucent_bsdf.osl` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/lib/` |
| 1810 | 414 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/lib/mx_microfacet.osl` |
| 544 | 268 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/lib/mx_microfacet_sheen.osl` |
| 2348 | 855 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/lib/mx_microfacet_specular.osl` |
| 245 | 180 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_anisotropic_vdf.osl` |
| 609 | 310 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_artistic_ior.osl` |
| 1821 | 744 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_blackbody.osl` |
| 611 | 219 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_dielectric_bsdf.osl` |
| 145 | 97 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_displacement_float.osl` |
| 140 | 95 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_displacement_vector3.osl` |
| 759 | 241 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_generalized_schlick_bsdf.osl` |
| 278 | 189 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_generalized_schlick_edf.osl` |
| 466 | 208 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_roughness_anisotropy.osl` |
| 308 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_roughness_dual.osl` |
| 228 | 171 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_subsurface_bsdf.osl` |
| 190 | 127 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/mx_surface.osl` |
| 5085 | 830 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/genosl/pbrlib_genosl_impl.mtlx` |
| 22274 | 2875 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/pbrlib_defs.mtlx` |
| 816 | 347 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/pbrlib/pbrlib_ng.mtlx` |
| 4994 | 1493 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/README.md` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/` |
| 3569 | 1523 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_hsv.glsl` |
| 175 | 89 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_math.glsl` |
| 20239 | 4072 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_noise.glsl` |
| 2930 | 857 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_sampling.glsl` |
| 121 | 81 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_transform_uv.glsl` |
| 141 | 98 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/lib/mx_transform_uv_vflip.glsl` |
| 205 | 141 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_aastep.glsl` |
| 259 | 132 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_burn_color3.glsl` |
| 309 | 139 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_burn_color4.glsl` |
| 232 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_burn_float.glsl` |
| 143 | 109 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_cellnoise2d_float.glsl` |
| 143 | 109 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_cellnoise3d_float.glsl` |
| 213 | 123 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_creatematrix_vector3_matrix33.glsl` |
| 283 | 138 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_creatematrix_vector3_matrix44.glsl` |
| 291 | 139 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_creatematrix_vector4_matrix44.glsl` |
| 619 | 262 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_disjointover_color4.glsl` |
| 264 | 133 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_dodge_color3.glsl` |
| 317 | 140 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_dodge_color4.glsl` |
| 231 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_dodge_float.glsl` |
| 277 | 164 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_fractal3d_float.glsl` |
| 275 | 170 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_fractal3d_vector2.glsl` |
| 275 | 166 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_fractal3d_vector3.glsl` |
| 275 | 170 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_fractal3d_vector4.glsl` |
| 120 | 98 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_hsvtorgb_color3.glsl` |
| 135 | 110 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_hsvtorgb_color4.glsl` |
| 389 | 218 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_color3.glsl` |
| 385 | 213 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_color4.glsl` |
| 388 | 215 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_float.glsl` |
| 389 | 215 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_vector2.glsl` |
| 390 | 218 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_vector3.glsl` |
| 386 | 214 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_image_vector4.glsl` |
| 118 | 92 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_luminance_color3.glsl` |
| 135 | 106 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_luminance_color4.glsl` |
| 239 | 122 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_mix_surfaceshader.glsl` |
| 217 | 141 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise2d_float.glsl` |
| 218 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise2d_vector2.glsl` |
| 215 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise2d_vector3.glsl` |
| 283 | 177 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise2d_vector4.glsl` |
| 217 | 140 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise3d_float.glsl` |
| 218 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise3d_vector2.glsl` |
| 215 | 145 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise3d_vector3.glsl` |
| 287 | 178 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_noise3d_vector4.glsl` |
| 703 | 296 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_normalmap.glsl` |
| 101 | 83 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_premult_color4.glsl` |
| 155 | 110 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramplr_float.glsl` |
| 154 | 109 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramplr_vector2.glsl` |
| 154 | 111 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramplr_vector3.glsl` |
| 154 | 111 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramplr_vector4.glsl` |
| 155 | 111 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramptb_float.glsl` |
| 154 | 110 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramptb_vector2.glsl` |
| 154 | 112 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramptb_vector3.glsl` |
| 154 | 112 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_ramptb_vector4.glsl` |
| 120 | 100 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_rgbtohsv_color3.glsl` |
| 135 | 111 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_rgbtohsv_color4.glsl` |
| 256 | 143 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_rotate_vector2.glsl` |
| 911 | 293 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_rotate_vector3.glsl` |
| 234 | 126 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_smoothstep_float.glsl` |
| 237 | 134 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_smoothstep_vector2.glsl` |
| 295 | 143 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_smoothstep_vector3.glsl` |
| 353 | 152 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_smoothstep_vector4.glsl` |
| 199 | 129 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splitlr_float.glsl` |
| 198 | 132 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splitlr_vector2.glsl` |
| 198 | 134 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splitlr_vector3.glsl` |
| 198 | 134 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splitlr_vector4.glsl` |
| 199 | 131 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splittb_float.glsl` |
| 198 | 133 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splittb_vector2.glsl` |
| 198 | 135 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splittb_vector3.glsl` |
| 198 | 135 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_splittb_vector4.glsl` |
| 146 | 108 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_transformmatrix_vector2M3.glsl` |
| 147 | 109 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_transformmatrix_vector3M4.glsl` |
| 103 | 85 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_unpremult_color4.glsl` |
| 172 | 121 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise2d_float.glsl` |
| 172 | 126 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise2d_vector2.glsl` |
| 172 | 127 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise2d_vector3.glsl` |
| 172 | 120 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise3d_float.glsl` |
| 172 | 127 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise3d_vector2.glsl` |
| 172 | 126 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/mx_worleynoise3d_vector3.glsl` |
| 76686 | 5747 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genglsl/stdlib_genglsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmdl/` |
| 92058 | 6550 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmdl/stdlib_genmdl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/lib/` |
| 4171 | 1025 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/lib/mx_math.metal` |
| 1064 | 191 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/lib/mx_matscalaroperators.metal` |
| 2975 | 864 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/lib/mx_sampling.metal` |
| 747 | 239 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/lib/mx_texture.metal` |
| 295 | 141 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_burn_color3.metal` |
| 352 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_burn_color4.metal` |
| 232 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_burn_float.metal` |
| 300 | 142 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_dodge_color3.metal` |
| 360 | 150 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_dodge_color4.metal` |
| 231 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_dodge_float.metal` |
| 706 | 299 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_normalmap.metal` |
| 234 | 126 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_smoothstep_float.metal` |
| 266 | 142 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_smoothstep_vector2.metal` |
| 357 | 159 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_smoothstep_vector3.metal` |
| 396 | 161 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/mx_smoothstep_vector4.metal` |
| 76418 | 5775 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genmsl/stdlib_genmsl_impl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/` |
| 6337 | 1124 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/color4.h` |
| 2859 | 701 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/matrix33.h` |
| 16449 | 2592 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/mx_funcs.h` |
| 6030 | 1075 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/vector2.h` |
| 9398 | 1531 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/include/vector4.h` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/lib/` |
| 5609 | 1243 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/lib/mx_sampling.osl` |
| 71 | 58 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/lib/mx_transform_uv.osl` |
| 100 | 76 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/lib/mx_transform_uv_vflip.osl` |
| 188 | 140 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_ambientocclusion_float.osl` |
| 261 | 133 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_burn_color3.osl` |
| 347 | 145 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_burn_color4.osl` |
| 226 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_burn_float.osl` |
| 121 | 93 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_cellnoise2d_float.osl` |
| 106 | 86 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_cellnoise3d_float.osl` |
| 928 | 193 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_creatematrix.osl` |
| 603 | 256 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_disjointover_color4.osl` |
| 266 | 134 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_dodge_color3.osl` |
| 356 | 149 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_dodge_color4.osl` |
| 216 | 145 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_dodge_float.osl` |
| 236 | 145 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_fractal3d_float.osl` |
| 244 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_fractal3d_vector2.osl` |
| 241 | 146 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_fractal3d_vector3.osl` |
| 244 | 148 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_fractal3d_vector4.osl` |
| 84 | 72 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_frame_float.osl` |
| 100 | 85 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geomcolor_color3.osl` |
| 240 | 136 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geomcolor_color4.osl` |
| 99 | 86 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geomcolor_float.osl` |
| 156 | 115 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_boolean.osl` |
| 158 | 114 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_color3.osl` |
| 384 | 174 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_color4.osl` |
| 181 | 120 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_float.osl` |
| 156 | 114 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_integer.osl` |
| 161 | 111 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_string.osl` |
| 279 | 154 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_vector2.osl` |
| 161 | 114 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_vector3.osl` |
| 333 | 165 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_geompropvalue_vector4.osl` |
| 178 | 127 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_heighttonormal_vector3.osl` |
| 109 | 95 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_hsvtorgb_color3.osl` |
| 126 | 103 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_hsvtorgb_color4.osl` |
| 786 | 356 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_color3.osl` |
| 963 | 414 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_color4.osl` |
| 786 | 362 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_float.osl` |
| 839 | 378 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_vector2.osl` |
| 758 | 345 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_vector3.osl` |
| 994 | 424 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_image_vector4.osl` |
| 116 | 89 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_luminance_color3.osl` |
| 136 | 102 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_luminance_color4.osl` |
| 248 | 125 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_mix_surfaceshader.osl` |
| 199 | 128 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise2d_float.osl` |
| 210 | 129 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise2d_vector2.osl` |
| 204 | 131 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise2d_vector3.osl` |
| 210 | 131 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise2d_vector4.osl` |
| 184 | 122 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise3d_float.osl` |
| 195 | 125 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise3d_vector2.osl` |
| 189 | 121 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise3d_vector3.osl` |
| 195 | 125 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_noise3d_vector4.osl` |
| 765 | 281 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_normalmap.osl` |
| 106 | 82 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_premult_color4.osl` |
| 109 | 94 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_rgbtohsv_color3.osl` |
| 126 | 103 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_rgbtohsv_color4.osl` |
| 268 | 145 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_rotate_vector2.osl` |
| 1090 | 337 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_rotate_vector3.osl` |
| 421 | 181 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_surface_unlit.osl` |
| 142 | 101 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_time_float.osl` |
| 192 | 129 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_transformmatrix_vector2M3.osl` |
| 108 | 84 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_unpremult_color4.osl` |
| 146 | 103 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise2d_float.osl` |
| 152 | 105 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise2d_vector2.osl` |
| 151 | 107 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise2d_vector3.osl` |
| 145 | 103 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise3d_float.osl` |
| 151 | 105 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise3d_vector2.osl` |
| 150 | 105 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/mx_worleynoise3d_vector3.osl` |
| 77356 | 5871 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/genosl/stdlib_genosl_impl.mtlx` |
| 257283 | 17780 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/stdlib_defs.mtlx` |
| 220628 | 15135 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/stdlib/stdlib_ng.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/` |
| 476 | 227 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/essl.mtlx` |
| 467 | 220 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/genglsl.mtlx` |
| 466 | 218 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/genmdl.mtlx` |
| 484 | 227 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/genmsl.mtlx` |
| 466 | 218 | `Windows/Engine/Binaries/ThirdParty/MaterialX/libraries/targets/genosl.mtlx` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MsQuic/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MsQuic/v220/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/MsQuic/v220/win64/` |
| 2547104 | 1239898 | `Windows/Engine/Binaries/ThirdParty/MsQuic/v220/win64/msquic.dll` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/NVIDIA/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/NVIDIA/NVaftermath/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/NVIDIA/NVaftermath/Win64/` |
| 5442616 | 2004125 | `Windows/Engine/Binaries/ThirdParty/NVIDIA/NVaftermath/Win64/GFSDK_Aftermath_Lib.x64.dll` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Ogg/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Ogg/Win64/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Ogg/Win64/VS2015/` |
| 59856 | 21132 | `Windows/Engine/Binaries/ThirdParty/Ogg/Win64/VS2015/libogg_64.dll` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Vorbis/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Vorbis/Win64/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/` |
| 48592 | 27168 | `Windows/Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbisfile_64.dll` |
| 1724880 | 250244 | `Windows/Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbis_64.dll` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Windows/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Windows/XAudio2_9/` |
| 0 | 0 | `Windows/Engine/Binaries/ThirdParty/Windows/XAudio2_9/x64/` |
| 858176 | 431129 | `Windows/Engine/Binaries/ThirdParty/Windows/XAudio2_9/x64/xaudio2_9redist.dll` |
| 0 | 0 | `Windows/Engine/Config/` |
| 3 | 3 | `Windows/Engine/Config/StagedBuild_GirlFishing.ini` |
| 0 | 0 | `Windows/Engine/Content/` |
| 0 | 0 | `Windows/Engine/Content/Renderer/` |
| 259568 | 122975 | `Windows/Engine/Content/Renderer/TessellationTable.bin` |
| 0 | 0 | `Windows/Engine/Content/Slate/` |
| 0 | 0 | `Windows/Engine/Content/Slate/Cursor/` |
| 326 | 52 | `Windows/Engine/Content/Slate/Cursor/invisible.cur` |
| 0 | 0 | `Windows/Engine/Content/SlateDebug/` |
| 0 | 0 | `Windows/Engine/Content/SlateDebug/Fonts/` |
| 930 | 502 | `Windows/Engine/Content/SlateDebug/Fonts/LastResort.tps` |
| 5395052 | 1038521 | `Windows/Engine/Content/SlateDebug/Fonts/LastResort.ttf` |
| 0 | 0 | `Windows/Engine/Plugins/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/Binaries/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/Binaries/ThirdParty/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/Binaries/ThirdParty/Onnxruntime/` |
| 0 | 0 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/Binaries/ThirdParty/Onnxruntime/Win64/` |
| 14692896 | 5342832 | `Windows/Engine/Plugins/NNE/NNERuntimeORT/Binaries/ThirdParty/Onnxruntime/Win64/onnxruntime.dll` |
| 0 | 0 | `Windows/GirlFishing/` |
| 0 | 0 | `Windows/GirlFishing/Binaries/` |
| 0 | 0 | `Windows/GirlFishing/Binaries/Win64/` |
| 28112 | 16009 | `Windows/GirlFishing/Binaries/Win64/boost_atomic-mt-x64.dll` |
| 46544 | 23016 | `Windows/GirlFishing/Binaries/Win64/boost_chrono-mt-x64.dll` |
| 163280 | 73241 | `Windows/GirlFishing/Binaries/Win64/boost_filesystem-mt-x64.dll` |
| 59856 | 27112 | `Windows/GirlFishing/Binaries/Win64/boost_iostreams-mt-x64.dll` |
| 355792 | 124114 | `Windows/GirlFishing/Binaries/Win64/boost_program_options-mt-x64.dll` |
| 204752 | 81945 | `Windows/GirlFishing/Binaries/Win64/boost_python311-mt-x64.dll` |
| 240080 | 112418 | `Windows/GirlFishing/Binaries/Win64/boost_regex-mt-x64.dll` |
| 20432 | 12113 | `Windows/GirlFishing/Binaries/Win64/boost_system-mt-x64.dll` |
| 85456 | 39596 | `Windows/GirlFishing/Binaries/Win64/boost_thread-mt-x64.dll` |
| 0 | 0 | `Windows/GirlFishing/Binaries/Win64/D3D12/` |
| 0 | 0 | `Windows/GirlFishing/Binaries/Win64/D3D12/x64/` |
| 3344912 | 1131593 | `Windows/GirlFishing/Binaries/Win64/D3D12/x64/D3D12Core.dll` |
| 5784080 | 2290021 | `Windows/GirlFishing/Binaries/Win64/D3D12/x64/d3d12SDKLayers.dll` |
| 0 | 0 | `Windows/GirlFishing/Binaries/Win64/DML/` |
| 0 | 0 | `Windows/GirlFishing/Binaries/Win64/DML/x64/` |
| 18537992 | 9318077 | `Windows/GirlFishing/Binaries/Win64/DML/x64/DirectML.dll` |
| 152220160 | 58688897 | `Windows/GirlFishing/Binaries/Win64/GirlFishing-Win64-Shipping.exe` |
| 182292480 | 50584739 | `Windows/GirlFishing/Binaries/Win64/GirlFishing-Win64-Shipping.pdb` |
| 331728 | 103131 | `Windows/GirlFishing/Binaries/Win64/tbb12.dll` |
| 117712 | 53041 | `Windows/GirlFishing/Binaries/Win64/tbbmalloc.dll` |
| 0 | 0 | `Windows/GirlFishing/Content/` |
| 0 | 0 | `Windows/GirlFishing/Content/Paks/` |
| 21775283 | 20549081 | `Windows/GirlFishing/Content/Paks/GirlFishing-Windows.pak` |
| 314955120 | 308851537 | `Windows/GirlFishing/Content/Paks/GirlFishing-Windows.ucas` |
| 285772 | 172432 | `Windows/GirlFishing/Content/Paks/GirlFishing-Windows.utoc` |
| 2599376 | 1027294 | `Windows/GirlFishing/Content/Paks/global.ucas` |
| 674 | 172 | `Windows/GirlFishing/Content/Paks/global.utoc` |
| 173568 | 95192 | `Windows/GirlFishing.exe` |
| 230 | 142 | `Windows/Manifest_DebugFiles_Win64.txt` |
| 33478 | 2504 | `Windows/Manifest_NonUFSFiles_Win64.txt` |
| 0 | 0 | `Windows/Manifest_ObsoleteNonUFSFiles_DESKTOPTM05KNT.txt` |
| 0 | 0 | `Windows/Manifest_ObsoleteUFSFiles_DESKTOPTM05KNT.txt` |
| 241125 | 22094 | `Windows/Manifest_UFSFiles_Win64.txt` |