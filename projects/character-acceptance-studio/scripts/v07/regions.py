"""Per-character garment/leg regions measured from native anatomy; no fixed world-height crop."""
from v06.collision import regions

def native_regions(body,rig):
 r=regions(body);me=body.data;me.calc_loop_triangles();leg=sum((rig.data.bones['J_Bip_L_'+a].head_local-rig.data.bones['J_Bip_L_'+b].head_local).length for a,b in [('UpperLeg','LowerLeg'),('LowerLeg','Foot')]);hips=rig.data.bones['J_Bip_L_UpperLeg'].head_local.z;knee=rig.data.bones['J_Bip_L_LowerLeg'].head_local.z
 r['leg_triangles']=[tuple(f.vertices) for f in me.loop_triangles if f.material_index==0 and all(knee-leg*.3<me.vertices[i].co.z<hips+leg*.15 for i in f.vertices)];r['leg_region']={'lower_z':knee-leg*.3,'upper_z':hips+leg*.15,'measured_leg_length_m':leg};return r
