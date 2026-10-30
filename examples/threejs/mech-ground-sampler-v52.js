/**
 * Taipei Mech v5.2 - opt-in, evidence-based walkable scene sampling.
 * Only raycast explicit walkable meshes (road/sidewalk/ground/terrain names or
 * userData.walkable), never arbitrary mesh roofs, façades or vehicles.
 * If no certified geometry exists, return NaN so the foot IK uses the original
 * pedestrian controller ground plane. OSM line geometry is not a heightmap.
 */
export function createMechGroundSampler({THREE, scene, getReferenceHeight = () => 0, maxMeshes = 1500} = {}) {
  const candidate = [];
  let enabled = true, samples = 0, hits = 0, rejected = 0;
  const allow = /(?:road|street|sidewalk|pavement|asphalt|ground|terrain|walkway|路面|人行道|道路|地面)/i;
  const deny = /(?:building|fa[cç]ade|wall|vehicle|car|tree|roof|water|river|bridge|debris|collider|建築|屋頂|水面|橋墩|殘骸)/i;
  const ray = THREE?.Raycaster ? new THREE.Raycaster() : null;
  const origin = THREE?.Vector3 ? new THREE.Vector3() : null;
  const down = THREE?.Vector3 ? new THREE.Vector3(0, -1, 0) : null;
  const normal = THREE?.Vector3 ? new THREE.Vector3() : null;
  const normalMatrix = THREE?.Matrix3 ? new THREE.Matrix3() : null;
  function isWalkable(o) {
    if (!o?.isMesh || o.userData?.walkable === false) return false;
    if (o.userData?.walkable === true) return true;
    const category = [o.name, o.userData?.kind, o.userData?.category, o.parent?.name].join(' ');
    return allow.test(category) && !deny.test(category);
  }
  function rebuild() {
    candidate.length = 0;
    if (!ray || !scene?.traverse) return 0;
    scene.traverse(o => {
      if (candidate.length < maxMeshes && isWalkable(o)) candidate.push(o);
    });
    return candidate.length;
  }
  rebuild();
  function sample(x, z) {
    samples++;
    if (!enabled || !ray || !candidate.length || !Number.isFinite(x) || !Number.isFinite(z)) return NaN;
    const reference = Number(getReferenceHeight());
    if (!Number.isFinite(reference)) return NaN;
    // Candidate roads/sidewalks must be at walker height; do not treat roofs,
    // elevated scenery, and random horizontal world geometry as ground.
    origin.set(x, reference + .9, z);
    ray.set(origin, down);
    ray.far = 1.7;
    let intersections;
    try { intersections = ray.intersectObjects(candidate, false); }
    catch { rejected++; return NaN; }
    for (const hit of intersections) {
      const h = hit?.point?.y;
      if (!Number.isFinite(h) || Math.abs(h - reference) > .55) {rejected++;continue;}
      if (hit.face?.normal && normal) {
        normal.copy(hit.face.normal);
        if (normalMatrix && hit.object?.matrixWorld) {
          normalMatrix.getNormalMatrix(hit.object.matrixWorld);
          normal.applyMatrix3(normalMatrix).normalize();
        }
        if (normal.y < .72) {rejected++;continue;} // slope > ~44 degrees
      }
      hits++;return h;
    }
    return NaN;
  }
  return {
    sample, rebuild, setEnabled(v){enabled=!!v;return enabled;},
    get enabled(){return enabled;}, get available(){return !!ray && candidate.length>0;},
    snapshot(){return {available:!!ray && candidate.length>0, enabled, meshCount:candidate.length,
      samples,hits,rejected,coverage:samples?Number((hits/samples).toFixed(3)):0,
      limitation:'Only verified road/sidewalk meshes, controller-ground fallback; OSM routes alone are not elevation data'};},
    dispose(){enabled=false;candidate.length=0;},
  };
}
