/*
 * The test submitted for review, preserved verbatim and excluded from execution by
 * `testIgnore` in playwright.config.ts.
 *
 * It is kept in the repository on purpose. A review that only produces a rewrite asks the
 * reader to take the reviewer's word for what was wrong; keeping the original lets anyone
 * diff the two and judge for themselves. The written review is in
 * docs/04-playwright-code-review.md and the replacement is ../load-map.spec.ts.
 */

const { test } = require('@playwright/test');

test('load map', async ({ page }) => {
  await page.goto('https://github.io');
  await page.waitForTimeout(5000);
  await page.click('div.menu-button:nth-child(2)');
  await page.click('text=Load Map');
  const fileInput = await page.$('input[type="file"]');
  await fileInput.setInputFiles('qa_escher_map.json');
  await page.waitForTimeout(3000);
  console.log('Map loaded');
});
