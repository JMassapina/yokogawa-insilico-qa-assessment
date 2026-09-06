import { expect, test } from '@playwright/test';
import { EXPECTED_MAP, EscherViewerPage } from '../pages/EscherViewerPage';

const LOADED_LABELS = ['PGI 10.0', 'PFK 10.0', 'GLCpts 10.0'];

test.describe('Escher viewer — clearing reaction data', () => {
  test('reaction data can be loaded and then cleared', async ({ page }) => {
    test.fail(
      true,
      'ESC-01: "Clear reaction data" remains disabled after reaction data is loaded',
    );

    const viewer = new EscherViewerPage(page);
    await viewer.goto();
    await viewer.loadMap('qa_escher_map.json');
    await viewer.loadReactionData('qa_escher_data.json');

    await expect(viewer.reactionLabels).toHaveText(LOADED_LABELS);

    await viewer.openMenu('Data');
    await viewer.menuItem('Data', 'Clear reaction data').click();

    await expect(viewer.reactionLabels).toHaveText([...EXPECTED_MAP.reactionLabels]);
  });

  test('the clear control is offered once there is data to clear', async ({ page }) => {
    test.fail(true, 'ESC-01: the control never leaves its disabled state');

    const viewer = new EscherViewerPage(page);
    await viewer.goto();
    await viewer.loadMap('qa_escher_map.json');

    expect(await viewer.isMenuItemEnabled('Data', 'Clear reaction data')).toBe(false);

    await viewer.loadReactionData('qa_escher_data.json');

    expect(await viewer.isMenuItemEnabled('Data', 'Clear reaction data')).toBe(true);
  });

  test('loading data renders flux values on the reaction labels', async ({ page }) => {
    const viewer = new EscherViewerPage(page);
    await viewer.goto();
    await viewer.loadMap('qa_escher_map.json');

    expect(await viewer.hasReactionDataOverlay()).toBe(false);

    await viewer.loadReactionData('qa_escher_data.json');

    await expect(viewer.reactionLabels).toHaveText(LOADED_LABELS);
    await expect(viewer.statusLine).toContainText('reaction data');

    expect(await viewer.firstSegmentStrokeWidth()).not.toBe('');
  });

  test.describe('invalid and edge-case data', () => {
    test('marks reactions with no matching value as "(nd)" rather than blank', async ({ page }) => {
      const viewer = new EscherViewerPage(page);
      await viewer.goto();
      await viewer.loadMap('qa_escher_map.json');

      await viewer.loadReactionData('absent-reaction-keys.json');

      await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
      await expect(viewer.reactionLabels).toHaveText(
        EXPECTED_MAP.reactionLabels.map((label) => `${label} (nd)`),
      );
    });

    test('survives a data file whose values are not numbers', async ({ page }) => {
      const viewer = new EscherViewerPage(page);
      await viewer.goto();
      await viewer.loadMap('qa_escher_map.json');

      await viewer.loadReactionData('invalid-coercion-types.json');

      await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
      await viewer.openMenu('Data');
      await expect(viewer.menuBar).toBeVisible();
    });

    test('survives an empty data object', async ({ page }) => {
      const viewer = new EscherViewerPage(page);
      await viewer.goto();
      await viewer.loadMap('qa_escher_map.json');

      await viewer.loadReactionData('invalid-empty-object.json');

      await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
    });

    test('renders negative, zero and very large fluxes without losing the map', async ({ page }) => {
      const viewer = new EscherViewerPage(page);
      await viewer.goto();
      await viewer.loadMap('qa_escher_map.json');

      await viewer.loadReactionData('extreme-magnitudes.json');

      await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
      expect(await viewer.hasReactionDataOverlay()).toBe(true);
    });
  });
});