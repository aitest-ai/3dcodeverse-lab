#!/usr/bin/env python3
"""V27 original-V06-GLB-BBOX projection, geometry-only. Zero field road permits.
Original private GLB binary and actual road-width are NOT in this public repository.
"""
import json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
STATIONS=ROOT/"assets/setouchi/onomichi-v26-field-stations.json"
OUT=ROOT/"outputs/onomichi-v27/derived-geometry-only.json"
BIKE_WIDTH=0.59478  # verified private V06 original GLB visible-axis bounding box
BIKE_LENGTH=1.77699
ORIGINAL_BIKE_SHA="7cb53e92247cf081354c1551b91ae812aab56be7c07748ed00764f0d2c844ece"
YAW=[0,10,20,30]
WIDTHS=[1.,1.2,1.5,1.8,2.2,3.]
BUFFER=.15
def half_projection(deg):
    a=math.radians(deg)
    return (BIKE_WIDTH*abs(math.cos(a))+BIKE_LENGTH*abs(math.sin(a)))/2
def main():
    src=json.loads(STATIONS.read_text())
    assert src["source_osm_way"]=="388716484"
    assert src["source_osm_sha256"]=="5adaecd750f1bea9517ddb9b0ebfabec11414b4f60309e98122d1434859ada76"
    stations=src["station_measurements"]
    assert len(stations)==9 and all(s["measured_clear_width_m"] is None for s in stations)
    cases=[]
    for angle in YAW:
        half=half_projection(angle)
        for w in WIDTHS:
            rem=w/2-half-BUFFER
            cases.append({"yaw_deg":angle,"hypothetical_width_m":w,
              "half_projection_m":round(half,4),"assumed_buffer_each_side_m":BUFFER,
              "remaining_half_geometry_m":round(rem,4),
              "geometry_only_fit":rem>=0,"bicycle_riding_approved":False})
    assert len(cases)==24
    assert any(x["geometry_only_fit"] for x in cases)
    assert any(not x["geometry_only_fit"] for x in cases)
    report={"schema_version":1,"source_way_id":"388716484",
       "private_bike_sha256":ORIGINAL_BIKE_SHA,"bicycle_visual_bbox_length_m":BIKE_LENGTH,
       "bicycle_visual_bbox_width_m":BIKE_WIDTH,
       "station_count":9,"hypothetical_centerline_position_count":371,
       "case_count":24,"cases":cases,
       "actual_field_width_m":None,"actual_road_surface_height_m":None,
       "private_original_v06_models_in_public_ci":False,
       "approvals":{"traffic_rights":False,"rider_dynamics":False,
         "actual_curb_sweep":False,"physics_collision":False,
         "gameplay_route_added":False,"android_or_browser_ride_passed":False}}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print("V27 source-bbox projection PASS; actual riding remains blocked",len(cases))
if __name__=="__main__":main()
