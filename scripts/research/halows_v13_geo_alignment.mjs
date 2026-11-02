#!/usr/bin/env node
/**
 * V13 WGS84/ECEF alignment gate from the original V06 known WGS84 route anchor.
 * This NEVER approves vertical placement, bicycle route legality or gameplay.
 */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const lockPath=path.resolve(process.argv[2] || process.env.HALOWS_V13_SITE_LOCK || 'outputs/halows-v13/site_lock.json');
const raw=fs.readFileSync(lockPath);
const siteHash=createHash('sha256').update(raw).digest('hex');
const expectedSiteHash='71873821d96c937465fd6cbd3f05d0f6a66c564f4f3cbcd6f6e968b462f2ccf9';
if(siteHash!==expectedSiteHash)throw new Error('V09 site lock changed: '+siteHash);
const site=JSON.parse(raw.toString('utf8'));
if(site.asset_id!=='halows-mukaishima-v09-geosite' || site.building.osm_way_id!=='661155704')throw new Error('OSM footprint source mismatch');
const v06={
  origin:{lon:133.201729,lat:34.4059115},
  anchor:{lon:133.2026783,lat:34.4043239,x:87.2815,y:2.39,z:176.1121,osm_node_id:'8255588823'},
  world_sha256:'bfab5d3222aefa77abd5986f3d5be202bf340e10c1252b024f90e99cb094f6be'
};
const rad=Math.PI/180;
function ecef(p){
 const phi=p.lat*rad,lambda=p.lon*rad,a=6378137,e2=6.6943799901413165e-3;
 const N=a/Math.sqrt(1-e2*Math.sin(phi)**2);
 return [(N+(p.alt||0))*Math.cos(phi)*Math.cos(lambda),(N+(p.alt||0))*Math.cos(phi)*Math.sin(lambda),(N*(1-e2)+(p.alt||0))*Math.sin(phi)];
}
function v06xyz(base,p){
 const q=ecef(base),t=ecef(p),dx=t[0]-q[0],dy=t[1]-q[1],dz=t[2]-q[2];
 const lat=base.lat*rad,lon=base.lon*rad;
 const east=-Math.sin(lon)*dx+Math.cos(lon)*dy;
 const north=-Math.sin(lat)*Math.cos(lon)*dx-Math.sin(lat)*Math.sin(lon)*dy+Math.cos(lat)*dz;
 return {x:east,z:-north};
}
const round=(x)=>Number(x.toFixed(4));
const halows=v06xyz(v06.origin,site.origin_wgs84),anchor=v06xyz(v06.origin,v06.anchor);
const error=Math.hypot(anchor.x-v06.anchor.x,anchor.z-v06.anchor.z);
if(error>=0.25)throw new Error('V06 reference route does not agree with WGS84 transformation: '+error);
if(Math.abs(halows.x+194.586)>0.25 || Math.abs(halows.z-985.935)>0.25)throw new Error('Unreviewed transform drift');
const report={
 schema_version:1,asset_id:'halows-v13-geobridge',v06_origin_wgs84:v06.origin,
 source_v06_world_sha256:v06.world_sha256,
 source_v09_site_lock_sha256:siteHash,
 source_v11_candidate_commit:'877ce296e6001092307bd7681d46b7f843fda258',
 source_v11_glb_sha256:'19d633a04d1821249a9964471f63d530cbd8ed44eba707f2d17052210140ab9e',
 position_from_v09_into_v06_gltf_m:{x:round(halows.x),y:null,z:round(halows.z)},
 conventions:'glTF x East / y up / z South, V11 local elevation relative to the estimated Halows pad',
 v06_anchor_check:{osm_node_id:v06.anchor.osm_node_id,expected_xz:[v06.anchor.x,v06.anchor.z],computed_xz:[round(anchor.x),round(anchor.z)],error_m:round(error),horizontal_result:'PASS'},
 y_gate:'BLOCKED_NO_SHARED_V06_VERTICAL_DATUM',
 height_warning:'The V11 Blender terrain and roads already subtract PAD=2.70m; NEVER blindly apply +2.70m world translation.',
 local_graph_gate:'V12 centerline checks passed, but 317/trunk, service access and ferry connection are NOT approved bike paths',
 valid_ferries:['尾道駅前－富浜','尾道土堂－向島兼吉'],
 fukumoto_ferry:'DISCONTINUED_2025_03',
 route_ferry_to_halows_confirmed:false,
 original_v06_runtime_available_for_full_integration:false,
 v11_glb_source_asset_available_via_github_actions:true,
 visual_3d_browser_tested:false,android_tested:false
};
const output=path.resolve('outputs/halows-v13/geo_alignment.json');
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:'HORIZONTAL_PASS_VERTICAL_BLOCKED',x:report.position_from_v09_into_v06_gltf_m.x,z:report.position_from_v09_into_v06_gltf_m.z,anchor_error_m:round(error)},null,2));
