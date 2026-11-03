from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
R=Path(__file__).resolve().parents[1];text=''.join(p.read_text() for p in (R/'godot/scripts').glob('*.gd'))+'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ林汐海風里·←→↑↓'
f=TTFont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',fontNumber=3);sub=subset.Subsetter(options=subset.Options());sub.populate(text=text);sub.subset(f)
for n in f['name'].names:
 if n.nameID in [1,2,3,4,6]:n.string={1:'Harbor UI Subset',2:'Regular',3:'HarborUISubset-Regular-v02',4:'Harbor UI Subset Regular',6:'HarborUISubset-Regular'}[n.nameID].encode(n.getEncoding())
f.save(R/'godot/fonts/harbor.otf')
