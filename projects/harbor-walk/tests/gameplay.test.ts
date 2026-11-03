import { test } from "node:test";
import assert from "node:assert/strict";
import { Quest } from "../src/gameplay/quest";
import { PhysicsWorld } from "../src/physics/world";
import {
  Vector3,
  PerspectiveCamera,
  Mesh,
  BoxGeometry,
  MeshBasicMaterial,
} from "three";
import { ThirdPersonCamera } from "../src/camera/third-person";
import { Input } from "../src/core/input";
test("quest rejects early delivery, collection before acceptance, invalid/duplicate stamps and duplicate rewards", () => {
  const q = new Quest();
  assert.equal(q.deliver(), false);
  assert.equal(q.collect("tea"), false);
  assert.equal(q.accept(), true);
  assert.equal(q.accept(), false);
  assert.equal(q.collect("unknown"), false);
  assert.equal(q.collect("tea"), true);
  assert.equal(q.collect("tea"), false);
  assert.equal(q.score, 25);
  assert.equal(q.deliver(), false);
  q.collect("garden");
  q.collect("pier");
  assert.equal(q.state, "deliver");
  assert.equal(q.deliver(), true);
  assert.equal(q.score, 150);
  assert.equal(q.deliver(), false);
  assert.equal(q.collect("tea"), false);
  assert.equal(q.score, 150);
});
test("quest timer freezes before acceptance and after completion", () => {
  const q = new Quest();
  q.update(5);
  assert.equal(q.elapsed, 0);
  q.accept();
  q.update(2);
  q.collect("tea");
  q.collect("pier");
  q.collect("garden");
  q.update(3);
  q.deliver();
  q.update(9);
  assert.equal(q.elapsed, 5);
});
test("real Rapier capsule falls, grounds, collides with a wall and slides along it", async () => {
  const p = await PhysicsWorld.create();
  p.box(0, -0.25, 0, 30, 0.5, 30);
  p.box(0, 1, -2, 12, 2, 0.4);
  const actor = p.actor(new Vector3(0, 2, 0));
  for (let i = 0; i < 180; i++) {
    p.move(actor, new Vector3(), 1 / 60);
    p.step();
  }
  assert.equal(actor.grounded, true);
  assert.ok(Math.abs(actor.body.translation().y - 0.905) < 0.03);
  for (let i = 0; i < 240; i++) {
    p.move(actor, new Vector3(0.01, 0, -0.05), 1 / 60);
    p.step();
  }
  assert.ok(
    actor.body.translation().z > -1.51,
    "capsule must not cross front of wall",
  );
  assert.ok(actor.body.translation().x > 2, "capsule should slide along wall");
  p.dispose();
});
test("camera retracts in front of solid geometry and recovers when clear", () => {
  const camera = new PerspectiveCamera(50, 1, 0.1, 100);
  const wall = new Mesh(new BoxGeometry(5, 5, 0.4), new MeshBasicMaterial());
  wall.position.set(0, 1.5, 2);
  wall.updateMatrixWorld(true);
  const rig = new ThirdPersonCamera(camera, [wall]);
  rig.pitch = 0;
  const input = { lookX: 0, lookY: 0, zoom: 0 } as Input;
  rig.update(input, new Vector3(), 0.1, true);
  assert.ok(rig.actualDistance < 1.6);
  assert.ok(camera.position.z < 1.6);
  rig.obstacles = [];
  for (let i = 0; i < 60; i++) rig.update(input, new Vector3(), 1 / 60, true);
  assert.ok(rig.actualDistance > 5.4);
});
