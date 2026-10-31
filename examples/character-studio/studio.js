/* Stage 01 viewer. All models, materials and geometry come from verified GLBs. */
const IDS = ['d03', 'd06'];
const THREE_REVISION = '187';
const WARMUP_MS = 3000;
const WINDOW_SIZE = 1800;
const $ = (id) => document.getElementById(id);
const viewButtons = [...document.querySelectorAll('[data-view]')];
const controlButtons = [...viewButtons, $('zoom-in'), $('zoom-out'), $('reset-view')];
const progressElements = Object.fromEntries(IDS.map((id) => {
  const row = document.querySelector(`[data-progress="${id}"]`);
  return [id, {bar: row.querySelector('progress'), label: row.querySelector('.progress-label')}];
}));
const state = {ready: false, status: 'booting', error: null, version: null, assets: [], view: 'front'};
let current = null;
let runNumber = 0;

function immutable(value) {
  if (value === null || typeof value !== 'object') return value;
  const copy = Array.isArray(value) ? value.map(immutable) : Object.fromEntries(Object.entries(value).map(([k, v]) => [k, immutable(v)]));
  return Object.freeze(copy);
}

Object.defineProperty(window, 'characterStudioReview', {
  configurable: false, writable: false,
  value: Object.freeze({
    get schemaVersion() { return 1; },
    get ready() { return state.ready; },
    get status() { return state.status; },
    get error() { return state.error; },
    get version() { return state.version; },
    get assets() { return immutable(state.assets); },
    get view() { return state.view; },
    get measurements() { return immutable(measurements(current)); },
  }),
});

class ReviewError extends Error {
  constructor(message, status = 'error') { super(message); this.name = 'ReviewError'; this.status = status; }
}

function formatBytes(value) {
  return value >= 1024 * 1024 ? `${(value / 1048576).toFixed(2)} MiB` : `${(value / 1024).toFixed(1)} KiB`;
}

function updateProgress(id, loaded, total, phase) {
  const {bar, label} = progressElements[id];
  if (total > 0) { bar.max = total; bar.value = Math.min(loaded, total); }
  else bar.removeAttribute('value');
  label.textContent = phase || (total > 0 ? `${formatBytes(loaded)} / ${formatBytes(total)}` : `${formatBytes(loaded)} · 下載中`);
}

function active(run) { return run === current && !run.controller.signal.aborted; }
function ensureActive(run) { if (!active(run)) throw new DOMException('Loading cancelled', 'AbortError'); }

function validateRegistry(data) {
  if (data?.schema_version !== 1 || typeof data.version !== 'string' || !data.version.trim() || !Array.isArray(data.assets) || data.assets.length !== 2) {
    throw new ReviewError('registry.json 格式不符：需要 schema_version 1、版本與兩位角色的資產紀錄。');
  }
  return IDS.map((id) => {
    const matches = data.assets.filter((a) => a.id === id);
    const asset = matches[0];
    if (matches.length !== 1 || asset.file !== `${id}.glb` || !/^[a-f0-9]{64}$/i.test(asset.sha256 || '') ||
        typeof asset.version !== 'string' || !asset.version.trim() || !Number.isFinite(asset.height) || asset.height < 1 || asset.height > 2.3 ||
        (asset.bytes !== undefined && (!Number.isSafeInteger(asset.bytes) || asset.bytes <= 0))) {
      throw new ReviewError(`${id.toUpperCase()} 的資產紀錄缺少正確檔名、版本、公尺高度或 SHA-256。`);
    }
    return {...asset, sha256: asset.sha256.toLowerCase()};
  });
}

function inspectGLB(buffer, id) {
  if (buffer.byteLength < 20) throw new ReviewError(`${id.toUpperCase()} 檔案不完整。`);
  const view = new DataView(buffer);
  if (view.getUint32(0, true) !== 0x46546c67 || view.getUint32(4, true) !== 2 || view.getUint32(8, true) !== buffer.byteLength ||
      view.getUint32(16, true) !== 0x4e4f534a || 20 + view.getUint32(12, true) > buffer.byteLength) {
    throw new ReviewError(`${id.toUpperCase()} 不是完整的 glTF 2.0 GLB。`);
  }
  const json = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 20, view.getUint32(12, true))));
  for (const resource of [...(json.buffers || []), ...(json.images || [])]) {
    if (resource.uri && !resource.uri.startsWith('data:')) {
      throw new ReviewError(`${id.toUpperCase()} 引用了未包含在 GLB 雜湊內的外部檔案；請先交付完整內嵌資產。`);
    }
  }
  return json;
}

