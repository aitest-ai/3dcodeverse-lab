/** Only cosmetic effects are scalable. All GLB geometry, skinning, PBR maps,
 * actual city collisions, AI and weapon damage stay identical in every mode. */
export const VISUAL_QUALITY_V73=Object.freeze({
  full:Object.freeze({label:'完整',shardFactor:1,groundStride:3,wallStride:2,maxParked:24,ringScale:1}),
  balanced:Object.freeze({label:'平衡',shardFactor:.70,groundStride:4,wallStride:3,maxParked:16,ringScale:.85}),
  light:Object.freeze({label:'精簡',shardFactor:.40,groundStride:6,wallStride:5,maxParked:8,ringScale:.65})
});
export const QUALITY_ORDER_V73=Object.freeze(['full','balanced','light']);
export function qualityProfileV73(mode='full'){return VISUAL_QUALITY_V73[mode]||VISUAL_QUALITY_V73.full;}
export function nextQualityV73(mode='full'){
 const index=QUALITY_ORDER_V73.indexOf(mode);
 return QUALITY_ORDER_V73[(index+1)%QUALITY_ORDER_V73.length];
}
