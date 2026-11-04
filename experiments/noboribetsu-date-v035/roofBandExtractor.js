/**
 * V035 reusable, reversible TWO-FACE roof-band extraction for Three.js.
 * Input: original V004 'plaster_offwhite' mesh loaded by GLTFLoader.
 * Original GLB and original THREE.BufferGeometry are NEVER mutated.
 * This is a visual diagnostic, not a historically validated roof repair.
 */
export function createV035RoofBand(THREE, plaster) {
  if (!plaster?.isMesh || plaster.name !== 'plaster_offwhite') {
    throw Error('Expected V004 plaster_offwhite mesh');
  }
  const original = plaster.geometry;
  const ix = original.index?.array;
  const pos = original.attributes.position;
  if (!ix || ix.length !== 144 || pos?.count !== 32) {
    throw Error('V004 geometry contract failed: 48 indexed faces and 32 vertices required');
  }
  const bandFaces = [8, 9];
  const target = [], rest = [];
  for (let face = 0; face < 48; face++) {
    const part = bandFaces.includes(face) ? target : rest;
    part.push(...Array.from(ix.slice(face * 3, face * 3 + 3)));
  }
  if (target.join(',') !== '3,7,6,3,6,2' || rest.length !== 138) {
    throw Error('Face order differs from V004 sealed GLB');
  }
  const cornerIds = [3,7,6,2];
  const corner = cornerIds.map(i => new THREE.Vector3().fromBufferAttribute(pos, i));
  const xSpan = Math.max(...corner.map(v => v.x)) - Math.min(...corner.map(v => v.x));
  const zSpan = Math.max(...corner.map(v => v.z)) - Math.min(...corner.map(v => v.z));
  const meanY = corner.reduce((s,v) => s + v.y, 0) / 4;
  if (Math.abs(xSpan - 20.1475) > .003 ||
      Math.abs(zSpan - 11.7526) > .003 ||
      Math.abs(meanY - 6.72852039) > .0005) {
    throw Error('Roof-band source geometry unexpectedly moved');
  }
  function indexed(indices) {
    const g = original.clone();
    g.setIndex(indices);
    return g;
  }
  const restGeometry = indexed(rest);
  const bandGeometry = indexed(target);
  const studyGeometry = bandGeometry.clone();
  const p = studyGeometry.attributes.position.clone();
  for (const i of cornerIds) {
    const v = new THREE.Vector3().fromBufferAttribute(p, i);
    if (v.z > 56) p.setY(i, v.y - .035);
  }
  studyGeometry.setAttribute('position', p);
  studyGeometry.computeVertexNormals();
  if (Array.isArray(plaster.material)) throw Error('Unexpected multi-material plaster');
  const material = plaster.material.clone();
  material.color.multiplyScalar(.64);
  material.name = 'V035_DIAGNOSTIC_WARM_GREY';
  const parent = plaster.parent;
  if (!parent) throw Error('Original must be attached to scene');
  function sibling(name, geometry, mat) {
    const node = new THREE.Mesh(geometry, mat);
    node.name = name;
    node.position.copy(plaster.position);
    node.rotation.copy(plaster.rotation);
    node.scale.copy(plaster.scale);
    parent.add(node);
    node.visible = false;
    return node;
  }
  const retained = sibling('V035_preserved_46', restGeometry, plaster.material);
  const tint = sibling('V035_tint_2', bandGeometry, material);
  const slope = sibling('V035_diagnostic_slope_2', studyGeometry, plaster.material);
  let selected = 'original';
  function setMode(next, allow = true) {
    if (!['original','material','geometry'].includes(next)) throw Error('Unknown V035 mode');
    selected = next;
    plaster.visible = allow && next === 'original';
    retained.visible = allow && next !== 'original';
    tint.visible = allow && next === 'material';
    slope.visible = allow && next === 'geometry';
  }
  function dispose() {
    parent.remove(retained,tint,slope);
    restGeometry.dispose();bandGeometry.dispose();studyGeometry.dispose();material.dispose();
    plaster.visible = true;
  }
  setMode('original');
  return { setMode, dispose, mode: () => selected, bandFaces, retainedFaces: 46,
           originalFaces: 48, sourceVertices: cornerIds, geometryDeltaY: -.035,
           visible: () => ({original: plaster.visible, retained: retained.visible,
                            material: tint.visible, geometry: slope.visible}) };
}
