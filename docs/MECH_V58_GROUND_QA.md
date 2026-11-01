# Taipei Mech v5.8 — grounded dodge, actual GLB audit, diagnostic QA

## Scope and lineage
Draft branch derived from v5.7 Draft PR #54, which in turn depends on v5.5 PR #23 and preceding mecha work. **Do not merge out of order** and **do not edit the live Taipei site**. The full v5.8 Windows overlay is a separate candidate ZIP, not duplicated in this asset-pipeline GitHub repo.

## Implemented in the full independent Windows overlay
- A conservative grounded-only dodge start check; no dash while jumping or unknown height.
- Post-resolver height reconciliation for small verified uphill/downhill steps (max .38 m), no snap while airborne.
- Real Taipei Slop controller and OSM collision, editable building wall panels and traffic/water logic remain authoritative. No invulnerability or 3D controller teleport.
- On-screen performance diagnostic and explicit privacy-limited local JSON export. Frame update-cadence Hz (measured on callback starts) is **NOT** GPU FPS.
- Every ~20 frames: read GLB IK error, real city collision counts, optional renderer.info geometry/triangle metadata. Excludes >250ms browser tab suspensions. Bounded history with a circular buffer.
- The 4.15MB authentic v5.0 GLB was parsed directly: 6 clips, 15 bones; authored `Mecha_Dodge` root X movement about 0.14m over 2.0s, so that root track must be masked when the real city controller moves 3.2m. The GLB was NOT modified.

## Evidence and limitations
- Full independent Windows overlay: 42 Node/Python automated tests passed (including legacy 38 regression tests). Synthetic Chromium browser smoke test verified the QA page and explicit JSON download, including desktop and phone-width views. These do not establish in-game WebGPU quality.
- Still **NOT** verified: Windows WebGPU actual map gameplay, camera/foot clipping at Taipei 101, real graphics FPS or VRAM, 5-minute city battle acceptance.
- Original v5.0 GLB SHA-256: `296217e110585d06a1c0ddfa6de3f89bb221aeaf88b80e4fdbf90d5f61168e3c`.
- City source fixed to shwang1979/slop-taipei `1d70708fc92a088b779c8c0e22677adb64966a1b`. The original city is downloaded on user Windows and is not redistributed in the ZIP.

## Portable code
- `examples/threejs/mech-ground-safety-v58.js`: ground-level checks for the real city's authoritative height API.
- `examples/threejs/mech-qa-v58.js`: bounded diagnostic collector; does not contain app-specific UI or networking.
- `tests/mecha/v58-ground-and-qa.mjs`: real portable JS tests.

## Required manual acceptance (blocked by lack of Windows city source + GPU browser access here)
In actual Taipei game test: V / Shift+V while grounded, jumping, near intact/destroyed wall, on uphill and downhill kerb, under bridge, next to traffic and river; then F/Shift+F/G; 5 min resets. Export JSON for each 30-sec stage and compare screenshots at identical viewpoints. If GPU timer/VRAM are unavailable, record as **not measured**, not guessed.
