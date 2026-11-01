import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import * as THREE from '../dist/vendor/three.module.js';
import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'..'),app=fs.readFileSync(path.join(root,'dist/app.js'),'utf8');
const view=JSON.parse(fs.readFileSync(path.join(root,'dist/scene_view.json'),'utf8'));
const primitive=JSON.parse(fs.readFileSync(path.join(root,'evidence/osm_primitive.json'),'utf8'));
const geometry=new THREE.BufferGeometry();
geometry.setAttribute('position',new THREE.Float32BufferAttribute(primitive.positions.flat(),3));
geometry.setIndex(primitive.indices);
const material=new THREE.MeshStandardMaterial();material.name='Unrefined_OSM_mass';
const mesh=new THREE.Mesh(geometry,material);const root3d=new THREE.Group();root3d.add(mesh);
const take=(start,end)=>{const i=app.indexOf(start),j=app.indexOf(end,i);assert(i>=0&&j>i);return app.slice(i,j)};
const source=take('function pointInPolygonEUS(','async function loadV004Extension(){');
const metrics={};const context=vm.createContext({THREE,manifest:view,metrics,refreshDiagnostics:()=>{},console});
vm.runInContext(source,context);
function doPass(ids){context.buildingIds=ids;context.root=root3d;return vm.runInContext('suppressGreyBuildingPlaceholders(root,buildingIds)',context);}
const before=mesh.geometry.getIndex().count/3;
doPass(view.extension.building_ids);const afterV004=mesh.geometry.getIndex().count/3;
doPass(view.extension_v005.building_ids);const afterV005=mesh.geometry.getIndex().count/3;
const actual=Object.fromEntries(Object.entries(metrics.placeholder_removal_by_building));
const expected={'way/283905599':28,'way/283905598':28,'way/283905593':20,'way/283905573':12,'way/283905580':12};
assert.deepEqual(actual,expected);
assert.equal(before,368);assert.equal(afterV004,368-76);assert.equal(afterV005,368-100);
const oldData=primitive.indices.length;assert.equal(oldData,368*3);
let rejectedMissing=false;
try{doPass(view.extension_v005.building_ids)}catch(e){rejectedMissing=String(e).includes('未成功排除')}
assert(rejectedMissing);
const report={schema:'date-v006-real-osm-primitive-runtime-mask/1',status:'PASS_NODE_THREE_GEOMETRY_NOT_WEBGL',frozen_B_sha256:primitive.sha256_frozen_B,
 removed_by_building:actual,triangles_before:before,after_V004:afterV004,after_V005:afterV005,remaining:afterV005,
 fail_closed_when_reapplying:true,original_source_positions_unchanged:primitive.positions.length};
fs.writeFileSync(path.join(root,'evidence/V006_placeholder_qa.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));