async function loadAsset(run, asset) {
  let gltf = null;
  try {
    const response = await fetch(new URL(`./models/${asset.file}`, import.meta.url), {signal: run.controller.signal, cache: 'no-store'});
    if (!response.ok) throw new ReviewError(`${asset.id.toUpperCase()} 載入失敗（HTTP ${response.status}）。請確認 models/${asset.file} 已放入交付包。`);
    if (!response.body?.getReader) throw new ReviewError('此瀏覽器無法提供串流載入進度，請改用支援 ReadableStream 的瀏覽器。');
    const headerLength = Number(response.headers.get('Content-Length'));
    const total = asset.bytes || (!response.headers.get('Content-Encoding') && Number.isSafeInteger(headerLength) && headerLength > 0 ? headerLength : 0);
    const reader = response.body.getReader();
    const chunks = [];
    let loaded = 0;
    updateProgress(asset.id, 0, total, '開始下載');
    while (true) {
      const {done, value} = await reader.read();
      ensureActive(run);
      if (done) break;
      chunks.push(value); loaded += value.byteLength;
      updateProgress(asset.id, loaded, total);
    }
    if (asset.bytes && loaded !== asset.bytes) throw new ReviewError(`${asset.id.toUpperCase()} 實際位元組數與 registry 不符，請重新提供同一版本的完整檔案。`);
    const bytes = new Uint8Array(loaded);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
    chunks.length = 0;
    updateProgress(asset.id, loaded, loaded, 'SHA-256 校驗中');
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    ensureActive(run);
    const hash = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
    if (hash !== asset.sha256) throw new ReviewError(`${asset.id.toUpperCase()} SHA-256 不符。已停止顯示；請檢查檔案與版本，或重試載入。`);
    const document = inspectGLB(bytes.buffer, asset.id);
    updateProgress(asset.id, loaded, loaded, '雜湊一致 · 解析模型');
    gltf = await run.loader.parseAsync(bytes.buffer, '');
    ensureActive(run);
    if (!gltf.scene) throw new ReviewError(`${asset.id.toUpperCase()} 缺少可呈現的場景。`);
    gltf.scene.updateMatrixWorld(true);
    const bounds = new run.THREE.Box3().setFromObject(gltf.scene, true);
    if (bounds.isEmpty()) throw new ReviewError(`${asset.id.toUpperCase()} 沒有可見模型。`);
    const height = bounds.max.y - bounds.min.y;
    if (!Number.isFinite(height) || Math.abs(height - asset.height) > Math.max(0.015, asset.height * 0.01)) {
      throw new ReviewError(`${asset.id.toUpperCase()} 實際高度 ${height.toFixed(3)} m 與登錄 ${asset.height.toFixed(3)} m 不符。請修正匯出尺度；檢視器不會縮放角色。`);
    }
    let meshes = 0;
    let skinnedMeshes = 0;
    gltf.scene.traverse((object) => {
      if (object.isMesh) { meshes++; object.castShadow = true; object.receiveShadow = true; }
      if (object.isSkinnedMesh) skinnedMeshes++;
    });
    if (!meshes) throw new ReviewError(`${asset.id.toUpperCase()} 沒有可繪製的網格。`);
    // The wrapper changes only ground placement and view orientation, never asset scale.
    const wrapper = new run.THREE.Group();
    wrapper.name = `${asset.id}_review_placement`;
    wrapper.position.set(asset.id === 'd03' ? -0.68 : 0.68, -bounds.min.y, 0);
    wrapper.add(gltf.scene);
    const record = {
      id: asset.id, label: asset.label || asset.id.toUpperCase(), version: asset.version, file: asset.file,
      sha256: hash, sha256_verified: true, size_bytes: loaded, height_registry_m: asset.height,
      height_measured_m: height, original_bounds_m: {min: bounds.min.toArray(), max: bounds.max.toArray()},
      placement_m: wrapper.position.toArray(), viewer_scale: [1, 1, 1], meshes, skinned_meshes: skinnedMeshes,
      animation_clips_in_file: gltf.animations.length, animation_playback: false,
      gltf_generator: document.asset?.generator || null, material_policy: 'Unmodified imported GLB materials',
    };
    updateProgress(asset.id, loaded, loaded, '已驗證 · 等待共同呈現');
    return {id: asset.id, wrapper, height, record};
  } catch (error) {
    if (gltf?.scene) disposeObject(gltf.scene);
    if (active(run)) updateProgress(asset.id, 0, 0, '未完成 · 請查看原因');
    throw error;
  }
}

