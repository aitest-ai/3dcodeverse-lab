#!/usr/bin/env python3
"""Estimate *in-place* horse Gallop root travel from deformed hoof-mesh contact.

No IK changes, no overwrite of Quaternius's 13 original animations.
Fits one longitudinal displacement per Blender Action frame to minimize the
XY residual of hoof-center motion in near-ground frame pairs. It is a
treadmill-to-world retarget hint, NOT proof of zero hoof slip on actual ground.
"""
import argparse
import json
import math
from pathlib import Path

def fit(data):
    steps=[]
    samples=data["samples"]
    height=float(data["horse_height_source_units"])
    frames=[float(x["frame"]) for x in samples]
    for hoof in ("front_L","front_R","hind_L","hind_R"):
        coords=[tuple(float(v) for v in s["hoof"][hoof]["xyz"]) for s in samples]
        z=[p[2] for p in coords]
        threshold=max(.01*height,.15*(max(z)-min(z)))
        contact=[v<=min(z)+threshold for v in z]
        for i in range(1,len(samples)):
            if not (contact[i] and contact[i-1]):continue
            dt=frames[i]-frames[i-1]
            if dt<=0:continue
            steps.append({"hoof":hoof,"dx":coords[i][0]-coords[i-1][0],
                          "dy":coords[i][1]-coords[i-1][1],
                          "dt":dt,"from_frame":frames[i-1],"to_frame":frames[i]})
    if len(steps)<20:raise RuntimeError("Too few near-ground hoof intervals for calibration")
    # Least-squares root move over source local +Y, with 0.0 lateral correction.
    denom=sum(s["dt"]**2 for s in steps)
    root_per_frame=-sum(s["dy"]*s["dt"] for s in steps)/denom
    def rms(subset,corrected):
        return math.sqrt(sum(s["dx"]**2+(s["dy"]+(root_per_frame*s["dt"] if corrected else 0))**2
                             for s in subset)/len(subset))
    before,after=rms(steps,False),rms(steps,True)
    if after>=before:raise RuntimeError("Root motion fit did not improve contact residual")
    per_hoof={}
    for hoof in ("front_L","front_R","hind_L","hind_R"):
        subset=[s for s in steps if s["hoof"]==hoof]
        per_hoof[hoof]={"contact_step_count":len(subset),
                       "raw_contact_step_rms":round(rms(subset,False),6),
                       "translated_contact_step_rms":round(rms(subset,True),6)}
    return {
      "schema_version":1,"source":"Quaternius original CC0 horse, V2 armature evaluated hoof mesh",
      "reference_animation":"Gallop","source_frames":len(samples),
      "source_action_frame_range":data["action_frame_range"],
      "horse_height_source_units":height,
      "root_translation_y_source_units_per_action_frame":round(root_per_frame,9),
      "root_speed_by_horse_height_per_action_frame":round(abs(root_per_frame)/height,7),
      "root_direction":"source local +Y" if root_per_frame>0 else "source local -Y",
      "fit_contact_step_count":len(steps),
      "raw_contact_step_rms":round(before,6),
      "translated_contact_step_rms":round(after,6),
      "rms_residual_reduction_percent":round(100*(1-after/before),2),
      "limbs":per_hoof,
      "warning":"Root translation is derived from contact geometry and may not match race speed or surface physics; it does not alter animation joints, track friction, hoof intersection or create a world-space controller.",
      "integration_hint":"Use absolute per-frame speed * action source frame range / glTF clip.duration * imported horse scale; align signed source local Y to actual world forward heading."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("hoof_qa_json")
    p.add_argument("--output",help="Write calibrated JSON (default adjacent race_motion_calibration.json)")
    args=p.parse_args()
    source=Path(args.hoof_qa_json)
    result=fit(json.loads(source.read_text(encoding="utf-8")))
    target=Path(args.output) if args.output else source.parent/"race_motion_calibration.json"
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("HORSE_ROOT_MOTION_CALIBRATION",json.dumps(result,ensure_ascii=False))
if __name__=="__main__":main()
