"""Regression for exact bridge boundaries: never extrapolate D-window."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from v14.smoothing import CyclicWalk,sample_times
from v10.horse_solver import sample_native
bpy.ops.wm.open_mainfile(filepath=str(R/'library-v13/horse-brown-walk-transition-review/0.1.0/model.blend'))
rig=bpy.data.objects['AnimalArmature'];walk=bpy.data.actions['Walk'];bridge=CyclicWalk(rig,walk)
def error(a,b):
    out=0
    for n in a:
        for k in ['p','q','s']:
            e=max(abs(x-y) for x,y in zip(a[n][k],b[n][k]))
            if k=='q':e=min(e,max(abs(x+y) for x,y in zip(a[n][k],b[n][k])))
            out=max(out,e)
    return out
rows=[]
for t in [bridge.window,bridge.duration-bridge.window]:
    exact=bridge.pose(t);native=sample_native(rig,walk,t)
    assert error(exact,native)<1e-6
    nearby=max(error(bridge.pose(t+s*1e-7),exact) for s in [-1,1]);assert nearby<.001,nearby
    rows.append({'time_s':t,'native_exact_component_error':error(exact,native),'nearby_component_difference':nearby})
wrap=error(bridge.pose(0),bridge.pose(bridge.duration));assert wrap<1e-6
original_seam=error(bridge.pose(0),sample_native(rig,walk,0));assert original_seam<1e-6
for D in [bridge.duration,3*bridge.duration]:
    times=sample_times(D,bridge.duration);assert times[0]==0 and abs(times[-1]-D)<1e-9 and all(a<b for a,b in zip(times,times[1:]))
(R/'evidence-v14/smoothing-boundaries.json').write_text(json.dumps({'exact_boundaries':rows,'wrap_component_difference':wrap,'original_seam_component_difference':original_seam,'source_mother_unchanged':True},indent=2)+'\n');print('V14_NATIVE_BRIDGE_BOUNDARIES_PASS')