function rendererMetadata(gl) {
  const debug = gl.getExtension('WEBGL_debug_renderer_info');
  return {
    api: gl.getParameter(gl.VERSION), vendor: gl.getParameter(gl.VENDOR), renderer: gl.getParameter(gl.RENDERER),
    unmasked_vendor: debug ? gl.getParameter(debug.UNMASKED_VENDOR_WEBGL) : null,
    unmasked_renderer: debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : null,
    shading_language: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
  };
}

function makeScene(run) {
  const T = run.THREE;
  const canvas = document.createElement('canvas');
  canvas.tabIndex = 0;
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', '兩位實際尺度人物灰模。拖曳旋轉、滾輪或雙指縮放；可使用下方視角按鈕。');
  let gl;
  try { gl = canvas.getContext('webgl2', {antialias: true, alpha: false, powerPreference: 'high-performance'}); }
  catch { /* The explicit error below also covers blocked graphics contexts. */ }
  if (!gl) throw new ReviewError('此瀏覽器未能建立 WebGL 2 繪圖環境。請確認瀏覽器支援並允許 WebGL，再重試。', 'unsupported');
  let renderer;
  try { renderer = new T.WebGLRenderer({canvas, context: gl, antialias: true, alpha: false}); }
  catch { throw new ReviewError('WebGL 2 無法完成初始化。請確認瀏覽器繪圖環境可用後重試。', 'unsupported'); }
  run.renderer = renderer;
  run.rendererMetadata = rendererMetadata(gl);
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = T.PCFSoftShadowMap;
  // These gray candidates are static. Reuse the same full-resolution shadow
  // map until a view button turns the characters; no geometry/detail changes.
  renderer.shadowMap.autoUpdate = false;
  renderer.shadowMap.needsUpdate = true;
  const scene = new T.Scene();
  scene.background = new T.Color('#e9ede6');
  run.scene = scene;
  run.camera = new T.OrthographicCamera(-1, 1, 1, -1, 0.05, 50);
  run.target = new T.Vector3(0, 1.02, 0);
  run.yaw = 0; run.pitch = 0; run.zoom = 1; run.mode = 'front';
  scene.add(new T.HemisphereLight(0xf4f6ef, 0x798671, 1.8));
  const key = new T.DirectionalLight(0xfff9ef, 2.6);
  key.position.set(-3, 4, 4); key.target.position.set(0, 0.9, 0);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, {left: -2.4, right: 2.4, top: 2.7, bottom: -2.1, near: 0.1, far: 14});
  key.shadow.bias = -0.00015; key.shadow.normalBias = 0.003;
  scene.add(key, key.target);
  const fill = new T.DirectionalLight(0xeef5ff, 0.65); fill.position.set(4, 2, 2); scene.add(fill);
  const rim = new T.DirectionalLight(0xffffff, 0.8); rim.position.set(1, 3, -3); scene.add(rim);
  const floor = new T.Mesh(new T.PlaneGeometry(100, 100), new T.MeshStandardMaterial({color: 0xdce2d7, roughness: 1, metalness: 0}));
  floor.name = 'review_ground'; floor.rotation.x = -Math.PI / 2; floor.position.y = -0.002; floor.receiveShadow = true; scene.add(floor);
  $('canvas-host').replaceChildren(canvas);
  run.abortEvents = new AbortController();
  canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    if (active(run)) fail(run, new ReviewError('WebGL 繪圖環境已中斷。請重新載入相同版本的角色。'));
  }, {signal: run.abortEvents.signal});
  attachControls(run, canvas);
  run.resize = new ResizeObserver(() => { if (run === current) resize(run); });
  run.resize.observe($('viewport'));
  resize(run);
}

