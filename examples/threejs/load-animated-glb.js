/**
 * ESM helper for web systems already using Three.js.
 *
 * Install: npm install three
 * Include /public/models/<asset_id>.glb in your project.
 * No Blender or AI API calls are needed at game runtime.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/**
 * @param {string} url - an HTTP(S) URL/path to a GLB file
 * @param {THREE.Scene|THREE.Group} parent - target scene
 * @returns {Promise<{object: THREE.Group, animationNames: string[],
 *            play: (name:string,fade?:number)=>void, update:(dt:number)=>void,
 *            stop:()=>void, dispose:()=>void}>}
 */
export async function loadAnimatedGLB(url, parent) {
  if (!parent || !parent.add) {
    throw new TypeError('A Three.js Scene or Group is required');
  }
  const gltf = await new GLTFLoader().loadAsync(url);
  parent.add(gltf.scene);
  const mixer = new THREE.AnimationMixer(gltf.scene);
  const actions = new Map();
  for (const clip of gltf.animations) {
    actions.set(clip.name, mixer.clipAction(clip));
  }
  let active = null;

  function lookup(name) {
    if (actions.has(name)) return actions.get(name);
    const matching = Array.from(actions.entries()).filter(([key]) => key.endsWith('_' + name));
    if (matching.length === 1) return matching[0][1];
    throw new Error('Animation clip not found/ambiguous: ' + name +
      '. Available: ' + [...actions.keys()].join(', '));
  }

  function play(name, fade = 0.15) {
    const next = lookup(name);
    if (active === next) return;
    next.reset().setLoop(THREE.LoopRepeat, Infinity).play();
    if (active) next.crossFadeFrom(active, fade, false);
    active = next;
  }

  return {
    object: gltf.scene,
    animationNames: [...actions.keys()],
    play,
    update(deltaSeconds) {
      // Call exactly once per rendered frame.
      mixer.update(Math.min(Math.max(deltaSeconds, 0), 0.1));
    },
    stop() {
      mixer.stopAllAction();
      active = null;
    },
    dispose() {
      mixer.stopAllAction();
      mixer.uncacheRoot(gltf.scene);
      parent.remove(gltf.scene);
      // Mesh, texture and material GPU disposal belongs to the caller,
      // because some apps deliberately share these assets between models.
    },
  };
}
