#!/usr/bin/env python3
"""V20 centreline-topology study only, never player navigation or legal access advice.
Reads the exact pinned 2026-11-02 official OSM XML, no live network needed.
"""
from __future__ import annotations
import collections, hashlib, heapq, json, math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"assets/setouchi/osm/onomichi-v20-20261102.osm"
OUTPUT=ROOT/"outputs/v20/route-topology-report.json"
PIN="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
FRONTIER="1296327682"
TARGET="1296327655"
EAST="6191315891"
SOUTH="6191315885"

def length_m(a,b):
    lat=(a[0]+b[0])*.5
    return math.hypot((a[1]-b[1])*111320*math.cos(math.radians(lat)),
                      (a[0]-b[0])*111132)

def build_graph(nodes,ways,allow_trunk):
    adj=collections.defaultdict(list)
    for w in ways:
        tags={t.get("k"):t.get("v") for t in w.findall("tag")}
        road=tags.get("highway")
        if not road or road in ("construction","proposed","motorway","motorway_link","steps"):
            continue
        if not allow_trunk and road in ("trunk","trunk_link"):
            continue
        refs=[x.get("ref") for x in w.findall("nd")]
        for a,b in zip(refs,refs[1:]):
            if a not in nodes or b not in nodes:continue
            d=length_m(nodes[a],nodes[b])
            if not d:continue
            edge={"osm_way_id":w.get("id"),"road_class":road,
                  "bicycle_tag":tags.get("bicycle"),"access_tag":tags.get("access"),
                  "oneway_tag":tags.get("oneway"),"meters":d}
            adj[a].append((b,edge));adj[b].append((a,edge))
    return adj

def shortest(adj,source,target,nodes):
    best={source:0.}; prev={};q=[(0.,source)]
    while q:
        dist,u=heapq.heappop(q)
        if dist>best.get(u,float("inf")):continue
        if u==target:break
        for v,e in adj[u]:
            nd=dist+e["meters"]
            if nd<best.get(v,float("inf")):
                best[v]=nd;prev[v]=(u,e);heapq.heappush(q,(nd,v))
    if target not in best: return None
    names=[target]; edges=[];cur=target
    while cur!=source:
        v,e=prev[cur]
        edges.append(e); names.append(v);cur=v
    names.reverse();edges.reverse()
    return {"distance_m":round(best[target],2),
            "node_count":len(names),"node_ids":names,
            "polyline_lat_lon":[list(nodes[n]) for n in names],
            "unique_way_ids":list(dict.fromkeys(e["osm_way_id"] for e in edges)),
            "road_classes":list(dict.fromkeys(e["road_class"] for e in edges)),
            "segments":[{**{k:v for k,v in e.items() if k!="meters"},
                         "meters":round(e["meters"],2)} for e in edges],
            "legal_bicycle_route":False,"real_road_width_verified":False,
            "safe_junctions_verified":False,"road_surface_height_verified":False,
            "directional_turn_restrictions_applied":False}

def main():
    raw=SOURCE.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=PIN:raise RuntimeError("Pinned official OSM snapshot checksum changed")
    root=ET.fromstring(raw)
    if root.tag!="osm":raise RuntimeError("Non OSM source")
    nodes={n.get("id"):(float(n.get("lat")),float(n.get("lon")))
           for n in root.findall("node")}
    ways=root.findall("way")
    hw=[w for w in ways if any(t.get("k")=="highway" for t in w.findall("tag"))]
    if (len(nodes),len(ways),len(hw))!=(1436,154,70):
        raise RuntimeError("OSM source scope unexpectedly changed")
    for id in (FRONTIER,TARGET,EAST,SOUTH):
        if id not in nodes:raise RuntimeError("Known anchor not present: "+id)
    all_g=build_graph(nodes,ways,True)
    no_trunk=build_graph(nodes,ways,False)
    any_path=shortest(all_g,FRONTIER,TARGET,nodes)
    nontrunk_path=shortest(no_trunk,FRONTIER,TARGET,nodes)
    east_path=shortest(no_trunk,FRONTIER,EAST,nodes)
    if not all((any_path,nontrunk_path,east_path)):
        raise RuntimeError("OSM data cannot geometrically connect known anchors")
    # A route with an OSM shared node is NOT yet a safety, law or collision pass.
    if not (450<any_path["distance_m"]<520 and 575<nontrunk_path["distance_m"]<640):
        raise RuntimeError("Unexpected path distances, review source and algorithm")
    report={
      "schema_version":1,"asset_id":"onomichi-v20-route-topology-candidate",
      "source_file":str(SOURCE.relative_to(ROOT)),
      "source_sha256":sha,"source_date_utc":"2026-11-02T05:29:20Z",
      "source_license":"© OpenStreetMap contributors / ODbL",
      "data_counts":{"nodes":len(nodes),"ways":len(ways),"road_ways":len(hw)},
      "previous_snapshot_minimum_centerline_gap_m":441.24,
      "current_centerline_connected":True,
      "start_node":FRONTIER,"target_halows_v09_road_node":TARGET,
      "shortest_any_road":any_path,
      "candidate_avoiding_trunk":nontrunk_path,
      "candidate_avoiding_trunk_to_east":east_path,
      "risk_flags":{"bicycle_tagged_yes_and_access_no_at_start":True,
          "bicycle_legality_field_checked":False,"local_turn_restriction_checked":False,
          "lane_width_and_curb_cuts_surveyed":False,"road_surface_or_bridge_grade_surveyed":False,
          "V06_V15_shared_vertical_datum_verified":False,"cycling_blue_line_field_verified":False,
          "continuous_actor_bicycle_sweep_collision_tested":False,
          "ferry_to_halows_3d_runtime_connected":False,
          "browser_android_gameplay_verified":False},
      "conclusion":"OSM_GRAPH_CONNECTED_ONLY__NOT_A_VERIFIED_CYCLING_ROUTE"
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("V20 connected OSM research topology; not a legal bicycle route.")
    print(json.dumps({"any_m":any_path["distance_m"],"no_trunk_m":nontrunk_path["distance_m"],
       "no_trunk_to_east_m":east_path["distance_m"],"ways":nontrunk_path["unique_way_ids"]},ensure_ascii=False))
if __name__=="__main__":main()
