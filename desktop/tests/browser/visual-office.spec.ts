import {test,expect} from '@playwright/test';
import path from 'node:path';
import {writeFile} from 'node:fs/promises';
import AxeBuilder from '@axe-core/playwright';
const evidence=path.resolve('../evidence/desktop');
for(const width of [1440,390]) test(`provider settings and preserved work at ${width}px`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.setViewportSize({width,height:width===390?780:1000});
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeEnabled();
  await expect(page.locator('.office-canvas canvas')).toBeVisible();


  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  await expect(page.getByRole('button',{name:'Expand',exact:true})).toBeVisible();

  await page.getByRole('button',{name:'Expand',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();

  const selected=await page.getByTestId('diff-editor').getAttribute('data-file-id');
  await page.getByRole('button',{name:'Settings',exact:true}).click();
  const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  await expect(settings).toBeVisible();await expect(settings.getByRole('heading',{name:/Codex$/})).toBeVisible();
  await expect(settings.getByLabel('Binary path')).toHaveValue(/codex/);
  await expect(settings.getByText('Authentication',{exact:true})).toBeVisible();
  await expect(settings.getByText('Service reachability',{exact:true})).toBeVisible();

  if(width===1440){
    await settings.getByRole('button',{name:/Claude/}).click();
    await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
    await settings.getByRole('button',{name:/Codex/}).click();
  }else{
    await settings.locator('.provider-mobile-picker__button').click();
    await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Claude',exact:true}).click();
    await expect(settings.getByRole('heading',{name:/Claude$/})).toBeVisible();
    await settings.locator('.provider-mobile-picker__button').click();
    await settings.getByRole('navigation',{name:'Choose provider'}).getByRole('button',{name:'Codex',exact:true}).click();
  }
  await settings.getByRole('button',{name:'Refresh provider discovery'}).click();
  await expect(settings.getByRole('button',{name:'Refresh provider discovery'})).toBeEnabled();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:path.join(evidence,`provider-settings${width===1440?'':'-390'}.png`)});
  await settings.getByRole('navigation',{name:'Settings view'}).getByRole('button',{name:'Usage',exact:true}).click();
  await expect(settings.getByText('No usage data reported',{exact:true})).toBeVisible();
  await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Tokens',exact:true}).click();
  await expect(settings.getByText('Processed tokens unavailable',{exact:true})).toBeVisible();
  await settings.getByRole('group',{name:'Usage breakdown'}).getByRole('button',{name:'Day',exact:true}).click();
  await expect(settings.getByText('No daily usage data reported',{exact:true})).toBeVisible();
  await page.screenshot({path:path.join(evidence,`provider-settings-analytics${width===1440?'':'-390'}.png`)});
  await settings.getByRole('group',{name:'Usage metric'}).getByRole('button',{name:'Limits',exact:true}).click();
  await expect(settings.getByText('— remaining',{exact:true})).toHaveCount(2);
  await expect(settings.getByText('Reset unknown',{exact:true})).toHaveCount(2);
  await page.screenshot({path:path.join(evidence,`provider-settings-limits${width===1440?'':'-390'}.png`)});
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

for(const width of [1440,390]) test(`compact provider picker and guarded monitor task setup at ${width}px`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));await page.setViewportSize({width,height:width===390?780:1000});await page.emulateMedia({reducedMotion:'reduce'});await page.goto('/');await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  const settings=page.getByRole('dialog',{name:'Provider settings dialog'});
  const mutations:string[]=[];page.on('request',request=>{if(/__sidequest\/runtime\/(submitCoding|runCoding|enableCoding)$/.test(request.url()))mutations.push(request.url());});
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('work:parent_019');
  const picker=page.getByRole('dialog',{name:'Choose provider'});await expect(picker).toBeVisible();await expect(picker).toContainText('No connected providers');
  await expect(picker.getByRole('button',{name:'Connect provider'})).toBeEnabled();await expect(picker.locator('input,select,textarea,form')).toHaveCount(0);await expect(picker.getByRole('button',{name:'Submit task'})).toHaveCount(0);await expect(picker.locator('.provider-tile')).toHaveCount(0);
  const pickerBox=(await picker.boundingBox())!;expect(pickerBox.width).toBeLessThanOrEqual(280);expect(pickerBox.height).toBeLessThan(200);
  await page.screenshot({path:path.join(evidence,`provider-selector${width===1440?'':'-390'}.png`)});
  await picker.getByRole('button',{name:'Connect provider'}).click();await expect(settings).toBeVisible();await page.keyboard.press('Escape');
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');await page.getByRole('button',{name:'Task setup',exact:true}).click();const launcher=page.getByRole('region',{name:'Task setup',exact:true});await expect(launcher).toBeVisible();
  await expect(launcher.getByLabel('Prompt',{exact:true})).toHaveValue('');await launcher.getByLabel('Prompt',{exact:true}).fill('Test-only draft prompt. No coding task will be submitted.');
  await launcher.getByText('Scope and spending',{exact:false}).click();await expect(launcher.getByLabel('Allowed folder',{exact:true})).toHaveValue('');await expect(launcher.getByLabel('USD limit',{exact:true})).toHaveValue('');
  await launcher.getByLabel('Allowed folder',{exact:true}).fill('desktop/src');await launcher.getByLabel('USD limit',{exact:true}).fill('0.01');await expect(launcher.getByRole('button',{name:'Submit task',exact:true})).toBeDisabled();
  await launcher.getByRole('button',{name:'Refresh setup',exact:true}).click();await expect(launcher.getByRole('button',{name:'Submit task',exact:true})).toBeDisabled();
  const launcherAxe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();expect(launcherAxe.violations.map(v=>({id:v.id,impact:v.impact}))).toEqual([]);
  await page.screenshot({path:path.join(evidence,`monitor-task-setup${width===1440?'':'-390'}.png`)});await page.keyboard.press('Escape');await expect(launcher).toHaveCount(0);
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  const session=page.getByRole('dialog',{name:'Agent session'});await expect(session).toContainText('No live session attached');
  await page.screenshot({path:path.join(evidence,`agent-session${width===1440?'':'-390'}.png`)});
  await page.keyboard.press('Escape');await expect(session).toHaveCount(0);
  expect(mutations).toEqual([]);
  expect(errors).toEqual([]);
});
