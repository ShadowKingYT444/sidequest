# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: rendering.spec.ts >> static office shadows stay cached while opening the lazy editor and returning
- Location: tests/browser/rendering.spec.ts:3:1

# Error details

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator:  locator('.office-canvas canvas')
Expected: "10"
Received: "12"
Timeout:  15000ms

Call log:
  - Expect "toHaveAttribute" locator('.office-canvas canvas') with timeout 15000ms
  - waiting for locator('.office-canvas canvas')
    34 × locator resolved to <canvas width="1440" height="820" data-agent-badges="[]" data-shadow-passes="12" data-engine="three.js r186" data-render-frame-count="12" data-camera-target="[1,-0.3,-3.8]" data-camera-position="[11.5,8.5,12]"></canvas>
       - unexpected value "12"

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - main [ref=e3]:
    - generic [ref=e4]:
      - generic [ref=e5]: sidequest
      - generic [ref=e6]: sidequest-eval-source
      - button "Notifications" [ref=e8] [cursor=pointer]
      - button "Settings" [ref=e12] [cursor=pointer]
      - button "Jobs" [ref=e13] [cursor=pointer]
      - button "Refresh Git" [ref=e14] [cursor=pointer]
    - generic [ref=e19]:
      - combobox "Office navigation" [active] [ref=e20]:
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
      - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e21]: 26 staged · 1 recorded sessions
      - generic "UI refresh and file viewing make zero model calls." [ref=e22]: Local Git · read-only
  - generic [ref=e23]:
    - alert
    - alert
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
> 16 |   await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
     |                        ^ Error: expect(locator).toHaveAttribute(expected) failed
  17 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('parent_019');
  18 |   await expect(page.getByTestId('diff-editor')).toHaveCount(1);
  19 |   await expect(canvas).toHaveAttribute('data-shadow-passes',String(shadows));
  20 | });
  21 | 
```