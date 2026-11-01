/** Preserve authored vertical foot grounding while suppressing horizontal root drift.
 * The original v5.0 / v6.2 GLBs have world-up at root.position.y (glTF Y-up).
 * In-place OSM controller owns X/Z translation; deleting the entire root track
 * also deleted Run foot-ground corrections (up to 0.1m+ in the sampled mesh).
 */
export function retainVerticalGroundingV63(clip) {
  if(!clip || !Array.isArray(clip.tracks))throw new TypeError('AnimationClip tracks required');
  let preserved=0,removed=0;
  clip.tracks=clip.tracks.filter(track=>{
    if(!(typeof track?.name==='string'&&track.name.toLowerCase().includes('root')&&track.name.endsWith('.position')))return true;
    const values=track.values;
    if(!values||typeof values.length!=='number'||values.length<3||values.length%3!==0){removed++;return false;}
    const x0=values[0],z0=values[2];
    if(![x0,z0].every(Number.isFinite)){removed++;return false;}
    for(let i=0;i<values.length;i+=3){
      if(!Number.isFinite(values[i+1])){removed++;return false;}
    }
    for(let i=0;i<values.length;i+=3){values[i]=x0;values[i+2]=z0;}
    preserved++;return true;
  });
  return {preserved,removed};
}
