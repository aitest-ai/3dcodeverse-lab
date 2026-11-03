import * as T from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { Character } from "./characters/character";
import { Animator } from "./animation/state-machine";
const status = document.getElementById("status")!;
async function boot() {
  const renderer = new T.WebGLRenderer({
    canvas: document.getElementById("view") as HTMLCanvasElement,
    antialias: true,
  });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  const scene = new T.Scene();
  scene.background = new T.Color("#e9e5d6");
  scene.add(new T.HemisphereLight("#eaf2dc", "#aba385", 2));
  const key = new T.DirectionalLight("#fff1d0", 3);
  key.position.set(3, 5, 5);
  scene.add(key);
  const rim = new T.DirectionalLight("#dee9ec", 1);
  rim.position.set(-3, 3, -3);
  scene.add(rim);
  const camera = new T.PerspectiveCamera(
    32,
    innerWidth / innerHeight,
    0.01,
    60,
  );
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 0.95, 0);
  camera.position.set(0, 1, 4.3);
  controls.update();
  const floor = new T.Mesh(
    new T.CircleGeometry(2.3, 64),
    new T.MeshStandardMaterial({ color: "#c7cbb6", roughness: 1 }),
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.04;
  scene.add(floor);
  const gltf = await Character.loadTemplate(() => {});
  scene.add(gltf.scene);
  const animator = new Animator(gltf.scene, gltf.animations);
  let selected = "Idle";
  document.getElementById("clip")!.onchange = (e) => {
    selected = (e.target as HTMLSelectElement).value;
    animator.play(selected);
  };
  for (const button of document.querySelectorAll<HTMLButtonElement>(
    "[data-view]",
  ))
    button.onclick = () => {
      const view = button.dataset.view!;
      controls.target.set(0, view === "face" ? 1.66 : 0.95, 0);
      camera.position.set(
        ...(
          {
            front: [0, 1.05, 4.3],
            side: [4.3, 1.05, 0],
            back: [0, 1.05, -4.3],
            face: [0, 1.68, 0.78],
          } as Record<string, [number, number, number]>
        )[view],
      );
      controls.update();
    };
  document.getElementById("smile")!.oninput = (e) => {
    const value = Number((e.target as HTMLInputElement).value);
    gltf.scene.traverse((o) => {
      const m = o as T.Mesh;
      if (m.morphTargetDictionary?.Smile !== undefined)
        m.morphTargetInfluences![m.morphTargetDictionary.Smile] = value;
    });
  };
  status.textContent = `65 根骨架 · ${gltf.animations.length} 段動畫 · 1 個表情控制\n真 GLB 即時渲染 · 美術候選，尚未通過商用品質驗收`;
  Object.defineProperty(window, "__atelier", {
    value: {
      snapshot: () => ({
        selected,
        time: animator.active?.time,
        bones: ["upperarm_l", "thigh_l", "calf_l"].map((name) => ({
          name,
          q: gltf.scene.getObjectByName(name)?.quaternion.toArray(),
        })),
        smile: (document.getElementById("smile") as HTMLInputElement).value,
      }),
    },
  });
  const clock = new T.Clock();
  function frame() {
    requestAnimationFrame(frame);
    animator.update(Math.min(clock.getDelta(), 0.1));
    controls.update();
    renderer.render(scene, camera);
  }
  frame();
  addEventListener("resize", () => {
    renderer.setSize(innerWidth, innerHeight);
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
  });
}
boot().catch((e) => {
  status.textContent = String(e);
  console.error(e);
});
