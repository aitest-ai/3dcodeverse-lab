/**
 * Taipei Mech v8.5 portable validation of 288 authentic Blender pose samples.
 * NO sample generation, no WebGPU graphics, and no assertion of gameplay success.
 */
export const V85_CLIPS=Object.freeze(['Idle','Run','Punch','Dodge','Fire','Hit']);
const NUMBER=v=>typeof v==='number'&&Number.isFinite(v);
export function validateV85Report(raw){
 const errors=[];
 if(!raw||raw.schema!=='taipei-mecha-v85-fullframe-muzzle-qa'||raw.version!=='8.5')
   return {accepted:false,errors:['schema_or_version_mismatch'],summary:null};
 if(!Array.isArray(raw.samples)||raw.samples.length!==288)
   return {accepted:false,errors:['incomplete_288_frame_coverage'],summary:null};
 if(!/^[a-f0-9]{64}$/.test(raw.source_blend_sha256??'')||
    !/^[a-f0-9]{64}$/.test(raw.candidate_glb_sha256??''))
   errors.push('missing_asset_sha256');
 const byClip=Object.fromEntries(V85_CLIPS.map(c=>[c,[]]));
 const seen=new Set();
 for(const s of raw.samples){
  if(!s||!V85_CLIPS.includes(s.clip)||!Number.isInteger(s.frame)||s.frame<1||s.frame>48||
     !NUMBER(s.gap_m)||!NUMBER(s.angle_deg)||s.gap_m<0||s.angle_deg<0){errors.push('invalid_frame');continue;}
  const key=s.clip+'/'+s.frame;
  if(seen.has(key)){errors.push('duplicate_frame');continue;}
  seen.add(key);byClip[s.clip].push(s);
 }
 if(V85_CLIPS.some(c=>byClip[c].length!==48))errors.push('clip_coverage_error');
 if(errors.length)return {accepted:false,errors:[...new Set(errors)],summary:null};
 const clips={};
 for(const c of V85_CLIPS){
  const rows=byClip[c].sort((a,b)=>a.frame-b.frame);
  const worstDistance=rows.reduce((a,b)=>b.gap_m>a.gap_m?b:a);
  const worstDirection=rows.reduce((a,b)=>b.angle_deg>a.angle_deg?b:a);
  clips[c]={
    frames:48,maxGapMeters:worstDistance.gap_m,maxGapFrame:worstDistance.frame,
    maxAngleDegrees:worstDirection.angle_deg,maxAngleFrame:worstDirection.frame,
    passed:rows.every(s=>s.gap_m<=0.025&&s.angle_deg<=9),
    points:rows.map(s=>({frame:s.frame,gapMm:s.gap_m*1000,angle:s.angle_deg}))
  };
 }
 const passed=V85_CLIPS.every(c=>clips[c].passed);
 if(raw.passed!==passed)errors.push('reported_outcome_mismatch');
 if(raw.total_samples!==288)errors.push('reported_sample_count_mismatch');
 return {accepted:!errors.length,errors,summary:{passed,clips,samples:288,
    caveat:'Real Blender trace is required; validated JSON structure alone cannot establish scene provenance or Windows WebGPU approval.'}};
}
export function createV85ReviewExport(raw,review){
 const v=validateV85Report(raw);
 if(!v.accepted)throw Error('Invalid or incomplete Blender QA report');
 const notes=String(review?.notes??'').trim().slice(0,600);
 return {schema:'taipei-mecha-v85-review',version:'8.5',
    inputSource:'user-supplied Blender QA JSON, not a live GPU reading',
    sourceBlendSHA256:raw.source_blend_sha256,candidateGlbSHA256:raw.candidate_glb_sha256,
    animationQA:v.summary.passed?'passed_geometry_only':'failed_geometry',
    clips:Object.fromEntries(V85_CLIPS.map(c=>{const {points,...summary}=v.summary.clips[c];return [c,summary]})),
    humanReviewCompleted:review?.humanReviewCompleted===true,notes,
    limitations:'No screenshots or GPS included. Geometry test does not validate real Windows WebGPU scene, animation aesthetics, projectile hits, FPS or VRAM.'};
}
