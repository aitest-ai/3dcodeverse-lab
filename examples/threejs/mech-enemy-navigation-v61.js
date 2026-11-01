/**
 * Taipei Mech v6.1 incremental tactical navigation over the ORIGINAL OSM city.
 * Only a short-range planner: no baked synthetic map, teleports, or collision bypass.
 * The host owns terrain/water/traffic clearance and authentic building LOS.
 * Incremental A*: capped expansions per update to avoid 45k-building frame spikes.
 */
const finite = Number.isFinite;
const dist = (a,b) => Math.hypot(a.x-b.x,a.z-b.z);
const dirs = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];

export function createEnemyNavigationV61({cell=2.8,maxNodes=240,maxRadius=64,budget=5,maxWaypoints=40}={}) {
  if (![cell,maxNodes,maxRadius,budget,maxWaypoints].every(finite) || cell<1.2 || cell>6 ||
      maxNodes<20 || maxNodes>1000 || maxRadius<10 || maxRadius>150 || budget<1 || budget>50 ||
      maxWaypoints<2 || maxWaypoints>128) throw new RangeError('Unsafe navigation budget');
  let status='idle',origin=null,target=null,goalMin=0,goalMax=0;
  let open=[],nodes=new Map(),path=[],cursor=0,expanded=0,lastResult=null;
  const key=(ix,iz)=>ix+','+iz;
  const world=(ix,iz)=>({x:origin.x+ix*cell,z:origin.z+iz*cell});
  const point=(n)=>({...world(n.ix,n.iz),y:n.y});
  const heuristic=(p)=>Math.max(0,dist(p,target)-goalMax);
  function reset(){status='idle';origin=null;target=null;open=[];nodes=new Map();path=[];cursor=0;expanded=0;lastResult=null;}
  function begin({from,to,minRange=4,maxRange=16}={}){
    reset();
    if(!from||!to||![from.x,from.y,from.z,to.x,to.z].every(finite) ||
      ![minRange,maxRange].every(finite)||minRange<0||maxRange<minRange)return false;
    origin={x:from.x,y:from.y,z:from.z};target={x:to.x,z:to.z};
    goalMin=minRange;goalMax=maxRange;
    const start={ix:0,iz:0,y:from.y,g:0,f:heuristic(origin),parent:null,closed:false};
    nodes.set(key(0,0),start);open.push(start);status='planning';return true;
  }
  function step({canStep,hasSight,limit=budget}={}){
    if(status!=='planning')return snapshot();
    if(typeof canStep!=='function'||typeof hasSight!=='function'){
      status='failed';lastResult='missing-city-collision';return snapshot();
    }
    let remaining=Math.max(1,Math.min(budget,Math.floor(Number(limit)||budget)));
    while(remaining-->0&&status==='planning'){
      if(!open.length){status='failed';lastResult='no-route';break;}
      // Bounded open list <= maxNodes; deterministic tie-breaking.
      let best=0;
      for(let i=1;i<open.length;i++)if(open[i].f<open[best].f-1e-8 ||
          (Math.abs(open[i].f-open[best].f)<1e-8&&open[i].g<open[best].g))best=i;
      const current=open.splice(best,1)[0];
      if(current.closed)continue;
      current.closed=true;expanded++;
      const cp=point(current),gap=dist(cp,target);
      // A shooting position must really see the target; distance alone is not enough.
      if(gap>=goalMin&&gap<=goalMax&&hasSight(cp,target)){
        const reversed=[];let node=current;
        while(node&&reversed.length<maxWaypoints+1){reversed.push(point(node));node=node.parent;}
        if(node){status='failed';lastResult='too-many-waypoints';break;}
        path=reversed.reverse();cursor=path.length>1?1:0;status='ready';lastResult='line-of-sight-vantage';break;
      }
      if(expanded>=maxNodes){status='failed';lastResult='node-budget';break;}
      for(const [ix,iz] of dirs){
        const nx=current.ix+ix,nz=current.iz+iz,neighbor=world(nx,nz);
        if(dist(neighbor,origin)>maxRadius)continue;
        const k=key(nx,nz);let known=nodes.get(k);
        if(known?.closed)continue;
        const w=Math.hypot(ix,iz)*cell;
        const g=current.g+w;
        if(known&&g>=known.g-1e-8)continue;
        // Reject all blocked segments, even if their endpoints are open. The host
        // samples actual OSM collider, rivers, dynamic traffic & deck elevations.
        let newY;
        try{newY=canStep(cp,{x:neighbor.x,z:neighbor.z},w);}catch{newY=null;}
        if(!finite(newY))continue;
        const n={ix:nx,iz:nz,y:newY,g,f:g+heuristic(neighbor),parent:current,closed:false};
        nodes.set(k,n);open.push(n);
        if(nodes.size>maxNodes*8){status='failed';lastResult='memory-budget';break;}
      }
    }
    return snapshot();
  }
  function waypoint(current){
    if(status!=='ready'||!current||![current.x,current.z].every(finite))return null;
    while(cursor<path.length-1&&dist(current,path[cursor])<cell*.45)cursor++;
    if(cursor>=path.length || (cursor===path.length-1 && dist(current,path[cursor])<cell*.45)){
      status='done';return null;
    }
    const p=path[cursor];
    return {x:p.x,z:p.z,y:p.y};
  }
  function invalidated({position,target:nextTarget}={}){
    if(!origin||!target)return true;
    if(nextTarget&&[nextTarget.x,nextTarget.z].every(finite)&&dist(target,nextTarget)>8)return true;
    if(position&&[position.x,position.z].every(finite)&&dist(origin,position)>maxRadius+cell)return true;
    return false;
  }
  function snapshot(){return {status,expanded,nodes:nodes.size,waypoints:path.length,
    waypointIndex:cursor,reason:lastResult};}
  return {begin,step,waypoint,invalidated,snapshot,reset};
}
