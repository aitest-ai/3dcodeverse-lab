import { retainVerticalGroundingV63 } from './mech-root-motion-v63.js';
import { createEnemyActionDirectorV63 } from './mech-enemy-action-v63.js';
/**
 * Taipei Mech v6.3 event-synchronized skinned GLB enemy visuals.
 * Does not own collisions, AI, HP, weapon rays or enemy positions. The game
 * keeps its original fallback meshes if loading fails or is unsupported.
 * Textures/materials are shared between clones and disposed only on shutdown.
 */
export const ENEMY_ASSETS_V63 = Object.freeze({
  assault:'enemy_assault_v63.glb',
  ranger:'enemy_ranger_v63.glb',
  heavy:'enemy_heavy_v63.glb'
});

export function createEnemyVisualLoaderV63({THREE,loaderFactory=null,cloneFactory=null,onStatus=()=>{}}={}) {
  const roles=Object.keys(ENEMY_ASSETS_V63);
  const previousAssets={assault:'enemy_assault_v62.glb',ranger:'enemy_ranger_v62.glb',heavy:'enemy_heavy_v62.glb'};
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
        // If the verified new GLB is unavailable, try the previous equally
        // detailed v6.2 GLB before falling back to the old procedural model.
        let gltf=null,selected='none',lastError=null;
        for(const [version,name] of [['v63',ENEMY_ASSETS_V63[role]],['v62',previousAssets[role]]]){
          try{
            const url=new URL('../models/'+name,import.meta.url).href;
            const candidate=await loader.loadAsync(url);
            if(!candidate?.scene||!Array.isArray(candidate.animations)||candidate.animations.length<6)
              throw new Error('GLB missing scene or six clips');
            const names=new Set(candidate.animations.map(a=>a.name));
            for(const required of ['Mecha_Idle','Mecha_Run','Mecha_Fire','Mecha_Hit','Mecha_Dodge','Mecha_Punch'])
              if(!names.has(required))throw new Error('Missing '+required);
            gltf=candidate;selected=version;break;
          }catch(error){lastError=error;}
        }
        if(disposed)return null;
        if(!gltf)throw lastError??new Error('No valid GLB');
        const entry={gltf,clone,version:selected};templates.set(role,entry);
        safeStatus(role,'loaded:'+selected);return entry;
      }catch(error){safeStatus(role,'fallback:'+String(error?.message||error));return null;}
      finally{loading.delete(role);}
    })();
    loading.set(role,promise);return promise;
  }
  function createEntry(enemy,entry){
    if(disposed||!enemy?.mesh?.parent||enemy.dead||enemy._v63)return false;
    const visual=entry.clone(entry.gltf.scene);
    visual.name='EnemyV62_'+enemy.role;
    visual.rotation.y=Math.PI;
    visual.scale.setScalar(1.32); // parent uses role profile.scale; gameplay collider unchanged
    enemy.mesh.add(visual);
    const mixer=new THREE.AnimationMixer(visual),actions=new Map();
    // The authoritative OSM controller already animates world-space movement.
    // Remove GLB root position tracks from enemy clips to avoid drift/teleport.
    for(const source of entry.gltf.animations){
      const clip=source.clone();
      retainVerticalGroundingV63(clip);
      const short=clip.name.replace(/^Mecha_/, '');
      actions.set(short,mixer.clipAction(clip));
    }
    const director=createEnemyActionDirectorV63(actions,{loopOnce:THREE.LoopOnce??null});
    const state={enemy,visual,mixer,actions,director};
    enemy._v63=state;enemy.torso.visible=false;instances.add(state);
    return true;
  }
  function attach(enemy){
    if(disposed||!enemy||!roles.includes(enemy.role))return;
    if(templates.has(enemy.role)){createEntry(enemy,templates.get(enemy.role));return;}
    loadRole(enemy.role).then(entry=>{if(entry)createEntry(enemy,entry);});
  }
  // A real FIRE occurs only when a shot is released, not during telegraph.
  // Damage received from the player's original combat HP pipeline starts Hit.
  function update(enemy,dt,{moving=false,shot=false}={}){
    const v=enemy?._v63;if(!v||disposed)return;
    v.director.update(dt,{moving,shot,health:enemy.hp});
    v.mixer.update(Math.max(0,Math.min(Number.isFinite(dt)?dt:0,.05)));
  }
  function detach(enemy){
    const v=enemy?._v63;if(!v)return;
    v.mixer.stopAllAction();v.mixer.uncacheRoot(v.visual);
    enemy.mesh.remove(v.visual);
    enemy.torso.visible=true;enemy._v63=null;instances.delete(v);
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
