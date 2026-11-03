import * as T from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { PhysicsWorld } from "../physics/world";
import { Input } from "./input";
import { Harbor } from "../world/harbor";
import { Character } from "../characters/character";
import { ThirdPersonCamera } from "../camera/third-person";
import { NPC } from "../npc/npc";
import { InteractionSystem } from "../interaction/system";
import { Quest } from "../gameplay/quest";
import { HUD, el } from "../ui/hud";
export class Game {
  renderer: T.WebGLRenderer;
  scene = new T.Scene();
  camera = new T.PerspectiveCamera(48, innerWidth / innerHeight, 0.08, 180);
  input: Input;
  physics!: PhysicsWorld;
  harbor!: Harbor;
  player!: Character;
  npcs: NPC[] = [];
  cameraRig!: ThirdPersonCamera;
  quest = new Quest();
  hud = new HUD(this.quest);
  interaction = new InteractionSystem();
  accumulator = 0;
  last = 0;
  time = 0;
  running = false;
  quality = "standard";
  frameTimes: number[] = [];
  nearest?: NPC;
  frames = 0;
  interactions = 0;
  constructor() {
    this.renderer = new T.WebGLRenderer({
      canvas: el<HTMLCanvasElement>("game"),
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    this.renderer.setSize(innerWidth, innerHeight);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = T.PCFSoftShadowMap;
    this.renderer.outputColorSpace = T.SRGBColorSpace;
    this.renderer.toneMapping = T.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.95;
    this.scene.background = new T.Color("#bbd1c8");
    this.scene.fog = new T.Fog("#bbd1c8", 35, 95);
    const pmrem = new T.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(
      new RoomEnvironment(),
      0.04,
    ).texture;
    pmrem.dispose();
    this.scene.environmentIntensity = 0.45;
    const hemi = new T.HemisphereLight("#e4efdc", "#b6a57b", 1.1);
    this.scene.add(hemi);
    const sun = new T.DirectionalLight("#ffe8bc", 2.5);
    sun.position.set(-13, 22, 14);
    sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048);
    sun.shadow.camera.left = -23;
    sun.shadow.camera.right = 23;
    sun.shadow.camera.top = 22;
    sun.shadow.camera.bottom = -22;
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 65;
    sun.shadow.normalBias = 0.025;
    sun.shadow.bias = -0.0002;
    this.scene.add(sun);
    this.input = new Input(this.renderer.domElement);
    window.addEventListener("resize", () => {
      this.renderer.setSize(innerWidth, innerHeight);
      this.camera.aspect = innerWidth / innerHeight;
      this.camera.updateProjectionMatrix();
    });
    document.addEventListener("visibilitychange", () => {
      this.input.clear();
      this.accumulator = 0;
      this.last = performance.now();
    });
    el("quality").onclick = () => {
      this.quality = this.quality === "standard" ? "low" : "standard";
      const low = this.quality === "low";
      this.renderer.setPixelRatio(Math.min(devicePixelRatio, low ? 0.75 : 1.5));
      this.renderer.shadowMap.enabled = !low;
      sun.shadow.mapSize.set(low ? 1024 : 2048, low ? 1024 : 2048);
      sun.shadow.map?.dispose();
      sun.shadow.map = null;
      el("quality").textContent = `畫質：${low ? "省電" : "標準"}`;
    };
  }
  async load() {
    this.physics = await PhysicsWorld.create();
    el("load-fill").style.width = "18%";
    el("load-status").textContent = "正在鋪好港邊的石板路…";
    this.harbor = new Harbor(this.physics);
    this.scene.add(this.harbor.root);
    el("load-status").textContent = "正在準備角色與骨架動畫…";
    const template = await Character.loadTemplate(
      (n) => (el("load-fill").style.width = `${25 + Math.round(n * 60)}%`),
    );
    this.player = new Character(
      template,
      this.physics,
      new T.Vector3(0, 0.08, 5),
    );
    this.player.heading = Math.PI;
    this.scene.add(this.player.root);
    const guide = new Character(
      template,
      this.physics,
      new T.Vector3(-2, 0.08, 1),
      0xd0ad78,
    );
    const keeper = new Character(
      template,
      this.physics,
      new T.Vector3(7, 0.08, -6),
      0x538485,
    );
    this.npcs = [
      new NPC("guide", "阿澄", "街區嚮導", guide, [
        new T.Vector3(-2, 0, 1),
        new T.Vector3(-3, 0, -1),
        new T.Vector3(-1, 0, -1),
      ]),
      new NPC("keeper", "阿青", "潮間書店", keeper, [
        new T.Vector3(7, 0, -6),
        new T.Vector3(5.5, 0, -6),
        new T.Vector3(5.5, 0, -5),
      ]),
    ];
    for (const n of this.npcs) this.scene.add(n.character.root);
    this.cameraRig = new ThirdPersonCamera(this.camera, this.harbor.obstacles);
    this.cameraRig.yaw = -0.3;
    this.cameraRig.pitch = 0.3;
    this.cameraRig.distance = 7;
    el("load-fill").style.width = "100%";
    el("loading").hidden = true;
    el("intro").hidden = false;
    el("start").onclick = () => {
      this.hud.start();
      this.input.clear();
      this.renderer.domElement.focus();
      this.cameraRig.yaw = 0;
      this.cameraRig.distance = 5.5;
    };
    this.running = true;
    this.last = performance.now();
    requestAnimationFrame(this.frame);
    // Read-only observations for browser QA. No teleport, task completion or input injection API.
    Object.defineProperty(window, "__harbor", {
      value: Object.freeze({ snapshot: () => this.snapshot() }),
      configurable: false,
    });
  }
  snapshot() {
    return {
      ready: this.running,
      started: this.hud.started,
      position: this.player.root.position.toArray(),
      velocity: this.player.velocity.toArray(),
      heading: this.player.heading,
      bones: ["upperarm_l", "thigh_l", "calf_l"].map((name) => {
        const bone = this.player.visual.getObjectByName(name);
        return { name, q: bone?.quaternion.toArray() };
      }),
      grounded: this.player.actor.grounded,
      animation: this.player.animator.state,
      animationTime: this.player.animator.active?.time,
      quest: this.quest.state,
      collected: [...this.quest.collected],
      score: this.quest.score,
      distance: this.player.distance,
      camera: {
        yaw: this.cameraRig.yaw,
        pitch: this.cameraRig.pitch,
        distance: this.cameraRig.actualDistance,
        desiredDistance: this.cameraRig.distance,
      },
      dialogue: this.hud.dialogue,
      interactions: this.interactions,
      npcs: this.npcs.map((n) => ({
        id: n.id,
        position: n.character.root.position.toArray(),
        state: n.state,
        animation: n.character.animator.state,
      })),
      frames: this.frames,
      render: {
        calls: this.renderer.info.render.calls,
        triangles: this.renderer.info.render.triangles,
        geometries: this.renderer.info.memory.geometries,
        textures: this.renderer.info.memory.textures,
      },
      frameMs: this.frameTimes.slice(-300),
      quality: this.quality,
    };
  }
  frame = (now: number) => {
    if (!this.running) return;
    const raw = (now - this.last) / 1000;
    this.last = now;
    const dt = Math.min(raw, 0.08);
    this.time += dt;
    if (this.hud.started && this.input.consume("Escape")) {
      this.hud.close();
      el("help-panel").hidden = true;
    }
    const blocked =
      !this.hud.started || this.hud.dialogue || this.hud.completion;
    this.accumulator += dt;
    while (this.accumulator >= 1 / 60) {
      this.player.player(
        this.input,
        this.cameraRig.yaw,
        this.physics,
        1 / 60,
        blocked,
      );
      for (const n of this.npcs)
        n.update(
          this.player.root.position,
          this.physics,
          1 / 60,
          this.hud.dialogue && this.nearest?.id === n.id,
        );
      this.physics.step();
      this.player.sync();
      this.npcs.forEach((n) => n.character.sync());
      this.accumulator -= 1 / 60;
      if (!blocked) this.quest.update(1 / 60);
    }
    this.nearest = this.interaction.nearest(
      this.player.root.position,
      this.npcs,
      this.harbor.obstacles,
    );
    if (!blocked && this.input.consume("KeyE") && this.nearest) {
      this.interactions++;
      this.hud.talk(this.nearest);
      this.nearest.character.animator.play("Talk");
    }
    for (const s of this.harbor.stamps) {
      s.object.visible =
        this.quest.state === "collecting" && !this.quest.collected.has(s.id);
      if (
        !blocked &&
        this.player.root.position.distanceTo(s.position) < 0.95 &&
        this.quest.collect(s.id)
      ) {
        this.hud.toast(`${s.label}已收集 · +25 旅途點數`);
        s.object.visible = false;
      }
    }
    this.harbor.update(this.time);
    this.player.animator.update(dt);
    this.npcs.forEach((n) => n.character.animator.update(dt));
    this.cameraRig.update(
      this.input,
      this.player.root.position,
      dt,
      !this.hud.dialogue,
    );
    this.hud.update(
      this.player.root.position,
      this.npcs,
      this.harbor.stamps,
      this.camera,
      this.nearest,
    );
    this.renderer.render(this.scene, this.camera);
    this.input.endFrame();
    this.frames++;
    if (this.hud.started && !document.hidden) {
      this.frameTimes.push(raw * 1000);
      if (this.frameTimes.length > 1800) this.frameTimes.shift();
    }
    requestAnimationFrame(this.frame);
  };
}
