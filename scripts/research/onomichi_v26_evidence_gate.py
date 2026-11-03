#!/usr/bin/env python3
"""V26: conservative 9-station OSM road-source evidence gate, not navigation."""
import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
SRC=ROOT/"assets/setouchi/onomichi-v26-field-stations.json"
OSM_SHA="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
GSI_SHA="03726ce15167b760f6a738c1862097c258857299cae7a32353a84931c44cdbf1"
def inspect(d):
    assert d["schema_version"]==1
    assert d["candidate"]=="V26" and d["source_osm_way"]=="388716484"
    assert d["source_osm_sha256"]==OSM_SHA and d["source_derived_gsi_grid_sha256"]==GSI_SHA
    assert not any(d[k] for k in ["roadway_width_surveyed","actual_pavement_height_surveyed","cycling_legal_access_verified","shared_v06_v15_vertical_datum_verified","game_swept_collision_verified","browser_webgl2_riding_verified","android_riding_verified","site_deployed"])
    assert d["private_game_assets_in_public_git"] is False
    pts=d["station_measurements"]
    assert len(pts)==9
    assert [p["id"] for p in pts]==[f"S{i:02}" for i in range(9)]
    assert [p["chainage_m"] for p in pts]==[0,10,20,30,40,50,60,70,74.364]
    assert abs(pts[0]["lat"]-34.3996339)<1e-7
    assert abs(pts[-1]["lon"]-133.2049673)<1e-7
    for p in pts:
        assert 34.3989<p["lat"]<34.3997 and 133.2047<p["lon"]<133.2051
        assert 0<p["estimated_gsi_ground_m"]<20
        assert p["measured_clear_width_m"] is None or 0<p["measured_clear_width_m"]<25
        assert p["measured_pavement_m"] is None or -50<p["measured_pavement_m"]<500
        assert p["curb_height_cm"] is None or 0<=p["curb_height_cm"]<150
        assert p["field_bicycle_sign"] in ["unknown","permitted","prohibited","walk-bike"]
        assert p["barrier"] in ["unknown","clear","present"]
        assert p["evidence_source_url"] is None or p["evidence_source_url"].startswith(("https://","http://"))
        if p["measured_clear_width_m"] is not None:
            assert p["evidence_source_url"] and p["observed_date"] and p["measured_by"],"Unattributed measurement"
    return {"stations":len(pts),"measured_width_count":sum(p["measured_clear_width_m"] is not None for p in pts),
      "source_only":True,"road_navigation_approved":False,"actual_road_collision_tested":False}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--evidence",type=pathlib.Path,default=SRC)
    args=parser.parse_args()
    print(json.dumps(inspect(json.loads(args.evidence.read_text())),ensure_ascii=False))
