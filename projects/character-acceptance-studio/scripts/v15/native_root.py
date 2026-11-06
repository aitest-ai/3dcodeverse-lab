"""Editable root actions with exact sorted dense key preservation."""
import bpy
from mathutils import Matrix

def bake_roots(root,clips):
    root.animation_data_create();root.rotation_mode='QUATERNION'
    for name,rows in clips.items():
        assert bpy.data.actions.get(name+'_Root') is None
        a=bpy.data.actions.new(name+'_Root');a.use_fake_user=True;root.animation_data.action=a
        for prop in ['location','rotation_quaternion','scale']:root.keyframe_insert(data_path=prop,frame=0)
        for l in a.layers:
            for st in l.strips:
                for bag in st.channelbags:
                    for fc in bag.fcurves:
                        fc.keyframe_points.clear();fc.keyframe_points.add(len(rows))
                        fc.keyframe_points.foreach_set('co',[v for row in rows for v in (row['time']*24,row[fc.data_path][fc.array_index])])
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
        print('V15_ROOT_KEYS',name,len(rows),flush=True)
    root.animation_data.action=None;root.matrix_basis=Matrix.Identity(4)
