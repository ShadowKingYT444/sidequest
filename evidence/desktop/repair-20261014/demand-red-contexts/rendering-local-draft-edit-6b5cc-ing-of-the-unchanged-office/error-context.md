# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: rendering.spec.ts >> local draft edits preserve demand rendering of the unchanged office
- Location: tests/browser/rendering.spec.ts:23:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "10"
Received: "11"
```

# Page snapshot

```yaml
- main [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: sidequest
    - generic [ref=e6]: sidequest-eval-source
    - button "Notifications" [ref=e8] [cursor=pointer]
    - button "Settings" [ref=e12] [cursor=pointer]
    - button "Jobs" [ref=e13] [cursor=pointer]
    - button "Refresh Git" [ref=e14] [cursor=pointer]
  - generic "Computer session viewer" [ref=e20]:
    - generic [ref=e21]:
      - generic [ref=e22]: Computer 19
      - navigation "Computer view" [ref=e23]:
        - button "Trace" [pressed] [ref=e24] [cursor=pointer]
        - button "Files" [ref=e25] [cursor=pointer]
        - button "Task setup" [ref=e26] [cursor=pointer]
      - generic [ref=e27]:
        - button "Expand" [ref=e28] [cursor=pointer]
        - button "Return to office" [ref=e29] [cursor=pointer]: Office Esc
    - region "Session execution trace" [ref=e31]:
      - generic [ref=e32]:
        - generic [ref=e33]:
          - text: Local Git inspection ·
          - strong [ref=e34]: Checking
        - button "Refresh trace" [ref=e35] [cursor=pointer]: ↻
      - generic "Recorded output" [ref=e36]:
        - heading "Browser inspection 2026-10-14T18:11:35.434Z" [level=3] [ref=e37]
        - group [ref=e38]:
          - generic "Run details" [ref=e39] [cursor=pointer]
        - list [ref=e40]:
          - listitem [ref=e41]:
            - generic [aria-hidden] [ref=e42]: ·
            - generic [ref=e43]: Task dispatch reserved.
          - listitem [ref=e44]:
            - generic [aria-hidden] [ref=e45]: ·
            - generic [ref=e46]: Starting local Git inspection.
          - listitem [ref=e47]:
            - generic [aria-hidden] [ref=e48]: ·
            - generic [ref=e49]: Repository inspection completed.
          - listitem [ref=e50]:
            - generic [aria-hidden] [ref=e51]: ·
            - generic [ref=e52]: Independent repository clone prepared.
          - listitem [ref=e53]:
            - generic [aria-hidden] [ref=e54]: ·
            - generic [ref=e55]: Validating candidate scope and Git tree.
          - listitem [ref=e56]:
            - generic [aria-hidden] [ref=e57]: ·
            - generic [ref=e58]: Immutable candidate artifacts frozen.
          - listitem [ref=e59]:
            - generic [aria-hidden] [ref=e60]: ·
            - generic [ref=e61]: Attempt result recorded.
          - listitem [ref=e62]:
            - generic [aria-hidden] [ref=e63]: ·
            - generic [ref=e64]: Candidate recorded.
          - listitem [ref=e65]:
            - generic [aria-hidden] [ref=e66]: ✓
            - generic [ref=e67]: Frozen identity check passed.
      - form "Local prompt composer" [ref=e68]:
        - generic [ref=e69]:
          - button "Attach files" [ref=e70] [cursor=pointer]
          - generic [ref=e73]: Message this session
          - textbox "Message this session" [active] [ref=e74]:
            - /placeholder: Write a local draft…
            - text: Local draft only; no scene object or camera changed.
          - button "Send message" [disabled] [ref=e75]
        - button "Select local files" [ref=e78]
        - generic [ref=e79]:
          - group [ref=e80]:
            - generic "Local draft · sending unavailable ⌄" [ref=e81] [cursor=pointer]
          - generic [ref=e82]: 52/2,000
  - generic [ref=e83]:
    - combobox "Office navigation" [ref=e84]:
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
    - generic "Original staged poses; recorded runtime ownership is separate from provider connectivity." [ref=e85]: 26 staged · 1 recorded sessions
    - generic "UI refresh and file viewing make zero model calls." [ref=e86]: Local Git · read-only
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
> 38 |   expect(await canvas.getAttribute('data-render-frame-count')).toBe(before);
     |                                                                ^ Error: expect(received).toBe(expected) // Object.is equality
  39 |   await page.keyboard.press('Escape');
  40 |   await page.getByRole('combobox',{name:'Office navigation'}).selectOption('monitor:parent_019');
  41 |   await expect(prompt).toHaveValue('Local draft only; no scene object or camera changed.');
  42 | });
  43 | 
```