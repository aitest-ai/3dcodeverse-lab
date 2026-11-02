#!/usr/bin/env python3
"""Optional V18 OSM XML snapshot acquisition. Research only; no live runtime change."""
from pathlib import Path
import argparse,urllib.request,hashlib,json,datetime,xml.etree.ElementTree as ET,collections
BBOX="133.1985,34.3964,133.2060,34.4005"
FROM="1296327682"
TARGETS=("1296327655","1296327484","6191315885","6191315891")
def inspect(path):
 root=ET.parse(path).getroot()
 nodes={n.get("id") for n in root.findall("node")}
 graph=collections.defaultdict(set)
 classes={}
 for way in root.findall("way"):
  tags={t.get("k"):t.get("v") for t in way.findall("tag")}
  if "highway" not in tags:continue
  refs=[n.get("ref") for n in way.findall("nd")]
  for a,b in zip(refs,refs[1:]):
   if a in nodes and b in nodes:
    graph[a].add(b);graph[b].add(a)
    classes[(a,b)]=(way.get("id"),tags["highway"])
 found={}
 for target in TARGETS:
  if FROM not in nodes or target not in nodes:
   found[target]={"topology_connected":False,"reason":"endpoint not present in snapshot"}
   continue
  visited={FROM};queue=collections.deque([FROM])
  while queue and target not in visited:
   for neighbor in graph[queue.popleft()]:
    if neighbor not in visited:visited.add(neighbor);queue.append(neighbor)
  found[target]={"topology_connected":target in visited,"bicycle_legal_verified":False}
 return {"status":"RESEARCH_ONLY_NOT_NAVIGABLE","source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
         "nodes":len(nodes),"connections":found,"authorized_to_generate_player_routes":False,
         "note":"Shared node topology is not proof of legal bicycle access, curb cuts, or passable 3D terrain"}
def main():
 p=argparse.ArgumentParser();p.add_argument("--fetch",type=Path);p.add_argument("--input",type=Path)
 p.add_argument("--out",type=Path)
 a=p.parse_args()
 if bool(a.fetch)==bool(a.input):p.error("provide exactly one of --fetch or --input")
 src=a.input
 if a.fetch:
  src=a.fetch
  if src.exists():raise FileExistsError("Never overwrite research source")
  url="https://api.openstreetmap.org/api/0.6/map?bbox="+BBOX
  req=urllib.request.Request(url,headers={"User-Agent":"OnomichiV18GeodataStudy/0.1"})
  with urllib.request.urlopen(req,timeout=45) as response:payload=response.read(15000001)
  if len(payload)>15000000:raise RuntimeError("OSM response too large")
  ET.fromstring(payload)
  src.parent.mkdir(parents=True,exist_ok=True);src.write_bytes(payload)
  src.with_suffix(".source.json").write_text(json.dumps({"url":url,"retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"license":"ODbL © OpenStreetMap contributors"},indent=2))
 result=inspect(src)
 if a.out:
  a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
