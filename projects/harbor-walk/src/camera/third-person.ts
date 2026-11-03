import {
  PerspectiveCamera,
  Vector3,
  Raycaster,
  Object3D,
  MathUtils,
} from "three";
import { Input } from "../core/input";
export class ThirdPersonCamera {
  yaw = 0;
  pitch = 0.24;
  distance = 5.5;
  actualDistance = 5.5;
  target = new Vector3();
  ray = new Raycaster();
  initialized = false;
  constructor(
    public camera: PerspectiveCamera,
    public obstacles: Object3D[],
  ) {}
  update(input: Input, position: Vector3, dt: number, enabled: boolean) {
    if (enabled) {
      this.yaw -= input.lookX * 0.006;
      this.pitch = MathUtils.clamp(
        this.pitch + input.lookY * 0.004,
        -0.12,
        1.05,
      );
      this.distance = MathUtils.clamp(
        this.distance + input.zoom * 0.004,
        2.3,
        9,
      );
    }
    const desiredTarget = position.clone().add(new Vector3(0, 1.4, 0));
    if (!this.initialized) {
      this.target.copy(desiredTarget);
      this.initialized = true;
    }
    this.target.lerp(desiredTarget, 1 - Math.exp(-10 * dt));
    const direction = new Vector3(
      Math.sin(this.yaw) * Math.cos(this.pitch),
      Math.sin(this.pitch),
      Math.cos(this.yaw) * Math.cos(this.pitch),
    );
    this.ray.set(this.target, direction);
    this.ray.far = this.distance + 0.3;
    const hits = this.ray.intersectObjects(this.obstacles, false);
    const safe = hits.length
      ? Math.max(0.12, hits[0].distance - 0.28)
      : this.distance;
    this.actualDistance =
      safe < this.actualDistance
        ? safe
        : MathUtils.lerp(this.actualDistance, safe, 1 - Math.exp(-8 * dt));
    this.camera.position
      .copy(this.target)
      .addScaledVector(direction, this.actualDistance);
    this.camera.lookAt(this.target);
  }
}
