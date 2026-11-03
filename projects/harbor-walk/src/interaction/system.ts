import { NPC } from "../npc/npc";
import { Vector3, Raycaster, Object3D } from "three";
export class InteractionSystem {
  ray = new Raycaster();
  nearest(player: Vector3, npcs: NPC[], walls: Object3D[]): NPC | undefined {
    return npcs
      .filter((n) => {
        const d = n.character.root.position.clone().sub(player);
        if (d.length() > 2.65) return false;
        this.ray.set(
          player.clone().add(new Vector3(0, 1, 0)),
          d.clone().normalize(),
        );
        this.ray.far = d.length();
        return this.ray.intersectObjects(walls, false).length === 0;
      })
      .sort(
        (a, b) =>
          a.character.root.position.distanceToSquared(player) -
          b.character.root.position.distanceToSquared(player),
      )[0];
  }
}
