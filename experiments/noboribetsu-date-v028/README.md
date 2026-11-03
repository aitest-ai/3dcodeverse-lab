# 登別伊達時代村 V028 R1｜高等學問所獨立 3D 建築檢視器

> **QA-only / standalone tool**, not a new full-game Runtime or Blender-native render. Stack on V027 Draft PR #123, which itself extends V026 Draft PR #120. **Do not merge, deploy or overwrite any previous site or model.**

## Key finding (building identity)
Do not conflate **高等学問所 (Higher Learning Hall)** with **学問所寺子屋 (Terakoya)**. Existing 2023 traveler photos labelled 学問所/寺子屋 cannot certify the elevation or window ratios of 高等学問所. The official 2026 entry explicitly names 高等学問所 as a storefront location; external photos show its vertical sign in the Edo shopping street, but not a measurable orthogonal facade. Do **not** alter roof geometry based only on these photos.

Sources:
- Official overview: https://edo-trip.jp/tw/about/
- Official Jan. 2026 mention: https://edo-trip.jp/2026/01/24/kakizome2026/
- Building identification: https://www.cartogiraffe.com/日本/北海道地方/北海道/胆振総合振興局/登別市/高等学問所/
- Terakoya images (not same-building measurements): https://4travel.jp/travelogue/11854802

## Actual executable work
V028 is a standalone WebGL2 viewer built **only from original GLBs** extracted from private `Noboribetsu_Date_V026_R1_Runtime.zip`, SHA256:
`4e7436827c398689bc97906f268cbd49415ed2d08b2d612d868eb91d98e00167`.
The original **137 Runtime files are unchanged**. This small viewer selectively loads five independent GLBs:
- `v004_merchant_facades.glb` (17 meshes)
- `v021_v004_finish.glb` (2 meshes)
- `v022_v004_carpentry.glb` (3 meshes)
- `v024_v004_window_occlusion.glb` (5 meshes, 792 triangles)
- `v026_v004_sash_depth.glb` (7 meshes, 952 triangles)

Viewer controls: four deterministic camera positions (front, oblique, eave, street), V004/V024/V026 selector, V021/V022 overlays, existing roof toggle, sash wireframe and adjustable sunlight. Pointer drag/wheel, touch drag and pinch supported. It does **not** perform GPS, walking collisions or full-game controls.

Model-only dimensions: outer bay width 2.490 m, paper width 1.988 m, ratio 79.84%. **Author geometry, never site survey values.**

## Verification
- Clean replay: 12/12 essential UI and model/vendor files SHA-identical.
- Isolated Chromium / Xvfb / ANGLE SwiftShader: **real WebGL2 PASS**, five original GLBs loaded; V024/V026 switch, front/oblique/eave camera and roof visibility verified with five screenshots; JS errors zero.
- Chromium mobile emulation **430×932 PASS**, model load, version, oblique camera, wireframe and sunlight slider; JS errors zero.
- Source zip: original GLBs SHA-identical with sealed V026 ZIP, V025→V026 retained vertices/faces and 472 route points validated.
- Native Blender `.blend` / Cycles **NOT EXECUTED**, Android real device **NOT TESTED**, real private HTTPS/CDN/deployment **NOT TESTED**. No third-party photos embedded.

## Delivery and recreation
Full standalone inspector ZIP (around 3.9MB), independent offline screenshot comparison HTML, Comparison PNG, SourceQA ZIP (rebuild scripts, `site_source/`, QA logs/screenshots, SHA contracts), Validation JSON and delivery report are delivered outside GitHub. GitHub does **not** contain private GLBs or the full 76MB original Runtime.

To rebuild, extract SourceQA, then:
```bash
python source/build_v028_from_v026.py /private/Noboribetsu_Date_V026_R1_Runtime.zip /new/empty/Inspector --ui source/site_source
python -m http.server 8765 --directory /new/empty/Inspector
```
Open http://127.0.0.1:8765/ in Chrome/Edge; do not open `index.html` directly through file:// (ES modules and binary GLB CORS).

Next: obtain *same building* 高等学問所 elevation evidence, then create an isolated Blender source master and actual Cycles comparisons before promoting any roof proportion change into a new full Runtime.

**Keep Draft, no merge, no deployment, no permission changes.**
