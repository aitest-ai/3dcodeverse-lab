/**
 * v8.2 offline annotation contract for authentic v8.1 input-triggered screenshots.
 * Strictly IMAGE-normalized 2D coordinates, never a world position or weapon hit.
 * This file is also embedded byte-for-byte (minus ESM export keywords) in offline QA HTML.
 */
export const ACTIONS_V82=Object.freeze(['beam_input','charge_input','blast_input','dodge_right_input','dodge_left_input']);
export const MARK_KINDS_V82=Object.freeze([
  'muzzle','beam_origin','impact_visual','arm_clipping','smoke_occlusion',
  'street_collision_visual','dodge_pose','other_visual'
]);
export const SEVERITIES_V82=Object.freeze(['observation','minor','major','blocking']);
export const REPORT_SCHEMA_V82='taipei-mecha-v82-visual-annotations';

export function expectedFileNameV82(index,action){
 if(!Number.isInteger(index)||index<1||index>5||!ACTIONS_V82.includes(action))throw Error('Unknown input frame');
 return `Taipei_Mech_v81_input_${String(index).padStart(2,'0')}_${action}.png`;
}

export function validateEvidenceV82(evidence,media){
 const issues=[];
 if(!evidence||evidence.schema!=='taipei-mecha-v81-input-frame-evidence'||evidence.version!=='8.1'||
 !Array.isArray(evidence.shots)||evidence.shots.length<1||evidence.shots.length>5)
   return {ok:false,issues:['invalid_evidence_schema'],shots:[]};
 const known=new Set(),shots=[];
 for(const s of evidence.shots){
  if(!s||!Number.isInteger(s.index)||known.has(s.index)||
     !ACTIONS_V82.includes(s.action)||!Number.isFinite(s.elapsedMs)||s.elapsedMs<0||
     !Number.isInteger(s.bytes)||s.bytes<2000||s.bytes>30000000||
     !Number.isInteger(s.framesAfterInput)||s.framesAfterInput<2||s.framesAfterInput>10000){
    issues.push('invalid_or_duplicate_event');continue;
  }
  known.add(s.index);
  let name;
  try{name=expectedFileNameV82(s.index,s.action);}catch{issues.push('invalid_index');continue;}
  const item=media instanceof Map?media.get(name):media?.[name];
  if(!item||item.bytes!==s.bytes||!Number.isInteger(item.width)||!Number.isInteger(item.height)||
     item.width<256||item.height<144||item.width>16384||item.height>16384){
    issues.push('missing_or_mismatched_png:'+s.index);continue;
  }
  shots.push({index:s.index,action:s.action,elapsedMs:s.elapsedMs,
    framesAfterInput:s.framesAfterInput,width:item.width,height:item.height});
 }
 if(media){const count=media instanceof Map?media.size:Object.keys(media).length;
   if(count!==evidence.shots.length)issues.push('png_count_mismatch');}
 if(shots.length!==evidence.shots.length)issues.push('incomplete_match');
 shots.sort((a,b)=>a.index-b.index);
 return {ok:issues.length===0,issues:[...new Set(issues)],shots};
}

export function createVisualAnnotationV82({shotIndex,action,kind,severity='observation',x,y,detail=''}={}){
 if(!Number.isInteger(shotIndex)||shotIndex<1||shotIndex>5||!ACTIONS_V82.includes(action))throw Error('Unknown shot action');
 if(!MARK_KINDS_V82.includes(kind)||!SEVERITIES_V82.includes(severity))throw Error('Unknown visual annotation kind/severity');
 if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>1||y<0||y>1)throw Error('2D normalized coordinates must be 0..1');
 if(typeof detail!=='string'||detail.length>220)throw Error('Annotation note must be <=220 characters');
 return {shotIndex,action,kind,severity,x:Math.round(x*1000000)/1000000,y:Math.round(y*1000000)/1000000,detail:detail.trim()};
}

export function annotatedPixelV82(annotation,width,height){
 if(!Number.isInteger(width)||width<1||!Number.isInteger(height)||height<1)throw Error('Invalid canvas dimensions');
 if(!Number.isFinite(annotation?.x)||!Number.isFinite(annotation?.y)||annotation.x<0||annotation.x>1||annotation.y<0||annotation.y>1)throw Error('Invalid normalized annotation');
 return {x:annotation.x*width,y:annotation.y*height};
}

export function makeVisualReviewV82(shots,annotations,{manualReviewed=false}={}){
 if(!Array.isArray(shots)||shots.length<1||shots.length>5||!Array.isArray(annotations)||annotations.length>50)
   throw Error('Reviewed shot set must contain 1..5 images and <=50 annotations');
 const ids=new Map();
 for(const s of shots){if(ids.has(s.index)||!ACTIONS_V82.includes(s.action))throw Error('Duplicate or unsupported frame');ids.set(s.index,s.action);}
 const safe=annotations.map(a=>{
   if(ids.get(a.shotIndex)!==a.action)throw Error('Annotation references unknown frame');
   return createVisualAnnotationV82(a);
 });
 return {schema:REPORT_SCHEMA_V82,version:'8.2',source:'v8.1 keyboard-triggered PNGs, visually reviewed offline',
  imageEvidence:shots.map(s=>({index:s.index,action:s.action,reviewed:!!manualReviewed})),
  annotations:safe,annotationCount:safe.length,
  privacy:'No images, filenames, GPS/world camera coordinates, absolute timestamps or device identifiers.',
  limitations:'Coordinates are 2D relative to pixels, not 3D positions. A screenshot after input cannot prove actual firing, hit, dodge or collision. Human review and live gameplay are still required.'};
}
