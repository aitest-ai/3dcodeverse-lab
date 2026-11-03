"""Fetch only public web templates through HTTP Range; zip member CRC verified.
Avoid downloading the full 1.25GB multi-platform archive. Official Godot release only.
"""
import urllib.request,json,struct,zlib,pathlib,hashlib,binascii
R=pathlib.Path(__file__).resolve().parents[1];release=json.loads((R/'evidence/godot-release.json').read_text());a=next(x for x in release['assets'] if x['name']=='Godot_v4.6.3-stable_export_templates.tpz');url=a['browser_download_url']
entries=json.loads((R/'evidence/template-index.json').read_text());out=R/'tools/templates/4.6.3.stable';out.mkdir(parents=True,exist_ok=True);proof=[]
def get(start,end):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})) as f:
  assert f.status==206 and f.headers['Content-Range'].startswith(f'bytes {start}-');return f.read()
for e in entries:
 if e['name'] not in ['templates/web_release.zip','templates/web_nothreads_release.zip']:continue
 h=get(e['offset'],e['offset']+29);v=struct.unpack('<4s5H3I2H',h);name_len,extra_len=v[-2:];start=e['offset']+30+name_len+extra_len
 b=get(start,start+e['compressed']-1);raw=zlib.decompress(b,-15) if e['method']==8 else b
 assert len(raw)==e['bytes'] and binascii.crc32(raw)&0xffffffff==v[6]
 p=out/pathlib.Path(e['name']).name;p.write_bytes(raw);proof.append({'file':p.name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'crc32_verified':True,'official_source':url})
(R/'evidence/template-download.json').write_text(json.dumps(proof,indent=2));print(proof)
