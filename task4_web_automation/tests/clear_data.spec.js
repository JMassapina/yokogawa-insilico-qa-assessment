const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Escher Viewer Integration - Data Cleansing Workflow', () => {
    test('should load reaction pathway datasets and clear them cleanly from map edges', async ({ page }) => {
        await page.goto('/#/app?tool=Viewer');

        const dataMenu = page.locator('div.menu-button', { hasText: 'Data' });
        await expect(dataMenu).toBeVisible({ timeout: 5000 });
        await dataMenu.click();

        const fileChooserPromise = page.waitForEvent('filechooser');
        await page.locator('text=Load reaction data JSON').click();
        const fileChooser = await fileChooserPromise;

        const dynamicDataFixturePath = path.resolve(__dirname, '../fixtures/qa_escher_data.json');
        await fileChooser.setFiles(dynamicDataFixturePath);

        const liveConnectionEdge = page.locator('path.connection').first();
        await expect(liveConnectionEdge).toHaveAttribute('style', /stroke-width/, { timeout: 5000 });

        await dataMenu.click();
        await page.locator('text=Clear reaction data').click();

        await expect(liveConnectionEdge).not.toHaveAttribute('style', /stroke-width/);
    });
});
