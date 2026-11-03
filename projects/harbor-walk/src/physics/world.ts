import RAPIER from "@dimforge/rapier3d-compat";
import { Vector3 } from "three";
export class PhysicsWorld {
  world: RAPIER.World;
  constructor() {
    this.world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
    this.world.timestep = 1 / 60;
  }
  static async create() {
    await RAPIER.init();
    return new PhysicsWorld();
  }
  box(x: number, y: number, z: number, w: number, h: number, d: number) {
    return this.world.createCollider(
      RAPIER.ColliderDesc.cuboid(w / 2, h / 2, d / 2).setTranslation(x, y, z),
    );
  }
  actor(position: Vector3) {
    const body = this.world.createRigidBody(
      RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(
        position.x,
        position.y + 0.92,
        position.z,
      ),
    );
    const collider = this.world.createCollider(
      RAPIER.ColliderDesc.capsule(0.57, 0.32).setFriction(0),
      body,
    );
    const controller = this.world.createCharacterController(0.015);
    controller.enableAutostep(0.25, 0.15, true);
    controller.enableSnapToGround(0.25);
    controller.setMaxSlopeClimbAngle(Math.PI / 4);
    controller.setMinSlopeSlideAngle(Math.PI / 3);
    return { body, collider, controller, vertical: 0, grounded: false };
  }
  move(
    actor: ReturnType<PhysicsWorld["actor"]>,
    displacement: Vector3,
    dt: number,
  ) {
    actor.vertical = Math.max(-25, actor.vertical - 9.81 * dt);
    actor.controller.computeColliderMovement(
      actor.collider,
      { x: displacement.x, y: actor.vertical * dt, z: displacement.z },
      RAPIER.QueryFilterFlags.EXCLUDE_KINEMATIC,
    );
    const m = actor.controller.computedMovement();
    const p = actor.body.translation();
    actor.body.setNextKinematicTranslation({
      x: p.x + m.x,
      y: p.y + m.y,
      z: p.z + m.z,
    });
    actor.grounded = actor.controller.computedGrounded();
    if (actor.grounded) actor.vertical = 0;
  }
  step() {
    this.world.step();
  }
  dispose() {
    this.world.free();
  }
}
