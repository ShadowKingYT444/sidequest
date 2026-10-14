import { test, expect } from '@playwright/test';
import path from 'node:path';
import { writeFile } from 'node:fs/promises';
import AxeBuilder from '@axe-core/playwright';
const evidence = path.resolve('../evidence/desktop');
test('real Git diff, lazy single editor, expanded state, Escape and keyboard', async ({ page, request }) => {
  const errors: string[] = []; page.on('pageerror', error => errors.push(error.message));
  const snapshotResponse = await request.get('/__sidequest/snapshot');
  expect(snapshotResponse.ok()).toBeTruthy();
  const snapshot = await snapshotResponse.json();
  expect(snapshot.mode).toBe('local-git');
  expect(snapshot.agent.state).toBe('unavailable');
  const source = snapshot.files.find((file: {path:string}) => file.path === 'dev/luna.py') ?? snapshot.files.find((file: { additions?:number; path:string }) => (file.additions ?? 0) > 120 && /\.(tsx?|py|md)$/.test(file.path)) ?? snapshot.files[0];
  const diff = await (await request.get(`/__sidequest/diff/${source.id}`)).json();
  expect(diff.readOnly).toBe(true); expect(diff.modified.length).toBeGreaterThan(100);
  await page.goto('/');
  await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  await expect(page.getByRole('button', {name:'Inspect local Git diff'})).toBeEnabled();
  await page.screenshot({path:path.join(evidence,'setup-desktop.png')});
  await page.getByRole('button', {name:'Inspect local Git diff'}).click();
  await page.getByRole('button', {name:new RegExp(source.path.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))}).click();
  const editor = page.getByTestId('diff-editor');
  await expect(editor).toHaveCount(1);
  await expect(editor.locator('.view-lines').last()).toBeVisible();
  await editor.locator('.monaco-editor').last().hover();
  for (let count=0;count<10;count++) { await page.mouse.wheel(0, 800); await page.waitForTimeout(80); }
  await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(300);
  const before = Number(await editor.getAttribute('data-scroll-top'));
  await page.screenshot({path:path.join(evidence,'git-diff.png')});
  await page.getByRole('button',{name:'Expand'}).click();
  await expect(page.getByRole('dialog', {name:'Computer work viewer'})).toBeVisible();
  await expect(editor).toHaveCount(1);
  await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(Math.max(100,before-250));
  await page.screenshot({path:path.join(evidence,'expanded-diff.png')});
  await page.keyboard.press('Escape');
  await expect(editor).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Inspect local Git diff'})).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(editor).toHaveAttribute('data-file-id',source.id);
  await expect.poll(async () => Number(await editor.getAttribute('data-scroll-top'))).toBeGreaterThan(100);
  expect(errors).toEqual([]);
});
test('read API rejects outside origins and mutations',async ({request})=>{
  expect((await request.get('/__sidequest/snapshot',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
  expect((await request.post('/__sidequest/snapshot')).status()).toBe(405);
  expect((await request.get('/__sidequest/diff/not-a-file')).status()).toBe(404);
});
for (const width of [960,390]) test(`viewer reflows at ${width}px with reduced motion`,async ({page})=>{
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.setViewportSize({width,height:780});await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  await page.getByRole('button',{name:'Expand'}).click();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:path.join(evidence,`viewer-${width}.png`)});
  await page.keyboard.press('Escape');await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  expect(errors).toEqual([]);
});

test('keyboard-accessible viewer has no automated WCAG A/AA violations',async({page})=>{
  await page.goto('/'); await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  await page.getByRole('button',{name:'Expand'}).click();
  await expect(page.getByTestId('diff-editor').locator('.monaco-editor').last()).toBeVisible();
  const code=page.getByRole('button',{name:/dev\/luna\.py/});
  if(await code.count()) {await code.click();await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toBeVisible();}
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
  await writeFile(path.join(evidence,'accessibility.json'),JSON.stringify(results.violations,null,2));
  expect(results.violations.map(item=>({id:item.id,impact:item.impact,description:item.description}))).toEqual([]);
});

test('hostile source stays literal and a failed read can retry',async({page})=>{
  let fail=true;
  await page.route('**/__sidequest/diff/*',async route=>{
    if(fail){await route.fulfill({status:503,json:{error:'test-only failure'}});return;}
    const response=await route.fetch();const data=await response.json();
    await route.fulfill({json:{...data,original:'',modified:'<script>window.__executed=true</script>\n<img src=x onerror="window.__executed=true">',language:'plaintext'}});
  });
  await page.goto('/');await page.getByRole('button',{name:'Inspect local Git diff'}).click();
  await expect(page.getByRole('alert')).toContainText('Local Git read failed');
  fail=false;await page.getByRole('button',{name:'Refresh repository'}).click();
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  await expect(page.getByTestId('diff-editor').locator('.view-lines').last()).toContainText('<script>');
  expect(await page.evaluate(()=>Object.hasOwn(window,'__executed'))).toBe(false);
});
