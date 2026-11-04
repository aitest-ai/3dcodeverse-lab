import {build} from 'esbuild';
import {copyFile,mkdir,rm,writeFile,stat} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=dirname(fileURLToPath(import.meta.url));
const dist=resolve(root,'dist');
await rm(dist,{force:true,recursive:true});await mkdir(dist,{recursive:true});
const result=await build({
 entryPoints:[resolve(root,'main.mjs')],outfile:resolve(dist,'app.js'),
 bundle:true,format:'esm',platform:'browser',target:['es2022'],minify:true,
 legalComments:'eof',metafile:true
});
await copyFile(resolve(root,'index.html'),resolve(dist,'index.html'));
await copyFile(resolve(root,'node_modules/three/LICENSE'),resolve(dist,'LICENSE_THREE.txt'));
await writeFile(resolve(dist,'README-START-HERE.txt'),
 '瀨戶內 V30：真正 Three.js WebGL2 人物／自行車騎姿檢視\n\n'+
 '1. 本 ZIP 不包含私人 GLB，請保留原始 GLB 在自己的裝置上。\n'+
 '2. 解壓縮，用 Python 執行：python3 -m http.server 8766\n'+
 '3. 在瀏覽器打開 http://127.0.0.1:8766/ 。\n'+
 '4. 選兩個真正原人物與自行車 GLB，必須經 SHA256 完整核對。\n'+
 '5. 此工作臺不是尾道原版街景或實際道路遊玩驗收。\n', 'utf8');
const manifest={version:'V30',source:'public source-only bundled Three.js',
 status:'WEBGL2_VIEWER_BUILT_PRIVATE_GLBS_NOT_INCLUDED',originalModelsIncluded:false,
 originalGameModified:false,roadApproved:false,
 bundledJsBytes:(await stat(resolve(dist,'app.js'))).size,
 dependencies:['three@0.160.1']};
await writeFile(resolve(dist,'SOURCE_ONLY_MANIFEST.json'),JSON.stringify(manifest,null,2)+'\n');
if(!result.metafile?.outputs)throw new Error('esbuild missing output manifest');
console.log(JSON.stringify(manifest));