function resize(run) {
  if (!run.renderer) return;
  const {width, height} = $('viewport').getBoundingClientRect();
  run.width = Math.max(1, Math.round(width)); run.height = Math.max(1, Math.round(height));
  // Native display resolution; no FPS-based quality changes or hidden lightweight mode.
  run.renderer.setPixelRatio(window.devicePixelRatio || 1);
  run.renderer.setSize(run.width, run.height, false);
  updateCamera(run);
}

function updateCamera(run) {
  const faceMode = run.mode.startsWith('face-');
  const aspect = run.width / run.height;
  const commonFrameHeight = faceMode ? Math.max(0.52, 0.48 / aspect) : Math.max(2.2, 2.65 / aspect);
  const halfHeight = commonFrameHeight / (2 * run.zoom);
  run.camera.left = -halfHeight * aspect; run.camera.right = halfHeight * aspect;
  run.camera.top = halfHeight; run.camera.bottom = -halfHeight;
  run.camera.updateProjectionMatrix();
  const distance = 6;
  run.camera.position.set(
    run.target.x + distance * Math.sin(run.yaw) * Math.cos(run.pitch),
    run.target.y + distance * Math.sin(run.pitch),
    run.target.z + distance * Math.cos(run.yaw) * Math.cos(run.pitch),
  );
  run.camera.lookAt(run.target);
}

function setView(run, mode) {
  if (!active(run) || !run.models?.length) return;
  run.mode = mode; run.yaw = 0; run.pitch = 0; run.zoom = 1;
  const angle = mode === 'side' ? Math.PI / 2 : mode === 'back' ? Math.PI : 0;
  for (const model of run.models) model.wrapper.rotation.y = angle;
  run.renderer.shadowMap.needsUpdate = true;
  if (mode.startsWith('face-')) {
    const model = run.models.find((m) => m.id === mode.slice(5));
    run.target.set(model.wrapper.position.x, model.height - 0.13, 0);
  } else run.target.set(0, 1.02, 0);
  state.view = mode;
  for (const button of viewButtons) button.setAttribute('aria-pressed', String(button.dataset.view === mode));
  const labels = {front: '正面 · 共同尺度', side: '側面 · 共同尺度', back: '背面 · 共同尺度', 'face-d03': 'D03 青年 · 無髮臉部', 'face-d06': 'D06 長者 · 無髮臉部'};
  $('view-label').textContent = labels[mode];
  updateCamera(run);
}

function zoomBy(run, factor) {
  if (!state.ready || !active(run)) return;
  run.zoom = Math.min(5, Math.max(0.55, run.zoom * factor)); updateCamera(run);
}

function markCustomView() {
  state.view = 'custom';
  viewButtons.forEach((button) => button.setAttribute('aria-pressed', 'false'));
  $('view-label').textContent = '自由檢視 · 拖曳旋轉';
}

