#!/usr/bin/env python3
"""V22 source-locked 377 -> 317 OSM way and field-access QA, NOT routing.
Public GitHub CI validates OSM XML, not user-owned private 211 MB Runtime or GSI PNG.
The complete private V22 package additionally verifies original GSI tile pixels.
"""
import hashlib,json,math,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OSM=ROOT/"assets/setouchi/osm/onomichi-v20-20261102.osm"
OUT=ROOT/"outputs/v22/onomichi-shared-entry-gate.json"
SHA="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
WAY="388716484"
NODE_IDS=["1296327682","3918810183","3918810175","3918269426"]
EXPECTED_TAGS={"highway":"residential","access":"no","bicycle":"yes",
               "foot":"yes","motor_vehicle":"yes"}
def keytags(obj):return {tag.get("k"):tag.get("v") for tag in obj.findall("tag")}
def meters(a,b):
    lat=(a[0]+b[0])/2
    return math.hypot((a[0]-b[0])*111132,
                      (a[1]-b[1])*111320*math.cos(math.radians(lat)))
def main():
    raw=OSM.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise RuntimeError("Original XML SHA mismatch")
    root=ET.fromstring(raw)
    nodes={n.get("id"):n for n in root.findall("node")}
    ways={w.get("id"):w for w in root.findall("way")}
    original=ways[WAY]
    ids=[n.get("ref") for n in original.findall("nd")]
    if ids!=NODE_IDS:raise RuntimeError("OSM way 388716484 node ordering drift")
    tags=keytags(original)
    if any(tags.get(k)!=v for k,v in EXPECTED_TAGS.items()):
        raise RuntimeError("Access or bicycle tag changed; require manual re-review")
    positions=[(float(nodes[n].get("lat")),float(nodes[n].get("lon"))) for n in ids]
    edges=[round(meters(a,b),3) for a,b in zip(positions,positions[1:])]
    total=round(sum(edges),2)
    if abs(total-74.36)>.05:raise RuntimeError(f"Geometry drift {total}")
    joins={}
    for way in root.findall("way"):
        if way.get("id")==WAY:continue
        t=keytags(way)
        if "highway" not in t:continue
        other={q.get("ref") for q in way.findall("nd")}
        meet=[x for x in (ids[0],ids[-1]) if x in other]
        if meet: joins[way.get("id")]={"shared_endpoints":meet,
                    "highway":t["highway"],"ref":t.get("ref"),
                    "traffic_rules_and_signs_field_verified":False}
    for wid,tag,node in [("114435640","secondary",ids[0]),
                         ("167631309","trunk",ids[-1]),
                         ("388652159","residential",ids[-1])]:
        if joins.get(wid,{}).get("highway")!=tag or node not in joins[wid]["shared_endpoints"]:
            raise RuntimeError("Original junction network no longer matches")
    field={
      "updated_field_sign_photos":None,"actual_bicycle_legal_access":None,
      "road_surface_width_m":None,"road_curbs_and_barriers":None,
      "local_turn_restrictions":None,"road_surface_height_m":None,
      "continuous_bicycle_collision":None,"actual_browser_android_gameplay":None}
    gsi_derived=[2.81,2.70,2.80,2.48]
    report={"schema_version":1,"asset_id":"onomichi-v22-shared-entry-evidence",
      "source_osm_sha256":SHA,"osm_way_id":WAY,"tags":tags,
      "osm_node_ids":ids,"wgs84_lat_lon":positions,
      "edge_centerline_m":edges,"length_centerline_m":total,
      "known_ways_sharing_endpoints":joins,
      "gsi_dem_derived_estimates_m":gsi_derived,
      "gsi_tile_sha256_reference":"79dc9e009a448aec5726ee1c13906270fef196e92c36286075e5474310318e9c",
      "gsi_original_tile_pixel_check_in_public_ci":False,
      "source_osm_nodes_checked":True,
      "osm_tag_interpretation":"bicycle=yes is a mode-specific override for access=no in OSM tagging, not field permission proof",
      "field_evidence_pending":field,
      "approvals":{"bicycle_navigation":False,"actual_signage":False,
        "junction_roadwidth_and_curbcuts":False,"turning_legality":False,
        "road_surface_altimetry":False,"swept_bike_collision":False,
        "runtime_route_merge":False,"desktop_webgl2_gameplay":False,
        "android_gameplay":False},
      "note":"Unmapped traffic signs or barriers are not evidence of their absence. OSM centreline is not a navigable road mesh.",
      "license":"© OpenStreetMap contributors / ODbL"}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"result":"OSM_WAY_SOURCE_PASS__RIDEABILITY_BLOCKED",
                      "centerline_m":total,"segments":edges,
                      "endpoints":list(joins.keys())},ensure_ascii=False))
if __name__=="__main__":main()
