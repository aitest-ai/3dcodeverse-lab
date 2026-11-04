import test from 'node:test';
import assert from 'node:assert/strict';
import {createContactProbe,REQUIRED_MARKERS} from '../scripts/research/onomichi_v29_runtime_probe.mjs';
class WebGL2RenderingContextMock {}
globalThis.WebGL2RenderingContext=WebGL2RenderingContextMock;
const renderer={getContext(){return new WebGL2RenderingContextMock()}};
const marker=(i)=>({node:{getWorldPosition(){},updateWorldMatrix(){},localToWorld(p){p.x+=i}},
 vecFactory(x,y,z){return {x,y,z}},localOffset:[0,1,2]});
const markers=Object.fromEntries(REQUIRED_MARKERS.map((m,i)=>[m,marker(i)]));
test('synthetic node mocks yield eight world points; NOT WebGL visual acceptance',()=>{
 const p=createContactProbe({renderer,markers,browserName:'Mock Chromium 154'});
 p.captureFrame(0,'straight');p.captureFrame(.1,'turn');
 const d=p.exportData();
 assert.equal(d.frames.length,2);assert.equal(d.frames[0].markers.bike_pedal_right[0],7);
 assert.equal(d.environment.capture_method,'live_scene_world_matrices');
});
test('marker omissions refused',()=>assert.throws(()=>createContactProbe({renderer,markers:{},browserName:'Mock Chromium 154'}),/8 個 marker/));
test('fake DOM or WebGL1 refused',()=>assert.throws(()=>createContactProbe({renderer:{getContext:()=>({})},markers,browserName:'Mock Chromium 154'}),/WebGL2/));
test('time order and phase required',()=>{
 const p=createContactProbe({renderer,markers,browserName:'Mock Chromium 154'});
 assert.throws(()=>p.captureFrame(0,'other'));
 p.captureFrame(0,'straight');assert.throws(()=>p.captureFrame(0,'turn'));
});
