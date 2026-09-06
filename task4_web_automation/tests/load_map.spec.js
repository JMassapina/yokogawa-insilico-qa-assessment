const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Escher Viewer Integration - Map Loading Workflow', () => {
    test('should successfully load local json map file into the canvas viewer', async ({ page }) => {
        await page.goto('/#/app?tool=Viewer');

        const mapMenu = page.locator('div.menu-button', { hasText: 'Map' });
        await expect(mapMenu).toBeVisible({ timeout: 5000 });
        await mapMenu.click();

        const fileChooserPromise = page.waitForEvent('filechooser');
        await page.locator('text=Load Map JSON').click();
        const fileChooser = await fileChooserPromise;

        // Path safe resolution backtracks out of /tests and drops into /fixtures
        const dynamicMapFixturePath = path.resolve(__dirname, '../fixtures/qa_escher_map.json');
        await fileChooser.setFiles(dynamicMapFixturePath);

        const primaryMetaboliteNode = page.locator('g.node', { hasText: 'D-Glucose-6-phosphate' });
        await expect(primaryMetaboliteNode).toBeVisible({ timeout: 10000 });
    });
});
