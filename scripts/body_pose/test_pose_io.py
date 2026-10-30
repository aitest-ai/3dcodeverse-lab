import copy,json,tempfile,unittest
from pathlib import Path
from pose_io import load_nova,camera_to_blender,SEGMENTS,read_glb
class PoseIOTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'pose.json'
        self.body={'tracking_id':7,'keypoints_3d':[[.1,.2,2.] for _ in range(77)],'keypoints_confidence':[1.02]*77,'joint_rotations':[[0,0,0,1]]*77}
        self.rows=[{'frame_id':i,'detections':[copy.deepcopy(self.body)]} for i in range(3)]
    def load(self,**kwargs):
        self.path.write_text('\n'.join(json.dumps(r) for r in self.rows));return load_nova(self.path,kwargs.get('fps',30),7,kwargs.get('axes','opencv'))
    def test_valid(self):self.assertEqual(len(self.load()['frames']),3)
    def test_axes(self):self.assertEqual(camera_to_blender([1,2,3]),[1,3,-2])
    def test_no_live_claim(self):self.assertFalse(self.load()['live_inference_verified'])
    def test_confidence_above_one_allowed(self):self.assertEqual(self.load()['frames'][0]['confidence'][0],1.02)
    def test_missing_track(self):
        self.rows[1]['detections']=[]
        with self.assertRaisesRegex(ValueError,'absent'):self.load()
    def test_duplicate_track(self):
        self.rows[0]['detections'].append(copy.deepcopy(self.body))
        with self.assertRaisesRegex(ValueError,'duplicated'):self.load()
    def test_different_track_not_used(self):
        self.rows[1]['detections'][0]['tracking_id']=8
        with self.assertRaises(ValueError):self.load()
    def test_legacy34_rejected(self):
        self.rows[0]['detections'][0]['keypoints_3d']=[[0,0,1]]*34
        with self.assertRaisesRegex(ValueError,'Nova-77'):self.load()
    def test_nan(self):
        self.rows[0]['detections'][0]['keypoints_3d'][3][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'non-finite'):self.load()
    def test_duplicate_frame(self):
        self.rows[1]['frame_id']=0
        with self.assertRaisesRegex(ValueError,'frame'):self.load()
    def test_missing_frame(self):
        self.rows[1]['frame_id']=4
        with self.assertRaisesRegex(ValueError,'frame'):self.load()
    def test_fps(self):
        for v in [0,-1,float('nan'),300]:
            with self.assertRaises(ValueError):self.load(fps=v)
    def test_bad_axes(self):
        with self.assertRaises(ValueError):self.load(axes='guess')
    def test_bad_quaternion(self):
        self.rows[0]['detections'][0]['joint_rotations'][0]=[0,0,0,0]
        with self.assertRaisesRegex(ValueError,'quaternion'):self.load()
    def test_map_has_twenty_unique_bones(self):self.assertEqual(len(SEGMENTS),20)
    def test_left_right_indices_distinct(self):
        self.assertEqual(SEGMENTS['upperarm_l'],(12,13));self.assertEqual(SEGMENTS['upperarm_r'],(40,41))
    def test_empty(self):
        self.rows=[]
        with self.assertRaises(ValueError):self.load()
    def test_truncated_glb(self):
        self.path.write_bytes(b'glTF')
        with self.assertRaisesRegex(ValueError,'Truncated'):read_glb(self.path)
if __name__=='__main__':unittest.main()
