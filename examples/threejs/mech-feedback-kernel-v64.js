/**
 * Taipei 101 Defence v6.4: portable combat-feedback director, NO DOM dependencies.
 *
 * The full Windows overlay additionally provides the DOM HUD, original
 * WebAudio cue patterns, engine event hooks and authentic game assets.
 * This shared kernel is a self-contained reference for other AI/engines;
 * gameplay damage, actual OSM collision and mission state are authoritative.
 * It stores neither world coordinates nor identifiers nor GPS.
 */
const clamp=(n,a,b)=>Math.max(a,Math.min(b,Number.isFinite(n)?n:a));
export const FEEDBACK_TYPES_V64=Object.freeze({
 enemy_hit:{duration:.65,priority:1,label:"命中敵機",cue:"confirm",shake:.045},
 enemy_down:{duration:1.4,priority:2,label:"敵機擊毀",cue:"destroy",shake:.095},
 building_hit:{duration:.85,priority:1,label:"建築受損",cue:null,shake:.025},
 rocket_impact:{duration:1,priority:1,label:"爆破衝擊",cue:"impact",shake:.14},
 player_hit:{duration:1.1,priority:3,label:"我方受到攻擊",cue:"damage",shake:0},
 relay_hit:{duration:1.4,priority:3,label:"中繼站遭到攻擊",cue:"alert",shake:.065},
 wave_start:{duration:2.6,priority:2,label:"敵機來襲",cue:"wave",shake:0},
 heavy_arrival:{duration:3.5,priority:3,label:"重裝型敵機入侵",cue:"boss",shake:.095},
 victory:{duration:7.5,priority:4,label:"防衛成功",cue:"victory",shake:.12},
 defeat:{duration:7.5,priority:4,label:"防衛失敗",cue:"defeat",shake:.055},
 mission_start:{duration:2,priority:2,label:"臺北 101 防衛開始",cue:"wave",shake:0},
 reset:{duration:0,priority:0,label:"",cue:null,shake:0}
});
export function createPortableFeedbackV64({historyLimit=48}={}){
 if(!Number.isInteger(historyLimit)||historyLimit<1||historyLimit>256)
   throw new RangeError("Invalid history limit");
 let pending=null,remaining=0,elapsed=0,seq=0,accepted=0,suppressed=0,history=[],disposed=false;
 function reset(){pending=null;remaining=0;elapsed=0;seq=0;accepted=0;suppressed=0;history=[];}
 function record(type,{damage=0,wave=0,distance=0}={}){
   if(disposed||!Object.hasOwn(FEEDBACK_TYPES_V64,type))
     return {accepted:false,reason:"invalid-or-disposed"};
   if(type==="reset"){reset();return {accepted:true,kind:"reset",cue:null,intensity:0};}
   const spec=FEEDBACK_TYPES_V64[type];
   if(pending&&remaining>0&&spec.priority<pending.priority){
      suppressed++;return {accepted:false,reason:"lower-priority"};
   }
   if(pending&&pending.type===type&&elapsed<.18){
      suppressed++;return {accepted:false,reason:"rate-limit"};
   }
   const dmg=Math.round(clamp(damage,0,999)),nwave=Math.round(clamp(wave,0,12));
   const label=type==="enemy_hit"&&dmg?"命中敵機 −"+dmg:
     type==="player_hit"&&dmg?"我方裝甲 −"+dmg:
     type==="relay_hit"&&dmg?"中繼站 −"+dmg:
     type==="wave_start"&&nwave?"第 "+nwave+" 波敵機來襲":spec.label;
   pending={sequence:++seq,type,label,priority:spec.priority,damage:dmg,wave:nwave};
   remaining=spec.duration;elapsed=0;accepted++;
   history.push({kind:type,damage:dmg,wave:nwave});
   if(history.length>historyLimit)history.shift();
   const spatial=distance>0?clamp(1-clamp(distance,0,1000)/65,0,1):1;
   return {accepted:true,kind:type,label,cue:spec.cue,intensity:clamp(spec.shake*spatial,0,.16)};
 }
 function update(dt){
   if(!disposed){
     const step=clamp(dt,0,.05);elapsed+=step;remaining=Math.max(0,remaining-step);
     if(remaining===0)pending=null;
   }
   return snapshot();
 }
 function snapshot(){return {pending:pending?{...pending}:null,remaining,accepted,suppressed,
   recent:history.map(x=>({...x})),disposed};}
 function dispose(){reset();disposed=true;}
 return {record,update,snapshot,reset,dispose};
}
