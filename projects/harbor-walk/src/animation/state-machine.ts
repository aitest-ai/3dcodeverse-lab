import {
  AnimationMixer,
  AnimationClip,
  AnimationAction,
  Object3D,
  LoopRepeat,
  MathUtils,
} from "three";
export class Animator {
  mixer: AnimationMixer;
  actions = new Map<string, AnimationAction>();
  state = "";
  active?: AnimationAction;
  constructor(root: Object3D, clips: AnimationClip[]) {
    this.mixer = new AnimationMixer(root);
    for (const clip of clips)
      this.actions.set(clip.name, this.mixer.clipAction(clip));
    for (const name of ["Idle", "Walk", "Run"])
      if (!this.actions.has(name))
        throw new Error(`角色缺少必要骨架動畫：${name}`);
    this.play("Idle");
  }
  play(name: string) {
    if (this.state === name) return;
    const next = this.actions.get(name);
    if (!next) throw new Error(`Animation unavailable: ${name}`);
    next.reset().setLoop(LoopRepeat, Infinity).play();
    if (this.active) next.crossFadeFrom(this.active, 0.22, false);
    this.active = next;
    this.state = name;
  }
  locomotion(speed: number, turnRate = 0) {
    const next =
      speed > 0.15
        ? speed > 2.4
          ? "Run"
          : "Walk"
        : Math.abs(turnRate) > 1.1 && this.actions.has("Turn")
          ? "Turn"
          : "Idle";
    this.play(next);
    if (this.active)
      this.active.timeScale =
        next === "Walk"
          ? MathUtils.clamp(speed / 1.45, 0.45, 1.7)
          : next === "Run"
            ? MathUtils.clamp(speed / 4.2, 0.6, 1.5)
            : 1;
  }
  update(dt: number) {
    this.mixer.update(dt);
  }
  dispose(root: Object3D) {
    this.mixer.stopAllAction();
    this.mixer.uncacheRoot(root);
  }
}