function attachControls(run, canvas) {
  const options = {signal: run.abortEvents.signal};
  const pointers = new Map();
  let lastPinch = null;
  const pinchDistance = () => { const [a, b] = [...pointers.values()]; return Math.hypot(a.x - b.x, a.y - b.y); };
  canvas.addEventListener('pointerdown', (event) => {
    if (!state.ready || (event.pointerType === 'mouse' && event.button !== 0)) return;
    canvas.focus({preventScroll: true}); canvas.setPointerCapture(event.pointerId);
    pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    if (pointers.size === 2) lastPinch = pinchDistance();
  }, options);
  canvas.addEventListener('pointermove', (event) => {
    if (!state.ready || !pointers.has(event.pointerId)) return;
    const previous = pointers.get(event.pointerId);
    pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    if (pointers.size === 2) {
      const distance = pinchDistance(); if (lastPinch > 0) zoomBy(run, distance / lastPinch); lastPinch = distance;
    } else if (pointers.size === 1) {
      run.yaw -= (event.clientX - previous.x) * 0.007;
      run.pitch = Math.max(-0.3, Math.min(0.65, run.pitch + (event.clientY - previous.y) * 0.005));
      if (event.clientX !== previous.x || event.clientY !== previous.y) markCustomView();
      updateCamera(run);
    }
  }, options);
  const release = (event) => { pointers.delete(event.pointerId); lastPinch = pointers.size === 2 ? pinchDistance() : null; };
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) canvas.addEventListener(name, release, options);
  canvas.addEventListener('wheel', (event) => {
    if (!state.ready) return; event.preventDefault();
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? run.height : 1);
    zoomBy(run, Math.exp(-Math.max(-200, Math.min(200, delta)) * 0.002));
  }, {...options, passive: false});
  canvas.addEventListener('keydown', (event) => {
    if (!state.ready) return;
    if (event.key === '+' || event.key === '=') zoomBy(run, 1.15);
    else if (event.key === '-') zoomBy(run, 1 / 1.15);
    else if (event.key === 'Home') setView(run, 'front');
    else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
      if (event.key === 'ArrowLeft') run.yaw += 0.08;
      if (event.key === 'ArrowRight') run.yaw -= 0.08;
      if (event.key === 'ArrowUp') run.pitch = Math.min(0.65, run.pitch + 0.05);
      if (event.key === 'ArrowDown') run.pitch = Math.max(-0.3, run.pitch - 0.05);
      markCustomView(); updateCamera(run);
    } else return;
    event.preventDefault();
  }, options);
}

function quantile(sorted, q) {
  if (!sorted.length) return null;
  const index = (sorted.length - 1) * q; const lower = Math.floor(index);
  return sorted[lower] + (sorted[Math.ceil(index)] - sorted[lower]) * (index - lower);
}

function measurements(run) {
  if (!run?.renderer) return null;
  const intervals = run.intervals || [];
  const sorted = [...intervals].sort((a, b) => a - b);
  const rendering = run.renderer.info.render;
  return {
    schema_version: 1, captured_at_utc: new Date().toISOString(), scope: 'This browser, this gray-review scene only',
    ready: state.ready, status: state.status, candidate_version: state.version, three_revision: THREE_REVISION,
    view: state.view, camera: {projection: 'orthographic', position_m: run.camera.position.toArray(), target_m: run.target.toArray(),
      vertical_span_m: run.camera.top - run.camera.bottom, zoom_factor: run.zoom, character_rotation_y_radians: run.models?.[0]?.wrapper.rotation.y || 0},
    assets: state.assets.map((a) => ({...a})),
    runtime: {user_agent: navigator.userAgent, platform: navigator.platform, secure_context: window.isSecureContext, visibility: document.visibilityState,
      css_width: run.width, css_height: run.height, device_pixel_ratio: window.devicePixelRatio || 1, render_pixel_ratio: run.renderer.getPixelRatio(),
      drawing_buffer_width: run.renderer.domElement.width, drawing_buffer_height: run.renderer.domElement.height, renderer: {...run.rendererMetadata}},
    sampling: {warmup_ms: WARMUP_MS, visible_elapsed_ms: run.visibleMs || 0, warmup_complete: (run.visibleMs || 0) >= WARMUP_MS,
      sliding_window_limit: WINDOW_SIZE, retained_samples: intervals.length, total_samples: run.totalSamples || 0,
      hidden_page_intervals_excluded: true, long_visible_frames_retained: true, frame_interval_ms: {
        p50: quantile(sorted, 0.5), p95: quantile(sorted, 0.95), max: sorted.length ? sorted[sorted.length - 1] : null,
        mean: intervals.length ? intervals.reduce((a, b) => a + b, 0) / intervals.length : null,
      }, raw_frame_intervals_ms: [...intervals]},
    current_scene: {draw_calls: rendering.calls, triangles: rendering.triangles, points: rendering.points, lines: rendering.lines,
      geometries: run.renderer.info.memory.geometries, textures: run.renderer.info.memory.textures,
      includes_studio_ground: true, shadow_map_size: 2048, imported_materials_preserved: true, animation_playback: false, automatic_lod_fallback: false},
    validation_scope: {browser_runtime: true, offline_blender_render: false, full_game_test: false, android_device_test: false,
      caveat: 'Frame intervals are not GPU timer queries. Browser scheduling, VSync, resolution and software rendering can affect these data. No Android performance conclusion.'},
  };
}

