from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
scene=json.loads((root/'dist/scene_view.json').read_text());route=scene['route']
W,H=1600,1000;im=Image.new('RGB',(W,H),(248,247,240));draw=ImageDraw.Draw(im)
font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ft=lambda size:ImageFont.truetype(font,size)
margin=105;xmin,xmax=-77,139;zmin,zmax=-31,116
scale=min((W-2*margin)/(xmax-xmin),(H-2*margin-85)/(zmax-zmin))
xo=(W-(xmax-xmin)*scale)/2;yo=margin+35
pt=lambda x,z:(round(xo+(x-xmin)*scale),round(yo+(z-zmin)*scale))
# OSM building outline is real footprint but generic location background.
for b in scene['buildings']:
 poly=[pt(x,-n) for x,n in b['polygon']]
 draw.polygon(poly,fill=(231,227,216),outline=(187,179,164),width=2)

parts=[(0,82.877,(73,129,121),'V002 核心'),(82.877,130.015,(92,145,172),'V004 商家街'),(130.015,197.724,(181,132,72),'V005 擴建'),(197.724,232,(197,90,73),'V006 本輪')]
for lo,hi,color,_ in parts:
 sub=[]
 for p in route:
  if lo-0.51<=p['s']<=hi+0.51:sub.append(pt(p['x'],p['z']))
 if len(sub)>1:draw.line(sub,fill=color,width=10,joint='curve')
# endpoints and selected town locations
for s,text in [(0,'入口'),(82.877,'V002'),(130.015,'V004'),(197.724,'V005'),(231.566,'V006 街尾')]:
 p=min(route,key=lambda v:abs(v['s']-s));x,y=pt(p['x'],p['z']);draw.ellipse((x-9,y-9,x+9,y+9),fill=(255,254,252),outline=(73,81,69),width=3)
 off=(14,-32) if text=='V006 街尾' else (14,-24)
 draw.text((x+off[0],y+off[1]),text,font=ft(24),fill=(53,55,50),stroke_width=3,stroke_fill=(248,247,240))
# road-boundary waypoints
for x,n,y in scene.get('raw_route',[]):pass

# Title and key, lower row
draw.text((105,35),'登別伊達時代村　V006 商家街延伸',font=ft(46),fill=(47,61,54))
draw.text((106,93),'凍結 OSM 路線 + V002 地形高程｜總長約 231.6 m（非現地測量圖）',font=ft(24),fill=(95,99,91))
legendY=H-112
for i,(_,_,color,label) in enumerate(parts):
 x=107+i*365;draw.line(((x,legendY+11),(x+47,legendY+11)),fill=color,width=10);draw.text((x+62,legendY-6),label,font=ft(23),fill=(60,62,59))
draw.text((W-170,170),'N ↑',font=ft(27),fill=(60,68,63))
draw.text((110,H-48),'© OpenStreetMap contributors · ODbL；建物名稱、位置來源與外觀假設分開標示',font=ft(20),fill=(112,111,105))
p=root/'V006_route_overview.png';im.save(p,optimize=True);print(p,im.size)