# Private asset rebuild gate

All original V004/V021/V022/V024/V026 GLB bytes are taken unchanged from the exact V026 Runtime archive. Do not replace these with a generic stock Edo building, a different `学問所寺子屋` facade or a low-detail generated approximation.

Bundle source available in the user's standalone **Noboribetsu_Date_V028_R1_SourceQA.zip**:
`source/build_v028_from_v026.py`, `source/audit_v028.py`, `source/test_v028_mobile.py`, `source/site_source/index.html`, `source/site_source/style.css`, `source/site_source/app.js`, plus genuine Chromium screenshot and QA JSON evidence.

All UI code in the source ZIP is editable. The output is a private WebGL2 inspection website with a reproducible server startup, **not** a replacement for V026 full gameplay.

Acceptance checks: exact source ZIP SHA; original 137 files unchanged; extracted GLB byte-for-byte SHA; front/side/eave camera and V004/V024/V026 selector; mobile 430×932; no JS errors. Native Blender remains pending until real binary has executed and `.blend` and Cycles 4-angle output truly exist.

Do not claim site survey precision: the 2.49m outer bay dimension comes from the artist-authored model, not field measurements.
