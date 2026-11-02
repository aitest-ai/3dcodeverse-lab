#!/usr/bin/env python3
"""V21 OpenStreetMap bicycle access-tag audit; source only, NOT navigation."""
import hashlib,json,pathlib,xml.etree.ElementTree as ET
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[2]
SOURCE=ROOT/"assets/setouchi/osm/onomichi-v20-20261102.osm"
ROUTES=ROOT/"outputs/v20/route-topology-report.json"
OUTPUT=ROOT/"outputs/v21/bicycle-risk-audit.json"
PIN="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
ALLOWED_KEYS=("highway","access","bicycle","foot","motor_vehicle","vehicle",
              "oneway","oneway:bicycle","access:conditional","bicycle:conditional",
              "cycleway","lanes","width","maxspeed","surface","bridge","tunnel")
def tags(x):
    return {t.get("k"):t.get("v") for t in x.findall("tag")}
def audit():
    blob=SOURCE.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=PIN:
        raise ValueError("V21 refuses modified original OSM snapshot")
    root=ET.fromstring(blob)
    nodes={n.get("id"):n for n in root.findall("node")}
    ways={w.get("id"):w for w in root.findall("way")}
    relations=root.findall("relation")
    route=json.loads(ROUTES.read_text())
    if route["source_sha256"]!=PIN:
        raise ValueError("V20 derived routes are not tied to pinned XML")
    bicycle_routes=[r for r in relations if tags(r).get("type")=="route" and tags(r).get("route")=="bicycle"]
    cycling_ids={m.get("ref") for r in bicycle_routes for m in r.findall("member")
                 if m.get("type")=="way"}
    turn_restrictions=[r for r in relations if tags(r).get("type")=="restriction"]
    paths={}
    for key in ("shortest_any_road","candidate_avoiding_trunk","candidate_avoiding_trunk_to_east"):
        record=route[key]
        segments=record["segments"];node_ids=record["node_ids"]
        if len(node_ids)!=len(segments)+1:
            raise ValueError("Path edge/node count mismatch")
        unique=[];part_lengths={};part_notes={};backwards=[]
        for i,edge in enumerate(segments):
            way_id=edge["osm_way_id"];way=ways[way_id]
            refs=[n.get("ref") for n in way.findall("nd")]
            a,b=node_ids[i:i+2]
            forward=any((m,n)==(a,b) for m,n in zip(refs,refs[1:]))
            reverse=any((m,n)==(b,a) for m,n in zip(refs,refs[1:]))
            if not forward and not reverse:
                raise ValueError("OSM source way does not share route edge")
            t=tags(way);ow=t.get("oneway")
            if way_id not in unique:unique.append(way_id)
            part_lengths[way_id]=part_lengths.get(way_id,0)+edge["meters"]
            part_notes[way_id]={k:v for k,v in t.items() if k in ALLOWED_KEYS}
            if (ow in ("yes","1","true") and not forward and t.get("oneway:bicycle")!="no") or (ow=="-1" and forward and t.get("oneway:bicycle")!="no"):
                backwards.append(way_id)
        evidence=[]
        for way_id in unique:
            t=part_notes[way_id]
            mode_exception=t.get("access")=="no" and t.get("bicycle")=="yes"
            access_unknown=t.get("bicycle") is None and t.get("access") is None
            evidence.append({"way_id":way_id,"length_m":round(part_lengths[way_id],2),
                "tags":t,"osm_bicycle_relation_member":way_id in cycling_ids,
                "mode_specific_bicycle_override":mode_exception,
                "bicycle_permission_untagged":access_unknown,
                "trunk_or_trunk_link":t.get("highway") in ("trunk","trunk_link"),
                "actual_field_legality_confirmed":False,
                "pavement_width_and_curbs_confirmed":False})
        paths[key]={"distance_m":record["distance_m"],"unique_way_count":len(unique),
            "unique_way_ids":unique,"node_count":len(node_ids),
            "way_evidence":evidence,
            "intersection_with_bicycle_route":[wid for wid in unique if wid in cycling_ids],
            "oneway_reverse_tagged_way_ids":sorted(set(backwards)),
            "road_navigation_approved":False}
    assert paths["shortest_any_road"]["unique_way_count"]==2
    assert paths["candidate_avoiding_trunk"]["unique_way_count"]==9
    assert paths["candidate_avoiding_trunk_to_east"]["unique_way_count"]==9
    assert paths["shortest_any_road"]["intersection_with_bicycle_route"]==["167631309"]
    assert paths["candidate_avoiding_trunk"]["intersection_with_bicycle_route"]==[]
    assert "388716484" in paths["candidate_avoiding_trunk"]["unique_way_ids"]
    assert any(e["mode_specific_bicycle_override"] for e in paths["candidate_avoiding_trunk"]["way_evidence"])
    assert not paths["candidate_avoiding_trunk"]["oneway_reverse_tagged_way_ids"]
    roadtags={wid:tags(w) for wid,w in ways.items()}
    one_way=[wid for wid,t in roadtags.items() if t.get("highway") and t.get("oneway")]
    result={"schema_version":1,"asset_id":"onomichi-v21-bicycle-access-risk-audit",
      "source_osm_xml_sha256":PIN,
      "source_date":"2026-11-02","license":"© OpenStreetMap contributors ODbL",
      "status":"OSM_TAG_REVIEW_ONLY__NO_NAVIGATION",
      "road_ways_total":sum(1 for t in roadtags.values() if t.get("highway")),
      "bicycle_relation_count":len(bicycle_routes),
      "bicycle_relation_ids":[r.get("id") for r in bicycle_routes],
      "turn_restriction_relations_found":len(turn_restrictions),
      "absence_of_turn_restrictions_does_not_prove_all_turns_legal":True,
      "tagged_oneway_ways":one_way,
      "paths":paths,
      "approval_gates":{"bicycle_access_field_verified":False,"route_signs_verified":False,
        "curb_cuts_verified":False,"actual_road_surface_elevation":False,
        "all_local_turn_rules_verified":False,
        "person_bicycle_fullwidth_collision":False,
        "ferry_to_halows_runtime":False,"browser_and_android_realplay":False},
      "legal_interpretation":["A bicycle=yes specific-mode tag may override access=no; must field-verify.",
        "An OSM bicycle route relation is not a certification of safety or end-to-end legal access.",
        "Untagged bicycle access is unresolved here, not automatically legal.",
        "No mapped type=restriction relation does not establish permission for every turn.",
        "Tag-based one-way checks are incomplete without implicit law and barriers."]}
    if result["road_ways_total"]!=70 or len(way_recs:=paths["candidate_avoiding_trunk"]["way_evidence"])!=9:
        raise ValueError("Unreviewed source topology drift")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"roads":result["road_ways_total"],"bicycle_relations":result["bicycle_relation_count"],
     "turn_restrictions_in_bbox":result["turn_restriction_relations_found"],
     "nontrunk_unique_way_count":len(way_recs),"way388716484_mode_specific":True,
     "status":result["status"]},ensure_ascii=False))
if __name__=="__main__":audit()
