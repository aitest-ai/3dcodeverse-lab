import { Vector3 } from "three";
import { Character } from "../characters/character";
import { PhysicsWorld } from "../physics/world";
export class NPC {
  index = 0;
  waiting = 0;
  state = "patrol";
  celebrate = 0;
  constructor(
    public id: string,
    public name: string,
    public role: string,
    public character: Character,
    public route: Vector3[],
  ) {}
  update(
    player: Vector3,
    physics: PhysicsWorld,
    dt: number,
    dialogue: boolean,
  ) {
    if (this.celebrate > 0) {
      this.celebrate -= dt;
      this.character.steer(new Vector3(), 0, physics, dt);
      this.character.animator.play("Celebrate");
      return;
    }
    const p = this.character.root.position;
    const near = p.distanceTo(player) < 2.8;
    if (near || dialogue) {
      this.state = "attention";
      this.character.steer(new Vector3(), 0, physics, dt);
      this.character.face(player, dt);
      if (dialogue) this.character.animator.play("Talk");
      return;
    }
    if (this.waiting > 0) {
      this.state = "idle";
      this.waiting -= dt;
      this.character.steer(new Vector3(), 0, physics, dt);
      return;
    }
    const target = this.route[this.index];
    const d = target.clone().sub(p);
    d.y = 0;
    if (d.length() < 0.25) {
      this.index = (this.index + 1) % this.route.length;
      this.waiting = 2;
    }
    this.state = "patrol";
    this.character.steer(d.normalize(), 0.85, physics, dt);
  }
}
