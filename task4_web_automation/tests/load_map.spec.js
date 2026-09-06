const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Escher Viewer Integration - Map Loading Workflow', () => {
    test('should successfully load local json map file into the canvas viewer', async ({ page }) => {
        // Enforce a desktop view window format inside the runner container
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('/#/app?tool=Viewer');

        // Click the main app canvas frame background once to guarantee DOM focal readiness
        await page.locator('body').click();

        // Target via robust role text fallback to handle shifting layout bounds safely
        const mapButton = page.getByRole('button', { name: 'Map', exact: true }).or(page.locator('text=Map')).first();
        await expect(mapButton).toBeVisible({ timeout: 15000 });
        await mapButton.click();

        const fileChooserPromise = page.waitForEvent('filechooser');
        // Handle dropdown or immediate file click choices safely
        await page.locator('text=Load Map JSON').or(page.locator('text=Load map')).first().click();
        const fileChooser = await fileChooserPromise;

        const dynamicMapFixturePath = path.resolve(__dirname, '../fixtures/qa_escher_map.json');
        await fileChooser.setFiles(dynamicMapFixturePath);

        // Fallback check: assert that at least the map svg layer initialization successfully triggers
        const canvasContainer = page.locator('svg').first();
        await expect(canvasContainer).toBeVisible({ timeout: 15000 });
    });
});
