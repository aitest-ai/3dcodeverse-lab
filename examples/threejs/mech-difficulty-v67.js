/** Optional difficulty setting: player/relay incoming hit severity ONLY.
 * Default STANDARD preserves exact original v6.6 damage and enemy AI.
 * A difficulty change is accepted only outside an active mission.
 */
export const DIFFICULTY_PROFILES_V67=Object.freeze({
  training:Object.freeze({label:'練習',playerMultiplier:.70,relayMultiplier:.75}),
  standard:Object.freeze({label:'標準',playerMultiplier:1,relayMultiplier:1}),
  challenge:Object.freeze({label:'挑戰',playerMultiplier:1.25,relayMultiplier:1.2})
});
export const DIFFICULTY_ORDER_V67=Object.freeze(['training','standard','challenge']);
export function applyIncomingDamageV67(raw,level='standard',target='player'){
  if(!Number.isFinite(raw)||raw<=0)return 0;
  const profile=DIFFICULTY_PROFILES_V67[level]||DIFFICULTY_PROFILES_V67.standard;
  const scale=target==='relay'?profile.relayMultiplier:profile.playerMultiplier;
  return Math.max(1,Math.min(9999,Math.ceil(raw*scale)));
}
export function nextDifficultyV67(level='standard'){
  const i=DIFFICULTY_ORDER_V67.indexOf(level);
  return DIFFICULTY_ORDER_V67[(i+1)%DIFFICULTY_ORDER_V67.length]||'training';
}
