/**
 * Taipei Mech v6.2 actual skinned GLB enemy visuals.
 * Does not own collisions, AI, HP, weapon rays or enemy positions. The game
 * keeps its original fallback meshes if loading fails or is unsupported.
 * Textures/materials are shared between clones and disposed only on shutdown.
 */
export const ENEMY_ASSETS_V62 = Object.freeze({
  assault:'enemy_assault_v62.glb',
  ranger:'enemy_ranger_v62.glb',
  heavy:'enemy_heavy_v62.glb'
});

export function createEnemyVisualLoaderV62({THREE,loaderFactory=null,cloneFactory=null,onStatus=()=>{}}={}) {
  const roles=Object.keys(ENEMY_ASSETS_V62);
  const templates=new Map(), loading=new Map(), instances=new Set();
  let disposed=false;
  const safeStatus=(role,s)=>{try{onStatus(role,s);}catch{}};
  async function runtime(){
    const loader=loaderFactory ? await loaderFactory() :
      new (await import('three/addons/loaders/GLTFLoader.js')).GLTFLoader();
    const clone=cloneFactory || (await import('three/addons/utils/SkeletonUtils.js')).clone;
    return {loader,clone};
  }
  let ready=null;
  async function loadRole(role){
    if(!roles.includes(role)||disposed)return null;
    if(templates.has(role))return templates.get(role);
    if(loading.has(role))return loading.get(role);
    const promise=(async()=>{
      try{
        if(!ready)ready=runtime();
        const {loader,clone}=await ready;
        // Module-relative URL: works on both https:// and local city folder.
        const url=new URL('../models/'+ENEMY_ASSETS_V62[role],import.meta.url).href;
        const gltf=await loader.loadAsync(url);
        if(disposed)return null;
        if(!gltf?.scene||!Array.isArray(gltf.animations)||gltf.animations.length<6)
          throw new Error('GLB scene or six original action clips missing');
        const names=new Set(gltf.animations.map(a=>a.name));
        for(const name of ['Mecha_Idle','Mecha_Run','Mecha_Fire','Mecha_Hit','Mecha_Dodge','Mecha_Punch'])
          if(!names.has(name))throw new Error('Missing '+name);
        const entry={gltf,clone};templates.set(role,entry);
        safeStatus(role,'loaded');return entry;
      }catch(error){safeStatus(role,'fallback:'+String(error?.message||error));return null;}
      finally{loading.delete(role);}
    })();
    loading.set(role,promise);return promise;
  }
  function createEntry(enemy,entry){
    if(disposed||!enemy?.mesh?.parent||enemy.dead||enemy._v62)return false;
    const visual=entry.clone(entry.gltf.scene);
    visual.name='EnemyV62_'+enemy.role;
    visual.rotation.y=Math.PI;
    visual.scale.setScalar(1.32);
    enemy.mesh.add(visual);
    const mixer=new THREE.AnimationMixer(visual),actions=new Map();
    // The authoritative OSM controller already animates world-space movement.
    // Remove GLB root position tracks from enemy clips to avoid drift/teleport.
    for(const source of entry.gltf.animations){
      const clip=source.clone();
      clip.tracks=clip.tracks.filter(track =>
        !(track.name.toLowerCase().includes('root')&&track.name.endsWith('.position')));
      const short=clip.name.replace(/^Mecha_/, '');
      actions.set(short,mixer.clipAction(clip));
    }
    const first=actions.get('Idle');if(first)first.reset().play();
    const state={enemy,visual,mixer,actions,current:'Idle'};
    enemy._v62=state;enemy.torso.visible=false;instances.add(state);
    return true;
  }
  function attach(enemy){
    if(disposed||!enemy||!roles.includes(enemy.role))return;
    if(templates.has(enemy.role)){createEntry(enemy,templates.get(enemy.role));return;}
    loadRole(enemy.role).then(entry=>{if(entry)createEntry(enemy,entry);});
  }
  function update(enemy,dt,{moving=false,firing=false}={}){
    const v=enemy?._v62;if(!v||disposed)return;
    const next=firing?'Fire':moving?'Run':'Idle';
    if(v.current!==next){
      const action=v.actions.get(next),prev=v.actions.get(v.current);
      if(action){action.reset().play();if(prev&&prev!==action)action.crossFadeFrom(prev,.15,false);v.current=next;}
    }
    v.mixer.update(Math.max(0,Math.min(Number.isFinite(dt)?dt:0,.05)));
  }
  function detach(enemy){
    const v=enemy?._v62;if(!v)return;
    v.mixer.stopAllAction();v.mixer.uncacheRoot(v.visual);
    enemy.mesh.remove(v.visual);
    enemy.torso.visible=true;enemy._v62=null;instances.delete(v);
  }
  async function preload(){
    if(disposed)return;
    await Promise.all(roles.map(loadRole));
  }
  function status(){return {loaded:[...templates.keys()],pending:[...loading.keys()],activeClones:instances.size,disposed};}
  function dispose(){
    if(disposed)return;
    for(const {enemy} of [...instances])detach(enemy);
    disposed=true;
    for(const entry of templates.values()){
      const geometries=new Set(),materials=new Set(),textures=new Set();
      entry.gltf.scene.traverse(o=>{
        if(o.geometry)geometries.add(o.geometry);
        const mats=o.material?Array.isArray(o.material)?o.material:[o.material]:[];
        for(const m of mats){materials.add(m);
          for(const v of Object.values(m))if(v?.isTexture)textures.add(v);
        }
      });
      geometries.forEach(g=>g.dispose());textures.forEach(t=>t.dispose());materials.forEach(m=>m.dispose());
    }
    templates.clear();loading.clear();
  }
  return {preload,attach,update,detach,status,dispose,loadRole};
}