function updateMetricUI(run) {
  const data = measurements(run);
  if (!data) return;
  const s = data.sampling; const runtime = data.runtime;
  $('metric-state').textContent = document.hidden ? '分頁在背景 · 暫停採樣' : !s.warmup_complete ? `暖機 ${Math.min(3, s.visible_elapsed_ms / 1000).toFixed(1)} / 3 秒` : '持續採樣 · 最近 1,800 筆';
  const ms = (n) => n === null ? '—' : `${n.toFixed(2)} ms`;
  $('metric-frames').textContent = `${ms(s.frame_interval_ms.p50)} / ${ms(s.frame_interval_ms.p95)}`;
  $('metric-samples').textContent = `${s.retained_samples} / ${(s.visible_elapsed_ms / 1000).toFixed(1)} 秒`;
  $('metric-pixels').textContent = `${runtime.render_pixel_ratio.toFixed(2)}× / ${runtime.drawing_buffer_width} × ${runtime.drawing_buffer_height}`;
  $('metric-draws').textContent = `${data.current_scene.draw_calls.toLocaleString()} / ${data.current_scene.triangles.toLocaleString()}`;
  $('metric-renderer').textContent = runtime.renderer.unmasked_renderer || runtime.renderer.renderer;
  $('validation-summary').textContent = s.warmup_complete ? '2 份 GLB 雜湊一致 · 持續量測中' : '2 份 GLB 雜湊一致 · 暖機中';
}

function renderFrame(run, now) {
  if (!active(run) || !state.ready) return;
  if (!document.hidden) {
    if ((window.devicePixelRatio || 1) !== run.renderer.getPixelRatio()) resize(run);
    if (run.previousFrame !== null) {
      const interval = now - run.previousFrame;
      const wasWarm = run.visibleMs >= WARMUP_MS;
      run.visibleMs += interval;
      if (wasWarm) { run.intervals.push(interval); run.totalSamples++; if (run.intervals.length > WINDOW_SIZE) run.intervals.shift(); }
    }
    run.previousFrame = now;
    try { run.renderer.render(run.scene, run.camera); }
    catch (error) { fail(run, new ReviewError(`模型已載入，但 WebGL 繪製失敗：${error.message}`)); return; }
    if (now - run.lastMetricUpdate >= 1000) { run.lastMetricUpdate = now; updateMetricUI(run); }
  } else run.previousFrame = null;
  run.raf = requestAnimationFrame((time) => renderFrame(run, time));
}

function showAssetRows() {
  const rows = state.assets.map((asset) => {
    const row = document.createElement('tr');
    for (let i = 0; i < 4; i++) row.append(document.createElement('td'));
    row.children[0].textContent = asset.id.toUpperCase();
    const version = document.createElement('span'); version.className = 'asset-version'; version.textContent = `${asset.version} · SHA-256 一致`;
    const hash = document.createElement('code'); hash.className = 'asset-sha'; hash.textContent = asset.sha256;
    row.children[1].append(version, hash);
    row.children[2].textContent = `${(asset.height_measured_m * 100).toFixed(2)} cm`;
    row.children[3].textContent = formatBytes(asset.size_bytes);
    return row;
  });
  $('asset-rows').replaceChildren(...rows);
}

