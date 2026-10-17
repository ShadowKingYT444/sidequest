# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: rendering.spec.ts >> local figure details preserve the unchanged office frame
- Location: tests/browser/rendering.spec.ts:45:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "3"
Received: "4"
```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: sidequest
    - generic [ref=e6]: sidequest-eval-source
    - button "Notifications" [disabled] [ref=e8]
    - button "Settings" [ref=e12] [cursor=pointer]
    - button "Jobs" [ref=e13] [cursor=pointer]
    - button "Refresh Git" [ref=e14] [cursor=pointer]
  - dialog "Agent session" [ref=e19]:
    - generic [ref=e20]:
      - heading "Computer 19" [level=2] [ref=e21]
      - button "Close agent session" [active] [ref=e22] [cursor=pointer]: ×
    - generic [ref=e23]:
      - paragraph [ref=e24]: Recorded local inspection
      - heading "Browser inspection 2026-10-14T18:11:35.434Z" [level=3] [ref=e25]
      - paragraph [ref=e26]: Checking
      - generic [ref=e27]:
        - button "Open monitor" [ref=e28] [cursor=pointer]
        - button "Open results" [ref=e29] [cursor=pointer]
      - group [ref=e30]:
        - generic "Session details" [ref=e31] [cursor=pointer]
      - button "Refresh session" [ref=e32] [cursor=pointer]
  - generic [ref=e33]:
    - combobox "Office navigation" [ref=e34]:
      - option "Navigate…" [selected]
      - option "Tasks board"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
      - option "Computer 01"
      - option "Computer 02"
      - option "Computer 03"
      - option "Computer 04"
      - option "Computer 05"
      - option "Computer 06"
      - option "Computer 07"
      - option "Computer 08"
      - option "Computer 09"
      - option "Computer 10"
      - option "Computer 11"
      - option "Computer 12"
      - option "Computer 13"
      - option "Computer 14"
      - option "Computer 15"
      - option "Computer 16"
      - option "Computer 17"
      - option "Computer 18"
      - option "Computer 19"
      - option "Computer 20"
      - option "Computer 21"
      - option "Computer 22"
      - option "Computer 23"
      - option "Computer 24"
    - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e35]: 26 staged · 1 recorded sessions
    - generic "UI refresh and file viewing make zero model calls." [ref=e36]: Local Git · read-only
```

# Test source

```ts
  1  | import {test,expect} from './timing';
  2  | 
  3  | test('static office shadows stay cached while opening the lazy editor and returning',async({page})=>{
  4  |   await page.emulateMedia({reducedMotion:'reduce'});
  5  |   await page.goto('/');
  6  |   await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  7  |   const canvas=page.locator('.office-canvas canvas');
  8  |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  9  |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  10 |   const shadows=Number(await canvas.getAttribute('data-shadow-passes'));
  11 |   expect(shadows).toBeGreaterThan(0);
  12 |   await page.getByRole('button',{name:'Expand',exact:true}).click();
  13 |   await expect(page.getByRole('dialog',{name:'Computer work viewer'})).toBeVisible();
  14 |   await page.keyboard.press('Escape');
  15 |   await expect(page.getByTestId('diff-editor')).toHaveCount(0);
  16 |   await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
  17 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  18 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  19 |   await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
  20 | });
  21 | 
  22 | 
  23 | test('local draft edits preserve demand rendering of the unchanged office',async({page})=>{
  24 |   await page.emulateMedia({reducedMotion:'reduce'});
  25 |   await page.goto('/');
  26 |   await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  27 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');
  28 |   const prompt=page.getByRole('textbox',{name:'Message this session'});
  29 |   await expect(prompt).toBeVisible();
  30 |   const settle=()=>page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
  31 |   await settle();
  32 |   const canvas=page.locator('.office-canvas canvas');
  33 |   const before=await canvas.getAttribute('data-render-frame-count');
  34 |   expect(Number(before)).toBeGreaterThan(0);
  35 |   await prompt.fill('Local draft only; no scene object or camera changed.');
  36 |   await expect(prompt).toHaveValue('Local draft only; no scene object or camera changed.');
  37 |   await settle();
  38 |   expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
  39 |   await page.keyboard.press('Escape');
  40 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');
  41 |   await expect(prompt).toHaveValue('Local draft only; no scene object or camera changed.');
  42 | });
  43 | 
  44 | 
  45 | test('local figure details preserve the unchanged office frame',async({page})=>{
  46 |   await page.emulateMedia({reducedMotion:'reduce'});
  47 |   await page.goto('/');
  48 |   await expect(page.locator('.app-footer')).toHaveAttribute('data-actor-status','ready',{timeout:60000});
  49 |   const settle=()=>page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
  50 |   await settle();
  51 |   const canvas=page.locator('.office-canvas canvas');
  52 |   const before=await canvas.getAttribute('data-render-frame-count');
  53 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('actor:parent_019');
  54 |   await expect(page.getByRole('dialog',{name:'Agent session'})).toBeVisible();
  55 |   await settle();
> 56 |   expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
     |                                                                ^ Error: expect(received).toBe(expected) // Object.is equality
  57 |   await page.keyboard.press('Escape');
  58 |   await expect(page.getByRole('dialog',{name:'Agent session'})).toHaveCount(0);
  59 |   await expect(page.getByRole('combobox',{name:'Office navigation'})).toBeFocused();
  60 |   await settle();
  61 |   expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
  62 | });
  63 | 
```