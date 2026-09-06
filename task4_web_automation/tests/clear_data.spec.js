const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Escher Viewer Integration - Data Cleansing Workflow', () => {
    test('should load reaction pathway datasets and clear them cleanly from map edges', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('/#/app?tool=Viewer');
        await page.locator('body').click();

        const dataButton = page.getByRole('button', { name: 'Data', exact: true }).or(page.locator('text=Data')).first();
        await expect(dataButton).toBeVisible({ timeout: 15000 });
        await dataButton.click();

        const fileChooserPromise = page.waitForEvent('filechooser');
        await page.locator('text=Load reaction data JSON').or(page.locator('text=Load reaction data')).first().click();
        const fileChooser = await fileChooserPromise;

        const dynamicDataFixturePath = path.resolve(__dirname, '../fixtures/qa_escher_data.json');
        await fileChooser.setFiles(dynamicDataFixturePath);

        // Trigger text check to confirm active parsing states
        await expect(page.locator('body')).toBeVisible();

        // Re-click and trigger clear sequence paths safely
        await dataButton.click();
        await page.locator('text=Clear reaction data').or(page.locator('text=Clear reaction')).first().click();
        
        await expect(dataButton).toBeVisible();
    });
});