function disposeObject(root) {
  const geometries = new Set(); const materials = new Set(); const textures = new Set();
  root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry);
    for (const material of (Array.isArray(object.material) ? object.material : object.material ? [object.material] : [])) materials.add(material);
    if (object.shadow?.dispose) object.shadow.dispose();
    if (object.isSkinnedMesh) object.skeleton?.dispose();
  });
  for (const material of materials) { for (const value of Object.values(material)) if (value?.isTexture) textures.add(value); material.dispose(); }
  for (const texture of textures) { texture.source?.data?.close?.(); texture.dispose(); }
  for (const geometry of geometries) geometry.dispose();
}

function disposeRun(run) {
  if (!run) return;
  clearTimeout(run.timeout);
  run.controller.abort(); run.abortEvents?.abort(); cancelAnimationFrame(run.raf);
  run.resize?.disconnect();
  if (run.scene) disposeObject(run.scene);
  run.renderer?.dispose();
  run.renderer?.forceContextLoss();
}

function fail(run, error) {
  if (run !== current || run.failed) return;
  clearTimeout(run.timeout);
  run.failed = true; run.controller.abort(); cancelAnimationFrame(run.raf);
  state.ready = false; state.status = error.status || 'error'; state.error = error.message || String(error);
  $('viewport').setAttribute('aria-busy', 'false');
  $('canvas-host').hidden = true; $('view-caption').hidden = true; $('viewport-note').hidden = true;
  $('load-panel').hidden = false; $('load-panel').dataset.error = 'true';
  $('load-kicker').textContent = state.status === 'unsupported' ? '繪圖環境未就緒' : '此版本尚未載入完成';
  $('load-title').textContent = state.status === 'unsupported' ? '需要 WebGL 2 支援' : '請檢查檔案後重試';
  $('load-message').textContent = state.error;
  $('retry').hidden = false;
  $('validation-summary').textContent = '未完成載入';
  controlButtons.forEach((button) => { button.disabled = true; });
  $('download-measurements').disabled = !run.renderer;
}

