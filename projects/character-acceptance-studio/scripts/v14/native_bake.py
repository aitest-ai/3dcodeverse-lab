"""Bulk write dense native keys; keyframe_insert merges very close frames."""
import bpy
from v05.blender_utils import restore_basis

def bake_body_actions(rig,clips):
    rig.animation_data_clear();rig.animation_data_create()
    for name,rows in clips.items():
        old=bpy.data.actions.get(name)
        if old:bpy.data.actions.remove(old)
        action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
        restore_basis(rig,rows[0]['pose']);tracks={}
        for bone in rig.pose.bones:
            for prop,source in [('location','p'),('rotation_quaternion','q'),('scale','s')]:
                bone.keyframe_insert(data_path=prop,frame=0,group=bone.name)
                values=[list(row['pose'][bone.name][source]) for row in rows]
                if source=='q':
                    for i in range(1,len(values)):
                        if sum(x*y for x,y in zip(values[i-1],values[i]))<0:values[i]=[-v for v in values[i]]
                tracks[bone.path_from_id(prop)]=values
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        vals=tracks[fc.data_path];fc.keyframe_points.clear();fc.keyframe_points.add(len(rows))
                        fc.keyframe_points.foreach_set('co',[v for row,values in zip(rows,vals) for v in (row['time']*24,values[fc.array_index])])
                        for key in fc.keyframe_points:key.interpolation='LINEAR'
                        # Keys are already sorted; fc.update() deduplicates close frames.
                        assert len(fc.keyframe_points)==len(rows),'Dense keys unexpectedly merged'
        print('V14_NATIVE_KEYS',name,len(rows),flush=True)
    rig.animation_data.action=bpy.data.actions['Idle']
    if rig.animation_data.action.slots:rig.animation_data.action_slot=rig.animation_data.action.slots[0]
    bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(0)
