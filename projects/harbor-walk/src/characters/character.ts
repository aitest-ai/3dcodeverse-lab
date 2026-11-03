import {
  Group,
  Vector3,
  Mesh,
  MeshStandardMaterial,
  MathUtils,
  SkinnedMesh,
} from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { clone } from "three/addons/utils/SkeletonUtils.js";
import { Animator } from "../animation/state-machine";
import { PhysicsWorld } from "../physics/world";
import { Input } from "../core/input";
export class Character {
  root = new Group();
  visual: Group;
  animator: Animator;
  velocity = new Vector3();
  heading = 0;
  turnRate = 0;
  distance = 0;
  actor: ReturnType<PhysicsWorld["actor"]>;
  last = new Vector3();
  static async loadTemplate(progress: (n: number) => void) {
    const gltf = await new GLTFLoader().loadAsync(
      `${import.meta.env.BASE_URL}models/harbor-courier.glb`,
      (e) => progress(e.total ? e.loaded / e.total : 0.5),
    );
    let skins = 0;
    gltf.scene.traverse((o) => {
      if ((o as SkinnedMesh).isSkinnedMesh) skins++;
    });
    if (!skins) throw new Error("需要真正的 SkinnedMesh，角色資產載入中止");
    return gltf;
  }
  constructor(
    template: Awaited<ReturnType<typeof Character.loadTemplate>>,
    physics: PhysicsWorld,
    position: Vector3,
    tint?: number,
  ) {
    this.visual = clone(template.scene) as Group;
    this.root.add(this.visual);
    this.visual.traverse((o) => {
      if ((o as Mesh).isMesh) {
        const m = o as Mesh;
        m.castShadow = true;
        m.receiveShadow = true;
        if (tint && /jacket|shirt|coat|outfit/i.test(m.name)) {
          m.material = (m.material as MeshStandardMaterial).clone();
          (m.material as MeshStandardMaterial).color.set(tint);
        }
      }
    });
    this.animator = new Animator(this.visual, template.animations);
    this.actor = physics.actor(position);
    this.root.position.copy(position);
    this.last.copy(position);
  }
  sync() {
    const p = this.actor.body.translation();
    this.root.position.set(p.x, p.y - 0.86, p.z);
    this.distance += this.root.position.distanceTo(this.last);
    this.last.copy(this.root.position);
  }
  steer(direction: Vector3, speed: number, physics: PhysicsWorld, dt: number) {
    const target = direction.clone().multiplyScalar(speed);
    this.velocity.lerp(target, 1 - Math.exp(-(speed ? 9 : 14) * dt));
    if (this.velocity.length() > 0.08) {
      const desired = Math.atan2(this.velocity.x, this.velocity.z);
      const delta = Math.atan2(
        Math.sin(desired - this.heading),
        Math.cos(desired - this.heading),
      );
      this.turnRate = delta / dt;
      this.heading += delta * (1 - Math.exp(-12 * dt));
    } else this.turnRate = 0;
    this.root.rotation.y = this.heading;
    physics.move(this.actor, this.velocity.clone().multiplyScalar(dt), dt);
    this.animator.locomotion(this.velocity.length(), this.turnRate);
  }
  player(
    input: Input,
    yaw: number,
    physics: PhysicsWorld,
    dt: number,
    blocked: boolean,
  ) {
    const x = blocked
      ? 0
      : Number(input.down("KeyD", "ArrowRight")) -
        Number(input.down("KeyA", "ArrowLeft"));
    const z = blocked
      ? 0
      : Number(input.down("KeyS", "ArrowDown")) -
        Number(input.down("KeyW", "ArrowUp"));
    const direction = new Vector3(x, 0, z)
      .normalize()
      .applyAxisAngle(new Vector3(0, 1, 0), yaw);
    if (!blocked && input.consume("Space") && this.actor.grounded)
      this.actor.vertical = 4.5;
    this.steer(
      direction,
      x || z ? (input.down("ShiftLeft", "ShiftRight") ? 4.2 : 1.45) : 0,
      physics,
      dt,
    );
  }
  face(point: Vector3, dt: number) {
    const d = point.clone().sub(this.root.position);
    const a = Math.atan2(d.x, d.z);
    this.heading +=
      Math.atan2(Math.sin(a - this.heading), Math.cos(a - this.heading)) *
      (1 - Math.exp(-5 * dt));
    this.root.rotation.y = this.heading;
  }
}
