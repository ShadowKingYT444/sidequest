import {test,expect} from '@playwright/test';
import path from 'node:path';
import {writeFile} from 'node:fs/promises';
import AxeBuilder from '@axe-core/playwright';
const evidence=path.resolve('../evidence/desktop');
for(const width of [1440,390]) test(`provider settings and preserved work at ${width}px`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.setViewportSize({width,height:width===390?780:1000});
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');await expect(page.getByRole('button',{name:'Inspect local Git diff'})).toBeEnabled();
  await expect(page.getByRole('region',{name:'Office asset pending'})).toBeVisible();

  await page.waitForTimeout(1000);
  if(width===1440)await page.screenshot({path:path.join(evidence,'original-office-pending.png')});
  await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  await expect(page.getByRole('button',{name:'Expand',exact:true})).toBeVisible();

  await page.getByRole('button',{name:'Expand',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();

  const selected=await page.getByTestId('diff-editor').getAttribute('data-file-id');
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  await expect(settings).toBeVisible();await expect(settings.getByRole('heading',{name:'Codex',exact:true})).toBeVisible();
  await expect(settings.getByLabel('Binary path')).toHaveValue(/codex/);
  await expect(settings.getByText('Account status',{exact:true})).toBeVisible();

  if(width===1440){
    await settings.getByRole('button',{name:/Claude/}).click();
    await expect(settings.getByRole('heading',{name:'Claude',exact:true})).toBeVisible();
    await settings.getByRole('button',{name:/Codex/}).click();
  }else{
    await settings.locator('.provider-mobile-picker__button').click();
    await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Claude',exact:true}).click();
    await expect(settings.getByRole('heading',{name:'Claude',exact:true})).toBeVisible();
    await settings.locator('.provider-mobile-picker__button').click();
    await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Codex',exact:true}).click();
  }
  await settings.getByRole('button',{name:'Refresh provider discovery'}).click();
  await expect(settings.getByRole('button',{name:'Refresh provider discovery'})).toBeEnabled();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:path.join(evidence,`provider-settings${width===1440?'':'-390'}.png`)});
  if(width===1440){await settings.locator('.provider-scroll').evaluate(node=>{node.scrollTop=node.scrollHeight;});await page.screenshot({path:path.join(evidence,'provider-settings-analytics.png')});await settings.locator('.provider-scroll').evaluate(node=>{node.scrollTop=0;});}
  const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  await writeFile(path.join(evidence,`provider-accessibility-${width}.json`),JSON.stringify(result.violations,null,2));
  expect(result.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  const first=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').first(),last=settings.locator('button:visible:not(:disabled),input:visible,select:visible,[tabindex="0"]:visible').last();
  await last.focus();await page.keyboard.press('Tab');await expect(first).toBeFocused();
  await page.keyboard.press('Escape');await expect(settings).toHaveCount(0);
  await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  await expect(page.getByTestId('diff-editor')).toHaveAttribute('data-file-id',selected!);
  await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  expect(errors).toEqual([]);
});
