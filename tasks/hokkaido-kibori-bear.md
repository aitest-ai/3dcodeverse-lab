# 北海道木雕熊（咬鮭魚）｜3DCodeVerse 官方 Harness 任務

本任務必須由官方 Harness 的 `static_object` + `blender` 生成，不能用事先寫死的幾何替代，且不得以 AI 圖片充當 3D 模型。

## Prompt (English)

Create a single, highly recognizable, traditional Hokkaido Japanese kibori-kuma (wood-carved bear) souvenir sculpture, not a living bear. Four legs, large rounded heavy body, short robust legs with paws planted flat, arched shoulders, broad expressive face with small round ears. The bear firmly bites and carries a LARGE entire salmon horizontally and crosswise in its jaws; clearly show distinct fish head, eyes, tapering fish body, dorsal fin, pectoral fin and broad tail protruding to the side. The salmon must visibly intersect/clamp at the mouth, not float. The bear is entirely carved from dark brown wood and has bold directional overlapping chisel-gouged fur marks; realistic handcrafted wood carving sculptural geometry, not just a flat photographic texture. Include carved eye sockets, nose, mouth line, claws and hand-chiseled fur. No pedestal, no labels, no typography, no landscape. Solid connected mesh components, physically coherent, full-object views from front, side and three-quarter. Prioritize iconic Hokkaido tourist souvenir silhouette and accurate anatomical placement of fish over random surface texture.

## Criteria
- Bear has recognizable compact bear anatomy (not a stretched sausage or table)
- Four stout paws touch same plane
- Clearly visible fish held crosswise in mouth; fish has head, tail, fins
- No free-floating ear/fish/leg mesh, major self intersection, or broken normals
- Dark brown sculpted wood, chisel-cut fur pattern visible in geometry
- Generate actual `object.glb`, render images, `record.json`, and script source from official Harness
- If run fails: preserve diagnostic logs and explicitly mark failed, never substitute procedural fallback.
