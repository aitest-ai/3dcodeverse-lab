"""Execute INSIDE licensed Unreal Editor, not host Python.
UnrealEditor-Cmd HarborPilot.uproject -unattended -nop4 -NullRHI -ExecutePythonScript=/.../import_character.py
This task's environment does not have Unreal Editor; this script is an unverified handoff.
"""
import json,os,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'evidence/unreal-import.json'
report={'status':'STARTED','scope':'FBX import and native asset-class verification, not gameplay/render acceptance'}
try:
 source=Path(os.environ.get('HARBOR_FBX',str(ROOT/'assets/harbor-courier-v02.fbx')))
 if not source.is_file():raise FileNotFoundError(source)
 destination='/Game/HarborPilot/Characters/LinXi'
 options=unreal.FbxImportUI()
 options.automated_import_should_detect_type=False
 options.import_mesh=True
 options.import_as_skeletal=True
 options.import_animations=True
 options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
 options.skeletal_mesh_import_data.import_morph_targets=True
 task=unreal.AssetImportTask()
 task.filename=str(source)
 task.destination_path=destination
 task.automated=True
 task.replace_existing=False
 task.save=True
 task.options=options
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 assets=[]
 for path in task.imported_object_paths:
  asset=unreal.EditorAssetLibrary.load_asset(path)
  if asset:assets.append({'path':path,'class':asset.get_class().get_name()})
 if not any(a['class']=='SkeletalMesh' for a in assets):raise RuntimeError('No imported SkeletalMesh')
 if not any(a['class']=='AnimSequence' for a in assets):raise RuntimeError('No imported AnimSequence; inspect FBX take import settings')
 unreal.EditorAssetLibrary.save_directory(destination,only_if_is_dirty=False,recursive=True)
 report.update(status='PASS_IMPORT_ONLY',engine=unreal.SystemLibrary.get_engine_version(),assets=assets)
except Exception:
 report.update(status='FAIL',error=traceback.format_exc())
 raise
finally:
 OUTPUT.parent.mkdir(exist_ok=True,parents=True)
 OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2))
