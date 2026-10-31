/* Actual local WebGL integration review. Requires Playwright + Chromium.
 * Does not claim a physical GPU, a full game, or an Android device test.
 * Usage: node browser_review.cjs http://127.0.0.1:8067 OUTPUT_DIRECTORY
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES
  ? require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'playwright'))
  : require('playwright');
const url = process.argv[2], out = path.resolve(process.argv[3] || 'browser-review');
if (!/^http:\/\/(127\.0\.0\.1|localhost):\d+\/?$/.test(url || '')) throw Error('Use the explicitly started localhost viewer URL');
fs.mkdirSync(out, {recursive:true});
const write = (name, value) => fs.writeFileSync(path.join(out, name), JSON.stringify(value, null, 2)+'\n');
const ready = async page => {
  await page.waitForFunction(() => window.characterStudioReview && ['ready','error','unsupported'].includes(window.characterStudioReview.status), null, {timeout:90000});
  assert.equal(await page.evaluate(() => window.characterStudioReview.status), 'ready', await page.locator('#load-message').textContent());
};
(async () => {
  const browser = await chromium.launch({headless:true,
    executablePath:process.env.CHARACTER_STUDIO_CHROMIUM_BIN || undefined,
    args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const errors=[];
  try {
    const context = await browser.newContext({viewport:{width:1440,height:1400}, deviceScaleFactor:1});
    const page=await context.newPage();
    page.on('pageerror', e=>errors.push(e.message));
    await page.goto(url);await ready(page);
    assert.equal(await page.evaluate(()=>window.characterStudioReview.assets.length), 2);
    assert.ok(await page.evaluate(()=>window.characterStudioReview.assets.every(a=>a.sha256_verified && a.viewer_scale.every(x=>x===1))));
    await page.waitForTimeout(33000);
    const measured=await page.evaluate(()=>window.characterStudioReview.measurements);
    write('desktop_measurements.json', measured);
    await page.screenshot({path:path.join(out,'browser_fullpage.png'), fullPage:true});
    await page.locator('#viewport').screenshot({path:path.join(out,'browser_front.png')});
    for (const view of ['side','back','face-d03','face-d06']) {
      await page.locator(`[data-view="${view}"]`).click();
      await page.waitForTimeout(500);
      assert.equal(await page.evaluate(()=>window.characterStudioReview.view), view);
      await page.locator('#viewport').screenshot({path:path.join(out,`browser_${view}.png`)});
    }
    await page.locator('#reset-view').click();
    const canvas=page.locator('canvas'); const box=await canvas.boundingBox();
    await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();
    await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5,{steps:4});await page.mouse.up();
    assert.equal(await page.evaluate(()=>window.characterStudioReview.view), 'custom');
    await page.locator('#reset-view').click();
    await page.setViewportSize({width:390,height:844});await page.waitForTimeout(600);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth <= window.innerWidth+1));
    await page.screenshot({path:path.join(out,'browser_mobile_layout.png'),fullPage:true});
    write('mobile_layout_only.json',await page.evaluate(()=>window.characterStudioReview.measurements));
    // Release the successful software WebGL scene before testing a fresh failure
    // and retry path. Parallel software renderers distort measurements and can
    // exhaust the headless process; this is not evidence about Android hardware.
    await page.close();
    const negative=await context.newPage();
    let corrupt=true;
    await negative.route('**/models/registry.json',async route=>{
      const response=await route.fetch(); const data=await response.json();
      if(corrupt)data.assets[0].sha256='0'.repeat(64);
      await route.fulfill({response, json:data});
    });
    await negative.goto(url);
    await negative.waitForFunction(()=>window.characterStudioReview?.status==='error', null, {timeout:90000});
    assert.equal(await negative.locator('#canvas-host').isVisible(),false);
    assert.ok((await negative.locator('#load-message').textContent()).includes('SHA-256'));
    await negative.locator('#viewport').screenshot({path:path.join(out,'browser_hash_failure.png')});
    corrupt=false;await negative.locator('#retry').click();await ready(negative);
    await negative.close();
    assert.deepEqual(errors,[]);
    write('browser_review.json',{schema_version:1,status:'ACTUAL_WEBGL_REVIEW_COMPLETED',renderer_requested:'SwiftShader software WebGL',
      browser:browser.version(),real_glb_loaded:true,sha256_verified:true,both_original_scales_preserved:true,
      positive_view_controls:true,drag_rotation:true,hash_failure_blocks_display:true,retry_same_assets:true,
      mobile_layout_width:390,mobile_layout_overflow:false,page_errors:errors,
      offline_render:false,full_game_test:false,android_device_test:false,art_approved:false,
      note:'Software WebGL executes the real Three.js shaders and GLBs. Frame intervals are not a mobile capability verdict. Screenshots require visual review.'});
    console.log('ACTUAL_WEBGL_REVIEW_COMPLETED',JSON.stringify({renderer:measured.runtime.renderer,samples:measured.sampling.total_samples,frames:measured.sampling.frame_interval_ms}));
    await context.close();
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
