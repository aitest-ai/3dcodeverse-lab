import tempfile,unittest
from pathlib import Path
from capture_nvidia import validate_media,validate_boxes
class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.meta={'streams':[{'codec_name':'h264','pix_fmt':'yuv420p','avg_frame_rate':'30/1','width':640,'height':480}],'frames':[{'best_effort_timestamp_time':f'{i/30:.6f}'} for i in range(4)]}
    def test_cfr(self):self.assertEqual(validate_media(self.meta)['frames'],4)
    def test_variable_rate(self):
        self.meta['frames'][2]['best_effort_timestamp_time']='0.09'
        with self.assertRaisesRegex(ValueError,'Variable'):validate_media(self.meta)
    def test_wrong_codec(self):
        self.meta['streams'][0]['codec_name']='hevc'
        with self.assertRaises(ValueError):validate_media(self.meta)
    def test_hdr(self):
        self.meta['streams'][0]['color_transfer']='smpte2084'
        with self.assertRaises(ValueError):validate_media(self.meta)
    def boxes(self,text):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'b.txt';p.write_text(text);validate_boxes(p,{'frames':2,'width':640,'height':480},1)
    def test_good_boxes(self):self.boxes('1\n0 1 0 0 640 480\n1 1 0 0 640 480')
    def test_missing_box(self):
        with self.assertRaisesRegex(ValueError,'every frame'):self.boxes('1\n0 1 0 0 640 480')
    def test_bad_box(self):
        with self.assertRaisesRegex(ValueError,'outside'):self.boxes('1\n0 1 0 0 999 480')
if __name__=='__main__':unittest.main()
