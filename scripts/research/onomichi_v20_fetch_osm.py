#!/usr/bin/env python3
"""Acquire one fresh OpenStreetMap XML research snapshot, without changing game state.
Source: api.openstreetmap.org/api/0.6/map. Return non-zero on incomplete/blocked fetch.
This is data acquisition only; no permission to derive legal bicycle routes.
"""
import argparse, datetime as dt, hashlib, json, os, pathlib, time, urllib.request, xml.etree.ElementTree as ET
BBOX="133.1985,34.3964,133.2060,34.4005"
URL=f"https://api.openstreetmap.org/api/0.6/map?bbox={BBOX}"
MAX_BYTES=18_000_000
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=pathlib.Path,default=pathlib.Path("outputs/v20/onomichi-v20-current-bbox.osm"))
    a=ap.parse_args()
    if a.out.exists(): raise FileExistsError("Refuse to overwrite source evidence: "+str(a.out))
    errors=[]
    for attempt in range(3):
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":"Onomichi-3D-Cycling-Research/0.20 (+https://github.com/aitest-ai/3dcodeverse-lab)","Accept":"application/xml"})
            with urllib.request.urlopen(req,timeout=55) as res:
                content_type=res.headers.get("Content-Type","")
                raw=res.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES:raise ValueError("XML exceeds allowed response size")
                if res.status!=200:raise ValueError(f"Unexpected HTTP status {res.status}")
            root=ET.fromstring(raw)
            if root.tag!="osm" or root.get("version")!="0.6":raise ValueError("Response is not OSM v0.6 XML")
            nodes=root.findall("node");ways=root.findall("way")
            highway=[w for w in ways if any(t.get("k")=="highway" for t in w.findall("tag"))]
            if len(nodes)<40 or len(highway)<3:raise ValueError("Unreasonably small bbox, refuse incomplete source")
            a.out.parent.mkdir(parents=True,exist_ok=True)
            a.out.write_bytes(raw)
            sha=hashlib.sha256(raw).hexdigest()
            result={"schema_version":1,"asset_id":"onomichi-v20-fresh-source-only",
              "downloaded_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
              "source_url":URL,"bbox_wgs84":list(map(float,BBOX.split(","))),
              "license":"© OpenStreetMap contributors, ODbL",
              "sha256":sha,"bytes":len(raw),"osm_nodes":len(nodes),"osm_ways":len(ways),
              "highway_ways":len(highway),
              "frontier_node_present":any(x.get("id")=="1296327682" for x in nodes),
              "halows_v09_south_node_present":any(x.get("id")=="6191315885" for x in nodes),
              "halows_v09_east_node_present":any(x.get("id")=="6191315891" for x in nodes),
              "conclusion":"UNREVIEWED_OSM_ROAD_DATA_NOT_A_BICYCLE_ROUTE",
              "bicycle_access_approved":False,"runtime_changed":False,
              "source_immutable":True}
            a.out.with_suffix(".source.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
            print(json.dumps(result,indent=2,ensure_ascii=False))
            return
        except Exception as e:
            errors.append(f"{type(e).__name__}: {e}")
            print("OSM attempt",attempt+1,"failed:",errors[-1],flush=True)
            time.sleep(3+attempt*3)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    (a.out.parent/"fetch_failure.json").write_text(json.dumps({"source_url":URL,"attempt_errors":errors,"status":"SOURCE_FETCH_FAILED_DO_NOT_CLAIM_CONNECTED","runtime_changed":False},indent=2))
    raise RuntimeError("Official OSM API could not be fetched or validated; no new route created")
if __name__=="__main__":main()
