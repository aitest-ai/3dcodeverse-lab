/**
 * Taipei Mech v5.2 - authoritatively measured, visual-only inertia.
 * Player movement and collisions never change. No hidden visual root translation.
 */
export function createMechMotion() {
  let last = null, speedFiltered = 0, accelerationFiltered = 0;
  let turnFiltered = 0, pitch = 0, roll = 0, braking = 0;
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const angleDelta = (a, b) => Math.atan2(Math.sin(a-b), Math.cos(a-b));
  function reset() {
    last = null; speedFiltered = 0; accelerationFiltered = 0;
    turnFiltered = 0; pitch = 0; roll = 0; braking = 0;
  }
  function update({dt, position, heading, speed = 0} = {}) {
    const d = Number(dt);
    if (!Number.isFinite(d) || d <= 0 || !position ||
      !Number.isFinite(position.x) || !Number.isFinite(position.z) ||
      !Number.isFinite(heading)) return snapshot();
    const step = clamp(d, 1 / 240, .08);
    const current = {x: position.x, z: position.z, heading};
    if (!last) {
      last = current;
      // First-frame motion state must never synthesize a violent acceleration.
      return snapshot();
    }
    const travel = Math.hypot(current.x - last.x, current.z - last.z);
    const headingChange = angleDelta(heading, last.heading);
    if (travel > Math.max(1.65, step * 35) || Math.abs(headingChange) > 2.6) {
      reset();last = current;
      return snapshot();
    }
    const measuredSpeed = clamp(travel / step, 0, 15);
    const rawAcceleration = clamp((measuredSpeed - speedFiltered) / step, -18, 18);
    const rawTurn = clamp(headingChange / step, -3.5, 3.5);
    const smoothing = 1 - Math.exp(-step * 10);
    const loadSmoothing = 1 - Math.exp(-step * 7);
    speedFiltered += (measuredSpeed - speedFiltered) * smoothing;
    accelerationFiltered += (rawAcceleration - accelerationFiltered) * loadSmoothing;
    turnFiltered += (rawTurn - turnFiltered) * smoothing;
    // Pitch and roll are applied only to spine/head skeleton, not world rig.
    const pitchTarget = clamp(-accelerationFiltered * .009, -.085, .085);
    const rollTarget = clamp(-turnFiltered * (speedFiltered / (speedFiltered + 1.8)) * .042, -.105, .105);
    pitch += (pitchTarget - pitch) * loadSmoothing;
    roll += (rollTarget - roll) * loadSmoothing;
    const brakeTarget = rawAcceleration < -1.9 && speedFiltered < 4.5 ? clamp(-rawAcceleration / 14, 0, 1) : 0;
    braking += (brakeTarget - braking) * (1 - Math.exp(-step * (brakeTarget ? 9 : 4)));
    last = current;
    return snapshot();
  }
  function snapshot() {
    const mode = braking > .38 ? 'brake' :
      Math.abs(turnFiltered) > .65 && speedFiltered > .55 ? 'turn' :
      accelerationFiltered > 2.2 && speedFiltered > .2 ? 'accelerate' :
      speedFiltered > .4 ? 'cruise' : 'idle';
    return {mode, speed: speedFiltered, acceleration: accelerationFiltered,
      yawRate: turnFiltered, pitch, roll, braking};
  }
  return {update, reset, snapshot};
}
