import { expect, test } from '@playwright/test';
import { EXPECTED_MAP, EscherViewerPage } from '../pages/EscherViewerPage';

/**
 * Loading a map — the rewrite of the reviewed test.
 *
 * The original asserted nothing. It clicked through a flow and logged "Map loaded" to the
 * console, which means it reported success for a blank canvas, a rendering failure, or a
 * silently rejected file. The written review is in docs/04-playwright-code-review.md; what
 * follows is what the feature actually needs covered.
 *
 * Invalid-input cases sit alongside the happy path rather than in a separate file. A
 * loader is only as good as its behaviour on the files users actually drop into it, and
 * scientists hand-edit these JSON files.
 */

test.describe('Escher viewer — loading a map', () => {
  test('renders every reaction and node in a valid map', async ({ page }) => {
    const viewer = new EscherViewerPage(page);
    await viewer.goto();

    await expect(
      viewer.reactions,
      'no reactions on the canvas before loading — the fixture is not the source of this state',
    ).toHaveCount(0);

    await viewer.loadMap('qa_escher_map.json');

    // Counts, then identities. A count alone passes when three arbitrary reactions render;
    // identities alone pass when a stale fourth is left over from a previous map.
    await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
    await expect(viewer.nodes).toHaveCount(EXPECTED_MAP.nodes);
    await expect(viewer.reactionLabels).toHaveText(EXPECTED_MAP.reactionLabels);
  });

  test('labels reactions by BiGG id, and carries no data values before data is loaded', async ({
    page,
  }) => {
    const viewer = new EscherViewerPage(page);
    await viewer.goto();
    await viewer.loadMap('qa_escher_map.json');

    // Escher renders `bigg_id`, not the human-readable `name`. Worth its own assertion:
    // it is the single most common wrong guess when writing selectors for this app, and
    // getting it wrong produces a suite that times out rather than one that fails clearly.
    const labels = await viewer.reactionLabelTexts();
    expect(labels).toEqual([...EXPECTED_MAP.reactionLabels]);
    expect(labels).not.toContain('glucose-6-phosphate isomerase');

    expect(
      await viewer.hasReactionDataOverlay(),
      'a freshly loaded map must not display flux values',
    ).toBe(false);
  });

  test('loading a second map replaces the first rather than merging into it', async ({ page }) => {
    // The state transition users hit constantly and suites usually skip: every test that
    // starts from a blank page never exercises the reset path.
    const viewer = new EscherViewerPage(page);
    await viewer.goto();

    await viewer.loadMap('qa_escher_map.json');
    await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);

    await viewer.loadMap('qa_escher_map.json');
    await expect(
      viewer.reactions,
      'reaction count grew on reload — the previous map was not discarded',
    ).toHaveCount(EXPECTED_MAP.reactions);
  });

  test.describe('invalid input', () => {
    /**
     * The rule these three share: whatever the application does with a bad file, it must
     * not end up in a state that looks like success.
     *
     * The assertions are deliberately weak on *how* the app should complain, because I do
     * not have a specification that says. They are strict on the part that is not a
     * matter of opinion — a rejected file must not leave a half-drawn map behind, and the
     * app must still be usable afterwards. Asserting a specific error message I invented
     * would be testing my preference rather than a requirement.
     */
    const badMaps = [
      {
        fixture: 'invalid-truncated.json',
        why: 'truncated JSON that cannot be parsed',
        knownDefect: undefined,
      },
      {
        fixture: 'invalid-wrong-schema.json',
        why: 'valid JSON that is not an Escher map',
        knownDefect: 'ESC-03: uncaught TypeError tears down the menu bar',
      },
      {
        fixture: 'invalid-empty-array.json',
        why: 'an empty array where a map is expected',
        knownDefect: 'ESC-03: uncaught TypeError tears down the menu bar',
      },
    ];

    for (const { fixture, why, knownDefect } of badMaps) {
      test(`stays usable and draws nothing when given ${why}`, async ({ page }) => {
        // The split in this table is the finding. Escher handles unparseable JSON
        // correctly — nothing renders, the app carries on. Valid JSON with the wrong
        // shape gets past the parse and then dies inside the renderer, taking the whole
        // menu bar with it and leaving no message on screen.
        //
        // Which is the more dangerous of the two, because a scientist who hand-edits a
        // map and breaks its structure produces exactly this file, not a truncated one.
        if (knownDefect) test.fail(true, knownDefect);

        const viewer = new EscherViewerPage(page);
        await viewer.goto();

        await viewer.loadMap(fixture);

        await expect(
          viewer.reactions,
          `${fixture} produced reactions on the canvas — a rejected file must draw nothing`,
        ).toHaveCount(0);

        // Still interactive: the failure did not take the application down with it.
        await viewer.openMenu('Map');
        await expect(viewer.menuBar).toBeVisible();
      });
    }

    test('recovers: a valid map still loads after a rejected one', async ({ page }) => {
      // The case that matters in practice. A scientist mistypes a file, gets an error, and
      // loads the right one. If the first failure left the app wedged, they restart their
      // browser and lose their session — and nobody files that as a bug, they just
      // stop trusting the tool.
      //
      // Which is what happens here: after ESC-03 there is no menu left to load from, so
      // recovery needs a page reload the user is never told to perform.
      test.fail(true, 'ESC-03: no menu bar survives the first rejected map, so retry is impossible');

      const viewer = new EscherViewerPage(page);
      await viewer.goto();

      await viewer.loadMap('invalid-wrong-schema.json');
      await viewer.loadMap('qa_escher_map.json');

      await expect(viewer.reactions).toHaveCount(EXPECTED_MAP.reactions);
      await expect(viewer.reactionLabels).toHaveText([...EXPECTED_MAP.reactionLabels]);
    });
  });
});
