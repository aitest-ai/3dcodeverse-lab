"""Six rendered horse views from real Blender 5.2 images, not generated illustrations."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
folder=Path(sys.argv[1])
names=["front","side","back","isometric","motion_a","motion_b"]
tile=440;head=36;pad=18
sheet=Image.new("RGB",(3*(tile+pad)+pad,2*(tile+head+pad)+pad),(29,36,46))
draw=ImageDraw.Draw(sheet)
font=ImageFont.load_default()
for i,name in enumerate(names):
    row,col=divmod(i,3)
    with Image.open(folder/("preview_"+name+".png")) as image:
        image=image.convert("RGB")
        image.thumbnail((tile,tile),Image.Resampling.LANCZOS)
        x=pad+col*(tile+pad)+(tile-image.width)//2
        y=pad+row*(tile+head+pad)+head+(tile-image.height)//2
        sheet.paste(image,(x,y))
        draw.text((pad+col*(tile+pad)+10,pad+row*(tile+head+pad)+11),
            folder.name+" / "+name.upper(),font=font,fill=(240,240,245))
out=folder/"preview_contact_sheet.png"
sheet.save(out,optimize=True)
print("CONTACT_SHEET",out,out.stat().st_size)
