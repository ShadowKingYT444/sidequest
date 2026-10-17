import {test,expect} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
import path from 'node:path';
import {evidenceDirectory} from './evidence';

// Failure injection only. No SwiftShader opt-in, GPU blocklist override or provider calls.
test.use({launchOptions:{executablePath:process.env.CHROMIUM_PATH??'/usr/bin/chromium',args:[],ignoreDefaultArgs:['--enable-unsafe-swiftshader'],chromiumSandbox:true}});

test('WebGL failure stays distinct from assets and leaves local tools accessible',async({page})=>{
  const evidence=evidenceDirectory();
  await page.addInitScript(()=>{
    const original=HTMLCanvasElement.prototype.getContext;
    (window as any).failedGraphicsAttempts=0;
    HTMLCanvasElement.prototype.getContext=function(type:string,...args:any[]){
      if(type==='webgl2'||type==='webgl'){
        (window as any).failedGraphicsAttempts++;
        throw new Error('WebGL2 blocklisted');
      }
      return (original as any).call(this,type,...args);
    } as typeof original;
  });
  const mutations:string[]=[];
  page.on('request',request=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|sendSessionMessage)$/.test(request.url()))mutations.push(request.url());});
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'3D graphics unavailable'})).toBeVisible();
  await expect(page.getByText('Original office assets have not been imported.')).toHaveCount(0);
  await expect(page.locator('.app-footer')).toContainText('Office unavailable');
  await page.getByText('Recovery help',{exact:true}).click();
  await expect(page.locator('.office-recovery')).toContainText('run --browser');
  const before=await page.evaluate(()=>(window as any).failedGraphicsAttempts);
  await page.getByRole('button',{name:'Retry office',exact:true}).click();
  await expect.poll(()=>page.evaluate(()=>(window as any).failedGraphicsAttempts)).toBeGreaterThan(before);
  await expect(page.getByRole('heading',{name:'3D graphics unavailable'})).toBeVisible();
  await page.screenshot({path:path.join(evidence,'graphics-unavailable.png')});
  await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  await expect(page.getByRole('region',{name:'Computer work viewer'})).toBeVisible();
  await expect(page.getByRole('navigation',{name:'Changed files'}).getByRole('button').first()).toBeVisible();
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Provider settings dialog'})).toBeVisible();
  await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Jobs',exact:true}).click();
  await expect(page.getByRole('region',{name:'Local jobs board'})).toBeVisible();
  expect(mutations).toEqual([]);
  await writeFile(path.join(evidence,'graphics-unavailable.json'),JSON.stringify({scope:'Browser failure injection with actual local Git reads; runtime not configured; no provider turns',webglError:'WebGL2 blocklisted',retryRecreatedContext:true,gitSettingsJobsAccessible:true,providerMutations:mutations},null,2));
});

test('bindings failure is retryable and does not claim WebGL or missing imported assets',async({page})=>{
  let bindingsReads=0;
  await page.route('**/office/bindings.json',async route=>{bindingsReads++;await route.fulfill({status:503,body:'temporarily unavailable'});});
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Office layout unavailable'})).toBeVisible();
  await expect(page.getByText('Original office assets have not been imported.')).toHaveCount(0);
  const before=bindingsReads;
  await page.getByRole('button',{name:'Retry office',exact:true}).click();
  await expect.poll(()=>bindingsReads).toBeGreaterThan(before);
  await expect(page.getByRole('heading',{name:'Office layout unavailable'})).toBeVisible();
});
