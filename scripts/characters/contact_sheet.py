"""Combine four real Blender render outputs into one contact sheet."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else "outputs/human_mpfb")
names=["front","side","back","isometric","face","outfit"]
tile=520;pad=26;header=42
sheet=Image.new("RGB",(3*tile+4*pad,2*(tile+header)+3*pad),(26,32,42))
font=ImageFont.load_default()
draw=ImageDraw.Draw(sheet)
for i,n in enumerate(names):
  file=p/("preview_"+n+".png")
  assert file.is_file(), "Missing actual Blender render: "+n
  with Image.open(file) as im:
    im=im.convert("RGB")
    im.thumbnail((tile,tile),Image.Resampling.LANCZOS)
    row,col=divmod(i,3)
    x=pad+col*(tile+pad)+(tile-im.width)//2
    y=pad+row*(tile+header+pad)+header+(tile-im.height)//2
    sheet.paste(im,(x,y))
    draw.text((pad+col*(tile+pad)+8,pad+row*(tile+header+pad)+15),n.upper()+"  /  BLENDER RENDER",fill=(235,235,235),font=font)
out=p/"preview_contact_sheet.png"
sheet.save(out,optimize=True)
print("4-view real MPFB contact sheet:",out)
