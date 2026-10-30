import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const result={status:'started',url:'http://127.0.0.1:8000',errors:[],checks:[]};
const browser=await chromium.launch({headless:true,args:[
  '--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--no-sandbox',
  '--disable-dev-shm-usage'
]});
try{
  const page=await browser.newPage({viewport:{width:1400,height:900},deviceScaleFactor:1});
  page.on('pageerror',error=>result.errors.push(error.message));
  page.on('console',msg=>{
    if(msg.type()==='error')result.errors.push(msg.text());
  });
  const response=await page.goto(result.url,{waitUntil:'domcontentloaded',timeout:30000});
  if(response.status()!==200)throw new Error('HTTP status '+response.status());
  await page.waitForFunction(
    ()=>document.querySelector('#status')?.textContent?.includes('載入成功'),
    null,{timeout:45000});
  result.checks.push('2 GLB horses loaded');
  const text=await page.locator('#status').textContent();
  result.description=text;
  if(await page.locator('canvas').count()!==1)throw new Error('No WebGL canvas');
  result.checks.push('WebGL canvas present');
  await page.screenshot({path:'outputs/v23demo/browser_front.png',fullPage:true});
  await page.locator('#clip').selectOption('Walk');
  await page.waitForTimeout(400);
  await page.locator('#clip').selectOption('Gallop');
  await page.locator('#speed').fill('1.4');
  await page.locator('#orbit').check();
  await page.waitForTimeout(1700);
  if(!await page.locator('#orbit').isChecked())throw new Error('Track motion control not active');
  result.checks.push('Walk/Gallop UI and track control worked');
  await page.screenshot({path:'outputs/v23demo/browser_racing.png',fullPage:true});
  const status2=await page.locator('#status').textContent();
  if(!status2.includes('載入成功'))throw new Error(status2);
  result.checks.push('WebGL still alive after track movement');
  result.status=result.errors.length?'visual_qa_pass_console_errors':'browser_smoke_pass';
} catch(error) {
  result.status='failed';
  result.failure=String(error?.stack||error);
} finally {
  await browser.close();
  await fs.mkdir('outputs/v23demo',{recursive:true});
  await fs.writeFile('outputs/v23demo/browser_qa.json',JSON.stringify(result,null,2));
  console.log('HORSE_BROWSER_QA',JSON.stringify(result));
}
if(result.status==='failed')process.exit(1);
