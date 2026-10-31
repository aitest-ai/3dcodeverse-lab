"""Auditable V31 second experiment recipe over the pinned first experiment.
Writes the complete executed script to qa/executed_build.py. Exact anchors
and source SHA must match; no silent fallback or editing of input assets.
"""
from pathlib import Path
import hashlib,os
base=Path(__file__).with_name('build.py')
source=base.read_text()
assert hashlib.sha256(base.read_bytes()).hexdigest()=='1bd9e6b2a6a6f2774df77a17dbf4561d1a6ac8debf6ea56b6d84675b1cac5033'
def change(old,new):
    global source
    if source.count(old)!=1:raise RuntimeError('Recipe anchor not unique: '+old[:80])
    source=source.replace(old,new)

change("data={'rays':9801,'shirt_hits':0,'pants_in_front':0,'body_in_front':0,'either_in_front':0}",
"data={'rays':9801,'shirt_hits':0,'pants_in_front':0,'body_in_front':0,'either_in_front':0,'raw_either_in_front':0,'opposite_facing_shirt_hits':0}")
change("data['body_in_front']+=int(b);data['pants_in_front']+=int(p);data['either_in_front']+=int(b or p)",
"""data['raw_either_in_front']+=int(b or p)
            # A rear cloth hit below the front hem must not be counted as a hole.
            if sh[1].dot(direction)>-.05:
                data['opposite_facing_shirt_hits']+=1
                continue
            data['body_in_front']+=int(b);data['pants_in_front']+=int(p);data['either_in_front']+=int(b or p)""")
change("np.savez_compressed(OUT/'qa/hem_source_delta.npz',before=start,after=target,delta=world_delta)",
"""np.savez_compressed(OUT/'qa/hem_source_delta.npz',before=start,after=target,delta=world_delta)
from lower_band import rebuild
hem_report['lower_band_rebuild']=rebuild(shirt,body,pants,rig)
hem_report['original_faces_preserved']=False
hem_report['metric_revision']='Only camera-facing first shirt surface counted; old raw depth hits also retained'
hem_report['scope']='Source shirt lower band intentionally reconstructed, not an unchanged-topology claim'""")
change("if not pin:raise RuntimeError('No small shoulder pin patch')",
"""# The first run's five point pin allowed the entire width to twist around
# the contact. Use one actual shoulder-contact cross-section plus soft neighbours.
pin=[];soft_pin=[]
for j,s in enumerate(np.linspace(0,length,rows)):
    offset=abs(s-(front_len+arc_len/2))
    if offset>.032:continue
    for i in range(cols):
        idx=j*cols+i;q=Vector(verts[idx]);support=[]
        for t in obstacles:
            hit,_,_,_=t.ray_cast(Vector((q.x,q.y,height+.15)),Vector((0,0,-1)),1.)
            if hit is not None:support.append(hit.z)
        if not support:raise RuntimeError('Support patch must lie over real shoulder')
        q.z=max(support)+.007;verts[idx]=tuple(q)
        if offset<.012:pin.append(idx)
        else:soft_pin.append(idx)
if not pin:raise RuntimeError('No supported shoulder strip')
old.hide_render=True;old.hide_set(True)""")
change("vg=cloth.vertex_groups.new(name='SIM_small_shoulder_contact');vg.add(pin,1.,'REPLACE')",
"vg=cloth.vertex_groups.new(name='SIM_supported_shoulder_strip');vg.add(pin,1.,'REPLACE');vg.add(soft_pin,.35,'REPLACE')")
change("settings.quality=12;settings.mass=.15;settings.tension_stiffness=25.;settings.compression_stiffness=25.",
"settings.quality=12;settings.mass=.08;settings.tension_stiffness=80.;settings.compression_stiffness=80.")
change("settings.shear_stiffness=8.;settings.bending_stiffness=.08","settings.shear_stiffness=30.;settings.bending_stiffness=.25")
change("settings.air_damping=2.;settings.vertex_group_mass=vg.name;settings.pin_stiffness=1.",
"settings.air_damping=5.;settings.vertex_group_mass=vg.name;settings.pin_stiffness=1.")
change("scene.gravity=(0,0,-9.81);scene.frame_start=1;scene.frame_end=120", "scene.gravity=(0,0,-9.81);scene.frame_start=1;scene.frame_end=180")
change("modifier.point_cache.frame_start=1;modifier.point_cache.frame_end=120", "modifier.point_cache.frame_start=1;modifier.point_cache.frame_end=180")
change("for f in range(1,121):", "for f in range(1,181):")
change("if f in (1,12,24,48,72,96,120):snapshots.append((f,p.copy()))", "if f in (1,24,60,96,120,156,180):snapshots.append((f,p.copy()))")
change("'frames':120,'fps':24,", "'frames':180,'fps':24,'soft_pin_vertices':soft_pin,")
change("'quality_steps':12,'mass_setting':.15,", "'quality_steps':12,'mass_setting':.08,")
change("'tension_stiffness':25.,'shear_stiffness':8.,'bending_stiffness':.08,'self_collision':True,", "'tension_stiffness':80.,'shear_stiffness':30.,'bending_stiffness':.25,'self_collision':True,")
change("'pin_note':'small fixed shoulder-contact patch prevents drift; not a validated friction-only resting solution'", "'pin_note':'One supported full-width shoulder strip and soft neighbours prevent twisting; not friction-only validation'")
change("cloth['drape']='Actual120-frame gravity/collision solve, frozen neutral surface + source rig skinning; no realtime cloth'", "cloth['drape']='Actual180-frame gravity/collision solve with supported shoulder strip, frozen surface + rig; no realtime cloth'")
out=Path(os.getenv('V31_OUT','outputs/v31')).resolve();(out/'qa').mkdir(parents=True,exist_ok=True)
(out/'qa/executed_build.py').write_text(source)
print('V31_REVISED_RECIPE_SHA256',hashlib.sha256(source.encode()).hexdigest(),flush=True)
exec(compile(source,str(base),'exec'),{'__name__':'__main__','__file__':str(base)})