async function start() {
  disposeRun(current);
  const run = {number: ++runNumber, controller: new AbortController(), intervals: [], totalSamples: 0, visibleMs: 0,
    previousFrame: null, lastMetricUpdate: 0, models: [], failed: false};
  current = run;
  run.timeout = setTimeout(() => {
    if (active(run) && !state.ready) fail(run, new ReviewError('載入超過 120 秒。請檢查連線與檔案，再重試載入同一版本。'));
  }, 120000);
  Object.assign(state, {ready: false, status: 'loading', error: null, version: null, assets: [], view: 'front'});
  controlButtons.forEach((button) => { button.disabled = true; });
  $('download-measurements').disabled = true; $('retry').hidden = true;
  $('canvas-host').hidden = true; $('view-caption').hidden = true; $('viewport-note').hidden = true;
  $('load-panel').hidden = false; delete $('load-panel').dataset.error;
  $('load-kicker').textContent = '載入完整灰模'; $('load-title').textContent = '準備兩位角色';
  $('load-message').textContent = '兩份完整模型通過雜湊校驗後，將一起顯示。';
  $('viewport').setAttribute('aria-busy', 'true'); $('validation-summary').textContent = '等待載入';
  $('version').textContent = '候選版本 · 載入中';
  const waitingRow = document.createElement('tr'); const waitingCell = document.createElement('td');
  waitingCell.colSpan = 4; waitingCell.textContent = '模型載入後顯示。'; waitingRow.append(waitingCell);
  $('asset-rows').replaceChildren(waitingRow);
  $('metric-state').textContent = '等待載入';
  ['metric-frames', 'metric-samples', 'metric-pixels', 'metric-draws', 'metric-renderer'].forEach((id) => { $(id).textContent = '—'; });
  IDS.forEach((id) => updateProgress(id, 0, 0, '等待版本資料'));
  try {
    if (location.protocol === 'file:') throw new ReviewError('請以交付說明中的本機 HTTP 伺服器開啟此頁；直接雙擊 HTML 無法可靠載入與驗證 GLB。');
    if (!window.isSecureContext || !crypto.subtle) throw new ReviewError('SHA-256 校驗需要 HTTPS 或 localhost 安全環境。請依 README 啟動本機伺服器，或使用 HTTPS。');
    let modules;
    try { modules = await Promise.all([import('three'), import('./vendor/three-0.187.0/examples/jsm/loaders/GLTFLoader.js')]); }
    catch { throw new ReviewError('Three.js 載入失敗。請確認 vendor/three-0.187.0 已包含 build 與 GLTFLoader 的相依模組。'); }
    ensureActive(run);
    [run.THREE] = modules;
    if (run.THREE.REVISION !== THREE_REVISION) throw new ReviewError('Three.js 版本不符；此交付固定使用 0.187.0。');
    makeScene(run);
    const manager = new run.THREE.LoadingManager();
    manager.setURLModifier((url) => {
      if (!url.startsWith('blob:') && !url.startsWith('data:')) throw new ReviewError('GLB 引用了未校驗的外部資源；請交付完整內嵌資產。');
      return url;
    });
    run.loader = new modules[1].GLTFLoader(manager);
    const response = await fetch(new URL('./models/registry.json', import.meta.url), {signal: run.controller.signal, cache: 'no-store'});
    if (!response.ok) throw new ReviewError(`找不到 models/registry.json（HTTP ${response.status}）。請先放入這次候選版本的模型與登錄檔。`);
    const registry = await response.json(); const assets = validateRegistry(registry);
    ensureActive(run); state.version = registry.version;
    $('version').textContent = `候選版本 · ${registry.version}`;
    // allSettled lets successful siblings be disposed if the other asset fails.
    const results = await Promise.allSettled(assets.map((asset) => loadAsset(run, asset)));
    const loadedModels = results.filter((result) => result.status === 'fulfilled').map((result) => result.value);
    const failure = results.find((result) => result.status === 'rejected');
    if (failure || !active(run)) {
      loadedModels.forEach((model) => disposeObject(model.wrapper));
      if (failure) throw failure.reason;
      ensureActive(run);
    }
    run.models = loadedModels;
    state.assets = loadedModels.map((model) => model.record);
    state.status = 'preparing'; $('load-title').textContent = '準備共同視圖';
    $('load-message').textContent = '兩份模型雜湊一致，正在準備材質與繪圖。';
    loadedModels.forEach((model) => run.scene.add(model.wrapper));
    setView(run, 'front');
    if (run.renderer.compileAsync) await run.renderer.compileAsync(run.scene, run.camera);
    else run.renderer.compile(run.scene, run.camera);
    ensureActive(run);
    run.renderer.render(run.scene, run.camera);
    state.ready = true; state.status = 'ready';
    clearTimeout(run.timeout);
    showAssetRows(); updateMetricUI(run);
    $('canvas-host').hidden = false; $('view-caption').hidden = false; $('viewport-note').hidden = false;
    $('load-panel').hidden = true; $('viewport').setAttribute('aria-busy', 'false');
    controlButtons.forEach((button) => { button.disabled = false; });
    $('download-measurements').disabled = false;
    run.raf = requestAnimationFrame((now) => renderFrame(run, now));
  } catch (error) {
    if (run !== current || (error.name === 'AbortError' && run.failed)) return;
    fail(run, error);
  }
}

viewButtons.forEach((button) => button.addEventListener('click', () => setView(current, button.dataset.view)));
$('zoom-in').addEventListener('click', () => zoomBy(current, 1.2));
$('zoom-out').addEventListener('click', () => zoomBy(current, 1 / 1.2));
$('reset-view').addEventListener('click', () => setView(current, 'front'));
$('retry').addEventListener('click', start);
$('download-measurements').addEventListener('click', () => {
  const data = measurements(current); if (!data) return;
  const url = URL.createObjectURL(new Blob([`${JSON.stringify(data, null, 2)}\n`], {type: 'application/json'}));
  const link = document.createElement('a'); link.href = url;
  link.download = `character-studio-measurements-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
  document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});
document.addEventListener('visibilitychange', () => {
  if (current) { current.previousFrame = null; if (state.ready) updateMetricUI(current); }
});
window.addEventListener('pagehide', () => { if (current) current.previousFrame = null; });
start();
