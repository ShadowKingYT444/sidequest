import {test,expect} from './timing';

test('static office shadows stay cached while opening the lazy editor and returning',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  const canvas=page.locator('.office-canvas canvas');
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  const shadows=Number(await canvas.getAttribute('data-shadow-passes'));
  expect(shadows).toBeGreaterThan(0);
  await page.getByRole('button',{name:'Expand',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
});


test('local draft edits preserve demand rendering of the unchanged office',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');
  const prompt=page.getByRole('textbox',{name:'Message this session'});
  await expect(prompt).toBeVisible();
  const settle=()=>page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
  await settle();
  const canvas=page.locator('.office-canvas canvas');
  const before=await canvas.getAttribute('data-render-frame-count');
  expect(Number(before)).toBeGreaterThan(0);
  await prompt.fill('Local draft only; no scene object or camera changed.');
  await expect(prompt).toHaveValue('Local draft only; no scene object or camera changed.');
  await settle();
  expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
  await page.keyboard.press('Escape');
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');
  await expect(prompt).toHaveValue('Local draft only; no scene object or camera changed.');
});


test('local figure details preserve the unchanged office frame',async({page})=>{
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  const settle=()=>page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
  await settle();
  const canvas=page.locator('.office-canvas canvas');
  const before=await canvas.getAttribute('data-render-frame-count');
  await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  await expect(page.getByRole('dialog',{name:'Agent session'})).toBeVisible();
  await expect(canvas).toHaveAttribute('data-office-controls-enabled','false');
  await settle();
  expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog',{name:'Agent session'})).toHaveCount(0);
  await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeFocused();
  await expect(canvas).toHaveAttribute('data-office-controls-enabled','true');
  await settle();
  expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
});
