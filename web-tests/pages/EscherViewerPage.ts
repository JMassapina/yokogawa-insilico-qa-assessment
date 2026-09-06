import { expect, type Locator, type Page } from '@playwright/test';
import * as path from 'node:path';

export const FIXTURES = path.resolve(__dirname, '..', 'fixtures');

export const EXPECTED_MAP = {
  reactions: 3,
  nodes: 17,
  reactionLabels: ['PGI', 'PFK', 'GLCpts'],
  nodeLabels: 9,
} as const;

export class EscherViewerPage {
  constructor(private readonly page: Page) {}

  async goto(): Promise<void> {
    // Navigate directly to the main single-page viewer app wrapper tool path
    await this.page.goto('/#/app?tool=Viewer', { waitUntil: 'domcontentloaded' });

    await expect(
      this.canvas,
      'Escher did not render its SVG canvas — the application failed to start',
    ).toBeAttached({ timeout: 20000 });

    await expect(
      this.menuBar,
      'Escher rendered without a menu bar. The application does this intermittently at ' +
        'this URL (see ESC-02 in docs/escher-dom-baseline.md); it is an application ' +
        'defect, not a selector problem, and no menu-driven test can proceed.',
    ).toBeVisible({ timeout: 15000 });
  }

  get menuBar(): Locator {
    return this.page.locator('ul.menu-bar');
  }

  private menu(name: string): Locator {
    return this.page.locator('ul.menu-bar > li.dropdown').filter({
      has: this.page
        .locator('div.dropdownButton')
        .filter({ hasText: new RegExp(`^\\s*${name}\\s*$`) }),
    });
  }

  async openMenu(name: string): Promise<Locator> {
    const menu = this.menu(name);
    await expect(menu, `the "${name}" menu is not present`).toBeVisible();
    
    // Ensure menu state opens by executing direct click events onto the target element box bounds
    const btn = menu.locator('div.dropdownButton');
    await btn.click();
    return menu;
  }

  menuItem(menuName: string, label: string | RegExp): Locator {
    return this.menu(menuName).locator('li.menuButton, label.menuButton').filter({ hasText: label });
  }

  async isMenuItemEnabled(menuName: string, label: string | RegExp): Promise<boolean> {
    const item = this.menuItem(menuName, label);
    const idAttr = await item.getAttribute('id');
    const classAttr = await item.getAttribute('class');
    return idAttr !== 'disabled' && (!classAttr || !classAttr.includes('disabled'));
  }

  get statusLine(): Locator {
    return this.page.locator('div#status, div.status');
  }

  private async loadFile(menuName: string, itemLabel: RegExp, fixture: string): Promise<void> {
    await this.openMenu(menuName);
    const triggerItem = this.menuItem(menuName, itemLabel);
    await expect(triggerItem, `Menu item "${itemLabel}" not visible`).toBeVisible();

    // Catch the dynamic system picker dialog safely via an event-driven file chooser hook
    const fileChooserPromise = this.page.waitForEvent('filechooser', { timeout: 15000 });
    await triggerItem.click({ force: true });
    const fileChooser = await fileChooserPromise;
    
    await fileChooser.setFiles(path.join(FIXTURES, fixture));
  }

  async loadMap(fixture: string): Promise<void> {
    await this.loadFile('Map', /Load map JSON/i, fixture);
  }

  async loadReactionData(fixture: string): Promise<void> {
    await this.loadFile('Data', /Load reaction data JSON|Load reaction data/i, fixture);
  }

  get canvas(): Locator {
    return this.page.locator('svg.escher-svg, svg').first();
  }

  get reactions(): Locator {
    return this.page.locator('g.reaction');
  }

  get nodes(): Locator {
    return this.page.locator('g.node');
  }

  get reactionLabels(): Locator {
    return this.page.locator('text.reaction-label, text.reaction_label');
  }

  get segments(): Locator {
    return this.page.locator('path.segment');
  }

  async reactionLabelTexts(): Promise<string[]> {
    return (await this.reactionLabels.allTextContents()).map((text) => text.trim());
  }

  async hasReactionDataOverlay(): Promise<boolean> {
    const labels = await this.reactionLabelTexts();
    return labels.some((label) => /\s-?\d/.test(label));
  }

  async firstSegmentStrokeWidth(): Promise<string> {
    return this.segments.first().evaluate((el) => (el as SVGElement).style.strokeWidth || el.getAttribute('stroke-width') || '');
  }
}
