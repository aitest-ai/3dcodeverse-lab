"""Package the exact working viewer and pinned GLBs into one offline HTML (no server/CDN).
Uses esbuild 0.25.12 only as a build tool; set ESBUILD_BIN to an installed executable,
or use the pinned npx fallback. Runtime SHA-256 verification remains native WebCrypto.
"""
import argparse,base64,json,mimetypes,os,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'OPEN_STUDIO.html');a=p.parse_args()
work=R/'work/standalone-build';work.mkdir(parents=True,exist_ok=True)
source=(R/'web/app.js').read_text().replace("from 'three'",'from '+json.dumps(str(R/'web/vendor/three.module.js'))).replace("from 'three/addons/loaders/GLTFLoader.js'",'from '+json.dumps(str(R/'web/vendor/jsm/loaders/GLTFLoader.js'))).replace("from 'three/addons/controls/OrbitControls.js'",'from '+json.dumps(str(R/'web/vendor/jsm/controls/OrbitControls.js')))
(work/'app.mjs').write_text(source)
binary=os.environ.get('ESBUILD_BIN');command=[binary] if binary else ['npx','--yes','--package','esbuild@0.25.12','esbuild']
subprocess.run([*command,str(work/'app.mjs'),'--bundle','--format=esm','--minify','--alias:three='+str(R/'web/vendor/three.module.js'),'--outfile='+str(work/'bundle.js')],check=True)
registry=json.loads((R/'assets/registry.json').read_text());paths={'../assets/registry.json'}
for c in registry['characters']:paths.update([c['profile'],c['source']['url'],c['candidate']['url']])
files={}
for url in paths:
    path=(R/'web'/url).resolve();mime=mimetypes.guess_type(path)[0] or 'application/octet-stream';files[url]={'mime':mime,'base64':base64.b64encode(path.read_bytes()).decode()}
html=(R/'web/index.html').read_text();html=re.sub(r'<script type="importmap">.*?</script>','',html)
html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+(R/'web/style.css').read_text()+'</style>')
for name in ['INVENTORY.md','ACCEPTANCE.md']:
    path=R/'docs'/name
    if path.exists():html=html.replace('href="../docs/'+name+'" target="_blank"','href="data:text/plain;base64,'+base64.b64encode(path.read_bytes()).decode()+'" download="'+name+'"')
embed=json.dumps({'schema_version':1,'files':files},ensure_ascii=True,separators=(',',':'))
bundle=(work/'bundle.js').read_text().replace('</script','<\\/script')
html=html.replace('<script type="module" src="app.js"></script>','<script>window.STUDIO_EMBED='+embed+';</script><script type="module">'+bundle+'</script>')
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(html);print('Standalone HTML',a.output,a.output.stat().st_size,'bytes; embedded',len(files),'exact pinned resources')
