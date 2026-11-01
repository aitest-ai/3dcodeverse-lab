// V006 surgical replacement: remove whole connected OSM mass components, not only triangle centroids.
// Exact 3-D vertices are keyed at 0.1 mm to connect flat-shaded faces with duplicated indices.
function suppressGreyBuildingPlaceholders(root,buildingIds){
  const ids=[...new Set(buildingIds)];
  if(ids.length!==buildingIds.length||!ids.length)throw new Error('OSM 替換建物清單重複或為空');
  const byId=new Map(manifest.buildings.map(b=>[b.id,b]));
  const polygons=ids.map(id=>{
    const b=byId.get(id);
    if(!b||!Array.isArray(b.polygon)||b.polygon.length<3)throw new Error('OSM 指定建物底面不存在：'+id);
    return {id,poly:b.polygon.map(([x,n])=>[x,-n])};
  });
  const removedById=Object.fromEntries(ids.map(id=>[id,0]));let affectedMeshes=0;
  root.updateMatrixWorld(true);
  root.traverse(o=>{
    if(!o.isMesh||!o.geometry)return;
    const mats=Array.isArray(o.material)?o.material:[o.material];
    if(!mats.some(m=>m?.name==='Unrefined_OSM_mass'))return;
    if(mats.length!==1)throw new Error('OSM 量體不再是單一材質，拒絕排除');
    const g=o.geometry,positions=g.getAttribute('position'),ix=g.getIndex();
    if(!positions)throw new Error('OSM 量體缺少位置緩衝');
    const count=ix?ix.count:positions.count;
    if(count%3!==0)throw new Error('OSM 三角面結構異常');
    const n=count/3,parents=Array.from({length:n},(_,i)=>i),keys=new Map(),cent=[];
    const find=i=>{let j=i;while(parents[j]!==j){parents[j]=parents[parents[j]];j=parents[j]}return j};
    const union=(a,b)=>{const ra=find(a),rb=find(b);if(ra!==rb)parents[ra]=rb};
    const p=new THREE.Vector3();
    for(let i=0;i<n;i++){
      let cx=0,cz=0;
      for(let k=0;k<3;k++){
        const idx=ix?ix.getX(i*3+k):i*3+k;
        p.fromBufferAttribute(positions,idx).applyMatrix4(o.matrixWorld);
        cx+=p.x/3;cz+=p.z/3;
        const key=[p.x,p.y,p.z].map(v=>Math.round(v*10000)).join(',');
        const previous=keys.get(key);
        if(previous===undefined)keys.set(key,i);else union(i,previous);
      }
      cent.push([cx,cz]);
    }
    const groups=new Map();
    for(let i=0;i<n;i++){
      const parent=find(i);
      if(!groups.has(parent))groups.set(parent,[]);
      groups.get(parent).push(i);
    }
    const keep=[];let localRemoved=0;
    for(const group of groups.values()){
      let x=0,z=0;for(const i of group){x+=cent[i][0];z+=cent[i][1]}
      x/=group.length;z/=group.length;
      const hits=polygons.filter(b=>pointInPolygonEUS(x,z,b.poly));
      if(hits.length>1)throw new Error('OSM 建物連通塊落入多個底面：'+hits.map(h=>h.id).join(','));
      if(hits.length){removedById[hits[0].id]+=group.length;localRemoved+=group.length;}
      else for(const i of group)for(let k=0;k<3;k++)keep.push(ix?ix.getX(i*3+k):i*3+k);
    }
    if(localRemoved){
      const safeCopy=g.clone();safeCopy.setIndex(keep);
      safeCopy.computeBoundingBox();safeCopy.computeBoundingSphere();
      o.geometry=safeCopy;affectedMeshes++;
    }
  });
  for(const id of ids)if(removedById[id]===0)throw new Error('OSM 舊量體未成功排除：'+id);
  metrics.placeholder_removal_by_building={...(metrics.placeholder_removal_by_building||{}),...removedById};
  (metrics.placeholder_removal_runs??=[]).push({building_ids:ids,triangles_removed:Object.values(removedById).reduce((a,b)=>a+b,0),affected_meshes:affectedMeshes,method:'connected original OSM mass component by world-space vertex',counts:removedById});
  refreshDiagnostics();
}