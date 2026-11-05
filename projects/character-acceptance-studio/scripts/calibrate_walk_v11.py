import json,math,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];F=R/'inputs-v11/v10/horse-brown-grounded-review/0.1.0';meta=json.loads((F/'adaptation.json').read_text());a=json.loads((F/'motion-audit.json').read_text())['clips']['Walk'];rows=a['samples'][:-1];N=len(rows);T=a['duration_s'];feet={}
for key in rows[0]['feet']:
 mask=[r['feet'][key]['minimum_sole_y_m']<.012 and r['feet'][key]['reference_m'][2]<.022 for r in rows];runs=[]
 for i in range(N):
  if mask[i] and not mask[(i-1)%N]:
   j=i
   while mask[j%N] and j-i<N:j+=1
   runs.append((i,j))
 start,end=max(runs,key=lambda x:x[1]-x[0]);xs=[(i-start)*T/N for i in range(start,end)];ys=[rows[i%N]['feet'][key]['reference_m'][1] for i in range(start,end)];xm=statistics.mean(xs);ym=statistics.mean(ys);v=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs);err=math.sqrt(statistics.mean((y-(ym+v*(x-xm)))**2 for x,y in zip(xs,ys)));p=[statistics.mean(rows[i%N]['feet'][key]['reference_m'][j] for i in range(start,end)) for j in range(3)];feet[key]={'phase':start/N,'duty':(end-start)/N,'source_stance_mean_m':p,'fitted_speed_m_s':v,'fit_rms_m':err,'source_stance_span_m':max(ys)-min(ys),'source_max_lift_m':max(r['feet'][key]['minimum_sole_y_m'] for r in rows)}
v=statistics.mean(feet[k]['fitted_speed_m_s'] for k in ['FrontL','FrontR']);out={'source_model_sha256':meta['model_sha256'],'duration_s':T,'source_sampling_hz':120,'candidate_speed_m_s':v,'candidate_stride_m':v*T,'selection_note':'Measured fore-stance mean slope is the conservative initial root speed; rear source stance slopes disagree and require correction. Subject to native reachability and actual browser verification.','feet':feet,'display_calibration':meta['display_calibration']};(R/'work/v11/calibration-initial.json').write_text(json.dumps(out,indent=2)+'\n');print('CALIBRATED',v)

expected=json.loads((R/"config-v11/walk-plan.json").read_text());assert out["source_model_sha256"]==expected["source_model_sha256"]
for key,f in out["feet"].items():
 for field in ["phase","fitted_speed_m_s","fit_rms_m","source_max_lift_m"]:assert abs(f[field]-expected["feet"][key][field])<1e-5,(key,field)
 assert f["duty"]==expected["feet"][key]["source_duty"]
