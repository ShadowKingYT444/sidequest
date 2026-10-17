# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: office-failure.spec.ts >> WebGL failure stays distinct from assets and leaves local tools accessible
- Location: tests/browser/office-failure.spec.ts:9:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: '3D graphics unavailable' })
Expected: visible
Timeout: 15000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('heading', { name: '3D graphics unavailable' }) with timeout 15000ms
  - waiting for getByRole('heading', { name: '3D graphics unavailable' })

```

```yaml
- main:
  - text: sidequest sidequest
  - button "Notifications"
  - button "Settings"
  - button "Jobs"
  - button "Refresh Git"
  - region "Office asset pending":
    - paragraph: Original office assets pending
    - heading "Your office is waiting." [level=1]
    - paragraph: The supplied office is required for desk navigation. Your local Git changes and job results are available below.
    - button "Inspect local Git diff ↗"
    - text: Original office assets have not been imported.
  - combobox "Office navigation":
    - option "Navigate…" [selected]
    - option "Tasks board"
  - text: Loading figures… Local Git · read-only
```

# Test source

```ts
  1  | import {test,expect} from '@playwright/test';
  2  | import {writeFile} from 'node:fs/promises';
  3  | import path from 'node:path';
  4  | import {evidenceDirectory} from './evidence';
  5  | 
  6  | // Failure injection only. No SwiftShader opt-in, GPU blocklist override or provider calls.
  7  | test.use({launchOptions:{executablePath:process.env.CHROMIUM_PATH??'/usr/bin/chromium',args:[]}});
  8  | 
  9  | test('WebGL failure stays distinct from assets and leaves local tools accessible',async({page})=>{
  10 |   const evidence=evidenceDirectory();
  11 |   await page.addInitScript(()=>{
  12 |     const original=HTMLCanvasElement.prototype.getContext;
  13 |     (window as any).failedGraphicsAttempts=0;
  14 |     HTMLCanvasElement.prototype.getContext=function(type:string,...args:any[]){
  15 |       if(type==='webgl2'||type==='webgl'){
  16 |         (window as any).failedGraphicsAttempts++;
  17 |         throw new Error('WebGL2 blocklisted');
  18 |       }
  19 |       return (original as any).call(this,type,...args);
  20 |     } as typeof original;
  21 |   });
  22 |   const mutations:string[]=[];
  23 |   page.on('request',request=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding|sendSessionMessage)$/.test(request.url()))mutations.push(request.url());});
  24 |   await page.goto('/');
> 25 |   await expect(page.getByRole('heading',{name:'3D graphics unavailable'})).toBeVisible();
     |                                                                            ^ Error: expect(locator).toBeVisible() failed
  26 |   await expect(page.getByText('Original office assets have not been imported.')).toHaveCount(0);
  27 |   await expect(page.locator('.app-footer')).toContainText('Office unavailable');
  28 |   await page.getByText('Recovery help',{exact:true}).click();
  29 |   await expect(page.locator('.office-recovery')).toContainText('run --browser');
  30 |   const before=await page.evaluate(()=>(window as any).failedGraphicsAttempts);
  31 |   await page.getByRole('button',{name:'Retry office',exact:true}).click();
  32 |   await expect.poll(()=>page.evaluate(()=>(window as any).failedGraphicsAttempts)).toBeGreaterThan(before);
  33 |   await expect(page.getByRole('heading',{name:'3D graphics unavailable'})).toBeVisible();
  34 |   await page.screenshot({path:path.join(evidence,'graphics-unavailable.png')});
  35 |   await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  36 |   await expect(page.getByRole('region',{name:'Computer work viewer'})).toBeVisible();
  37 |   await expect(page.getByRole('navigation',{name:'Changed files'}).getByRole('button').first()).toBeVisible();
  38 |   await page.getByRole('button',{name:'Settings',exact:true}).click();
  39 |   await expect(page.getByRole('dialog',{name:'Provider settings dialog'})).toBeVisible();
  40 |   await page.keyboard.press('Escape');
  41 |   await page.getByRole('button',{name:'Jobs',exact:true}).click();
  42 |   await expect(page.getByRole('dialog',{name:'Jobs'})).toBeVisible();
  43 |   expect(mutations).toEqual([]);
  44 |   await writeFile(path.join(evidence,'graphics-unavailable.json'),JSON.stringify({scope:'Browser failure injection with actual local Git reads; runtime not configured; no provider turns',webglError:'WebGL2 blocklisted',retryRecreatedContext:true,gitSettingsJobsAccessible:true,providerMutations:mutations},null,2));
  45 | });
  46 | 
  47 | test('bindings failure is retryable and does not claim WebGL or missing imported assets',async({page})=>{
  48 |   let bindingsReads=0;
  49 |   await page.route('**/office/bindings.json',async route=>{bindingsReads++;await route.fulfill({status:503,body:'temporarily unavailable'});});
  50 |   await page.goto('/');
  51 |   await expect(page.getByRole('heading',{name:'Office layout unavailable'})).toBeVisible();
  52 |   await expect(page.getByText('Original office assets have not been imported.')).toHaveCount(0);
  53 |   const before=bindingsReads;
  54 |   await page.getByRole('button',{name:'Retry office',exact:true}).click();
  55 |   await expect.poll(()=>bindingsReads).toBeGreaterThan(before);
  56 |   await expect(page.getByRole('heading',{name:'Office layout unavailable'})).toBeVisible();
  57 | });
  58 | 
```