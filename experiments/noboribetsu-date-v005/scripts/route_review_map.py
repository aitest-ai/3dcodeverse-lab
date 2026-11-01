"""Diagnostic plan view derived from saved, local OSM footprints + route. Not official park map."""
from pathlib import Path
import json,os,matplotlib.pyplot as plt
ROOT=Path(os.environ.get('DATE_V005_PROJECT_ROOT',str(Path(__file__).resolve().parent.parent)))
v=json.loads((ROOT/'runtime/dist/scene_view.json').read_text())
r=v['route'];old=[p for p in r if p['s']<=130.01461218];new=[p for p in r if p['s']>=130.01461217]
fig,ax=plt.subplots(figsize=(10,5.4),dpi=150)
for b in v['buildings']:
 xs=[q[0] for q in b['polygon']];zs=[-q[1] for q in b['polygon']]
 ax.fill(xs,zs,facecolor='#cbd1c7',edgecolor='#63766b',alpha=.64,lw=.7)
ax.plot([p['x'] for p in old],[p['z'] for p in old],lw=3.3,label='Earlier route (V002-V004)')
ax.plot([p['x'] for p in new],[p['z'] for p in new],lw=3.9,label='Added V005 route')
for b in v['buildings']:
 if b['id'] in v['extension_v005']['building_ids']:
  x=sum(p[0] for p in b['polygon'])/len(b['polygon']);z=-sum(p[1] for p in b['polygon'])/len(b['polygon']);
  label='Waraji-ya' if 'わらじ' in b['name'] else 'Utsuroi-kan'
  textxy=(30,92) if 'わらじ' in b['name'] else (63,47)
  ax.annotate(label,(x,z),xytext=textxy,textcoords='data',fontsize=9,arrowprops=dict(arrowstyle='-',lw=.7))
ax.scatter([r[0]['x'],new[0]['x'],r[-1]['x']],[r[0]['z'],new[0]['z'],r[-1]['z']],s=44,zorder=5)
ax.annotate('Entrance',(r[0]['x'],r[0]['z']),xytext=(6,-12),textcoords='offset points',fontsize=8)
ax.annotate('V004 junction',(new[0]['x'],new[0]['z']),xytext=(7,10),textcoords='offset points',fontsize=8)
ax.annotate('V005 end',(r[-1]['x'],r[-1]['z']),xytext=(83,108),textcoords='data',fontsize=8)
ax.set_title('Noboribetsu Date Jidaimura — V005 R1 route / frozen OSM overview',fontsize=12)
ax.set_xlabel('East (metres, local model)');ax.set_ylabel('South (metres, local model)')
ax.set_aspect('equal');ax.invert_yaxis();ax.grid(alpha=.15);ax.legend(loc='upper right',fontsize=9)
fig.tight_layout();out=ROOT/'V005_route_overview.png';fig.savefig(out,bbox_inches='tight');plt.close(fig)
print(out)