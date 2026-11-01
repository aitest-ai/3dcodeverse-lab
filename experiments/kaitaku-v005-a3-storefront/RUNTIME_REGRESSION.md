# V005 A3 Runtime Regression

Status: **PASS for current Chromium/WebGL2 runtime candidate**.

This is a regression of FinalPolish A3 itself, not an inference from FinalPolish A.

## Identity

- A3 environment SHA-256: `8df3ada77443c390556e71c873d43dd65fe67996716e08ecfaff4e5faf60e27f`
- Visitor SHA-256: `01785edd6b177cca497787433a01ffc5da31d42b1224b1a9439b3c3c58dca0df`
- Both hashes matched the active scene manifest.
- Browser: Chromium / WebGL2 / SwiftShader in the current controlled environment.

## Runtime regression

- 14 舊島歌郵局 → 15 舊山本理髮店 → 16 舊渡邊商店: PASS
- Barber stair heights observed while entering and leaving:
  `0.00 -> 0.15 -> 0.30 -> 0.45 m`
- Third person:
  - mode = `third`
  - visitorLoaded = `true`
  - visitorVisible = `true`
- Pause/resume:
  `false -> true -> false`
- page errors: **0**
- failed asset requests: **0**

## Interpretation

A3 only changes two locally duplicated ground-floor closed-storefront materials at building 16. Its binary geometry chunk is byte-identical to FinalPolish A. This runtime regression confirms that the A3 material reassignment did not introduce a navigation, stair, third-person, pause/resume, asset identity, or loader regression in the tested browser session.

## Boundaries

This does **not** certify:
- Android physical-device performance or touch;
- native Blender V005 writeback;
- native five-view Cycles visual acceptance;
- Blender native export parity.

A remains the rollback baseline. A2 hedge remains experimental and is not included in A3. No fourth building is added.
